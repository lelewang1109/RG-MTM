"""Acquire selected original Tangaroa members from the ECNR public ZIP.

Anonymous HTTP Range requests avoid downloading unrelated Supernova data.
Validate central/local ZIP headers, member sizes, CRC32 and SHA256. No code
from the archive is executed. This is VTM, not the TMTM velocity magnitude.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import io
import json
import re
import struct
import time
import urllib.parse
import urllib.request
import zipfile
import zlib

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from experiments.volume3d.prepare import ROOT, sha256

SOURCE_PAGE='https://github.com/TouKaienn/ECNR'
FOLDER='https://drive.google.com/drive/folders/1Hy2QZppXBZKN6JGW6V21AA9btg5ZK1dh'
FILE_ID='1PEbEx27VPHxTwccnBB42-y9tbdxNukTP'
PROVIDER_COMMIT='4b33c3e98982f782e9ff908d66d7c23f82493f87'
DATA=ROOT/'data/real/Tangaroa-ECNR'
# Frozen coverage windows, determined before any layout or motion metric.
WINDOWS=((1,13),(70,82),(139,151))
TARGET_ZYX=(12,18,30)


def get(url,byte_range=None):
    headers={'Accept-Encoding':'identity'}
    if byte_range is not None:headers['Range']=f'bytes={byte_range[0]}-{byte_range[1]}'
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=90) as r:
                if byte_range is not None:
                    expected=f'bytes {byte_range[0]}-{byte_range[1]}/'
                    if r.status!=206 or not r.headers.get('Content-Range','').startswith(expected):
                        raise ValueError('server did not honor requested ZIP byte range')
                payload=r.read()
                if byte_range is not None and len(payload)!=byte_range[1]-byte_range[0]+1:raise ValueError('truncated range')
                return payload,dict(r.headers)
        except Exception:
            if attempt==3:raise
            time.sleep(1+attempt)


def prepare():
    DATA.mkdir(parents=True,exist_ok=True)
    provider_hashes={}
    for name in ['dataInfo/localDataInfo.json','dataio.py','utils/filesUtils.py']:
        path=DATA/('provider_'+Path(name).name)
        payload,_=get('https://raw.githubusercontent.com/TouKaienn/ECNR/'+PROVIDER_COMMIT+'/'+name)
        path.write_bytes(payload);provider_hashes[name]=sha256(path)
    info=json.loads((DATA/'provider_localDataInfo.json').read_text())['Tangaroa']
    if info['dim']!=[300,180,120] or info['vars']!=['VTM'] or info['total_samples']!=150:
        raise ValueError('provider dimensions, channel or frame count changed')
    html,_=get('https://drive.google.com/uc?export=download&id='+FILE_ID)
    params=dict(re.findall(r'type="hidden" name="([^"]+)" value="([^"]+)"',html.decode()))
    if params.get('id')!=FILE_ID:raise ValueError('expected public download form for the exact data file')
    url='https://drive.usercontent.google.com/download?'+urllib.parse.urlencode(params)
    # Learn total length from one checked response, then request EOCD+directory.
    _,header=get(url,(0,0));total=int(header['Content-Range'].split('/')[-1])
    tail_start=max(0,total-65536);tail,_=get(url,(tail_start,total-1))
    marker=tail.rfind(b'PK\x05\x06')
    if marker<0:raise ValueError('missing ZIP end-of-central-directory')
    eocd=struct.unpack('<4s4H2IH',tail[marker:marker+22])
    if eocd[1:3]!=(0,0) or eocd[3]!=eocd[4]:raise ValueError('multi-disk archive unsupported')
    directory_offset=eocd[6]
    if directory_offset<tail_start:raise ValueError('central directory exceeds tail')
    archive=zipfile.ZipFile(io.BytesIO(tail))
    inventory=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size,crc32=i.CRC,
        offset=i.header_offset+tail_start,compression=i.compress_type) for i in archive.infolist()]
    (DATA/'archive_inventory.json').write_text(json.dumps(dict(source_page=SOURCE_PAGE,folder=FOLDER,
        archive_bytes=total,central_directory_offset=directory_offset,members=inventory),indent=2)+'\n')
    items={int(re.search(r'tangaroa-(\d+)\.raw$',i['name'])[1]):i for i in inventory if re.search(r'tangaroa-\d+\.raw$',i['name'])}
    if sorted(items)!=list(range(1,151)):raise ValueError('expected 150 contiguous source frames, 1..150')
    indices=[t for a,b in WINDOWS for t in range(a,b)]
    def acquire(t):
        item=items[t];path=DATA/Path(item['name']).name
        if path.exists() and path.stat().st_size==item['size'] and zlib.crc32(path.read_bytes())==item['crc32']:return t,path,item
        offset=item['offset'];head,_=get(url,(offset,offset+29))
        h=struct.unpack('<4s5H3I2H',head)
        if h[0]!=b'PK\x03\x04' or h[3]!=item['compression'] or h[2]&1:raise ValueError('unsupported local ZIP header')
        extra,_=get(url,(offset+30,offset+29+h[-2]+h[-1]))
        if extra[:h[-2]].decode()!=item['name']:raise ValueError('local ZIP filename mismatch')
        start=offset+30+h[-2]+h[-1]
        packed,_=get(url,(start,start+item['compressed']-1))
        if item['compression']!=8:raise ValueError('expected deflated source member')
        raw=zlib.decompress(packed,-15)
        if len(raw)!=item['size'] or zlib.crc32(raw)!=item['crc32']:raise ValueError('member length / CRC mismatch')
        part=path.with_suffix('.part');part.write_bytes(raw);part.replace(path)
        print('validated source frame',t,flush=True)
        return t,path,item
    with ThreadPoolExecutor(max_workers=4) as pool:records=sorted(pool.map(acquire,indices))
    # Match ECNR dataio.py ReadData line 168: reshape(z,y,x), transpose to
    # (x,y,z). Our input remains (z,y,x). README wording conflicts with this
    # reader; the actual published reader is the declared convention here.
    bounds=np.array([[-.35,.65],[-.3,.3],[-.5,-.3]])
    nx,ny,nz=TARGET_ZYX[::-1]
    x,y,z=[np.linspace(*b,n) for b,n in zip(bounds,[nx,ny,nz])]
    Z,Y,X=np.meshgrid(z,y,x,indexing='ij');coords=np.stack([X,Y,Z],axis=-1).reshape(-1,3)
    grid=np.array(np.meshgrid(*[np.linspace(0,n-1,m) for n,m in zip((120,180,300),TARGET_ZYX)],indexing='ij'))
    factor=np.array((120,180,300))/np.array(TARGET_ZYX)
    sigma=.5*np.sqrt(np.maximum(factor**2-1,0))
    fields=[];source_records=[]
    for t,path,item in records:
        raw=np.fromfile(path,dtype='<f4').reshape(120,180,300)
        if not np.isfinite(raw).all():raise ValueError('nonfinite input')
        filtered=gaussian_filter(raw,sigma,mode='reflect')
        fields.append(map_coordinates(filtered,grid,order=1,mode='nearest',prefilter=False))
        source_records.append(dict(index=t,filename=path.name,sha256=sha256(path),crc32=item['crc32'],
            bytes=path.stat().st_size,min=float(raw.min()),max=float(raw.max())))
    metadata=dict(dataset='Tangaroa-ECNR-VTM',source_page=SOURCE_PAGE,source_url=FOLDER,
        original_provider='https://www.vc.tf.fau.de/publications/datasets/',
        source_kind='real 3-D time-dependent Gerris research-vessel flow simulation',scalar='VTM (vorticity magnitude), per ECNR localDataInfo.json',
        version_note='Same Tangaroa simulation family as TMTM; ECNR 150-frame VTM release, not TMTM 201-frame velocity magnitude. Not an exact replication. Negative released values imply an offset/normalization; exact provider transformation is undocumented, so values have no asserted physical units.',
        provider_commit=PROVIDER_COMMIT,provider_source_sha256=provider_hashes,
        provider_scalar_note='Source includes negative values although physical vorticity magnitude is nonnegative; normalization/offset inferred, exact transform undocumented. No additional frame-wise normalization applied.',
        exact_paper_input=False,source_shape_zyx=[120,180,300],shape_tzyx=[len(fields),*TARGET_ZYX],
        source_dtype='<f4',axis_convention='ECNR dataio.py ReadData reshape(z,y,x); README prose conflicts, reader convention explicitly adopted',
        source_reader_url='https://github.com/TouKaienn/ECNR/blob/main/dataio.py',
        bounds_xyz=bounds.tolist(),coordinate_note='FAU Tangaroa regular-grid physical bounding box; assumed same extent for ECNR release',
        indices=indices,windows=[list(w) for w in WINDOWS],break_before=[12,24],window_labels=['early','middle','late'],
        sample_measure=float((x[1]-x[0])*(y[1]-y[0])*(z[1]-z[0])),
        antialias_sigma_source_zyx=sigma.tolist(),resampling='full spatial domain; fixed Gaussian antialias then trilinear sampling; no per-frame normalization',
        selection='Three frozen 12-frame coverage windows; no physical stage labels or result-based frame selection',source_records=source_records)
    (DATA/'protocol.json').write_text(json.dumps(metadata,indent=2)+'\n')
    target=DATA/'prepared_vtm_36.npz'
    np.savez_compressed(target,fields=np.array(fields,dtype=float),coords=coords,metadata=json.dumps(metadata))
    (DATA/'acquisition_status.json').write_text(json.dumps(dict(status='complete',frames=len(fields),
        archive_bytes=total,archive_fully_downloaded=False,checks='central/local ZIP headers, selected member CRC32, sizes, SHA256',
        prepared_sha256=sha256(target)),indent=2)+'\n')
    print(target,flush=True)


if __name__=='__main__':prepare()
