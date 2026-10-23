"""Independent checks of the new case against unchanged annual source arrays."""
from pathlib import Path
import sys,json,pickle,hashlib,itertools
import numpy as np
R=Path(__file__).resolve().parents[1];C=R.parent/'code';sys.path[:0]=[str(C/'analysis'),str(C/'src'),str(C)]
O=R/'evidence/pm25_case20261023';j=json.loads((O/'case.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in j['source_sha256'].items():assert sha(p)==h,p
with(C/'results/pm25_2000/dataset.pkl').open('rb')as f:ds=pickle.load(f)
sc=ds['sc'];z=np.load(C/'results/pm25_2000/landmarks.npz');g=np.load(C/'results/pm25_2000/maps.npz');a=np.load(O/'case_arrays.npz');t=j['selected']['frame'];lo,hi=j['local_window']
np.testing.assert_array_equal(a['local_P'],g['A'][:,lo:hi]);np.testing.assert_array_equal(a['local_R20'],g['R 20%'][:,lo:hi]);np.testing.assert_array_equal(a['processed_case'],sc['fields'][t])
# Reconstruct the projection independently from tracked displacements and domain corners.
delta=[]
for u in range(1,366):
 prev={tr:i for i,tr in enumerate(sc['tracks'][u-1])}
 for i,tr in enumerate(sc['tracks'][u]):
  if tr in prev:delta.append(z['extrema'][u,i]-z['extrema'][u-1,prev[tr]])
delta=np.array(delta);e,v=np.linalg.eigh(np.einsum('ni,nj->ij',delta,delta));axis=v[:,-1]
if np.einsum('ni,i->',delta,axis)<0:axis=-axis
corners=np.array(list(itertools.product(*zip(ds['lo'],ds['hi']))));projected=np.einsum('ni,i->n',corners,axis);origin=projected.min();extent=np.ptp(projected)
for u,n in enumerate(z['count']):
 q=(np.einsum('ni,i->n',z['extrema'][u,:n],axis)-origin)/extent;np.testing.assert_allclose(q,a['reference'][u,:n],atol=1e-12)
# Independently measure every labelled barrier in the selected window, including diagonals.
span=float(np.ptp(sc['fields']));direct={};position={}
for method,key,ui in [('P','A','u2'),('R20','R 20%','u3')]:
 vals=[]
 for u in range(lo,hi):
  ids=sc['ids'][u];fr=sc['frames'][u];col=g[key][:,u];anchors=np.rint(z[ui][u,:len(ids)]*(len(col)-1)).astype(int);errors=[]
  for ii in range(len(ids)):
   for jj in range(ii,len(ids)):
    left,right=sorted([anchors[ii],anchors[jj]]);actual=float(col[left:right+1].min());truth=float(fr.values[fr.lca(ids[ii],ids[jj])]);errors.append(abs(actual-truth))
  vals.append(max(errors)/span)
 direct[method]=vals
 position[method]=float(max(abs(z[ui][t,:z['count'][t]]-a['reference'][t,:z['count'][t]])))
assert max(direct['P'])<1e-12
np.testing.assert_allclose(direct['R20'],[x['share']for x in j['local_NMLE']],atol=1e-12)
for m,v in position.items():assert abs(v-j['displayed_anchor_error'][m])<1e-12
assert j['local_max_concentration']<=100
assert [x['frame']for x in j['candidates']if x['consecutive_frames']>=3]==[185,186,195,196,317]
assert j['selected']['frame']==195 and j['selected']['tracks']==[153,146,152]
for u in range(195,198):assert set(j['selected']['tracks'])<=set(sc['tracks'][u])
# Validate the reported C jump against the saved reference and actual raster anchors.
for x in j['track_C_Jul14_to_15']:
 rows=a['reference']if x['method']=='reference'else z['u2'if x['method']=='P'else'u3'];indices=[int(np.flatnonzero(z['tracks'][u]==152)[0])for u in [195,196]];change=rows[196,indices[1]]-rows[195,indices[0]];assert abs(change-x['change_L'])<1e-12
rep=json.loads((O/'display_reconstruction.json').read_text());assert rep['annual_R20']['original_frames_exact']
for m in ['P','R20']:assert rep['local'][m]['original_frames_exact'] and rep['local'][m]['display_samples_per_frame']==41 and rep['local'][m]['no_scalar_overshoot']
# Preserve all former figures, with the former Fig13 moved intact to Fig14.
before=json.loads((R/'checks/pm25_case20261023/before.json').read_text())
for name,h in before['figure_sha256'].items():
 if Path(name).stem in {'Fig7','Fig10','Fig11'}:
  continue # Later authorized geographic and temporal display revisions have independent checks.
 path=R/name.replace('Fig13.','Fig14.');assert sha(path)==h,name
out=dict(status='passed',frames=366,case_frame=195,case_date='2000-07-14',eligible_frames=[185,186,195,196,317],source_hashes_verified=True,independent_annual_direction=axis.tolist(),unchanged_scientific_arrays=True,reference_verified_all_frames=True,displayed_anchor_error=position,measured_NMLE_case=direct['R20'][t-lo],measured_NMLE_window_max=max(direct['R20']),C_anchor_changes=j['track_C_Jul14_to_15'],former_figures_preserved_except_authorized_later_display_revisions=True,former_Fig13_preserved_as_Fig14=True)
p=R/'checks/pm25_case20261023/numerical.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
