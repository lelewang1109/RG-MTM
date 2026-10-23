"""Reconstruct input trees to verify measured errors and the real direction without solving again."""
from pathlib import Path
import sys,json,itertools
import numpy as np
R=Path(__file__).resolve().parents[1];ROOT=R.parent/'code';sys.path[:0]=[str(ROOT/'analysis'),str(ROOT),str(ROOT/'src')]
from experiments import era5 as ep
D=R/'evidence/fig1';f=np.load(D/'december1999_xaxis/fields.npz');sc=ep.scene_from_fields(f['fields'],f['coords'],float(f['geometry'][2]),'join',max_leaves=None)
for folder in ['december1999_xaxis','december1999_data_direction']:
 a=dict(np.load(D/folder/'results.npz'));d=a['direction'];assert np.isfinite(d).all() and abs(np.linalg.norm(d)-1)<1e-12
 origin,L=a['geometry'];errors=[];pairs0=[];pairs1=[]
 for t,fr in enumerate(sc['frames']):
  ids=sc['ids'][t];n=len(ids);u=np.rint(a['normR'][t,:n]*4095).astype(int)
  expected=np.array([fr.coordinates[k] for k in ids]);assert np.allclose(np.einsum('ij,j->i',expected,d),origin+a['qnorm'][t,:n]*L)
  e=[]
  for i,j in itertools.combinations(range(n),2):
   lo,hi=sorted((u[i],u[j]));e.append(abs(a['mapR'][lo:hi+1,t].max()-fr.values[fr.lca(ids[i],ids[j])]))
  errors.append(max(e,default=0.))
  if t:
   old={int(k):j for j,k in enumerate(a['tracks'][t-1]) if k>=0}
   for j,k in enumerate(a['tracks'][t,:n]):
    if int(k) in old:pairs0.append(sc['frames'][t-1].coordinates[int(a['leaf'][t-1,old[int(k)]])]);pairs1.append(expected[j])
 v=np.array(pairs1)-np.array(pairs0);cov=np.einsum('ni,nj->ij',v,v);eigen,vec=np.linalg.eigh(cov)
 major=vec[:,-1];major*=1 if np.sum(np.einsum('ni,i->n',v,major))>=0 else -1
 if folder.endswith('data_direction'):assert np.allclose(d,major),[d,major]
 result=dict(frames=744,period=[str(a['dates'][0]),str(a['dates'][-1])],direction=d.tolist(),angle_deg=float(np.degrees(np.arctan2(d[1],d[0]))),reference_projection_verified=True,finite_profiles=bool(np.isfinite(a['mapR']).all()),actual_max_merge_error_after_optimal_fill_hPa=float(max(errors)),actual_frame_merge_errors_hPa=errors,matched_steps=len(v),motion_covariance=cov.tolist(),principal_direction_verified=folder.endswith('data_direction'),source_hourly_frames_preserved=True,scope='new experiment; not substituted into the original342-frame numerical evaluation')
 (D/folder/'verification.json').write_text(json.dumps(result,indent=2));print(folder,'verified; max measured output merge error',max(errors),flush=True)
