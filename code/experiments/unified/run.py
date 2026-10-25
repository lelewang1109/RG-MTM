"""Recompute one-model operating regimes; preserve every earlier result folder."""
from pathlib import Path
from dataclasses import asdict,replace
from itertools import permutations
import json,sys,time,hashlib,pickle
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from rgmtm.unified import Controls,solve_unified_sequence
from rgmtm.error_budget import leaf_orders
from rgmtm.framework import interval_costs
from rgmtm.baselines.stmtm import optimal_hierarchical_leaf_order
from rgmtm.reference_points import reference_points_from_frames
from rgmtm.reference_guided import render_sequence
import general_method as gm,replicate,attainable,relax_hierarchy as rh,filling
from experiments import era5 as ep
OUT=ROOT/'results/unified20261025';OUT.mkdir(exist_ok=True)
REGIMES={
 'topology_time':Controls(reference_weight=0,geometry_weight=0,motion_fraction=0),
 'topology_geometry':Controls(reference_weight=0,geometry_weight=1,motion_fraction=0),
 'reference_0':Controls(topology_budget=0),
 'reference_2':Controls(topology_budget=.02),
 'reference_10':Controls(topology_budget=.1),
}


def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,(float,np.floating)):return None if not np.isfinite(x) else float(x)
 if isinstance(x,np.integer):return int(x)
 if isinstance(x,np.bool_):return bool(x)
 return x


def dump(path,obj):path.write_text(json.dumps(clean(obj),ensure_ascii=False,indent=1,allow_nan=False)+'\n')


def pools_for(sc,qs,p):
 pools=[]
 for t,(fr,c,q) in enumerate(zip(sc['frames'],sc['centers'],qs)):
  n=len(q)
  if n<=4:pool=set(permutations(range(n)))
  else:
   legal=leaf_orders(sc['hier'][t]);w=p.width_scale*np.asarray(sc['areas'][t])
   tau=interval_costs(np.array(legal),w,q,p)
   rank={k:i for i,k in enumerate(sc['ids'][t])}
   olo=tuple(rank[k] for k in optimal_hierarchical_leaf_order(fr))
   pool={tuple(legal[0]),tuple(legal[-1]),tuple(legal[int(np.argmin(tau))]),olo,olo[::-1]}
   if len(legal)<=16:pool.update(legal)
   for v in [q]+[np.asarray(c)[:,k] for k in range(c.shape[1])]:
    o=tuple(np.argsort(v,kind='stable'));pool.update([o,o[::-1]])
   pool.update([tuple(reversed(o)) for o in list(pool)])
  pools.append(sorted(pool))
 return pools


def render(sc,rows,p,length):
 """One source-value renderer and barrier correction for every inspired regime."""
 if any(r is None for r in rows):return None,None
 length=max(2048,length)
 while True:
  try:maps,sk,errors=render_sequence(sc['frames'],sc['ids'],rows,p.canvas,length,canvas_origin=p.canvas_origin)
  except ValueError as e:
   if 'increase resolution' not in str(e) or length>=131072:raise
   length*=2;continue
  maps=maps.astype(float)
  for t,(fr,d) in enumerate(zip(sc['frames'],sk)):
   maps[:,t],_=filling.optimal_fill(maps[:,t],d.ordering,d.anchors,fr,sc['trees'][0].kind)
  actual=[float(np.max(e)) if len(e) else 0. for e in rh.merge_errors(sc,maps,sk,sc['trees'][0].kind)]
  intended=np.array([r['delta'] for r in rows]);rng=float(np.ptp(sc['fields']))
  clearance=max((1+np.max(abs(fr.values[ids])))*filling.CLEARANCE for fr,ids in zip(sc['frames'],sc['ids']))/rng
  if np.max(abs(np.array(actual)-intended))/rng>clearance+1e-8:
   if length>=131072:raise RuntimeError(f'raster barrier discrepancy persists: {max(abs(np.array(actual)-intended))/rng}, clearance={clearance}')
   length*=2;continue
  for t,(r,e,d) in enumerate(zip(rows,errors,sk)):
   r['raster_topology']=actual[t]/rng;r['raster_position_rounding']=e['anchor_error']/p.canvas
   r['raster_length']=length
  return maps,dict(length=length,max_barrier_discrepancy=float(np.max(abs(np.array(actual)-intended))/rng),
      max_anchor_rounding=max(e['anchor_error']/p.canvas for e in errors),clearance_bound=clearance,
      clearance_rule='1e-6*(1+abs(adjacent extremum)) on relaxed barriers',
      scope='measured raster errors, not an exact hard raster cap at zero allowance')


