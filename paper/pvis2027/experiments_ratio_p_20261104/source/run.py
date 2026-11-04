"""Frozen four-dataset experiment. Core algorithm files are never edited."""
from pathlib import Path
import sys,json,csv,time,hashlib,subprocess,argparse,platform,shutil,importlib.util
from dataclasses import replace,asdict
from types import SimpleNamespace
from contextlib import contextmanager
import numpy as np
from scipy.spatial.distance import pdist,squareform
from threadpoolctl import threadpool_limits,threadpool_info
W=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1];C=(W/'RG-MTM/code') if (W/'RG-MTM/code').exists() else W/'code'
sys.path[:0]=[str(C),str(C/'src'),str(C/'analysis')]
import anchormtm as am
import general_method as gm
import native_io as native
import filling
import rgmtm.reference_guided as renderer
from experiments.ring.dataset import generate as ring_generate
from rgmtm.baselines import stmtm as st
from experiments.volume3d.compact_tmtm import CompactTMTM
import experiments.stmtm_completion.run as completion
import conic_qp as conic
import raster_checked
import project_checked
from netCDF4 import Dataset,num2date
from scipy.ndimage import uniform_filter1d,gaussian_filter

PARAMS={
 'Gaussian':dict(nx=128,ny=128,T=64,p=.001,W='uniform',K=65,r=.95,lam=1.5,L=4096,Start=1,k=1),
 'Ring':dict(nx=14,ny=14,T=40,p=.001,W='uniform',K=1,r=.95,lam=1.5,L=196,Start=0,k=3),
 'Wildfires':dict(nx=64,ny=64,T=32,p=.15,W='uniform',K=10,r=.85,lam=.5,L=4096,Start=5,k=5),
 'Storms':dict(nx=281,ny=181,T=744,p=.105,W='inverse',K=135,r=.65,lam=.05,L=4096,Start=40,k=3)}
EPS=[i/100 for i in range(1,11)]
_native_renderer=renderer.render_sequence
def repaired_renderer(*args,**kwargs):
 try:return _native_renderer(*args,**kwargs)
 except ValueError as e:
  if 'fixed-reference raster cannot represent' not in str(e):raise
  return raster_checked.render_sequence(*args,**kwargs)
renderer.render_sequence=repaired_renderer

