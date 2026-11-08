from pathlib import Path
import json,csv,hashlib,zipfile
import numpy as np
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
P=R/'output/PM25小时_AnchorMTM_20261106';audit=read(P/'input_audit.json');qs=audit['reference']['qs'];par=audit['parameters'];L=par['canvas'];origin=par['canvas_origin']
source=read(R/'output/paper_narrative_reproduced_9pages_20261108/reproduce/data/planar_source_matrices.json')['PM25'];old=list(csv.DictReader((R/'output/paper_narrative_reproduced_9pages_20261108/reproduce/data/planar_per_frame_recomputed.csv').open()));old={(float(x['epsilon']),int(x['frame'])):x for x in old if x['dataset']=='PM2.5'}
rows=[];summary=[]
def matrix(order,values,bar):
 n=len(order);a=np.diag(values.copy())
 for i in range(n):
  for j in range(i+1,n):a[i,j]=a[j,i]=max(bar[i:j])
 return a
for e in [0,.01,.02,.05,.1,.2]:
 path=P/f'eps_{e:g}' if e in [0,.05] else R/f'output/PM25预算补全_20261108/epsilon_{e:g}'
 layouts=read(path/'layouts.json');assert len(layouts)==len(qs)==744
 maps=np.load(path/'map.npz')['map'] if (path/'map.npz').exists() else None
 for t,(lay,q) in enumerate(zip(layouts,qs)):
  x=np.array(lay['pixel_x']);q=np.array(q);order=np.array(lay['order']);V=np.array(source['merge_values'][t]);ordered=V[np.ix_(order,order)]
  err=abs(x-q)/L;continuous=float(abs(matrix(order,np.diag(ordered),np.array(lay['barriers']))-ordered).max()/source['scalar_range'])
  assert continuous<=e+1.1e-7 and lay['NMLEmax']<=e+1.1e-7 and lay['continuous_budget_ok'] and lay['rendered_budget_ok']
  independent=None
  if maps is not None:
   ix=np.rint((x-origin)*(maps.shape[0]-1)/L).astype(int)[order];col=maps[:,t];bar=np.array([col[a:b+1].max() for a,b in zip(ix[:-1],ix[1:])]);independent=float(abs(matrix(order,col[ix],bar)-ordered).max()/source['scalar_range']);assert abs(independent-lay['NMLEmax'])<1e-9
  row=dict(dataset='PM2.5',epsilon=e,frame=t,features=len(x),E_mean=float(err.mean()),E_max=float(err.max()),NMLE_max=lay['NMLEmax'],continuous_NMLE=continuous,independent_raster_NMLE=independent,rendered_budget_ok=True)
  assert abs(row['E_max']-float(old[e,t]['E_max']))<1e-10 and abs(row['NMLE_max']-float(old[e,t]['NMLE_max']))<1e-10
  rows.append(row)
 rr=[x for x in rows if x['epsilon']==e];summary.append(dict(epsilon=e,frames=len(rr),mean_worst_displacement=np.mean([x['E_max'] for x in rr]),max_merge_error=max(x['NMLE_max'] for x in rr),independent_raster_frames=sum(x['independent_raster_NMLE'] is not None for x in rr)))
with (O/'PM25_six_budgets_per_frame.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
mirrors={}
for mode in ['tmtm','temporal']:
 path=R/'output/PM25结果表_20261107/results/PM25/baseline_npe';meta=read(path/f'{mode}.json');U=[np.array(x) for x in read(path/f'{mode}_anchors.json')];flip=meta['one_global_reflection'];raw=[2*origin+L-x for x in U] if flip else U
 for t,(u,q) in enumerate(zip(raw,qs)):
  q=np.array(q)
  if len(u)>1 and np.ptp(u)>0 and np.ptp(q)>0:
   cov=float(sum((u-u.mean())*(q-q.mean())));assert (cov<0)==flip;break
 npe=float(np.mean([max(abs(u-q))/L for u,q in zip(U,qs)]));assert abs(npe-meta['NPE'])<1e-12
 mirrors[mode]=dict(reflected=flip,decision_frame=t,covariance_sum=cov,NPE=npe)
report=dict(frames=4464,all_match_existing_figure_csv=True,summary=summary,mirrors=mirrors,scope='Recompute measurements from saved solutions; no new optimization sweep. Missing map arrays use stored rendered error checks, explicitly counted.')
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