def summary(rows,p):
 rr=[r for r in rows if r is not None]
 if not rr:return dict(feasible_frames=0,frames=len(rows))
 return dict(feasible_frames=len(rr),frames=len(rows),
     reference_mae=float(np.mean(np.concatenate([abs(r['x']-r['reference'])/p.canvas for r in rr]))),
     reference_rms=float(np.sqrt(np.mean([r['terms']['reference'] for r in rr]))),
     geometry_rms=float(np.sqrt(np.mean([r['terms']['geometry'] for r in rr]))),
     stationary_rms=float(np.sqrt(np.mean([r['terms']['stationary'] for r in rr]))),
     motion_rms=float(np.sqrt(np.mean([r['terms']['motion'] for r in rr]))),
     mean_topology=float(np.mean([r['measured_topology'] for r in rr])),
     max_topology=max(r['measured_topology'] for r in rr),
     max_position=max(r['position_error'] for r in rr),
     exhaustive_frames=sum(r['exhaustive'] for r in rr),
     qp_orders=sum(len(r['qp_orders']) for r in rr),
     max_normalized_qp_gap=max(r['normalized_qp_gap'] for r in rr))


def compare_native(native,rows,p):
 """One global affine gauge fit; never fit a separate transform per frame."""
 a=np.concatenate([r['pixel_x'] for r in native['rows']]);b=np.concatenate([r['x'] for r in rows])
 A=np.c_[a,np.ones(len(a))];scale,shift=np.linalg.lstsq(A,b,rcond=None)[0]
 residual=(scale*a+shift-b)/p.canvas
 same=total=0
 for old,new in zip(native['rows'],rows):
  x=scale*np.asarray(old['pixel_x']);y=np.asarray(new['x']);n=len(x)
  for i in range(n):
   for j in range(i+1,n):
    if abs(x[j]-x[i])>1e-9 and abs(y[j]-y[i])>1e-9:
     total+=1;same+=int(np.sign(x[j]-x[i])==np.sign(y[j]-y[i]))
 return dict(global_affine_scale=scale,global_affine_shift=shift,anchor_rmse=float(np.sqrt(np.mean(residual**2))),
      pair_order_agreement=same/max(1,total),pairs=total,
      interpretation='descriptive similarity after one sequence-wide affine fit including reflection; no equality claim')


