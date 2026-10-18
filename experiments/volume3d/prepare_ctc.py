"""Acquire real 3-D time-lapse microscopy from the Cell Tracking Challenge.

Use complete sequences 01 and 02, full spatial FOV, and documented voxel sizes.
No labels, future motion, or method scores are used to choose the inputs.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse
import io
import json
import re
import sys
import time
import urllib.request
import zipfile

import numpy as np
from PIL import Image,ImageSequence
from scipy.ndimage import map_coordinates,gaussian_filter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.volume3d.prepare import sha256

SOURCE_PAGE='https://celltrackingchallenge.net/3d-datasets/'
SOURCE_URL='https://data.celltrackingchallenge.net/training-datasets/Fluo-N3DH-CHO.zip'
DATA=ROOT/'data/real/CTC-Fluo-N3DH-CHO'
VOXEL_XYZ=np.array([.202,.202,1.])
TIME_MINUTES=9.5
SHAPE_XY=32
MAX_Z=12


def acquire(directory=DATA):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    archive=directory/'Fluo-N3DH-CHO.zip'
    if archive.exists():
        with zipfile.ZipFile(archive) as source:
            if source.testzip() is not None:raise ValueError('ZIP member CRC failed')
        return archive
    probe=urllib.request.Request(SOURCE_URL,headers={'Range':'bytes=0-0','Accept-Encoding':'identity'})
    with urllib.request.urlopen(probe,timeout=30) as response:
        if response.status!=206:raise RuntimeError('source did not honor the declared byte range')
        total=int(response.headers['Content-Range'].split('/')[-1]);etag=response.headers.get('ETag')
        response.read()
    chunk=8*1024*1024
    ranges=[(start,min(start+chunk,total)-1) for start in range(0,total,chunk)]
    record=dict(source_url=SOURCE_URL,size_bytes=total,etag=etag,parts=len(ranges),workers=4,status='running')
    status=directory/'acquisition_status.json';status.write_text(json.dumps(record,indent=2)+'\n')
    def download(bounds):
        start,end=bounds;part=directory/f'bytes_{start}_{end}.part'
        if part.exists() and part.stat().st_size==end-start+1:return start,part
        headers={'Range':f'bytes={start}-{end}','Accept-Encoding':'identity'}
        if etag:headers['If-Range']=etag
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(SOURCE_URL,headers=headers),timeout=40) as response:
                    if response.status!=206 or not response.headers['Content-Range'].startswith(f'bytes {start}-{end}/'):
                        raise RuntimeError('range or source version changed')
                    with part.open('wb') as output:
                        while block:=response.read(1024*1024):output.write(block)
                if part.stat().st_size!=end-start+1:raise ValueError('truncated range')
                print(f'Downloaded bytes {start}..{end}',flush=True)
                return start,part
            except Exception:
                if attempt==2:raise
                time.sleep(1)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            parts=[future.result() for future in as_completed([pool.submit(download,bounds) for bounds in ranges])]
        combined=directory/'Fluo-N3DH-CHO.complete.zip.part'
        with combined.open('wb') as output:
            for _,part in sorted(parts):
                with part.open('rb') as source:
                    while block:=source.read(1024*1024):output.write(block)
        if combined.stat().st_size!=total:raise ValueError('combined length mismatch')
        with zipfile.ZipFile(combined) as source:
            failed=source.testzip()
            if failed is not None:raise ValueError('ZIP member CRC failed: '+failed)
        combined.replace(archive)
        record.update(status='complete',archive_sha256=sha256(archive))
        # Only remove this downloader's temporary byte ranges after verification.
        for _,part in parts:part.unlink()
    except Exception as error:
        record.update(status='failed',error=str(error));raise
    finally:status.write_text(json.dumps(record,indent=2)+'\n')
    return archive


def read_stack(data):
    """TIFF pages are z, rows y, columns x; preserve native intensity units."""
    with Image.open(io.BytesIO(data)) as source:
        result=np.stack([np.array(page) for page in ImageSequence.Iterator(source)])
    if result.ndim!=3 or min(result.shape)<2 or not np.isfinite(result).all():
        raise ValueError('expected a finite volumetric TIFF with nontrivial xyz dimensions')
    return result


def resample_volume(volume,target_xyz):
    """Antialias and trilinearly sample the complete source FOV, endpoints fixed."""
    source=np.asarray(volume,float);nz,ny,nx=source.shape;tx,ty,tz=map(int,target_xyz)
    zz,yy,xx=np.meshgrid(np.linspace(0,nz-1,tz),np.linspace(0,ny-1,ty),np.linspace(0,nx-1,tx),indexing='ij')
    factors=(np.array([nz,ny,nx])-1)/(np.array([tz,ty,tx])-1)
    sigma=.5*np.sqrt(np.maximum(factors*factors-1,0.))
    filtered=gaussian_filter(source,sigma,mode='reflect')
    sampled=map_coordinates(filtered,[zz,yy,xx],order=1,mode='nearest',prefilter=False)
    coords=np.c_[xx.ravel()*VOXEL_XYZ[0],yy.ravel()*VOXEL_XYZ[1],zz.ravel()*VOXEL_XYZ[2]]
    spacing=(np.array([nx,ny,nz])-1)*VOXEL_XYZ/(np.array([tx,ty,tz])-1)
    return sampled,coords,spacing,sigma


def prepare(directory=DATA):
    directory=Path(directory);archive=acquire(directory);outputs=[]
    with zipfile.ZipFile(archive) as source:
        inventory=source.namelist()
        (directory/'archive_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
        for sequence in ('01','02'):
            names=sorted(name for name in inventory if re.fullmatch(r'(?:.*/)?'+sequence+r'/t\d+\.tif',name))
            if not names:raise ValueError('missing original sequence '+sequence)
            indices=[int(re.search(r't(\d+)\.tif$',name).group(1)) for name in names]
            if indices!=list(range(indices[0],indices[0]+len(indices))):raise ValueError('nonconsecutive source frames')
            fields=[];records=[];original_shape=None
            for name in names:
                raw=source.read(name);volume=read_stack(raw)
                if original_shape is None:original_shape=volume.shape
                if volume.shape!=original_shape:raise ValueError('time-varying source grid')
                field,coords,spacing,antialias=resample_volume(volume,(SHAPE_XY,SHAPE_XY,min(MAX_Z,len(volume))))
                fields.append(field)
                import hashlib
                records.append(dict(name=name,sha256=hashlib.sha256(raw).hexdigest(),shape_zyx=list(volume.shape),
                    dtype=str(volume.dtype),minimum=int(volume.min()),maximum=int(volume.max()),
                    archive_crc=source.getinfo(name).CRC))
                print(sequence,name,volume.shape,flush=True)
            # Preserve any supplied annotation resources for a separate identity
            # audit. They do not select smoothing, references, or method layouts.
            annotation_names=[name for name in inventory if re.search(r'/'+sequence+r'_GT/', '/'+name)]
            meta=dict(dataset='CTC-Fluo-N3DH-CHO-'+sequence,source_kind='real acquired fluorescence microscopy',
                source_page=SOURCE_PAGE,source_url=SOURCE_URL,source_archive_sha256=sha256(archive),sequence=sequence,
                institution='J. Essers, Department of Cell Biology, Erasmus Medical Center, Rotterdam, The Netherlands',
                specimen='Chinese Hamster Ovarian nuclei overexpressing GFP-PCNA',
                scalar='native fluorescence image intensity; no per-frame normalization',
                spatial_unit='micrometre',voxel_size_xyz_um=VOXEL_XYZ.tolist(),time_step_minutes=TIME_MINUTES,
                source_shape_tzyx=[len(fields),*original_shape],shape_tzyx=list(np.shape(fields)),indices=indices,
                physical_times_minutes=[i*TIME_MINUTES for i in indices],break_before=[],window_labels=[sequence],
                domain_xyz=np.c_[coords.min(0),coords.max(0)].tolist(),crop='none; complete FOV and all consecutive frames in this source sequence',
                interpolation='fixed endpoint-preserving trilinear resampling after separable Gaussian antialiasing',
                antialias_sigma_source_zyx=antialias.tolist(),processed_spacing_xyz_um=spacing.tolist(),
                sample_measure=float(np.prod(spacing)),domain_measure_rule='grid sample count times voxel measure, matching existing sample-bin convention',
                feature_semantics='maxima and leaf-arc supports of processed fluorescence, not a cell segmentation or physical nucleus identity',
                exact_paper_input=False,files=records,annotation_members=annotation_names,
                intended_evaluation='method comparison on shared intensity-extremum correspondences; annotations unused for selection')
            output=directory/('prepared_'+sequence+'.npz')
            np.savez_compressed(output,fields=np.array(fields),coords=coords,metadata=json.dumps(meta))
            (directory/('protocol_'+sequence+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
            outputs.append(output)
    return outputs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,default=DATA)
    args=parser.parse_args()
    for path in prepare(args.directory):print('Prepared:',path,flush=True)
