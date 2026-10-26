"""Read-only verification of the portable research snapshot."""
from pathlib import Path
from pathlib import PurePosixPath
import hashlib
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'docs/github/PUBLISHED_FILES.sha256'
count=0
omitted=0
# Git archive/GitHub Download ZIP omit only the explicit directory rules below.
# A Git checkout always requires the complete manifest, including large results.
archive=not (ROOT/'.git').exists()
excluded=[]
for line in (ROOT/'.gitattributes').read_text().splitlines():
 parts=line.split()
 if len(parts)==2 and parts[1]=='export-ignore':
  excluded.append(parts[0].lstrip('/').rstrip('/'))
for line in manifest.read_text().splitlines():
 expected,name=line.split('  ',1);p=ROOT/name
 if archive and not p.exists() and any(PurePosixPath(name).match(d) or name.startswith(d+'/') for d in excluded):
  omitted+=1
  continue
 assert p.is_file(),f'Missing published file: {name}'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,f'Changed published file: {name}'
 count+=1
for p in ROOT.rglob('*'):
 if '.git' in p.relative_to(ROOT).parts or '.venv' in p.relative_to(ROOT).parts:continue
 if p.is_symlink():
  assert p.exists(),f'Broken link: {p.relative_to(ROOT)}'
  assert p.resolve().is_relative_to(ROOT),f'External link: {p.relative_to(ROOT)}'
 if p.is_file():assert p.stat().st_size<100*1024**2,f'Oversized Git blob: {p.relative_to(ROOT)}'
print(f'Release verified: {count} unchanged files; all links resolve inside the repository.')
if omitted:
 print(f'Research ZIP: {omitted} duplicate/historical files omitted by export-ignore; published data, current paper, experiment code and results are retained. See docs/DOWNLOADS.md.')