def run(name):
 print('LOAD',name,flush=True);start=time.time()
 ds=pickle.loads((ROOT/'results/pm25_2000/dataset.pkl').read_bytes()) if name=='pm25_2000' else replicate.LOADERS[name]()
 sc=ds['sc'];ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum')
 ref=gm.auto_reference(sc,ext,ds['lo'],ds['hi']);qs=ref['qs']
 p=gm.universal_parameters(ref['origin'],ref['extent'],ds['domain_area']);rng=float(np.ptp(sc['fields']))
 V=[attainable.lca_matrix(fr,ids,sc['trees'][0].kind) for fr,ids in zip(sc['frames'],sc['ids'])]
 pools=pools_for(sc,qs,p);regimes={};maps={};allrows={}
 for key,controls in REGIMES.items():
  ts=time.time();print(name,key,'start',flush=True)
  rows=solve_unified_sequence(sc['centers'],sc['areas'],sc['hier'],qs,V,sc['tracks'],pools,rng,controls,p)
  m,render_check=render(sc,rows,p,ds['nominal']);maps[key]=m;allrows[key]=rows
  regimes[key]=dict(controls=asdict(controls),summary=summary(rows,p),rows=rows,render=render_check)
  print(name,key,clean(regimes[key]['summary']),'seconds',round(time.time()-ts,1),flush=True)
  dump(OUT/(name+'_progress.json'),dict(completed=list(regimes)))
 native={}
 # Dedicated native-output similarity controls; no baselines are called by the unified solver.
 if name in ['ring','era5']:
  for method,key in [('TMTM','topology_time'),('ST-MTM','topology_geometry')]:
   opts=dict(canvas=ds['native_span'],length=max(2048,ds['nominal']),refine_raster=False,strict_checks=False)
   if name=='ring' and method=='ST-MTM':opts['stmtm_parameters']=replace(ep.b2.LayoutParameters.from_preset('ring'),layout_length=opts['length'])
   r=ep.run_method(sc,method,p,**opts);maps['native_'+method]=r['maps']
   native[method]=dict(similarity=compare_native(r,allrows[key],p),rows=[dict(x=z['pixel_x'],order=z['order']) for z in r['rows']],
        parameters=r['records'].get('parameters'),seconds=r['compute_seconds'],
        topology_equal_frames=sum(x['topology_equal'] for x in r['checks']))
   print(name,method,native[method]['similarity'],flush=True)
 grid={}
 if name=='ring':
  for eps in [0,.02,.1]:
   for b in [np.inf,.1,.05]:
    key=f'epsilon_{eps:g}_position_{b:g}';ctrl=Controls(topology_budget=eps,position_budget=b)
    if np.isinf(b):
     rkey={0:'reference_0',.02:'reference_2',.1:'reference_10'}[eps]
     rows=allrows[rkey];m=maps[rkey];rc=regimes[rkey]['render']
    else:
     print(name,key,flush=True)
     rows=solve_unified_sequence(sc['centers'],sc['areas'],sc['hier'],qs,V,sc['tracks'],pools,rng,ctrl,p,allow_infeasible=True)
     m,rc=render(sc,rows,p,ds['nominal'])
    grid[key]=dict(controls=asdict(ctrl),summary=summary(rows,p),rows=rows,render=rc)
    # Keep missing columns explicit; render feasible frames independently for display.
    if m is None:
     m=np.full((2048,len(rows)),np.nan)
     for t,row in enumerate(rows):
      if row is None:continue
      sub=dict(frames=[sc['frames'][t]],ids=[sc['ids'][t]],trees=[sc['trees'][t]],fields=sc['fields'])
      col,check=render(sub,[row],p,2048)
      if len(col)!=len(m):
       ix=np.linspace(0,len(col)-1,len(m)).round().astype(int);col=col[ix]
      m[:,t]=col[:,0]
    maps[key]=m
 inputs=[dict(centers=c,measures=a,hierarchy=h,reference=q,merge_values=v,tracks=ids,candidate_orders=pool)
         for c,a,h,q,v,ids,pool in zip(sc['centers'],sc['areas'],sc['hier'],qs,V,sc['tracks'],pools)]
 result=dict(dataset=name,frames=len(sc['frames']),scalar_range=rng,parameters=asdict(p),reference=ref,
   field_sha256=hashlib.sha256(np.asarray(sc['fields'],dtype='<f8').tobytes()).hexdigest(),frame_inputs=inputs,
   regimes=regimes,native_controls=native,budget_grid=grid,seconds=time.time()-start,
   protocol='same fixed candidate pool, widths, canvas, source-value renderer and four-term QP; sequential temporal optimization, not a sequence-wide optimum',
   missing_grid_columns='no feasible candidate; no last-frame carry or hidden budget increase',
   display=dict(cmap=ds['cmap'],vmin=float(np.min(sc['fields'])),vmax=float(np.max(sc['fields']))))
 dump(OUT/(name+'.json'),result);np.savez_compressed(OUT/(name+'_maps.npz'),**maps)
 print('DONE',name,round(time.time()-start,1),'seconds',flush=True)


if __name__=='__main__':
 for name in (sys.argv[1:] or ['ring','era5','wildfire','olr','pm25_2000']):run(name)
