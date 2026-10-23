"""Read-only tree, feature and event selection helpers for real-case figures."""
import numpy as np
from real_case_studies import DATA,read,write

def load(name):
 with np.load(DATA/f'{name}.npz',allow_pickle=False) as z:d={k:z[k] for k in z.files}
 return d,read(DATA/f'{name}.json')
def leaves_below(tree,node):
 ch=tree['children'][str(node)]
 return [node] if not ch else sum([leaves_below(tree,k) for k in ch],[])
def tree_at(meta,t):
 if meta['name']=='tangaroa':
  r=meta['features']['frames'][t]
  return dict(root=r['root'],children=r['children'],values=r['source_node_values'])
 return meta['trees'][t]
def lca(tree,i,j):
 parent={k:int(v) for v,ch in tree['children'].items() for k in ch};anc={i};cur=i
 while cur in parent:cur=parent[cur];anc.add(cur)
 cur=j
 while cur not in anc:cur=parent[cur]
 return cur

def find_witness(d,meta,t):
 tree=tree_at(meta,t);ids=d['leaf'][t];ids=ids[ids>=0];q=d['q'][t,:len(ids)];rank={int(v):i for i,v in enumerate(ids)};best=(-1,None,None)
 for node,ch in tree['children'].items():
  if not ch or int(node)==tree['root']:continue
  inside=[rank[v] for v in leaves_below(tree,int(node))];outside=sorted(set(range(len(ids)))-set(inside))
  if len(inside)<2 or not outside:continue
  i=min(inside,key=lambda j:q[j]);j=max(inside,key=lambda j:q[j])
  for k in outside:
   if q[i]<q[k]<q[j]:
    bound=float(min(q[k]-q[i],q[j]-q[k])/2)
    if bound>best[0]:best=(bound,[i,j,k],int(node))
 return best

def select(name,d,meta):
 candidates=[];L=float(d['geometry'][1]);T=len(d['track'])
 for t in range(1,T-1):
  b,w,node=find_witness(d,meta,t)
  if w is None or d['H'][t]/L<=.02:continue
  tracks=[int(d['track'][t,j]) for j in w]
  persistent=all(k in d['track'][t-1] and k in d['track'][t+1] for k in tracks)
  eP=float(np.nanmax(abs(d['uP'][t]-d['q'][t]))/L);eR=float(np.nanmax(abs(d['uR'][t]-d['q'][t]))/L)
  candidates.append(dict(t=t,witness=w,node=node,bound=b,tracks=tracks,persistent_three_frames=persistent,H=float(d['H'][t]/L),gain=eP-eR,errorP=eP,errorR=eR,delta=float(d['delta'][t])))
 if name=='era5':chosen=next(c for c in candidates if c['t']==48);rule='Retained interior witness frame 48 from fig_witness.py; selected before this presentation revision; not chosen by proxy accuracy.'
 elif name=='wildfire':
  eligible=[c for c in candidates if c['persistent_three_frames'] and c['gain']>0 and c['delta']>1e-8]
  chosen=max(eligible,key=lambda c:(c['H'],-c['t']));rule='Among H>2% frames with a witness triple matched in all three adjacent frames and positive P-to-R max-error reduction and measured cost, choose largest H (earliest tie). Descriptive selection, not unbiased performance evidence.'
 else:
  eligible=[c for c in candidates if c['persistent_three_frames'] and c['gain']>0 and c['delta']>1e-8]
  chosen=max(eligible,key=lambda c:(c['gain'],-c['t']));rule='Among H_lower>2% frames with a three-frame matched witness triple and positive measured relaxation cost, choose largest achieved P-to-R max-error reduction (earliest tie). Descriptive selection biased toward visible relaxation benefit.'
 chosen.update(rule=rule,snapshots=[chosen['t']-1,chosen['t'],chosen['t']+1],window=[max(0,chosen['t']-5),min(T,chosen['t']+6)])
 write(DATA/f'{name}_selection.json',dict(chosen=chosen,candidates=candidates))
 print('SELECTED',name,chosen,flush=True);return chosen

def feature_index(d,t,track):
 ix=np.flatnonzero(d['track'][t]==track);return int(ix[0]) if len(ix) else None

