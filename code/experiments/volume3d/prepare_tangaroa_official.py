"""FAU official Tangaroa velocity -> speed, first 12 continuous volumes.

Use the public share's normal anonymous session. HTTP Range + ZIP64 directory
allow selecting individual Amira members without fetching a 14 GB archive.
No credentials, downloaded programs, or changes to the remote server are used.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import struct
import time
import zipfile
import zlib

import requests
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from experiments.volume3d.prepare import ROOT,sha256,read_amira_vector

SOURCE_PAGE='https://www.vc.tf.fau.de/publications/datasets/'
SOURCE_URL='https://gofile.me/6LCdM/B0QjKMfKX'
SHARE='B0QjKMfKX'
ALIAS='6LCdM'
ARCHIVE='tangaroa3d_am.zip'
DATA=ROOT/'data/real/Tangaroa-FAU'
TARGET_ZYX=(12,18,30)
FRAME_COUNT=12  # Fixed before layouts; source t=0.00,0.01,...,0.11.


class SavedTail:
    """Expose absolute ZIP64 offsets while keeping only the saved archive tail."""
    def __init__(self,tail,total):self.tail=tail;self.total=total;self.start=total-len(tail);self.pos=0
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else (self.pos if whence==1 else self.total)+offset
        return self.pos
    def tell(self):return self.pos
    def seekable(self):return True
    def read(self,n=-1):
        n=self.total-self.pos if n<0 else n
        if self.pos<self.start:raise ValueError('central directory exceeds saved ZIP tail')
        value=self.tail[self.pos-self.start:self.pos-self.start+n];self.pos+=len(value);return value


def public_session():
    payload=[dict(version=1,command='get_server_info',stop_when_error=False,stop_when_success=False,
        id='file_sharing_https',serverID=ALIAS,is_gofile=True,path=ALIAS)]
    site='global.quickconnect.to'
    for _ in range(3):
        r=requests.post('https://'+site+'/Serv.php',data=json.dumps(payload),timeout=30);r.raise_for_status()
        info=r.json()[0]
        if info.get('errno')==0:break
        sites=info.get('sites',[])
        if not sites:raise RuntimeError('official share discovery unavailable: '+str(info.get('errno')))
        site=sites[0]
    else:raise RuntimeError('official share discovery did not resolve')
    host=info['smartdns']['host'];port=info['service']['port']
    base=f'https://{host}:{port}'
    session=requests.Session()
    session.get(base+'/sharing/'+SHARE,timeout=30).raise_for_status()
    login=session.post(base+'/sharing/webapi/entry.cgi',data=dict(api='SYNO.Core.Sharing.Login',method='login',
        version=1,sharing_id=json.dumps(SHARE)),headers={'X-SYNO-SHARING':SHARE},timeout=30)
    login.raise_for_status()
    if not login.json().get('success'):raise RuntimeError('public anonymous sharing session failed')
    session.get(base+'/fsdownload/'+SHARE+'/tangaroa3d',timeout=30).raise_for_status()
    params=dict(api='SYNO.FolderSharing.Download',version=2,method='download',mode='download',
        path=json.dumps(['/tangaroa3d/'+ARCHIVE]),dlname=json.dumps(ARCHIVE),_sharing_id=json.dumps(SHARE),stdhtml='true')
    request=requests.Request('GET',base+'/fsdownload/webapi/file_download.cgi/'+ARCHIVE,params=params).prepare()
    return session,request.url


def read_range(session,url,start,end):
    for attempt in range(4):
        try:
            r=session.get(url,headers={'Range':f'bytes={start}-{end}','Accept-Encoding':'identity'},timeout=(20,90))
            r.raise_for_status()
            if r.status_code!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/'):
                raise ValueError('official server did not honor byte range')
            if len(r.content)!=end-start+1:raise ValueError('truncated archive byte range')
            return r.content,r.headers
        except Exception:
            if attempt==3:raise
            time.sleep(1+attempt)


def prepare():
    DATA.mkdir(parents=True,exist_ok=True)
    session,url=public_session()
    _,headers=read_range(session,url,0,0);total=int(headers['Content-Range'].split('/')[-1])
    tail,_=read_range(session,url,total-65536,total-1)
    archive=zipfile.ZipFile(SavedTail(tail,total))
    inventory=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size,offset=i.header_offset,
        crc32=i.CRC,compression=i.compress_type) for i in archive.infolist()]
    items=sorted([i for i in inventory if i['name'].endswith('.am')],key=lambda i:float(Path(i['name']).stem.split('tangaroa-')[-1]))
    times=[float(Path(i['name']).stem.split('tangaroa-')[-1]) for i in items]
    if len(items)!=201 or not np.allclose(times,np.arange(201)*.01,rtol=0,atol=1e-12):
        raise ValueError('expected official 201 volumes from t=0 to 2 in steps of .01')
    (DATA/'archive_inventory.json').write_text(json.dumps(dict(source_page=SOURCE_PAGE,source_url=SOURCE_URL,
        archive=ARCHIVE,archive_bytes=total,etag=headers.get('ETag'),members=inventory),indent=2)+'\n')
    chosen=items[:FRAME_COUNT]
    def acquire(item):
        path=DATA/Path(item['name']).name
        if path.exists() and path.stat().st_size==item['size'] and zlib.crc32(path.read_bytes())==item['crc32']:return path,item
        start=item['offset'];head,_=read_range(session,url,start,start+29)
        h=struct.unpack('<4s5H3I2H',head)
        if h[0]!=b'PK\x03\x04' or h[3]!=item['compression'] or h[2]&1:raise ValueError('unsupported local ZIP header')
        extra,_=read_range(session,url,start+30,start+29+h[-2]+h[-1])
        if extra[:h[-2]].decode()!=item['name']:raise ValueError('ZIP local/central filename mismatch')
        payload_start=start+30+h[-2]+h[-1]
        packed,_=read_range(session,url,payload_start,payload_start+item['compressed']-1)
        if item['compression']!=8:raise ValueError('expected deflated Amira member')
        raw=zlib.decompress(packed,-15)
        if len(raw)!=item['size'] or zlib.crc32(raw)!=item['crc32']:raise ValueError('source member size / CRC mismatch')
        part=path.with_suffix('.part');part.write_bytes(raw);part.replace(path)
        print('validated official volume',path.name,flush=True);return path,item
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(acquire,chosen))
    fields=[];source_records=[];coords=None;source_bounds=None
    for path,item in records:
        velocity,bounds=read_amira_vector(path)
        if velocity.shape!=(120,180,300,3):raise ValueError('official spatial shape differs from 300x180x120')
        if source_bounds is not None:np.testing.assert_array_equal(bounds,source_bounds)
        source_bounds=bounds
        # Magnitude MUST be formed on the source grid before scalar filtering.
        scalar=np.linalg.norm(velocity,axis=-1)
        factor=np.array(scalar.shape)/np.array(TARGET_ZYX)
        sigma=.5*np.sqrt(np.maximum(factor**2-1,0))
        filtered=gaussian_filter(scalar,sigma,mode='reflect')
        grid=np.array(np.meshgrid(*[np.linspace(0,n-1,m) for n,m in zip(scalar.shape,TARGET_ZYX)],indexing='ij'))
        fields.append(map_coordinates(filtered,grid,order=1,mode='nearest',prefilter=False))
        x,y,z=[np.linspace(bounds[2*k],bounds[2*k+1],m) for k,m in enumerate(TARGET_ZYX[::-1])]
        Z,Y,X=np.meshgrid(z,y,x,indexing='ij');coords=np.stack([X,Y,Z],axis=-1).reshape(-1,3)
        source_records.append(dict(filename=path.name,source_time=float(path.stem.split('tangaroa-')[-1]),
            sha256=sha256(path),crc32=item['crc32'],bytes=path.stat().st_size,
            speed_min=float(scalar.min()),speed_max=float(scalar.max()),velocity_bounds_xyz=bounds.tolist()))
    metadata=dict(dataset='Tangaroa-FAU-speed',source_page=SOURCE_PAGE,source_url=SOURCE_URL,
        source_kind='official acquired 3-D time-dependent Gerris velocity simulation',scalar='sqrt(u*u+v*v+w*w) on full source grid',
        version_note='Official 300x180x120x201 velocity release matches TMTM dataset dimensions and speed channel. This experiment uses the first 12 volumes and its own explicit spatial processing, not the full original experiment.',
        exact_paper_input=False,official_dataset_dimensions_match=True,source_total_frames=201,
        source_shape_zyx=[120,180,300],shape_tzyx=[len(fields),*TARGET_ZYX],indices=list(range(FRAME_COUNT)),
        times=times[:FRAME_COUNT],source_time_step=.01,break_before=[],window_labels=['first 12 continuous official times'],
        source_bounds_xyz=source_bounds.tolist(),sample_measure=float((x[1]-x[0])*(y[1]-y[0])*(z[1]-z[0])),
        axis_convention='Amira source header and x-fastest binary XYZ vector components, preserved as ZYX grid',
        antialias_sigma_source_zyx=sigma.tolist(),resampling='source speed then fixed full-domain Gaussian antialias and trilinear sampling; no per-frame normalization',
        selection='First 12 continuous frames fixed before layouts; no ROI or performance-driven time selection',source_records=source_records,
        preparation_source=str(Path(__file__).relative_to(ROOT)),preparation_sha256=sha256(Path(__file__)))
    (DATA/'protocol.json').write_text(json.dumps(metadata,indent=2)+'\n')
    target=DATA/'prepared_speed_12.npz'
    np.savez_compressed(target,fields=np.array(fields),coords=coords,metadata=json.dumps(metadata))
    (DATA/'acquisition_status.json').write_text(json.dumps(dict(status='complete',frames=len(fields),source_total_frames=201,
        archive_bytes=total,archive_fully_downloaded=False,checks='ZIP64 directory, local headers, source member CRC32, sizes and SHA256',
        prepared_sha256=sha256(target)),indent=2)+'\n')
    print(target,flush=True)


if __name__=='__main__':prepare()
