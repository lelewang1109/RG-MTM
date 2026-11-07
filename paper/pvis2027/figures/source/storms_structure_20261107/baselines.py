from pathlib import Path
import sys,pickle,types,numpy as np
O=Path(__file__).resolve().parent;P=O.parents[2];W=P.parents[1];C=W/'RG-MTM/code';sys.path[:0]=[str(C),str(C/'src'),str(C/'analysis')]
from rgmtm.baselines import stmtm as st
class NativeMultiwayFrame(st.AugmentedMergeTreeFrame):pass
NativeMultiwayFrame.__module__=st.__name__;st.NativeMultiwayFrame=NativeMultiwayFrame
sc=pickle.loads((W/'output/storms_hourly_anomaly_fine_20261030/scene.pkl').read_bytes());f=sc['frames'][0]
print(sc.keys(),flush=True);print(type(f),f.__dict__.keys(),flush=True);print(type(f.arcs),list(f.arcs)[:8],type(next(iter(f.arcs.values()))),flush=True)
import json,hashlib
from dataclasses import asdict,replace
from threadpoolctl import threadpool_limits
from experiments.volume3d.compact_tmtm import CompactTMTM
from experiments.stmtm_completion.run import Adapter,intervals
# Adapter-only interfaces; preserve every scalar sample and original leaf LCA.
NativeMultiwayFrame.lca_values=lambda f:np.array([[f.values[f.lca(a,b)] for b in f.leaves] for a in f.leaves])
for f in sc['frames']:
 owner=np.full(len(f.values),-1,dtype=np.int32)
 for i,arc in f.arcs.items():owner[np.asarray(arc.regular_vertices,dtype=int)]=i;owner[arc.child]=i
 owner[f.root]=next(iter(f.arcs));assert (owner>=0).all();f.owner=owner
n=len(sc['frames']);N=8192;focus=40;maps={};config={}
with threadpool_limits(limits=1):
 if (O/'baseline_maps.npz').exists():raise SystemExit('Baseline cache already exists')
 objects=[CompactTMTM(f) for f in sc['frames']];lays=[None]*n;dec=[None]*n;dec[focus]={};lays[focus]=objects[focus].layout()
 for t in range(focus+1,n):dec[t],lays[t],_=objects[t].align(objects[t-1],lays[t-1])
 for t in range(focus-1,-1,-1):dec[t],lays[t],_=objects[t].align(objects[t+1],lays[t+1])
 length=max(o.length for o in objects);idx=np.rint(np.linspace(0,length-1,N)).astype(int);cols=[]
 for obj,ds in zip(objects,dec):
  out=obj.layout(ds,render=True)['values'];cols.append(np.pad(out,(0,length-len(out)),mode='edge')[idx])
 maps['TMTM']=np.column_stack(cols);config['TMTM']=dict(Start=focus,native_length=length,multiway='normal/reverse subtree ordering and equal-level virtual separator copies',raster=N);print('TMTM done',flush=True)
 af=[Adapter(f,dict(centers=c,support_counts=[f.leaf_size(k) for k in f.leaves])) for f,c in zip(sc['frames'],sc['centers'])];params=st.LayoutParameters.from_preset('storms',mode='temporal');sk=[None]*n;logs=[]
 def one(t,prev):
  f=af[t]
  if prev is None:order=st.optimal_hierarchical_leaf_order(f);tmp=None
  else:
   match=sc['matches'][t] if prev==t-1 else {v:k for k,v in sc['matches'][prev].items()};order=st.choose_temporal_order(f,sk[prev].ordering,match,params.reorder_threshold_r);tmp=st._temporal_positions(order,match,sk[prev])
  x=st.project_leaf_anchors(f,order,params,tmp)
  try:a,b=st.allocate_leaf_intervals(f,order,x,params)
  except RuntimeError:
   a,b,cert=intervals(f,order,x,params);logs.append(dict(frame=t,certificate=cert))
  sk[t]=st.ContinuousSkeleton(tuple(order),x,a,b)
 one(focus,None)
 for t in range(focus+1,n):
  one(t,t-1)
  if t%100==0:print('ST-MTM',t,flush=True)
 for t in range(focus-1,-1,-1):one(t,t+1)
 discrete,pad=st.discretize_skeletons(af,sk,N);maps['STMTM']=np.column_stack([st.fill_frame(f,s,N) for f,s in zip(af,discrete)]);config['STMTM']=dict(parameters=asdict(params),multiway='stable-ID equal-level binary refinement; original leaf LCA matrices checked',interval_fallbacks=logs,padding=pad,raster=N)
 assert all(m.shape==(N,744) and np.isfinite(m).all() for m in maps.values());np.savez_compressed(O/'baseline_maps.npz',**maps)
 config.update(field_sha256=hashlib.sha256(sc['fields'].tobytes()).hexdigest(),same_input=True,frames=744,display_scale=[-35,35],whole_sequence_reflection=False,implementation='local implementations with explicit multiway adapters; not author binaries')
 (O/'baseline_protocol.json').write_text(json.dumps(config,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else float(x)))
 print('BASELINES COMPLETE',flush=True)
