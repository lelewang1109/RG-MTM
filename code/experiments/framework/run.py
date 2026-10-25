"""Recompute budgeted profiles on unchanged inputs; never overwrite old evidence.
Run from code/: PYTHONPATH=src ../../.venv/bin/python experiments/framework/run.py
"""
from pathlib import Path
import sys,json,time,hashlib,pickle,csv
from math import factorial
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from rgmtm.framework import cost_table,select_budget,minimum_topology_budget,native_profile
from rgmtm.error_budget import leaf_orders,InfeasibleLayout
from rgmtm.reference_points import reference_points_from_frames
import general_method as gm,relax_hierarchy as rh,attainable,replicate
from experiments import era5 as ep
OUT=ROOT/'results/framework20261025';OUT.mkdir(exist_ok=True)
EPS=[0,.005,.01,.02,.05,.1,.2,.5,1.]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else float(v))+'\n')

def candidates(sc,t,q):
 h=sc['hier'][t];out=set(leaf_orders(h));s=tuple(np.argsort(q));out.update([s,s[::-1]])
 for i in range(len(s)):
  for j in range(len(s)):
   a=list(s);x=a.pop(i);a.insert(j,x);out.add(tuple(a))
 return out

def run(name,ds):
 sc=ds['sc'];ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum')
 ref=gm.auto_reference(sc,ext,ds['lo'],ds['hi']);p=gm.universal_parameters(ref['origin'],ref['extent'],ds['domain_area'])
 rng=float(np.ptp(sc['fields']));rows=[];inverse=[];exact=0;summary=[];witnesses=[];inputs=[];start=time.time()
 for t,(fr,ids,q) in enumerate(zip(sc['frames'],sc['ids'],ref['qs'])):
  V=attainable.lca_matrix(fr,ids,sc['trees'][0].kind);w=p.width_scale*np.asarray(sc['areas'][t])
  inputs.append(dict(frame=t,widths=w.tolist(),reference=q.tolist(),merge_values=V.tolist(),hierarchy=sc['hier'][t]))
  exact_here=factorial(len(ids))<=40320
  table=cost_table(w,q,V,p,max_orders=40320,candidate_orders=None if exact_here else candidates(sc,t,q))
  exact+=exact_here;last=np.inf;err=[]
  for fraction in EPS:
   r=select_budget(table,fraction*rng);assert r['tau']<=last+1e-7;last=r['tau']
   assert r['measured_merge_error']<=fraction*rng+1e-7
   row=dict(dataset=name,frame=t,leaves=len(ids),epsilon=fraction,position=r['tau']/p.canvas,
      measured_topology=r['measured_merge_error']/rng,exact=bool(exact_here),orders=r['evaluated_orders'])
   rows.append(row);err.append(row)
   witnesses.append(dict(frame=t,epsilon_fraction=fraction,leaf_values=np.diag(V).tolist(),reference=q.tolist(),**r))
  lo=float(table['tau'].min())
  for beta in [0,.01,.02,.05,.1,.2]:
   try:d=minimum_topology_budget(table,beta*p.canvas);status='feasible';d=d/rng
   except InfeasibleLayout:d=None;status='infeasible in exhaustive set' if exact_here else 'not found in candidate set'
   inverse.append(dict(frame=t,position_budget=beta,minimum_epsilon=d,status=status,exact=bool(exact_here)))
  # Independent fixed-order LP witnesses; no source/raster array is modified.
  assert abs(err[0]['position']-float(rh.tau_orders(np.asarray(leaf_orders(sc['hier'][t])),w,q,p).min())/p.canvas)<1e-7
  if t%25==0:print(name,t,'/',len(sc['frames']),'leaves',len(ids),flush=True)
 for epsilon in EPS:
  rr=[r for r in rows if r['epsilon']==epsilon]
  summary.append(dict(epsilon=epsilon,mean_position=float(np.mean([r['position'] for r in rr])),
      max_position=max(r['position'] for r in rr),max_topology=max(r['measured_topology'] for r in rr),
      frames_with_positive_error=sum(r['measured_topology']>1e-10 for r in rr),exact_frames=exact,frames=len(rr)))
 result=dict(dataset=name,frames=len(sc['frames']),exact_frames=exact,candidate_only_frames=len(sc['frames'])-exact,
      scalar_range=rng,canvas=p.canvas,canvas_origin=p.canvas_origin,rho=p.rho,gap=p.gap,frame_inputs=inputs,reference=ref,summary=summary,rows=rows,inverse_queries=inverse,
      fields_sha256=hashlib.sha256(np.asarray(sc['fields'],dtype='<f8').tobytes()).hexdigest(),
      seconds=time.time()-start,scope='per-frame continuous non-strict optimum or declared candidate upper bound; no temporal QP')
 dump(OUT/(name+'.json'),result)
 if witnesses:dump(OUT/(name+'_witnesses.json'),dict(rows=witnesses,canvas_origin=p.canvas_origin,canvas=p.canvas,kind=sc['trees'][0].kind))
 return result

def native_check(ds):
 from rgmtm.baselines import tmtm,stmtm
 sc=ds['sc'];a=tmtm.compute_temporal_merge_tree_map(sc['fields'],kind='split',max_linearized_pixels=196)
 b=native_profile('TMTM',fields=sc['fields'],kind='split',max_linearized_pixels=196)
 p=stmtm.LayoutParameters.from_preset('ring');c=stmtm.compute_spatiotemporal_merge_tree_map(sc['frames'],p)
 d=native_profile('ST-MTM',frames=sc['frames'],parameters=p)
 assert np.array_equal(a.linearized_values,b.linearized_values) and a.decisions==b.decisions
 assert np.array_equal(c.linearized_values,d.linearized_values)
 return dict(frames=len(sc['frames']),TMTM_map_max_abs_difference=float(np.max(abs(a.linearized_values-b.linearized_values))),
      STMTM_map_max_abs_difference=float(np.max(abs(c.linearized_values-d.linearized_values))),
      note='Native-profile compatibility regression, not independent validation of published authors implementations or a new solver.')

if __name__=='__main__':
 args=sys.argv[1:] or ['ring','era5','wildfire','olr','pm25_2000'];results={}
 for name in args:
  print('LOAD',name,flush=True)
  if name=='pm25_2000':ds=pickle.loads((ROOT/'results/pm25_2000/dataset.pkl').read_bytes())
  else:ds=replicate.LOADERS[name]()
  if name=='ring':dump(OUT/'native_compatibility.json',native_check(ds))
  results[name]=run(name,ds)
  dump(OUT/'progress.json',dict(completed=list(results)))
 print('Complete',list(results),flush=True)
