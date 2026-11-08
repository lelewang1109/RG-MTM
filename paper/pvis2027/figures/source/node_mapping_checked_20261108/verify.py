from pathlib import Path
import sys,numpy as np,json
from types import SimpleNamespace as NS
R=Path('/Users/lele/Desktop/MergeTreeMaps');sys.path.insert(0,str(R/'RG-MTM/code/src'));from rgmtm.baselines.stmtm import fill_frame,DiscreteSkeleton
names=['R','r₂','r₁','S₀','u₂','u₁','S₁','a₃','a₂','a₁','A','d₃','d₂','d₁','D','c₁','C','b₁','B'];values=[18,17,16,15,14,13,12,11,10,9,3,8,7,6,2,5,0,4,1];ix={k:i for i,k in enumerate(names)}
arcs={c:NS(child=ix[c],parent=ix[p],regular_vertices=np.array([ix[k] for k in v],int)) for c,p,v in [('A','S₀',['a₁','a₂','a₃']),('D','S₀',['d₁','d₂','d₃']),('C','S₁',['c₁']),('B','S₁',['b₁']),('S₁','S₀',['u₁','u₂']),('S₀','R',['r₁','r₂'])]}
class Frame:
 timestep=0;root=ix['R'];values=np.array(values,float)
 def arc_for_child(self,k):return arcs[names[k]]
 def lca(self,a,b):
  def parents(k):
   result=[k]
   while k!=self.root:k=self.arc_for_child(k).parent;result.append(k)
   return result
  pa=parents(a);pb=parents(b);return next(k for k in pa if k in pb)
 def nonleaf_path_to_ancestor(self,leaf,ancestor):
  k=self.arc_for_child(leaf).parent;out=[]
  while k!=ancestor:arc=self.arc_for_child(k);out.append(arc);k=arc.parent
  return out
f=Frame();order=tuple(ix[k] for k in ['A','C','B','D']);sk=DiscreteSkeleton(order,np.array([4,10,13,19]),np.array([2,9,12,17]),np.array([5,10,13,20]));out=fill_frame(f,sk,23);seq=[names[values.index(int(v))] for v in out];expect=['r₂','r₁','a₃','a₁','A','a₂','S₀','u₂','u₁','c₁','C','S₁','b₁','B','u₁','u₂','S₀','d₃','d₁','D','d₂','r₁','r₂'];assert seq==expect
for i,a in enumerate(order):
 for j,b in enumerate(order):
  lo,hi=sorted([sk.anchors[i],sk.anchors[j]]);assert out[lo:hi+1].max()==f.values[f.lca(a,b)]
O=Path(__file__).parent;(O/'verified_sequence.json').write_text(json.dumps(dict(sequence=seq,anchors=sk.anchors.tolist(),starts=sk.starts.tolist(),ends=sk.ends.tolist(),values=out.tolist(),all_pair_LCA_preserved=True,regular_sampling_count_matches=True,root_not_forced_to_boundary=True,note='Example integer skeleton; real layouts may resample path values. Root critical sample need not occur explicitly; boundaries sample regular arc values.'),ensure_ascii=False,indent=2));print(seq)
