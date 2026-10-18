"""Acquire only official Tangaroa paper snapshots 0/100/200, with CRC checks."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import struct
import zipfile
import zlib

from experiments.volume3d.prepare import sha256
from experiments.volume3d.prepare_tangaroa_official import DATA,public_session,read_range,SavedTail,SOURCE_URL

INDICES=(0,100,200)


def fetch():
    DATA.mkdir(parents=True,exist_ok=True)
    inventory_path=DATA/'archive_inventory.json'
    inventory=json.loads(inventory_path.read_text()) if inventory_path.exists() else None
    def valid(item):
        p=DATA/Path(item['name']).name
        return p.exists() and p.stat().st_size==item['size'] and zlib.crc32(p.read_bytes())==item['crc32']
    def select(inv):
        members={round(float(Path(r['name']).stem.split('tangaroa-')[-1])*100):r
            for r in inv['members'] if r['name'].endswith('.am')}
        if sorted(members)!=list(range(201)):raise ValueError('expected official 201 time steps')
        return [members[i] for i in INDICES]
    chosen=select(inventory) if inventory else []
    if not chosen or not all(map(valid,chosen)):
        session,url=public_session()
        _,headers=read_range(session,url,0,0);total=int(headers['Content-Range'].split('/')[-1])
        tail,_=read_range(session,url,total-65536,total-1)
        archive=zipfile.ZipFile(SavedTail(tail,total))
        fresh=dict(source_url=SOURCE_URL,archive='tangaroa3d_am.zip',archive_bytes=total,
            members=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size,offset=i.header_offset,
                crc32=i.CRC,compression=i.compress_type) for i in archive.infolist()])
        if inventory and fresh['members']!=inventory['members']:
            raise ValueError('official archive directory changed; do not silently overwrite previous provenance')
        if not inventory:inventory_path.write_text(json.dumps(fresh,indent=2)+'\n')
        inventory=fresh;chosen=select(inventory)
        def acquire(item):
            if valid(item):return
            start=item['offset'];head,_=read_range(session,url,start,start+29)
            h=struct.unpack('<4s5H3I2H',head)
            if h[0]!=b'PK\x03\x04' or h[3]!=8 or h[2]&1:raise ValueError('unsupported ZIP member')
            extra,_=read_range(session,url,start+30,start+29+h[-2]+h[-1])
            if extra[:h[-2]].decode()!=item['name']:raise ValueError('ZIP filename mismatch')
            offset=start+30+h[-2]+h[-1]
            packed,_=read_range(session,url,offset,offset+item['compressed']-1)
            raw=zlib.decompress(packed,-15)
            if len(raw)!=item['size'] or zlib.crc32(raw)!=item['crc32']:raise ValueError('invalid source CRC/length')
            p=DATA/Path(item['name']).name;part=p.with_suffix('.snapshot.part');part.write_bytes(raw);part.replace(p)
        with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(acquire,chosen))
    record=dict(source_url=SOURCE_URL,archive_bytes=inventory['archive_bytes'],source_archive_volumes=201,
        inventory_sha256=sha256(inventory_path),fetch_source_sha256=sha256(__file__),
        records=[dict(paper_index=i,filename=Path(r['name']).name,source_time=i*.01,bytes=r['size'],
            crc32=r['crc32'],sha256=sha256(DATA/Path(r['name']).name)) for i,r in zip(INDICES,chosen)])
    (DATA/'paper_snapshot_acquisition.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Validated official original-resolution snapshots:',list(INDICES))
    return record


if __name__=='__main__':fetch()
