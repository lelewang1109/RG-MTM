"""Full 201-frame official Tangaroa, original grid and author scalar operations.

No Gaussian filtering, spatial resampling, cropping, or leaf-count selection.
Each independent ZIP member is resumable in 8 MiB ranges and CRC-checked.
Use the user's configured HTTPS proxy through ordinary proxy environment vars
when required by their network; no system proxy settings are changed here.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import argparse,json,os,struct,threading,time,zlib
import numpy as np
import requests
from experiments.volume3d.prepare import ROOT,sha256,read_amira_vector
from experiments.volume3d.prepare_tangaroa_official import DATA,public_session,read_range,SOURCE_URL

OUT=DATA/'paper_full_201'


def save(path,obj):
    temp=Path(str(path)+'.tmp');temp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');temp.replace(path)


def prepare(workers=6,indices=None):
    OUT.mkdir(parents=True,exist_ok=True)
    inv_path=DATA/'archive_inventory.json';inventory=json.loads(inv_path.read_text())
    items=sorted([r for r in inventory['members'] if r['name'].endswith('.am')],key=lambda r:float(Path(r['name']).stem.split('tangaroa-')[-1]))
    assert len(items)==201
    assert all(abs(float(Path(r['name']).stem.split('tangaroa-')[-1])-i*.01)<1e-12 for i,r in enumerate(items))
    chosen=list(range(201)) if indices is None else list(indices)
    session=url=None
    def cached(item):
        p=DATA/Path(item['name']).name
        return p.exists() and p.stat().st_size==item['size'] and zlib.crc32(p.read_bytes())==item['crc32']
    if not all(cached(items[i]) for i in chosen):session,url=public_session()
    local=threading.local();started=time.time()
    protocol=dict(source_url=SOURCE_URL,source_archive_bytes=inventory['archive_bytes'],source_inventory_sha256=sha256(inv_path),
        source_shape_xyz=[300,180,120],source_frames=201,requested_indices=chosen,requested_times=[i*.01 for i in chosen],
        scalar='float32 sqrt(u*u+v*v+w*w), arithmetic in float64 before final cast',near_zero_epsilon=1e-6,
        near_zero_replacement=1.,scalar_clip=[0.,2.],tree_kind='join',spatial_resampling=False,spatial_smoothing=False,
        ttk_simplification_applied=False,prepare_source_sha256=sha256(__file__))
    save(OUT/'input_protocol.json',protocol)
    records={}
    def acquire(index):
        item=items[index];p=DATA/Path(item['name']).name
        if cached(item):return index,p
        if not hasattr(local,'session'):
            local.session=requests.Session();local.session.cookies.update(session.cookies)
        s=local.session;start=item['offset'];head,_=read_range(s,url,start,start+29)
        h=struct.unpack('<4s5H3I2H',head)
        assert h[0]==b'PK\x03\x04' and h[3]==8 and not h[2]&1
        info,_=read_range(s,url,start+30,start+29+h[-2]+h[-1]);assert info[:h[-2]].decode()==item['name']
        offset=start+30+h[-2]+h[-1];part=OUT/(p.stem+'.deflate.part')
        count=part.stat().st_size if part.exists() else 0
        if count>item['compressed']:raise ValueError('oversized resumable member')
        with part.open('ab') as f:
            while count<item['compressed']:
                end=min(count+8*1024*1024,item['compressed'])
                block,_=read_range(s,url,offset+count,offset+end-1);f.write(block);f.flush();count=end
        raw=zlib.decompress(part.read_bytes(),-15)
        if len(raw)!=item['size'] or zlib.crc32(raw)!=item['crc32']:raise ValueError('bad official member CRC/length '+p.name)
        temp=p.with_suffix('.full.part');temp.write_bytes(raw);temp.replace(p);part.unlink()
        return index,p
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(acquire,i):i for i in chosen}
        for future in as_completed(futures):
            index,path=future.result();target=OUT/f'scalar_{index:03d}.npy';meta=OUT/f'scalar_{index:03d}.json'
            if target.exists() and meta.exists():
                record=json.loads(meta.read_text())
                if record.get('prepare_source_sha256')==protocol['prepare_source_sha256'] and record.get('scalar_sha256')==sha256(target) and record['source_sha256']==sha256(path):
                    records[index]=record
                    print('validated cached frame',index,flush=True)
                    continue
            velocity,bounds=read_amira_vector(path);assert velocity.shape==(120,180,300,3)
            np.testing.assert_array_equal(bounds,[-.35,.65,-.3,.3,-.5,-.3])
            speed=np.linalg.norm(velocity,axis=-1).astype(np.float32);del velocity
            masked=int((speed<1e-6).sum());clipped=int((speed>2).sum());raw_range=[float(speed.min()),float(speed.max())]
            speed[speed<1e-6]=1.;np.clip(speed,0.,2.,out=speed)
            temp=target.with_suffix('.npy.part')
            with temp.open('wb') as f:np.save(f,speed)
            temp.replace(target)
            record=dict(index=index,time=index*.01,source_filename=path.name,source_bytes=path.stat().st_size,
                source_crc32=items[index]['crc32'],source_sha256=sha256(path),scalar_sha256=sha256(target),
                scalar_shape_zyx=list(speed.shape),bounds_xyz=bounds.tolist(),raw_range=raw_range,
                processed_range=[float(speed.min()),float(speed.max())],masked_samples=masked,clipped_samples=clipped,
                prepare_source_sha256=protocol['prepare_source_sha256'])
            save(meta,record);records[index]=record
            save(OUT/'acquisition_status.json',dict(status='running',complete_indices=sorted(records),requested_indices=chosen,elapsed_seconds=time.time()-started))
            print('prepared original-resolution paper input',index,'completed',len(records),'of',len(chosen),flush=True)
    save(OUT/'source_manifest.json',dict(protocol=protocol,records=[records[i] for i in chosen],elapsed_seconds=time.time()-started))
    save(OUT/'acquisition_status.json',dict(status='complete',complete_indices=chosen,elapsed_seconds=time.time()-started))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--indices',type=int,nargs='+');args=parser.parse_args();prepare(args.workers,args.indices)
