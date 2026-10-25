"""Independent saved-witness, provenance and delivery checks of the unified model."""
from pathlib import Path
from itertools import combinations
from math import factorial
from dataclasses import replace
from zipfile import ZipFile
import json,hashlib,sys,re,unicodedata
import numpy as np
import pymupdf
P=Path(__file__).resolve().parents[1];C=P.parent/'code';L=P/'manuscript/latex';R=C/'results/unified20261025'
sys.path.insert(0,str(C/'src'))
from rgmtm.error_budget import Parameters,constraints,checked_lp
from rgmtm.framework import merge_costs,interval_costs
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(status='passed',date='2026-10-26',frames=0,layouts=0,grid_queries=0,grid_witnesses=0,
            selected_qp_oracles=0,max_qp_gap=0.,max_scalar_cap_excess=0.,coverage={})
manifest=json.loads((R/'manifest.json').read_text())
for name,h in manifest['source_sha256'].items():assert sha(C/name)==h,name
for name,h in manifest['results_sha256'].items():assert sha(R/name)==h,name


def check(rows,j,config,p,grid=False):
 prev=None
 for t,row in enumerate(rows):
  if row is None:prev=None;continue
  f=j['frame_inputs'][t];n=len(f['reference']);q=np.array(f['reference']);w=p.width_scale*np.array(f['measures'])
  x=np.array(row['x']);z=np.array(row['z']);o=np.array(row['order']);bar=np.array(row['barriers']);V=np.array(f['merge_values'])
  assert sorted(o)==list(range(n)) and tuple(o) in [tuple(v) for v in f['candidate_orders']]
  assert np.allclose(w,row['w'],atol=1e-12)
  A,b,bounds=constraints(w,o,p);y=np.r_[x,z]
  assert np.min(A@y-b)>=-1e-6
  assert all(lo-1e-6<=v<=hi+1e-6 for v,(lo,hi) in zip(y,bounds))
  B=config['position_budget']
  if B is not None:
   assert np.max(abs(x-q))<=B*p.canvas+1e-6
   rr=np.c_[np.eye(n),np.zeros((n,n))]
   A=np.vstack([A,rr,-rr]);b=np.r_[b,q-B*p.canvas,-q-B*p.canvas]
  measured=max([abs(max(bar[i:k])-V[o[i],o[k]]) for i,k in combinations(range(n),2)]+[0.])
  if n>1:assert np.min(bar-np.maximum(np.diag(V)[o[:-1]],np.diag(V)[o[1:]]))>=-1e-7
  assert abs(measured-row['delta'])<1e-7
  assert measured<=config['topology_budget']*j['scalar_range']+1e-7
  assert abs(measured/j['scalar_range']-row['measured_topology'])<1e-10
  assert abs(max(abs(x-q))/p.canvas-row['position_error'])<1e-10
  pool=np.array(f['candidate_orders'])
  ds=merge_costs(pool,V);ts=interval_costs(pool,w,q,p)
  admitted=(ds<=config['topology_budget']*j['scalar_range']+1e-9)
  if B is not None:admitted&=ts<=B*p.canvas+1e-9
  assert int(admitted.sum())==row['admitted_orders']==len(row['qp_orders'])
  assert row['exhaustive']==(len(pool)==factorial(n))
  # Reconstruct all four residuals and the gradient independently.
  terms=dict(reference=float(np.mean((x-q)**2)),eccentricity=float(np.mean((x-z)**2)))
  grad=np.zeros(2*n);grad[:n]+=2*config['reference_weight']*(x-q)/n
  grad[:n]+=2*config['eccentricity_weight']*(x-z)/n
  grad[n:]+=2*config['eccentricity_weight']*(z-x)/n
  pairs=list(combinations(o,2));geom=[]
  c=np.array(f['centers'])
  for i,k in pairs:
   v=x[k]-x[i]-np.linalg.norm(c[k]-c[i]);geom.append(v*v)
   grad[k]+=2*config['geometry_weight']*v/max(1,len(pairs))
   grad[i]-=2*config['geometry_weight']*v/max(1,len(pairs))
  terms['geometry']=float(np.mean(geom)) if geom else 0.
  temporal=[];stationary=[];motion=[]
  if prev is not None:
   lookup={k:i for i,k in enumerate(j['frame_inputs'][t-1]['tracks'])};indices=[]
   for i,k in enumerate(f['tracks']):
    if k in lookup:indices.append((i,lookup[k]))
   for i,k in indices:
    du=x[i]-prev['x'][k];dq=q[i]-j['frame_inputs'][t-1]['reference'][k]
    v=du-config['motion_fraction']*dq
    temporal.append(v*v);stationary.append(du*du);motion.append((du-dq)**2)
    grad[i]+=2*config['temporal_weight']*v/max(1,len(indices))
  for key,vals in [('temporal',temporal),('stationary',stationary),('motion',motion)]:
   terms[key]=float(np.mean(vals)) if vals else 0.
  for key,val in terms.items():assert abs(val/p.canvas**2-row['terms'][key])<1e-8,(t,key)
  objective=sum(config[a]*terms[b] for a,b in [('reference_weight','reference'),('geometry_weight','geometry'),
              ('temporal_weight','temporal'),('eccentricity_weight','eccentricity')])/p.canvas**2
  assert abs(objective-row['normalized_objective'])<1e-8
  oracle=checked_lp(grad,-A,-b,bounds);assert oracle is not None
  gap=max(0.,float(grad@(y-oracle.x)))/p.canvas**2
  assert gap<=row['normalized_qp_gap']+2e-7
  report['max_qp_gap']=max(report['max_qp_gap'],row['normalized_qp_gap'])
  report['selected_qp_oracles']+=1
  cap=config['topology_budget'];report['max_scalar_cap_excess']=max(report['max_scalar_cap_excess'],row['measured_topology']-cap)
  if not grid:
   render=j['regimes'][current_key]['render']
   assert abs(row['raster_topology']-row['measured_topology'])<=render['clearance_bound']+1e-8
   assert row['raster_position_rounding']<=.5/(row['raster_length']-1)+1e-10
  prev=row
  report['grid_witnesses' if grid else 'layouts']+=1
 # A missing query is justified by the same admissibility filter, not a QP failure.
 for t,row in enumerate(rows):
  if row is not None:continue
  f=j['frame_inputs'][t];pool=np.array(f['candidate_orders']);w=p.width_scale*np.array(f['measures'])
  ds=merge_costs(pool,f['merge_values']);ts=interval_costs(pool,w,f['reference'],p)
  ok=ds<=config['topology_budget']*j['scalar_range']+1e-9
  if config['position_budget'] is not None:ok&=ts<=config['position_budget']*p.canvas+1e-9
  assert not np.any(ok)


