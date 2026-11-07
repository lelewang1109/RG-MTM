from pathlib import Path
import sys,json,numpy as np,hashlib
from dataclasses import asdict
O=Path(__file__).resolve().parent;P=O.parents[2];sys.path.insert(0,str(P/'experiments_ratio_p_20261104/source'));import run as r
from experiments.volume3d.compact_tmtm import CompactTMTM
from experiments.stmtm_completion.run import Adapter,intervals
from rgmtm.baselines import stmtm as st
D=P/'experiments_ratio_p_20261104/results/Ring';prep=D/'preparation';F=np.load(prep/'fields.npy');xy=np.load(prep/'coordinates.npy');d=r.load('Ring',F,xy,225,prep/'trees');sc=d['scene'];frames=sc['frames'];n=len(frames);N=196;maps={};config={}
with r.threadpool_limits(limits=1):
 focus=0;objs=[CompactTMTM(f) for f in frames];lays=[None]*n;dec=[None]*n;lays[focus]=objs[focus].layout();dec[focus]={}
 for t in range(1,n):dec[t],lays[t],_=objs[t].align(objs[t-1],lays[t-1])
 L=max(o.length for o in objs);ix=np.rint(np.linspace(0,L-1,N)).astype(int);cols=[]
 for obj,ds in zip(objs,dec):
  v=obj.layout(ds,render=True)['values'];cols.append(np.pad(v,(0,L-len(v)),mode='edge')[ix])
 maps['TMTM']=-np.column_stack(cols);config['TMTM']=dict(Start=focus,native_length=L,raster=N,multiway='same-level separator copies; normal/reversed overlap alignment')
 af=[Adapter(f,dict(centers=c,support_counts=[f.leaf_size(k) for k in f.leaves])) for f,c in zip(frames,sc['centers'])];params=st.LayoutParameters.from_preset('ring',mode='temporal');sk=[None]*n;logs=[]
 for t,f in enumerate(af):
  if t==0:order=st.optimal_hierarchical_leaf_order(f);temp=None
  else:
   match=sc['matches'][t];order=st.choose_temporal_order(f,sk[t-1].ordering,match,params.reorder_threshold_r);temp=st._temporal_positions(order,match,sk[t-1])
  x=st.project_leaf_anchors(f,order,params,temp)
  try:a,b=st.allocate_leaf_intervals(f,order,x,params)
  except RuntimeError:
   a,b,cert=intervals(f,order,x,params);logs.append(dict(frame=t,certificate=cert))
  sk[t]=st.ContinuousSkeleton(tuple(order),x,a,b)
 ds,pad=st.discretize_skeletons(af,sk,N);maps['STMTM']=-np.column_stack([st.fill_frame(f,s,N) for f,s in zip(af,ds)]);config['STMTM']=dict(parameters=asdict(params),raster=N,padding=pad,interval_fallbacks=logs,multiway='stable-ID equal-level binary refinement; original labelled LCA verified')
 assert all(v.shape==(196,40) and np.isfinite(v).all() for v in maps.values());np.savez_compressed(O/'baseline_maps.npz',**maps)
 config.update(source_field_sha256=hashlib.sha256((prep/'fields.npy').read_bytes()).hexdigest(),frames=40,shape=[14,14],same_source_fields_and_trees=True,sign='join sign negated back to source scalar',main_tables_unchanged=True,local_implementations_not_author_binaries=True)
 (O/'baseline_protocol.json').write_text(json.dumps(config,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else float(x)));print('Ring baseline maps ready',flush=True)
