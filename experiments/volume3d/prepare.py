"""Public SquareCylinder acquisition and explicit 3-D scalar preprocessing.

The 102-frame public velocity volume is NOT the 508-frame scalar input of TMTM.
Q is derived on the source grid before spatial resampling. No file is executed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import urllib.request
import struct
import zlib
from datetime import datetime,timezone

import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[2]
SOURCE_PAGE='https://www.csc.kth.se/~weinkauf/notes/squarecylinder.html'
SOURCE_URL='https://www.csc.kth.se/~weinkauf/datasets/SquareCylinder.7z'
DATA=ROOT/'data/real/SquareCylinder'
# Frozen coverage windows: early/middle/late, independent of any method outcome.
WINDOWS=((0,12),(45,57),(90,102))


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def validate_archive(path):
    """Reject truncated 7z downloads before renaming or extracting them."""
    path=Path(path)
    with path.open('rb') as source:
        header=source.read(32)
        if len(header)!=32 or header[:6]!=b'7z\xbc\xaf\x27\x1c':raise ValueError('invalid 7z signature')
        if zlib.crc32(header[12:])!=struct.unpack('<I',header[8:12])[0]:raise ValueError('7z start-header CRC mismatch')
        offset,size,expected_crc=struct.unpack('<QQI',header[12:]);expected=32+offset+size
        if path.stat().st_size!=expected:
            raise ValueError(f'truncated 7z: {path.stat().st_size} bytes, expected {expected}')
        source.seek(32+offset)
        if zlib.crc32(source.read(size))!=expected_crc:raise ValueError('7z next-header CRC mismatch')
    return expected


def read_amira_vector(path):
    """Read uncompressed binary AmiraMesh float[3], x fastest, then y,z."""
    raw=Path(path).read_bytes()
    marker=re.search(rb'\n@1\r?\n',raw)
    if marker is None:raise ValueError('missing Amira data marker')
    header=raw[:marker.start()].decode('ascii')
    dims=re.search(r'define\s+Lattice\s+(\d+)\s+(\d+)\s+(\d+)',header)
    bbox=re.search(r'BoundingBox\s+([^\n}]+)',header)
    if dims is None or bbox is None or not re.search(r'float\s*\[3\]',header):
        raise ValueError('expected AmiraMesh float[3] lattice with BoundingBox')
    if 'HxZip' in header or 'HxByteRLE' in header:raise ValueError('compressed Amira payload unsupported')
    if 'BINARY-LITTLE-ENDIAN' in header:dtype='<f4'
    elif re.search(r'AmiraMesh\s+(?:3D\s+)?BINARY\s',header):dtype='>f4'
    else:raise ValueError('unrecognized Amira byte order')
    nx,ny,nz=map(int,dims.groups());bounds=np.array([float(x) for x in bbox.group(1).strip().rstrip(',').split()])
    if bounds.size!=6:raise ValueError('expected six BoundingBox values')
    count=nx*ny*nz*3
    v=np.frombuffer(raw,dtype=dtype,count=count,offset=marker.end()).reshape(nz,ny,nx,3).astype(float)
    if not np.isfinite(v).all():raise ValueError('nonfinite source velocities')
    return v,bounds


def q_criterion(velocity,spacing_xyz):
    """Q = -.5 tr(J²), equivalent to .5(||Omega||²-||S||²).

    Centered differences internally; second-order one-sided at domain boundaries.
    Source periodicity is not wrapped; boundary-supported features are flagged.
    """
    v=np.asarray(velocity,float)
    if v.ndim!=4 or v.shape[-1]!=3 or min(v.shape[:3])<3:
        raise ValueError('expected Z×Y×X×3 velocity with >=3 samples per axis')
    dx,dy,dz=spacing_xyz
    if not np.isfinite([dx,dy,dz]).all() or min(dx,dy,dz)<=0:raise ValueError('positive spatial spacing required')
    J=np.empty((*v.shape[:3],3,3))
    for c in range(3):
        gz,gy,gx=np.gradient(v[...,c],dz,dy,dx,edge_order=2)
        J[...,c,0]=gx;J[...,c,1]=gy;J[...,c,2]=gz
    return -.5*np.einsum('...ij,...ji->...',J,J)


def acquire(directory=DATA):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    archive=directory/'SquareCylinder.7z'
    if not archive.exists():
        part=archive.with_suffix('.7z.part')
        existing=part.stat().st_size if part.exists() else 0
        request=urllib.request.Request(SOURCE_URL,headers={'Range':f'bytes={existing}-','Accept-Encoding':'identity'} if existing else {})
        target=part
        record=dict(source_url=SOURCE_URL,started_utc=datetime.now(timezone.utc).isoformat(),previous_bytes=existing,status='running')
        try:
            with urllib.request.urlopen(request,timeout=60) as response:
                status=response.status;record.update(http_status=status,response_headers=dict(response.headers))
                if existing and status==206:
                    if not response.headers.get('Content-Range','').startswith(f'bytes {existing}-'):
                        raise ValueError('server resumed at an unexpected byte offset')
                    mode='ab'
                else:
                    # A 200 response to Range starts at byte zero. Preserve the
                    # old partial rather than appending a second 7z header.
                    if existing:target=directory/('SquareCylinder.retry-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'.7z.part')
                    mode='wb'
                record['partial_path']=str(target)
                with target.open(mode) as output:
                    while block:=response.read(1024*1024):output.write(block)
            validate_archive(target);target.replace(archive);record['status']='complete'
        except Exception as error:
            record.update(status='failed',error=str(error),saved_bytes=target.stat().st_size if target.exists() else 0)
            raise
        finally:
            (directory/'acquisition_status.json').write_text(json.dumps(record,indent=2)+'\n')
    validate_archive(archive)
    unpacked=directory/'unpacked'
    if not (unpacked/'.complete').exists():
        import py7zr
        with py7zr.SevenZipFile(archive,'r') as source:
            for name in source.getnames():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('unsafe archive member')
            source.extractall(path=unpacked)
        (unpacked/'.complete').write_text(sha256(archive)+'\n')
    return archive,unpacked


def prepare(directory=DATA,shape_xyz=(28,14,10)):
    directory=Path(directory);archive,unpacked=acquire(directory)
    files=[]
    for path in unpacked.rglob('*'):
        if path.is_file() and path.suffix.lower() in ('.am','.amiramesh'):
            # Exclude cylinder surfaces and other non-vector objects.
            with path.open('rb') as f:head=f.read(2048)
            if b'define Lattice' in head and re.search(rb'float\s*\[3\]',head):files.append(path)
    def numeric_key(path):return [int(v) if v.isdigit() else v for v in re.split(r'(\d+)',path.name)]
    files.sort(key=numeric_key)
    if len(files)!=102:raise ValueError(f'public source should contain 102 vector frames, found {len(files)}')
    indices=[i for start,end in WINDOWS for i in range(start,end)]
    nx,ny,nz=shape_xyz
    x=np.linspace(-2.,20.,nx);y=np.linspace(-4.,4.,ny);z=np.linspace(0.,6.,nz)
    Z,Y,X=np.meshgrid(z,y,x,indexing='ij');points=np.c_[Z.ravel(),Y.ravel(),X.ravel()]
    fields=[];records=[]
    for i in indices:
        v,bounds=read_amira_vector(files[i]);sz,sy,sx=v.shape[:3]
        spacing=np.diff(bounds.reshape(3,2),axis=1).ravel()/(np.array([sx,sy,sz])-1)
        q=q_criterion(v,spacing)
        axes=[np.linspace(bounds[4],bounds[5],sz),np.linspace(bounds[2],bounds[3],sy),np.linspace(bounds[0],bounds[1],sx)]
        sampled=RegularGridInterpolator(axes,q,bounds_error=True)(points).reshape(nz,ny,nx)
        fields.append(sampled)
        records.append(dict(source_index=i,name=str(files[i].relative_to(unpacked)),sha256=sha256(files[i]),
                            source_q_min=float(q.min()),source_q_max=float(q.max())))
        print(f'Q source {i}: range {q.min():.5g} .. {q.max():.5g}',flush=True)
    coords=np.c_[X.ravel(),Y.ravel(),Z.ravel()]
    meta=dict(dataset='Cylinder-public-102-Q',source_page=SOURCE_PAGE,source_url=SOURCE_URL,
              archive_sha256=sha256(archive),source_shape_tzyx=[102,48,64,192],paper_shape_tzyx=[508,48,64,135],
              exact_paper_input=False,scalar='Q = -0.5 trace(J^2), source-grid physical derivatives',
              windows=[list(w) for w in WINDOWS],indices=indices,break_before=[12,24],
              window_labels=['early','middle','late'],phase_interpretation='coverage windows, not verified physical phase boundaries',
              shape_tzyx=list(np.shape(fields)),domain_xyz=[[-2.,20.],[-4.,4.],[0.,6.]],
              crop='x >= -2, fixed a priori; all sampled y and z retained',
              interpolation='trilinear Q after source-grid derivatives; endpoints included',
              source_boundary_derivatives='second-order one-sided, periodic z not wrapped',
              sample_measure=float((x[1]-x[0])*(y[1]-y[0])*(z[1]-z[0])),
              domain_measure_rule='number of grid samples times sample measure; same sample-bin convention as 2-D experiments',
              files=records)
    output=directory/'prepared_q_36.npz'
    np.savez_compressed(output,fields=np.array(fields),coords=coords,metadata=json.dumps(meta))
    (directory/'source_protocol.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(output,flush=True)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=DATA)
    args=parser.parse_args();prepare(args.directory)
