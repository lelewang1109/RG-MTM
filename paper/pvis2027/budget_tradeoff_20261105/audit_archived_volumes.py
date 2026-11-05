"""Independently audit archived 3-D renders; do not mix continuous/raster metrics."""
from pathlib import Path
import json,csv,hashlib,sys
import numpy as np
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ARCH=ROOT/'output/current_method_parameter_sweep_20261029'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def measure():
 aggregate=[];per=[];sources=[]
 for name,slug in [('Tangaroa','tangaroa'),('Cylinder','cylinder')]:
  folder=ARCH/slug;protocol=read(folder/'protocol.json')
  recorded=next(p for p in protocol['source_sha256'] if p.endswith('/features.json'))
  # Rebase the original provenance path onto the supplied workspace root.
  # Keep the recorded key for its expected hash; do not use another workspace's file.
  prefix,found,suffix=recorded.partition('/output/github/')
  if found:features_path=ROOT/'output/github'/suffix
  else:
   prefix,found,suffix=recorded.partition('/RG-MTM/')
   if not found:raise ValueError('Unrecognized recorded feature path: '+recorded)
   features_path=ROOT/'RG-MTM'/suffix
  assert sha(features_path)==protocol['source_sha256'][recorded]
  features=read(features_path)['frames'];p=protocol['parameters'];L=p['canvas'];origin=p['canvas_origin'];R=protocol['scalar_range'];eps0=protocol['eps0']
  sources.append(dict(dataset=name,frames=len(features),archive=str(folder),feature_source=str(features_path),feature_sha256=sha(features_path),
   parameters=p,scalar_range=R,epsilon0=eps0,reference='fixed offline matched-extremum motion direction' if name=='Tangaroa' else 'fixed streamwise x axis',
   extraction='velocity magnitude, declared range [0,2], persistence absolute 0.2, 300x180x120' if name=='Tangaroa' else 'normalized negative Q scalar; 2% per-frame persistence; cropped 135x64x48',
   construction='archived width-aware order search + singleton capped four-term QP + optimal filling; no centered-tree-guidance prototype',
   metric='recompute rendered fixed-leaf matrix including diagonal and rendered anchors, not continuous summary'))
  for eps in protocol['epsilon']:
   jp=folder/f'epsilon_{eps:g}.json';mp=folder/f'epsilon_{eps:g}.npz';saved=read(jp)
   with np.load(mp) as z:maps=z['map']
   assert maps.shape[1]==len(features)==len(saved['rows'])==protocol['frames']
   H=maps.shape[0];error_pool=[];nm=[];continuous=[];rounding=[]
   for t,(rec,row) in enumerate(zip(features,saved['rows'])):
    order=np.array(row['order'],int);x=np.array(row['x']);q=np.array(row['reference']);n=len(order)
    assert n==len(rec['leaf_ids']) and sorted(order)==list(range(n))
    anchors=np.rint((x-origin)*(H-1)/L).astype(int);ordered=anchors[order]
    assert len(set(anchors))==n and np.all(np.diff(ordered)>0)
    assert anchors.min()>=0 and anchors.max()<H
    col=maps[:,t];assert np.isfinite(col).all()
    # Every pair's displayed merge is the maximum of intervening adjacent barriers.
    B=np.array([col[a:b+1].max() for a,b in zip(ordered[:-1],ordered[1:])])
    displayed=np.diag(col[ordered])
    for i in range(n-1):
     upper=np.maximum.accumulate(B[i:]);displayed[i,i+1:]=upper;displayed[i+1:,i]=upper
    V=np.array(rec['source_lca_values'])[np.ix_(order,order)]
    error=float(abs(displayed-V).max()/R);nm.append(error)
    cont=float(row['measured_topology']);continuous.append(cont)
    assert error<=eps+eps0+1e-12,(name,eps,t,error)
    assert cont<=eps+eps0+1e-8,(name,eps,t,cont)
    u=origin+anchors*L/(H-1);e=abs(u-q)/L;error_pool.extend(e)
    delta=float(abs(u-x).max()/L);rounding.append(delta)
    assert delta<=.5/(H-1)+1e-12
    per.append(dict(dataset=name,epsilon=eps,frame=t,features=n,E_mean=float(e.mean()),E_max=float(e.max()),NMLE_max=error,
     continuous_NMLE=cont,max_anchor_rounding=delta,rendered_budget_ok=True))
   error_pool=np.array(error_pool)
   assert abs(max(nm)-saved['render']['raster_merge_error_max'])<1e-10
   aggregate.append(dict(dataset=name,epsilon=eps,NMLE_max=max(nm),E_inf=float(error_pool.max()),E_pool=float(error_pool.mean()),
    feature_frames=len(error_pool),frames=len(features),raster_length=H,epsilon0=eps0,source=str(jp.relative_to(ROOT)),render_source=str(mp.relative_to(ROOT))))
   print(name,eps,'frames',len(features),'Einf',100*error_pool.max(),'Epool',100*error_pool.mean(),'NMLE',100*max(nm),flush=True)
 table(OUT/'volume_curve_metrics.csv',aggregate);table(OUT/'volume_per_frame_audit.csv',per)
 (OUT/'volume_protocol.json').write_text(json.dumps(sources,indent=2))
 (OUT/'verification.json').write_text(json.dumps(dict(passed=True,datasets=2,complete_sequence_configurations=len(aggregate),
  feature_frames_checked=sum(r['feature_frames'] for r in aggregate),frame_columns_checked=len(per),budget_violations=0,
  fixed_leaf_matrix_includes_diagonal=True,raw_raster_hashes={str(p.relative_to(ROOT)):sha(p) for s in ['tangaroa','cylinder'] for p in sorted((ARCH/s).glob('epsilon_*.npz'))}),indent=2))
 return aggregate

if __name__=='__main__':measure()
