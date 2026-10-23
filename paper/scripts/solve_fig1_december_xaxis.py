"""Run existing RG-MTM R20 on the newly authorized hourly X-reference experiment."""
from pathlib import Path
import sys,json,time
import numpy as np
R=Path(__file__).resolve().parents[1];ROOT=R.parent/'code';sys.path[:0]=[str(ROOT/'analysis'),str(ROOT),str(ROOT/'src')]
from experiments import era5 as ep
import relax_hierarchy as rh,general_method as gm,filling
from rgmtm.reference_points import reference_points_from_frames
D=R/'evidence/fig1/december1999_xaxis';a=np.load(D/'fields.npz');start=time.perf_counter()
auto='--data-direction' in sys.argv
OUT=D.parent/'december1999_data_direction' if auto else D
OUT.mkdir(exist_ok=True)
sc=ep.scene_from_fields(a['fields'],a['coords'],float(a['geometry'][2]),'join',max_leaves=None)
sc['dates']=list(a['dates']);print('Trees/tracking ready; max leaves',max(map(len,sc['ids'])),flush=True)
# Explicit reference injection selects the user-requested d; no scientific module is modified.
old=gm.auto_reference
lo=a['coords'].min(0);hi=a['coords'].max(0)
def fixed(sc,ext,lo,hi,*args,**kwargs):
 return dict(kind='direction',qs=[e[:,0] for e in ext],origin=float(lo[0]),extent=float(hi[0]-lo[0]),label='Eastward reference d=(1,0)',candidates={'direction':{'a':[1.,0.]}})
if not auto:gm.auto_reference=fixed
try:
 ds=dict(name='ERA5 December1999 hourly X-axis',sc=sc,lo=lo,hi=hi,domain_area=49*49*float(a['geometry'][2]),nominal=4096)
 print('Solving RG-MTM-R20...',flush=True)
 res=rh.run(ds,value_cap_fraction=.2,make_figure=False,return_internal=True)
finally:gm.auto_reference=old
internal=res.pop('_internal');rr=internal['results']['R_relaxed'];maps=rr['_maps'];rows=rr['_rows'];p=internal['p']
# Apply the same optimal scalar barriers as the published RG-MTM implementation.
maps,dsk,length=rh.render(sc,rows,p,4096)
errors=[]
for t,(fr,sk) in enumerate(zip(sc['frames'],dsk)):
 maps[:,t],er=filling.optimal_fill(maps[:,t],list(sk.ordering),sk.anchors,fr,'join');errors.append(er)
 n=len(rows[t]['x']);
 if t%120==0:print('Filling',t,flush=True)
N=max(map(len,sc['ids']));pad=lambda:np.full((744,N),np.nan)
anchor=pad();q=pad();value=pad();tracks=np.full((744,N),-1,int);leaf=tracks.copy();extrema=np.full((744,N,2),np.nan)
for t,(row,ids) in enumerate(zip(rows,sc['ids'])):
 n=len(ids);anchor[t,:n]=(row['x']-p.canvas_origin)/p.canvas;q[t,:n]=(row['reference']-p.canvas_origin)/p.canvas
 tracks[t,:n]=sc['tracks'][t];leaf[t,:n]=ids;value[t,:n]=[sc['frames'][t].values[k] for k in ids];extrema[t,:n]=a['lonlat'][ids]
direction=np.asarray(internal['ref']['candidates']['direction']['a'])
np.savez_compressed(OUT/'results.npz',mapR=maps,normR=anchor,qnorm=q,value=value,tracks=tracks,leaf=leaf,lonlat=extrema,dates=a['dates'],direction=direction,geometry=[p.canvas_origin,p.canvas],delta=np.asarray(errors))
res.update(seconds_total=time.perf_counter()-start,scalar_fill='existing filling.optimal_fill',direction=direction,original_results_modified=False)
res['results_before_optimal_scalar_fill']=res.pop('results')
res['actual_output_verification']='verification.json'
(OUT/'results.json').write_text(json.dumps(res,indent=2,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else float(v)))
print('Complete',maps.shape,'seconds',res['seconds_total'],flush=True)
