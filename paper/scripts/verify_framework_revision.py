"""Read-only numerical and delivery verification of the 2026-10-25 framework."""
from pathlib import Path
from itertools import combinations
from zipfile import ZipFile
import json,hashlib,re,sys
import numpy as np
import pymupdf
P=Path(__file__).resolve().parents[1];C=P.parent/'code';sys.path[:0]=[str(C/'src')]
from rgmtm.framework import cost_table,minimum_topology_budget
from rgmtm.error_budget import Parameters,leaf_orders,InfeasibleLayout
R=C/'results/framework20261025';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'date':'2026-10-25','status':'passed','frames':0,'exact_frames':0,'witnesses':0,'inverse_queries':0}
for name in ['era5','wildfire','olr','pm25_2000','ring']:
 j=json.loads((R/(name+'.json')).read_text());W=json.loads((R/(name+'_witnesses.json')).read_text());span=j['canvas'];rng=j['scalar_range']
 assert len(j['frame_inputs'])==j['frames'] and len(W['rows'])==9*j['frames']
 report['frames']+=j['frames'];report['exact_frames']+=j['exact_frames']
 for r in W['rows']:
  f=j['frame_inputs'][r['frame']];q=np.array(f['reference']);w=np.array(f['widths']);V=np.array(f['merge_values']);o=np.array(r['order']);x=np.array(r['x']);z=np.array(r['z']);b=np.array(r['barriers']);n=len(w)
  assert sorted(o)==list(range(n))
  assert np.max(abs(x-z)-j['rho']*w/2)<=1e-6
  assert min(z-w/2)>=j['canvas_origin']-1e-6 and max(z+w/2)<=j['canvas_origin']+span+1e-6
  assert np.all(np.diff(z[o])-(w[o[:-1]]+w[o[1:]])/2>=j['gap']-1e-6)
  assert np.max(abs(x-q))<=r['tau']+1e-6
  measured=max([abs(max(b[i:k])-V[o[i],o[k]]) for i,k in combinations(range(n),2)]+[0.])
  assert measured<=r['epsilon_fraction']*rng+1e-6
  assert abs(measured-r['delta'])<=1e-6
  if n>1:assert np.all(b>=np.maximum(np.diag(V)[o[:-1]],np.diag(V)[o[1:]])-1e-6)
  report['witnesses']+=1
 for t in range(j['frames']):
  rr=sorted([r for r in j['rows'] if r['frame']==t],key=lambda r:r['epsilon'])
  assert np.all(np.diff([r['position'] for r in rr])<=1e-8)
  f=j['frame_inputs'][t];p=Parameters(canvas=span,canvas_origin=j['canvas_origin'],gap=j['gap'],rho=j['rho'],width_scale=1)
  if rr[0]['exact']:cand=None
  else:
   s=tuple(np.argsort(f['reference']));cand=set(leaf_orders(f['hierarchy']));cand.update([s,s[::-1]])
   for i in range(len(s)):
    for k in range(len(s)):
     a=list(s);v=a.pop(i);a.insert(k,v);cand.add(tuple(a))
  table=cost_table(f['widths'],f['reference'],f['merge_values'],p,max_orders=40320,candidate_orders=cand)
  for query in [r for r in j['inverse_queries'] if r['frame']==t]:
   try:answer=minimum_topology_budget(table,query['position_budget']*span)/rng
   except InfeasibleLayout:answer=None
   assert answer is None and query['minimum_epsilon'] is None or answer is not None and abs(answer-query['minimum_epsilon'])<1e-9
   report['inverse_queries']+=1
 v=json.loads((R/'validation.json').read_text())
 for n,h in v['source_sha256'].items():assert sha(C/n)==h,n
 for r in j['summary']:
  rows=[q for q in j['rows'] if q['epsilon']==r['epsilon']]
  assert abs(np.mean([q['position'] for q in rows])-r['mean_position'])<1e-12
native=json.loads((R/'native_compatibility.json').read_text());assert native['frames']==40 and native['TMTM_map_max_abs_difference']==native['STMTM_map_max_abs_difference']==0
reg=json.loads((P/'FIGURE_INDEX.json').read_text())
for f in reg['figures']+reg['supplementary_figures']:
 assert sha(P/f['ppt'])==f['ppt_sha256']
 assert sha(P/f['asset'])==sha(P/f['export'])
for f in reg['additional_vector_figures']:assert sha(P/f['asset'])==sha(P/f['export'])
report['documents']=[]
for stem,name in [('main','Revised_RG-MTM.pdf'),('supplement','Revised_Supplement.pdf')]:
 p=P/'manuscript'/name;d=pymupdf.open(p);text='\n'.join(pg.get_text() for pg in d)
 assert '??' not in text and '\ufffd' not in text and 'Budgeted Framework' in text
 log=(P/'.build/framework20261025'/stem/(stem+'.log')).read_text()
 assert not re.search(r'Overfull|undefined references|Citation .*undefined|multiply defined|LaTeX Error',log)
 if stem=='main':assert {int(n) for n in re.findall(r'Figure\s+(\d+):',text)}==set(range(1,16))
 report['documents'].append(dict(file=name,pages=len(d),sha256=sha(p)))
with ZipFile(P/'manuscript/RG-MTM_LaTeX.zip') as z:
 assert z.testzip() is None
 for p in (P/'manuscript/latex').rglob('*.tex'):assert z.read(str(p.relative_to(P/'manuscript/latex')))==p.read_bytes(),p
assert report['frames']==614 and report['exact_frames']==603 and report['witnesses']==5526 and report['inverse_queries']==3684
testlog=(P/'.build/framework20261025/tests.log').read_text();assert 'Ran 50 tests' in testlog and 'FAILED' not in testlog and 'ERROR' not in testlog
report['tests']=50;report['native_compatibility']='zero array difference on 40 Ring fields';report['model']='continuous non-strict; 11 candidate-only frames; no reused motion score'
print(json.dumps(report,ensure_ascii=False,indent=2))
