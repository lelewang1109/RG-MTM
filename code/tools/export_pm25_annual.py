"""Independently export and validate annual arrays, landmarks and metric records."""
from pathlib import Path
import sys,json,pickle,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'analysis'),str(ROOT/'tools'),str(ROOT/'src'),str(ROOT)]
import pm25_annual as ann,replicate as rp,general_method as gm,relax_hierarchy as rh,filling as fi,evaluation as ev
from experiments import era5 as ep
from native_merge_errors import measure
from result_tables import position_metrics
from evaluate_public_metrics import pad,standard_metrics,PROTOCOL
from rgmtm.reference_points import reference_points_from_frames
ann.register();O=ann.OUT
with (O/'dataset.pkl').open('rb')as f:ds=pickle.load(f)
sc=ds['sc'];rp.LOADERS[ann.NAME]=lambda:ds
maps={};us={};physical={};native={};checks={};meta={}
span=ds['native_span'];px=gm.Parameters(canvas=span,canvas_origin=float(min(ds['lo'][0],0.)),width_scale=.5*span/ds['domain_area'],gap=span/240,extra_budget=span/120,rho=.5)
for method in ['TMTM','ST-MTM']:
 print('Export',method,flush=True);r=ep.run_method(sc,method,px,canvas=span,length=ds['nominal'],refine_raster=False,strict_checks=False)
 g=r['maps'];N=g.shape[0];scale=r['gauge']['scale'];shift=r['gauge']['shift']
 if method=='TMTM':a=[np.rint((x['pixel_x']-shift)/scale*(N-1)/span).astype(int)for x in r['rows']]
 else:a=[np.asarray(x['anchors'],int)[[x['ordering'].index(leaf)for leaf in ids]]for x,ids in zip(r['records']['discrete'],sc['ids'])]
 if scale<0:a=[N-1-v for v in a]
 maps[method]=g;us[method]=[v/(N-1)for v in a];physical[method]=[np.asarray(x['pixel_x'])for x in r['rows']]
 native[method]=measure(sc,g,a);assert native[method]['max_share']<1e-10
 native[method]['nominal_topology_failed_frames']=sum(x['nominal_topology_failed']for x in r['checks'])
 meta[method]=dict(raster_length=N,gauge=r['gauge'])
print('Export RG modes',flush=True);r=rh.run(ds,.2,False,True)['_internal'];p=r['p'];ref=r['ref'];kind=sc['trees'][0].kind
rep=json.loads((O/'replicate_pm25_2000.json').read_text());fill=json.loads((O/'filling.json').read_text())[ann.NAME]
for method,key,cap in [('A','A_full_hierarchy',0.),('R 20%','R_relaxed',.2)]:
 rows=r['results'][key]['_rows'];g,skeletons,N=rh.render(sc,rows,p,ds['nominal'])
 if cap:g=np.column_stack([fi.optimal_fill(g[:,t],list(sk.ordering),sk.anchors,sc['frames'][t],kind)[0]for t,sk in enumerate(skeletons)])
 a=[np.asarray(sk.anchors)[[sk.ordering.index(leaf)for leaf in ids]]for sk,ids in zip(skeletons,sc['ids'])]
 maps[method]=g;us[method]=[v/(N-1)for v in a];physical[method]=[np.asarray(x['x'])for x in rows]
 native[method]=measure(sc,g,a);f=next(x for x in fill if x['cap']==cap)
 assert abs(native[method]['mean_share']-f['mean_opt_share'])<1e-10
 assert abs(native[method]['max_share']-f['D_opt_share'])<1e-10
 errors=np.concatenate([abs(x['x']-x['reference'])for x in rows]);t=rep['tradeoff'][str(cap)]
 assert abs(errors.mean()-t['ref_err_mean'])<1e-10 and abs(errors.max()-t['ref_err_max'])<1e-10
 meta[method]=dict(raster_length=N,canvas_origin=p.canvas_origin,canvas=p.canvas)
ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum');cent=reference_points_from_frames(sc['frames'],sc['ids'],kind='centroid');metrics=[];frame_rows=[]
for method,g in maps.items():
 assert np.isfinite(g).all() and g.shape[1]==366
 errors=[]
 for t,ids in enumerate(sc['ids']):
  a=np.rint(us[method][t]*(g.shape[0]-1)).astype(int);expected=np.array([sc['frames'][t].values[i]for i in ids]);errors.extend(abs(g[a,t]-expected))
 assert max(errors)<1e-10,(method,max(errors));checks[method]=dict(extremum_checks=len(errors),maximum_extremum_error=max(errors),finite=True,frames=366)
 m,fr=standard_metrics(cent,us[method],sc['tracks']);metrics.append(dict(dataset=ann.NAME,method={'A':'RG-MTM-P','R 20%':'RG-MTM-R'}.get(method,method),**m));frame_rows.extend(dict(method=method,**x)for x in fr)
print('Recompute order-only metrics for complete diagnostic method set',flush=True)
allmethods,_,ref2,_,_,_=ev.methods(ds);perf=position_metrics({k:v['u']for k,v in allmethods.items()},ref2['qs'],sc['hier'],ref2['extent'])
for method in maps:
 test=position_metrics({method:physical[method]},ref['qs'],sc['hier'],ref['extent'])['methods'][method]
 np.testing.assert_allclose(test['per_frame'],perf['methods'][method]['per_frame'],atol=1e-12)
perf.update(frames=366,reference_extent=ref['extent'],definition='same order-only minimax metric as retained suite')
np.savez_compressed(O/'maps.npz',**maps)
w=max(map(len,sc['ids']));lm=dict(centroids=pad(cent,w),extrema=pad(ext,w),feature_ids=pad(sc['ids'],w,int,-1),tracks=pad(sc['tracks'],w,int,-1),count=np.array(list(map(len,sc['ids']))),dates=np.array(sc['dates']))
for i,m in enumerate(maps):lm['u'+str(i)]=pad(us[m],w)
np.savez_compressed(O/'landmarks.npz',**lm)
write=lambda n,v:(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
write('native_merge_errors.json',{ann.NAME:native});write('final_performance.json',{ann.NAME:perf});write('standard_metrics.json',dict(protocol=PROTOCOL,results=metrics,frames=frame_rows,methods=meta))
write('validation.json',dict(status='passed',dataset=ann.NAME,frames=366,checks=checks,native_barriers=native,source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [Path(__file__),O/'dataset.pkl',O/'maps.npz',O/'landmarks.npz',O/'processed_fields.npz']},scope='annual replacement only; historical January outputs unchanged'))
plan=json.loads((O/'run.json').read_text());plan['status']='complete_verified';plan['validation']='validation.json';write('run.json',plan)
print('Annual arrays and metrics independently verified',flush=True)
