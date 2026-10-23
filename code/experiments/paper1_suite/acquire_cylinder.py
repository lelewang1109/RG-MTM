"""Resume the original author's 3-D square-cylinder archive from KTH mirror.

The old incomplete file is preserved. Every appended range is checked; the
complete archive is validated by its 7z headers and every extracted-file CRC.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json, os, shutil, time
import requests
import py7zr
from experiments.volume3d.prepare import ROOT, DATA, sha256, validate_archive
from experiments.volume3d.run_paper import dump

URL='https://people.kth.se/~weinkauf/datasets/SquareCylinder.7z'
EXPECTED=542415447
CHUNK=8*1024*1024


def acquire():
    DATA.mkdir(parents=True,exist_ok=True)
    target=DATA/'SquareCylinder.7z'
    prefix=DATA/'SquareCylinder.7z.part'
    stage=DATA/'SquareCylinder.mirror-resume.7z.part'
    chunks=DATA/'mirror_chunks';chunks.mkdir(exist_ok=True)
    proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    proxies={'https':proxy} if proxy else None
    def get_range(start,end):
        for attempt in range(4):
            try:
                response=requests.get(URL,headers={'Range':f'bytes={start}-{end}','Accept-Encoding':'identity'},
                    proxies=proxies,timeout=(20,60))
                response.raise_for_status()
                if response.status_code!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{EXPECTED}':
                    raise ValueError('mirror did not return the exact requested range')
                if len(response.content)!=end-start+1:raise ValueError('incomplete mirror chunk')
                return response.content
            except Exception:
                if attempt==3:raise
                time.sleep(1+attempt)
    status=dict(url=URL,expected_bytes=EXPECTED,old_partial_preserved=True,status='running')
    status_file=DATA/'mirror_acquisition_20261022.json'
    dump(status_file,status)
    if not target.exists():
        if not stage.exists():
            if prefix.exists():
                # Confirm archive identity before reusing an old prefix. Final
                # decompression CRC validates all reused bytes, not just probes.
                with prefix.open('rb') as f:
                    for offset in [0,prefix.stat().st_size//2,prefix.stat().st_size-256]:
                        f.seek(offset)
                        if f.read(256)!=get_range(offset,offset+255):raise ValueError('mirror/prefix identity probe differs')
                shutil.copyfile(prefix,stage)
            else:stage.touch()
        start=stage.stat().st_size
        ranges=[(i,min(EXPECTED-1,i+CHUNK-1)) for i in range(start,EXPECTED,CHUNK)]
        def chunk(pair):
            a,b=pair;p=chunks/f'{a}-{b}.bin'
            if not p.exists() or p.stat().st_size!=b-a+1:
                tmp=p.with_suffix('.tmp');tmp.write_bytes(get_range(a,b));tmp.replace(p)
            return a,b,p
        completed=0
        with ThreadPoolExecutor(max_workers=6) as pool:
            for future in as_completed([pool.submit(chunk,p) for p in ranges]):
                a,b,p=future.result();completed+=b-a+1
                status.update(downloaded_new_bytes=completed,reused_prefix_bytes=start)
                dump(status_file,status);print('download',start+completed,'/',EXPECTED,flush=True)
        with stage.open('ab') as f:
            for a,b in ranges:
                with (chunks/f'{a}-{b}.bin').open('rb') as part:shutil.copyfileobj(part,f)
        validate_archive(stage);stage.replace(target)
    validate_archive(target)
    unpacked=DATA/'unpacked'
    if not (unpacked/'.complete').exists():
        with py7zr.SevenZipFile(target,'r') as archive:
            for name in archive.getnames():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('unsafe member')
            archive.extractall(unpacked)
        (unpacked/'.complete').write_text(sha256(target)+'\n')
    status.update(status='complete_extracted',archive_sha256=sha256(target),bytes=target.stat().st_size,
                  unpacked_files=len([p for p in unpacked.rglob('*') if p.is_file()]))
    dump(status_file,status)
    print(json.dumps(status,indent=2))


if __name__=='__main__':acquire()