def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not np.isfinite(x):return None
 return x
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def table(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(clean(rows))
def read(p):return json.loads(p.read_text())
def sha(p):
 if not p.exists() and p.is_relative_to(W/'RG-MTM'):p=W/p.relative_to(W/'RG-MTM')
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def source(name):
 """Rebuild without outcome-dependent smoothing, pruning or resampling choices."""
 if name=='Ring':
  F,xy,meta=ring_generate();area=210**2/(14*14);meta.update(reconstruction='archived first-paper author generator; second-paper processed array not confirmed',sign=-1)
 elif name=='Gaussian':
  axis=np.linspace(0,120,128);X,Y=np.meshgrid(axis,axis);xy=np.c_[X.ravel(),Y.ravel()];F=[];l1=np.array([25.,25.]);l2=np.array([85.,85.]);start=np.array([115.,60.]);end=np.array([75.,35.]);sigma=7.
  for t in range(64):
   l3=start+(end-start)*min(1.,t/(64*.8));F.append(sum(amp*np.exp(-((X-v[0])**2+(Y-v[1])**2)/(2*sigma**2)) for v,amp in [(l1,1.),(l2,.95),(l3,1.05)]))
  area=120**2/128**2;meta=dict(reconstruction='explicit3-Gaussian reconstruction; previous local ridge omitted because it produced33 extrema. NOT author field',l1=l1,l2=l2,moving_start=start,moving_end=end,sigma=sigma,amplitudes=[1.,.95,1.05],motion='linear to end over first80% of64 frames, then fixed',sign=-1,span=120.,no_ridge=True)
 elif name=='Wildfires':
  path=C/'data/real/wildfire/wildfire.json';j=read(path);dates=j['timeseries']['series'];i=dates.index('2019-11-01');days=61
  cells=[c for top in j['data'] for c in (top.get('children') or [])];V=np.array([c['data'][i:i+days] for c in cells],float);assert V.shape[1]==61
  edges=np.linspace(0,days,33);weights=np.maximum(0,np.minimum(edges[1:,None],np.arange(days)+1)-np.maximum(edges[:-1,None],np.arange(days)))
  np.testing.assert_allclose(weights.sum(0),1);V=V@weights.T;active=V.sum(1)>0
  lat=np.array([c['lat'] for c in cells]);lon=np.array([c['lng'] for c in cells]);phi=np.deg2rad(lat[active].mean());x=111.32*np.cos(phi)*lon;y=110.57*lat
  side=max(np.ptp(x[active]),np.ptp(y[active]))*1.02;cx=(x[active].min()+x[active].max())/2;cy=(y[active].min()+y[active].max())/2;x0=cx-side/2;y0=cy-side/2
  ix=np.clip(((x-x0)/side*64).astype(int),0,63);iy=np.clip(((y-y0)/side*64).astype(int),0,63);F=np.zeros((32,64,64))
  for z in np.flatnonzero(active):F[:,iy[z],ix[z]]+=V[z]
  axis=(np.arange(64)+.5)*side/64;X,Y=np.meshgrid(axis,axis);xy=np.c_[X.ravel(),Y.ravel()];area=(side/64)**2
  meta=dict(source=str(path),source_sha256=sha(path),reconstruction='author-derived10km dailyFRP aggregated into32 equal-duration bins over Nov1-Jan1; fixed square64x64 spatial bins; NOT author32-frame array',bin_edges_days_since_2019_11_01=edges,temporal_rule='fractional overlap integration of piecewise-constant daily FRP;61/32 days per bin',spatial_rule='full active-window square bounds plus2% margin; fixed equirectangular km coordinates; sumFRP',no_log_transform=True,no_smoothing=True,no_background_regularization=True,no_leaf_count_filter=True,side_km=side,cells_10km=int(active.sum()),sign=-1)
 elif name=='Storms':
  path=native.RAW
  with Dataset(path) as ds:
   lon=np.array(ds['longitude'][:]);lat=np.array(ds['latitude'][:]);dates=[str(x) for x in num2date(ds['valid_time'][:],ds['valid_time'].units)];ii=[i for i,s in enumerate(dates) if s.startswith('1999-12-')];pressure=np.asarray(ds['msl'][:],np.float32)/100.
  base=uniform_filter1d(pressure,size=192,axis=0,mode='nearest');A=pressure[ii]-base[ii];F=np.array([gaussian_filter(f,sigma=2.,truncate=2.5,mode='reflect') for f in A]);X,Y=np.meshgrid(lon,lat);xy=np.c_[X.ravel(),Y.ravel()];area=.0625
  meta=dict(source=str(path),source_sha256=sha(path),reconstruction='native ERA5; 192h moving-mean anomaly, spatialGaussian sigma2 radius5 reflect; NOT confirmed author processed array',sign=1,dates=[dates[i] for i in ii],longitude=[float(lon.min()),float(lon.max())],latitude=[float(lat.min()),float(lat.max())])
 else:raise KeyError(name)
 F=np.asarray(F,np.float32);cfg=PARAMS[name];assert F.shape==(cfg['T'],cfg['ny'],cfg['nx']) and np.isfinite(F).all();meta.update(shape=list(F.shape),sample_measure=area,p_number=cfg['p'],p_percent=100*cfg['p'],p_fraction=cfg['p'],p_interpretation='ST-MTM Table1 number tested as a scalar-range fraction by explicit user instruction; not an author-confirmed protocol',threshold_scope='each preprocessed frame range',author_input_identical_confirmed=False)
 return F,np.asarray(xy,float),area,meta

def extract(name,F,dest,cache=True):
 cfg=PARAMS[name];dest.mkdir(parents=True,exist_ok=True);records=[]
 for t,field in enumerate(F):
  prefix=dest/f'frame_{t:03d}';jp=Path(str(prefix)+'.json');threshold=cfg['p']*float(np.ptp(field));sign=1 if name=='Storms' else -1
  if not(cache and jp.exists()):
   ip=dest/'input.npy';np.save(ip,np.asarray(sign*field,dtype='<f4'))
   with Path(str(prefix)+'.log').open('w') as log:subprocess.run([str(native.BIN),str(ip),str(prefix),str(cfg['nx']),str(cfg['ny']),'1',str(threshold),'1','0'],stdout=log,stderr=subprocess.STDOUT,check=True)
  row=read(jp);assert np.isclose(row['absolute_persistence_threshold'],threshold,rtol=1e-5,atol=1e-12);records.append(row)
  if(t+1)%100==0:print(name,'TREES',t+1,flush=True)
 return records

def load(name,F,xy,area,td):
 frames=[native.Frame(t,td,xy) for t in range(len(F))];ids=[list(f.leaves) for f in frames];centers=[];areas=[];tracks=[];matches=[];counter=0
 for t,(f,ii) in enumerate(zip(frames,ids)):
  centers.append(np.array([f.leaf_centroid(k) for k in ii]));areas.append(np.array([f.leaf_size(k)*area for k in ii]));m=st.match_leaves_by_overlap(frames[t-1],f) if t else {};old=dict(zip(ids[t-1],tracks[t-1])) if t else {};tr=[]
  for k in ii:
   if k in m:tr.append(old[m[k]])
   else:tr.append(counter);counter+=1
  tracks.append(tr);matches.append(m)
 sc=dict(fields=np.array([f.values.reshape(F.shape[1:]) for f in frames]),frames=frames,trees=[SimpleNamespace(kind='join') for _ in frames],ids=ids,centers=centers,areas=areas,tracks=tracks,matches=matches,hier=[f.hierarchy() for f in frames],coords=xy)
 return am.prepare_sequence(sc,xy.min(0),xy.max(0),len(xy)*area,am.FixedConfiguration(raster_length=PARAMS[name]['L']))

def subset(d,n):
 sc=dict(d['scene'])
 for k in ['fields','frames','trees','ids','centers','areas','tracks','matches','hier']:sc[k]=sc[k][:n]
 return dict(d,scene=sc,extrema=d['extrema'][:n],merge_values=d['merge_values'][:n],reference=dict(d['reference'],qs=d['reference']['qs'][:n]))

@contextmanager
def optimization_timer():
 orig=am.solve_anchored_sequence;total=[0.]
 def wrapped(*a,**kw):
  begin=time.perf_counter()
  try:return orig(*a,**kw)
  finally:total[0]+=time.perf_counter()-begin
 am.solve_anchored_sequence=wrapped
 try:yield total
 finally:am.solve_anchored_sequence=orig

def solve(d,eps):
 z=dict(d,configuration=replace(d['configuration'],epsilon0=0. if eps==0 else 1e-7));p=d['parameters']
 # Necessary, order-independent packing certificate: do not waste search on impossible instances.
 bad=[t for t,a in enumerate(d['scene']['areas']) if p.width_scale*sum(a)+(len(a)-1)*p.gap>p.canvas+1e-9]
 if bad:return dict(success=False,failures=[dict(stage='preflight',reason='sum fixed interval widths plus mandatory gaps exceeds fixed canvas',frames=bad)],layouts=[],seconds=0.,t_opt=0.)
 with optimization_timer() as elapsed:res=am.anchor_mtm(z,eps)
 res['t_opt']=elapsed[0];return res

def evaluate(name,d,res):
 if not res['success']:return dict(success=False,error=res['failures'],SNS=None,TW=None,TD=None,NPE=None),[]
 sc=d['scene'];p=d['parameters'];k=PARAMS[name]['k'];U=[x['pixel_x'] for x in res['layouts']];per=[];ss=[];ww=[];motion=0.;count=0
 for t,(u,c,q,tr,row) in enumerate(zip(U,sc['centers'],d['reference']['qs'],sc['tracks'],res['layouts'])):
  u=np.asarray(u);src=pdist(c);dst=pdist(u[:,None]);s=None;tw=None
  if len(src) and sum(src*src)>0:
   alpha=sum(src*dst)/sum(dst*dst) if sum(dst*dst)>0 else 0.;s=float(sum((src-alpha*dst)**2)/sum(src*src));ss.append(s);np.testing.assert_allclose(s,st.scale_normalized_stress(squareform(src),u),atol=1e-12)
  if 0<k<len(u)/2:tw=float(st.trustworthiness(c,u,k));ww.append(tw)
  step=0.;ct=0
  if t:
   old=dict(zip(sc['tracks'][t-1],U[t-1]))
   for key,x in zip(tr,u):
    if key in old:step+=abs(x-old[key])/p.canvas;ct+=1
  motion+=step;count+=ct;per.append(dict(frame=t,features=len(u),SNS=s,TW=tw,NPE=float(max(abs(u-q))/p.canvas),TD_unit_canvas_increment=float(step),matched_steps=ct,topology_mean=row['NMLEmean'],topology_max=row['NMLEmax'],continuous_budget_ok=row['continuous_budget_ok'],rendered_budget_ok=row['rendered_budget_ok']))
 assert np.isfinite(res['map']).all()
 return dict(success=True,SNS=float(np.mean(ss)) if ss else None,TW=float(np.mean(ww)) if ww else None,TD=float(motion),NPE=float(np.mean([r['NPE'] for r in per])),SNS_valid_frames=len(ss),TW_valid_frames=len(ww),TW_k=k,frames=len(U),matched_steps=count,topology_mean=float(np.mean([r['topology_mean'] for r in per])),topology_max=max(r['topology_max'] for r in per),continuous_budget_violations=sum(not r['continuous_budget_ok'] for r in per),rendered_budget_violations=sum(not r['rendered_budget_ok'] for r in per),collapsed_anchor_frames=sum(len(set(u))!=len(u) for u in U)),per

def save_result(dest,name,d,res,eps):
 sm,per=evaluate(name,d,res);sm.update(epsilon=eps,t_opt=res['t_opt'],method_seconds=res['seconds']);dump(dest/'summary.json',sm);dump(dest/'status.json',dict(success=res['success'],failures=res.get('failures',[])))
 if res['layouts']:dump(dest/'layouts.json',res['layouts'])
 if res['success']:table(dest/'per_frame.csv',per);np.savez_compressed(dest/'map.npz',map=res['map'])
 return sm

def baseline_npe(name,d):
 cfg=PARAMS[name];sc=d['scene'];p=d['parameters'];n=len(sc['frames']);N=cfg['L'];out=[];dest=O/'results'/name/'baseline_npe';dest.mkdir(parents=True,exist_ok=True)
 completion.qp=conic.solve
 for label,mode in [('TMTM','tmtm'),('ST-MTM Temporal','temporal')]:
  jp=dest/(mode+'.json')
  if jp.exists():
   previous=read(jp)
   if previous['success']:out.append(previous);continue
   archive=dest/(mode+'_original_failure.json')
   if not archive.exists():dump(archive,previous)
  print(name,'BASELINE_NPE',label,flush=True)
  try:
   if mode=='tmtm':
    objects=[CompactTMTM(f) for f in sc['frames']];lay=[None]*n;focus=cfg['Start'];lay[focus]=objects[focus].layout()
    for t in range(focus+1,n):_,lay[t],_=objects[t].align(objects[t-1],lay[t-1])
    for t in range(focus-1,-1,-1):_,lay[t],_=objects[t].align(objects[t+1],lay[t+1])
    size=max(o.length for o in objects);U=[p.canvas_origin+np.rint(np.array([r['positions'][k] for k in ids])*(N-1)/(size-1))*p.canvas/(N-1) for r,ids in zip(lay,sc['ids'])];cert=[]
   else:
    frames=[completion.Adapter(f,dict(centers=c,support_counts=[f.leaf_size(k) for k in f.leaves])) for f,c in zip(sc['frames'],sc['centers'])];params=st.LayoutParameters.from_preset(name.lower() if name!='Gaussian' else 'gaussian',mode=mode);sk=[None]*n;cert=[];project_cert=[]
    def one(t,prev):
     f=frames[t]
     if prev is None or mode=='base':order=st.optimal_hierarchical_leaf_order(f);tmp=None
     else:
      m=sc['matches'][t] if prev==t-1 else {v:k for k,v in sc['matches'][prev].items()};order=st.choose_temporal_order(f,sk[prev].ordering,m,params.reorder_threshold_r);tmp=st._temporal_positions(order,m,sk[prev])
     try:x=st.project_leaf_anchors(f,order,params,tmp)
     except RuntimeError as ex:
      x,certificate=project_checked.project(f,order,params,tmp,completion.qp);project_cert.append(dict(frame=t,original_error=str(ex),certificate=certificate))
     a,b,c=completion.intervals(f,order,x,params);cert.append(dict(frame=t,certificate=c));sk[t]=st.ContinuousSkeleton(tuple(order),x,a,b)
    one(cfg['Start'],None)
    for t in range(cfg['Start']+1,n):one(t,t-1)
    for t in range(cfg['Start']-1,-1,-1):one(t,t+1)
    ds,pad=st.discretize_skeletons(frames,sk,N);U=[p.canvas_origin+np.array([s.anchors[s.ordering.index(k)] for k in ids])*p.canvas/(N-1) for s,ids in zip(ds,sc['ids'])]
    # Verify that the complete map can be produced; do not compute SNS/TW/TD for baselines.
    for f,s in zip(frames,ds):assert np.isfinite(st.fill_frame(f,s,N)).all()
   flip=False
   for u,q in zip(U,d['reference']['qs']):
    if len(u)>1 and np.ptp(u)>0 and np.ptp(q)>0:flip=bool(sum((u-u.mean())*(q-np.mean(q)))<0);break
   if flip:U=[2*p.canvas_origin+p.canvas-u for u in U]
   per=[float(max(abs(u-q))/p.canvas) for u,q in zip(U,d['reference']['qs'])];assert np.isfinite(per).all();sm=dict(Dataset=name,Method=label,NPE=float(np.mean(per)),success=True,frames=n,one_global_reflection=flip,collapsed_anchor_frames=sum(len(set(u))!=len(u) for u in U),note='local NPE only; published SNS/TW/TD are NOT recalculated')
   dump(dest/(mode+'_anchors.json'),U);dump(dest/(mode+'_Eq2_certificates.json'),cert)
   if mode!='tmtm':dump(dest/(mode+'_Eq1_fallback_certificates.json'),project_cert)
   table(dest/(mode+'_per_frame.csv'),[dict(frame=i,NPE=x) for i,x in enumerate(per)])
  except (ValueError,RuntimeError,AssertionError) as ex:sm=dict(Dataset=name,Method=label,NPE=None,success=False,error=repr(ex))
  dump(jp,sm);out.append(sm)
 return out

def run_dataset(name):
 root=O/'results'/name;root.mkdir(parents=True,exist_ok=True);warm=root/'preparation';warm.mkdir(exist_ok=True)
 if not(warm/'fields.npy').exists():
  F,xy,area,meta=source(name);np.save(warm/'fields.npy',F);np.save(warm/'coordinates.npy',xy);dump(warm/'protocol.json',meta)
 else:F=np.load(warm/'fields.npy');xy=np.load(warm/'coordinates.npy');meta=read(warm/'protocol.json');area=meta['sample_measure']
 assert meta['p_fraction']==PARAMS[name]['p'],'p cache fingerprint mismatch'
 records=extract(name,F,warm/'trees');d=load(name,F,xy,area,warm/'trees');cfg=PARAMS[name]
 dump(root/'input_audit.json',dict(protocol=meta,features_min=min(map(len,d['scene']['ids'])),features_max=max(map(len,d['scene']['ids'])),nodes_min=min(x['nodes'] for x in records),nodes_max=max(x['nodes'] for x in records),fields_sha256=sha(warm/'fields.npy'),source_reference=d['reference'],parameters=asdict(d['parameters'])))
 pilot=root/'pilot'
 if not(pilot/'summary.json').exists():save_result(pilot,name,subset(d,min(8,cfg['T'])),solve(subset(d,min(8,cfg['T'])),0),0)
 nval=max(2,int(np.ceil(cfg['T']*.25)));dv=subset(d,nval);sweep=[]
 for eps in [0.]+EPS:
  folder=root/'selection'/f'epsilon_{eps:g}';jp=folder/'summary.json'
  if jp.exists():sm=read(jp)
  else:
   print(name,'VALIDATE',eps,nval,flush=True);sm=save_result(folder,name,dv,solve(dv,eps),eps)
  sweep.append(sm)
 ex=sweep[0];eligible=[]
 for sm in sweep[1:]:
  gain=(ex['NPE']-sm['NPE'])/ex['NPE'] if ex['success'] and ex['NPE'] and sm['success'] else None
  ok=bool(sm['success'] and sm['NPE'] is not None and sm['SNS'] is not None and sm['topology_max']<=sm['epsilon']+1e-12 and sm['rendered_budget_violations']==0)
  sm.update(validation_gain=gain,eligible=ok,NPE_norm=None,SNS_norm=None,J=None)
  if ok:eligible.append(sm)
 if not eligible:raise RuntimeError(name+': no legal positive validation candidate; do not fall back to zero, repair numerical/data issue first')
 normalization={}
 for metric in ['NPE','SNS']:
  low=min(s[metric] for s in eligible);high=max(s[metric] for s in eligible);normalization[metric]=dict(min=low,max=high,constant=(high-low<=1e-12))
  for s in eligible:s[metric+'_norm']=0. if high-low<=1e-12 else (s[metric]-low)/(high-low)
 for s in eligible:s['J']=.5*s['NPE_norm']+.5*s['SNS_norm']
 jmin=min(s['J'] for s in eligible);near=[s for s in eligible if s['J']<=jmin+.01+1e-12];chosen=min(near,key=lambda s:(s['epsilon'],s['topology_max']));selected=chosen['epsilon'];assert selected>0
 selection=dict(validation_frames=list(range(nval)),assessment_frames=list(range(nval,cfg['T'])),rule='positive epsilon1..10%; actualmax<=nominal epsilon; minmax normalize validation NPE/SNS over legal positive candidates; J=.5NPE_norm+.5SNS_norm; within Jmin+.01 prefer lower epsilon then lower actualtopology; NEVER fallback0',epsilon=selected,status='positive_budget_balanced_selected',candidates=sweep,normalization=normalization,J_min=jmin,J_selected=chosen['J'],near_optimal_J_tolerance=.01,near_optimal_epsilons=[s['epsilon'] for s in near],rule_version=3)
 dump(root/'selection.json',selection)
 for label,eps in [('Exact',0.),('Balanced',selection['epsilon'])]:
  dest=root/label
  if (dest/'summary.json').exists():
   prior=read(dest/'summary.json')
   if prior['success'] and prior.get('epsilon')==eps and (label=='Exact' or prior.get('selection_rule_version')==3):continue
   archive=O/'archive/before_rule_v3_outputs'/name/label
   archive.parent.mkdir(parents=True,exist_ok=True)
   if not archive.exists():shutil.move(dest,archive)
  print(name,'COLD_PIPELINE',label,eps,flush=True);begin=time.perf_counter();F2,xy2,area2,meta2=source(name);t_pre=time.perf_counter()-begin;np.testing.assert_array_equal(F,F2);np.testing.assert_array_equal(xy,xy2)
  start=time.perf_counter();extract(name,F2,dest/'timing_trees',cache=False);t_tree=time.perf_counter()-start
  start=time.perf_counter();d2=load(name,F2,xy2,area2,dest/'timing_trees');t_features=time.perf_counter()-start;res=solve(d2,eps);total=time.perf_counter()-begin
  sm=save_result(dest,name,d2,res,eps);sm.update(t_total=total if res['success'] else None,failure_elapsed=total if not res['success'] else None,t_preprocess=t_pre,t_topology=t_tree,t_features_reference=t_features,repeats=1,cache_used_for_reported_timing=False,selection_rule_version=3,timing_scope='source read/generation, preprocessing, sequential native extraction including subprocess and I/O, matching/reference, optimization/reconstruction/intrinsic checks; excludes metric/report export')
  if res['success']:assert sm['topology_max']<=eps+1e-12,'final nominal topology budget exceeded; do not retune on test'
  if res['success']:
   per=read_csv(dest/'per_frame.csv');sm['assessment_NPE']=float(np.mean([float(r['NPE']) for r in per[nval:]]));sm['validation_NPE']=float(np.mean([float(r['NPE']) for r in per[:nval]]))
  dump(dest/'summary.json',sm);print(name,label,{k:sm.get(k) for k in ['success','SNS','TW','TD','NPE','epsilon','t_opt','t_total']},flush=True)
 baseline_npe(name,d)

def read_csv(p):
 with p.open() as f:return list(csv.DictReader(f))

def init():
 dump(O/'config/paper_parameters.json',PARAMS)
 dump(O/'config/protocol.json',dict(created='2026-11-04',rule_version=3,datasets=list(PARAMS),p_units='fraction of each preprocessed frame range: .001,.001,.15,.105; percent equivalents .1,.1,15,10.5; user-requested ratio test',reconstruction_permission='user explicitly approved clearly labelled reconstructed inputs',epsilon_candidates=[0.]+EPS,balanced_rule=dict(validation='first25% chronological frames; global unsupervised reference frozen from complete input',actual_topology_max='each candidate nominalepsilon, at most10%',minimum_relative_NPE_gain=None,normalization='minmax over legal positive validation candidates, component0 when range<=1e-12; raw metrics unchanged',score='J=.5NPE_norm+.5SNS_norm',near_optimal_J_tolerance=.01,selection='within .01 of minimumJ prefer lower epsilon then lower actualtopology',failure='NO epsilon0 fallback; repair illegality instead',post_selection='freeze independently per dataset then rerun final Balanced cold pipeline'),statistics='full-sequence main metrics; held-out75% NPE separately; historical results were previously observed, not a new blind test',ranking='Four displayed methods per dataset, no Base; SNS/TW/NPE numeric best/second; TD best/second within published and normalized-local unit groups; separate optimization and total time columns; TW coverage only in note',timing=dict(repeats=1,native_threads=1,workers=1,BLAS_threads=1,HiGHS_threads='auto/default',cold_source_and_trees=True,validation_cache='allowed but excluded from cold timings'),baseline_policy='quote SNS/TW/TD Table1; recompute NPE only',TD='sum adjacent matched final-anchor displacement / full fixed physical canvas extent, no percentage or temporal average',TW='paper k, valid only0<k<n/2; missing notzero',raster_fix='only if native independent rounding fails, solve closest legal integer skeleton at SAME L; continuous order,x,z,w unchanged; nearest anchors fixed where feasible; otherwise minimal joint rounding; validate rendered topology',no_core_algorithm_edits=True))
 dump(O/'config/environment.json',dict(platform=platform.platform(),python=sys.version,numpy=np.__version__,threadpools=threadpool_info(),cpu=subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip()))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',choices=list(PARAMS));ap.add_argument('--baseline-npe-only',action='store_true');args=ap.parse_args()
 with threadpool_limits(limits=1):
  init()
  for name in [args.dataset] if args.dataset else PARAMS:
   if args.baseline_npe_only:
    path=O/'results'/name/'preparation';F=np.load(path/'fields.npy');xy=np.load(path/'coordinates.npy');meta=read(path/'protocol.json');baseline_npe(name,load(name,F,xy,meta['sample_measure'],path/'trees'))
   else:run_dataset(name)
