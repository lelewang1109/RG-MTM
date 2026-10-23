from pathlib import Path
from collections import Counter
from zipfile import ZipFile
import os,json,hashlib,csv,re
R=Path(__file__).resolve().parents[3];D=R/'RG-MTM/docs/整理记录';T=D
ops=json.loads((T/'operations.json').read_text());before=json.loads((T/'before_inventory.json').read_text());oldhash=json.loads((T/'protected_hashes.json').read_text())
# A previous camera edit was withdrawn during the initial audit; its files already existed in reverted_source.
external={o['source']:o['destination'] for o in ops if o['action']=='external_relocated'}
def mapped(path):
 if path in external:return external[path]
 for o in ops:
  if o['action']!='move':continue
  a=o['source'];b=o['destination']
  if path==a or path.startswith(a+'/'):path=b+path[len(a):]
 return path
# Original entry-point documents were copied byte-for-byte before replacement.
backups={
 'README.md':'其他/归档/整理前说明/README.md',
 '.gitignore':'其他/归档/整理前说明/.gitignore',
}
for old,new in [('paper_revision','RG-MTM/paper'),('02-RG-MTM','RG-MTM/code'),('00-data','RG-MTM/data')]:
 for p in (R/'其他/归档/整理前说明'/new).rglob('*') if (R/'其他/归档/整理前说明'/new).exists() else []:
  if p.is_file():
   rel=p.relative_to(R/'其他/归档/整理前说明'/new)
   backups[old+'/'+str(rel)]=str(p.relative_to(R))
deleted={o['source'] for o in ops if o['action']=='delete_cache'}
missing=[];rows=[];size_changes=[]
for item in before:
 old=item['path'];new=mapped(old);p=R/new;status='当前投稿' if new.startswith('RG-MTM/') else '其他或历史归档'
 if old in backups:new=backups[old];p=R/new;status='原说明已保留；当前导航已更新'
 if new in deleted:status='删除可再生缓存'
 elif not p.exists() and not p.is_symlink():missing.append({'original':old,'expected':new});status='缺失'
 elif item['symlink']:status='相对链接已核对'
 elif p.is_file() and p.stat().st_size!=item['size']:size_changes.append({'original':old,'current':new,'before':item['size'],'after':p.stat().st_size})
 rows.append([old,new,status,item['size']])
with (D/'文件去向.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['整理前路径','整理后路径或原文备份','处置状态','原字节数']);w.writerows(rows)
# Check every originally hashed scientific record, original PDF and editable master.
changed=[];missing_hash=[];hash_verified=0
for old,h in oldhash.items():
 new=mapped(old);p=R/new
 if old in backups:p=R/backups[old]
 if mapped(old) in deleted:continue
 if not p.is_file():missing_hash.append([old,str(p.relative_to(R))]);continue
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if got==h:hash_verified+=1
 else:changed.append({'original':old,'current':str(p.relative_to(R)),'before_sha256':h,'after_sha256':got})
# TeX dependency closure, no source text or scientific assets are regenerated.
L=R/'RG-MTM/paper/manuscript/latex'
def tex_closure(stem):
 seen=set();images=set()
 def visit(p):
  p=p.with_suffix('.tex') if not p.suffix else p
  if p in seen:return
  assert p.is_file(),p;seen.add(p)
  s=re.sub(r'(?m)(?<!\\)%.*$','',p.read_text())
  for x in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',s):visit(L/x)
  for x in re.findall(r'\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}',s):
   q=L/x
   if not q.suffix:q=q.with_suffix('.pdf')
   assert q.is_file(),q;images.add(q)
 visit(L/(stem+'.tex'));return seen,images
main,mi=tex_closure('main');supp,si=tex_closure('supplement');assert len(main)==28 and len(supp)==25 and len(mi)==11 and len(si)==15
alltex=set(L.rglob('*.tex'));assert alltex==main|supp,(alltex-(main|supp))
links=[];broken=[]
for base,dirs,files in os.walk(R,followlinks=False):
 dirs[:]=[d for d in dirs if d not in {'.git','.venv','node_modules','__pycache__'}]
 for n in dirs+files:
  p=Path(base)/n
  if p.is_symlink():
   links.append(str(p.relative_to(R)))
   if not p.exists():broken.append([str(p.relative_to(R)),os.readlink(p)])
# All primary PDFs and PPTs, all algorithm source and all numeric arrays must remain original.
critical_changes=[x for x in changed if (
  x['original'].endswith(('.pptx','.pdf','.npz','.npy','.csv')) or
  x['original'].startswith(('02-RG-MTM/src/','02-RG-MTM/analysis/')) or
  (x['original'].startswith('02-RG-MTM/results/') and x['original'].endswith('.json') and not x['original'].endswith(('validation.json','rgmtm_rename_validation.json')))
 )]
report=dict(date='2026-10-23',original_files=len(before),unaccounted_files=missing,
 size_changes=size_changes,protected_files=len(oldhash),unchanged_protected_hashes=hash_verified,
 missing_protected_files=missing_hash,changed_protected_files=changed,critical_scientific_changes=critical_changes,
 main_tex_files=len(main),supplement_tex_files=len(supp),main_figures=len(mi),supplement_figures=len(si),
 reachable_tex_files=len(alltex),symlinks_checked=len(links),broken_symlinks=broken,
 operations=len(ops),operation_counts=dict(Counter(o['action'] for o in ops)),
 duplicate_bytes_removed=sum(o.get('bytes',0) for o in ops if o['action']=='deduplicate_to_symlink'),
 deleted_cache_bytes=sum(o.get('bytes',0) for o in ops if o['action']=='delete_cache'))
(D/'final_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'size_changes','changed_protected_files'}},ensure_ascii=False,indent=2))
print('Changed metadata/scripts:',len(changed),'size changes',len(size_changes))
assert not missing,missing
assert not missing_hash,missing_hash
assert not critical_changes,critical_changes
assert not broken,broken