for name in ['ring','era5','wildfire','olr','pm25_2000']:
 j=json.loads((R/(name+'.json')).read_text());p=Parameters(**j['parameters'])
 old=json.loads((C/'results/framework20261025'/(name+'.json')).read_text())
 assert j['field_sha256']==old['fields_sha256']
 assert len(j['frame_inputs'])==j['frames']
 report['frames']+=j['frames']
 with np.load(R/(name+'_maps.npz')) as maps:
  for current_key,regime in j['regimes'].items():
   check(regime['rows'],j,regime['controls'],p)
   assert np.isfinite(maps[current_key]).all()
   assert maps[current_key].shape[1]==j['frames']
   assert regime['summary']['feasible_frames']==j['frames']
   assert abs(np.mean([v['measured_topology'] for v in regime['rows']])-regime['summary']['mean_topology'])<1e-12
  report['coverage'][name]=dict(frames=j['frames'],exhaustive_frames=j['regimes']['reference_0']['summary']['exhaustive_frames'])
  for key,r in j['budget_grid'].items():
   check(r['rows'],j,r['controls'],p,grid=True);report['grid_queries']+=len(r['rows'])
   for t,row in enumerate(r['rows']):assert bool(np.isnan(maps[key][:,t]).all())==(row is None)
 # Recompute native similarity from saved anchors and one global affine fit.
 for native,key in [('TMTM','topology_time'),('ST-MTM','topology_geometry')]:
  if native not in j['native_controls']:continue
  n=j['native_controls'][native];a=np.concatenate([r['x'] for r in n['rows']])
  b=np.concatenate([r['x'] for r in j['regimes'][key]['rows']])
  s,h=np.linalg.lstsq(np.c_[a,np.ones(len(a))],b,rcond=None)[0]
  assert abs(np.sqrt(np.mean(((s*a+h-b)/p.canvas)**2))-n['similarity']['anchor_rmse'])<1e-12

assert report['frames']==614 and report['layouts']==3070 and report['grid_queries']==360
assert report['grid_witnesses']==343
testlog=(P/'.build/unified20261025/tests.log').read_text()
assert 'Ran 57 tests' in testlog and 'FAILED' not in testlog and 'ERROR' not in testlog
report['tests']=57
# Check every earlier scientific evidence file in the pre-edit delivery manifest.
before_path=P/'.build/unified20261025/before_delivery_manifest.json'
before=json.loads(before_path.read_text())['files'] if before_path.exists() else json.loads((P/'checks/unified20261025/prior_evidence_sha256.json').read_text())
preserved=0
for name,h in before.items():
 if name.startswith(('evidence/','manuscript/latex/evidence/')):
  assert sha(P/name)==h,name
  preserved+=1
report['unchanged_prior_evidence_files']=preserved
if '--numerical-only' in sys.argv:
 report['status']='numerical checks passed; document checks not requested'
 print(json.dumps(report,indent=2))
 sys.exit(0)
catalog=json.loads((P/'FIGURE_INDEX.json').read_text())
for f in catalog['figures']+catalog['supplementary_figures']:
 assert sha(P/f['asset'])==sha(P/f['export'])
 assert sha(P/f['ppt'])==f['ppt_sha256']
for f in catalog['additional_vector_figures']:
 assert sha(P/f['asset'])==sha(P/f['export'])
 assert (P/f['editable_master']).exists()
report['documents']=[]
for stem,name in [('main','Revised_RG-MTM.pdf'),('supplement','Revised_Supplement.pdf')]:
 d=pymupdf.open(P/'manuscript'/name);text=unicodedata.normalize('NFKC','\n'.join(page.get_text() for page in d))
 assert '??' not in text and '\ufffd' not in text and 'Unified Position' in text
 log=(P/'.build/unified20261025'/stem/(stem+'.log')).read_text()
 assert not re.search(r'Overfull|undefined references|Citation .*undefined|multiply defined|Float too large|LaTeX Error',log)
 if stem=='main':assert {int(n) for n in re.findall(r'Figure\s+(\d+):',text)}==set(range(1,18))
 report['documents'].append(dict(file=name,pages=len(d),sha256=sha(P/'manuscript'/name)))
with ZipFile(P/'manuscript/RG-MTM_LaTeX.zip') as z:
 assert z.testzip() is None
 for p in L.rglob('*.tex'):assert z.read(str(p.relative_to(L)))==p.read_bytes(),p
out=P/'checks/unified20261025';out.mkdir(parents=True,exist_ok=True)
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
