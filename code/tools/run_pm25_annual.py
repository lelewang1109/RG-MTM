"""Run the complete 366-day input in an isolated result directory.
No historical aggregate JSON or prior source arrays are overwritten.
"""
from pathlib import Path
import sys,json,time,hashlib,shutil,importlib,runpy,os
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'analysis'),str(ROOT/'tools'),str(ROOT/'src'),str(ROOT)]
import pm25_annual as ann,public_scalar as ps,prepare_cn_pm25 as cn
ann.register();out=ann.OUT;out.mkdir(exist_ok=True);plan=dict(dataset=ann.NAME,status='preparing',frames=366,region=dict(lon=[102,114],lat=[28,38]),fixed_sigma_km=100,grid=[49,49],stages=[],source_restoration=[])
def save():(out/'run.json').write_text(json.dumps(plan,indent=2)+'\n')
save();src=ROOT.parent/'data/real/CN-Reanalysis/2000';archive=ROOT.parents[1]/'其他/其他研究数据/CN-Reanalysis-unused'
for p in sorted(archive.glob('2000????.nc')):
 dst=src/p.name
 if not dst.exists():shutil.move(str(p),str(dst));plan['source_restoration'].append(dict(file=p.name,from_path=str(p),to_path=str(dst)))
assert len(list(src.glob('2000????.nc')))==366
save();cn.prepare(src,ann.NAME)
# Construct once and reuse the identical source scene in all stages of this process.
import replicate as rp
cached=ps.load(ann.NAME);rp.LOADERS[ann.NAME]=lambda:cached
import pickle
with (out/'dataset.pkl').open('wb')as f:pickle.dump(cached,f)
import numpy as np
np.savez_compressed(out/'processed_fields.npz',fields=cached['sc']['fields'],coords=cached['sc']['coords'],dates=np.array(cached['sc']['dates']))
plan['leaves']=[min(map(len,cached['sc']['ids'])),max(map(len,cached['sc']['ids']))];plan['status']='running';save();print('Prepared full year',plan['leaves'],flush=True)
# These modules all honor their own OUT; redirect only new outputs.
mods=['task_reference','general_method','relax_hierarchy','replicate','evaluation','attainable','filling','pointcert','native_merge_errors']
for name in mods:
 m=importlib.import_module(name)
 if hasattr(m,'OUT'):m.OUT=out
for stage in ['replicate','evaluation','filling','pointcert','attainable','native_merge_errors']:
 t=time.perf_counter();print('RUN',stage,flush=True)
 if stage=='replicate':rp.run(ann.NAME)
 elif stage=='attainable':
  m=importlib.import_module(stage);r=m.analyse(ann.NAME);(out/'attainable_pm25_2000.json').write_text(json.dumps(r,indent=2,default=float)+'\n')
 elif stage=='native_merge_errors':
  # Its historical CLI has a ROOT-relative output; the independent saved-array
  # measurement is performed in export_pm25_annual.py instead of patching ROOT.
  pass
 else:
  m=importlib.import_module(stage);sys.argv=[stage,ann.NAME];m.main()
 plan['stages'].append(dict(stage=stage,seconds=time.perf_counter()-t,status='complete'if stage!='native_merge_errors'else'deferred_to_export'));save()
plan['status']='computed';plan['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),ROOT/'analysis/pm25_annual.py',*[ROOT/'analysis'/(n+'.py')for n in mods]]};save();print('Annual scientific stages complete',flush=True)
