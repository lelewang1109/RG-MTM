"""Evaluate canonical sample-domain curves on the frozen ratio-p experiment."""
from pathlib import Path
import sys,json,csv,hashlib,argparse
import numpy as np
from scipy.spatial.distance import pdist,squareform
W=Path(__file__).resolve().parents[4]; P=W/'paper/pvis2027'; O=Path(__file__).resolve().parents[1]; E=P/'experiments_ratio_p_20261104'
C=W/'RG-MTM/code' if (W/'RG-MTM/code').exists() else W/'code'
sys.path[:0]=[str(C),str(C/'src'),str(E/'source')]
from native_io import Frame
from rgmtm.baselines.space_filling import inverse_order,sample_order
from rgmtm.baselines.stmtm import scale_normalized_stress,trustworthiness
K=dict(Gaussian=1,Ring=3,Wildfires=5,Storms=3)
def save(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main(pilot=False):
 out=O/('pilot' if pilot else 'results'); summaries=[];audits=[];provenance=[]
 for ds,k in K.items():
  root=E/'results'/ds; prep=root/'preparation'; audit=json.loads((root/'input_audit.json').read_text()); par=audit['parameters'];qs=audit['source_reference']['qs'];xy=np.load(prep/'coordinates.npy');F=np.load(prep/'fields.npy',mmap_mode='r');L=196 if ds=='Ring' else 4096;n=min(8,len(F)) if pilot else len(F)
  inv={m:inverse_order(F.shape[1:],m) for m in ['Hilbert','Morton']}; rows={m:[] for m in inv}; anchor=json.loads((root/'Exact/layouts.json').read_text());previous=list(csv.DictReader((root/'Exact/per_frame.csv').open()))
  for t in range(n):
   f=Frame(t,prep/'trees',xy);ii=np.array(f.leaves);c=np.array([f.leaf_centroid(int(i)) for i in ii]);q=np.asarray(qs[t]);src=pdist(c);valid=len(src)>0 and np.dot(src,src)>0;twvalid=0<k<len(ii)/2
   # Independently reproduce archived Anchor Exact values to verify matching/reference/scale.
   u=np.array(anchor[t]['pixel_x']);npe=float(np.max(abs(u-q))/par['canvas']);sns=scale_normalized_stress(squareform(src),u) if valid else None
   assert abs(npe-float(previous[t]['NPE']))<1e-11
   if valid:assert abs(sns-float(previous[t]['SNS']))<1e-11
   if twvalid:assert abs(trustworthiness(c,u,k)-float(previous[t]['TW']))<1e-11
   audits.append(dict(Dataset=ds,frame=t,features=len(ii),Exact_NPE_reproduced=True,Exact_SNS_reproduced=bool(valid),SNS_eligible=bool(valid),TW_eligible=twvalid))
   for m,inverse in inv.items():
    ranks=inverse[ii];pixels=np.rint(ranks*(L-1)/(len(inverse)-1)).astype(int);u=par['canvas_origin']+pixels*par['canvas']/(L-1)
    assert len(np.unique(ranks))==len(ranks) and np.all((pixels>=0)&(pixels<L))
    sns=scale_normalized_stress(squareform(src),u) if valid else None;tw=trustworthiness(c,u,k) if twvalid else None
    if valid:
     dst=pdist(u[:,None]);alpha=np.dot(src,dst)/np.dot(dst,dst) if np.dot(dst,dst)>0 else 0
     assert np.isclose(sns,np.dot(src-alpha*dst,src-alpha*dst)/np.dot(src,src),atol=1e-12)
    if tw is not None:assert 0<=tw<=1
    rows[m].append(dict(Dataset=ds,Method=m,frame=t,features=len(ii),SNS=sns,TW=tw,NPE=float(np.max(abs(u-q))/par['canvas']),k=k,coincident_display_anchors=len(ii)-len(np.unique(pixels))))
  for m,rr in rows.items():
   save(out/ds/(m+'_per_frame.csv'),rr);values=lambda metric:[r[metric] for r in rr if r[metric] is not None]
   summaries.append(dict(Dataset=ds,Method=m,SNS=float(np.mean(values('SNS'))) if values('SNS') else None,TW=float(np.mean(values('TW'))) if values('TW') else None,NPE=float(np.mean(values('NPE'))),frames=n,SNS_valid_frames=len(values('SNS')),TW_valid_frames=len(values('TW')),TW_k=k,L=L,coincident_anchor_frames=sum(r['coincident_display_anchors']>0 for r in rr),topology_preserving=False))
  provenance.append(dict(Dataset=ds,fields_sha256=digest(prep/'fields.npy'),coordinates_sha256=digest(prep/'coordinates.npy'),input_audit_sha256=digest(root/'input_audit.json')))
 save(out/'metrics.csv',summaries);save(out/'evaluation_audit.csv',audits)
 (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 protocol=dict(curves='existing canonical sample_order; x=column,y=row; no orientation search or reflection',mapping='full-grid valid-cell curve rank/(grid sample count-1), mapped to shared fixed physical canvas; rounded at original L; no per-frame feature rank packing',anchors='same original extremum sample IDs as Anchor Exact; SNS/TW source points are same support centroids',TW='shared stable distance-tie ordering by leaf ID; require0<k<n/2; missing neverzero',NPE='time mean of frame max abs(final position - frozen q)/canvas',interpretation='sample-domain spatial baselines, no topology preservation or finite feature-support layout guarantee; quantization collisions retained and reported',pilot=pilot)
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');print(json.dumps(summaries,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');main(ap.parse_args().pilot)
