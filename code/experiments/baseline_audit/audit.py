"""Audit both baselines on the existing real ERA5 and Wildfire inputs only.

No Gaussian/synthetic input, parameter tuning, scientific-result overwrite or
complete experiment rerun. C++ harness contains verbatim pinned official TMTM
landscape/greedy routines. ST-MTM is checked against its equations independently.
"""
from pathlib import Path
from itertools import combinations
import sys,json,hashlib,subprocess
import numpy as np
from scipy.optimize import nnls,linprog
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'analysis'),str(ROOT/'src')]
from rgmtm.baselines import tmtm as tm,stmtm as st
from experiments import era5 as ep
from real_case_studies import read,write,sha
OUT=ROOT/'results/baseline_audit_20261019'

def all_orders(fr,node=None):
 node=fr.root if node is None else node;ch=fr.children[node]
 if not ch:return [(node,)]
 if len(ch)==1:return all_orders(fr,ch[0])
 assert len(ch)==2
 left,right=[all_orders(fr,k) for k in ch]
 return [o for a in left for b in right for o in [a+b,b+a]]

def stress_kkt(fr,order,x,p,temporal):
 n=len(order)
 if n<=1:return 0.
 C=np.array([fr.leaf_centroid(k) for k in order]);D=np.linalg.norm(C[:,None]-C[None,:],axis=2)
 B=np.array([np.eye(n)[j]-np.eye(n)[i] for i,j in combinations(range(n),2)]);target=np.array([D[i,j] for i,j in combinations(range(n),2)])
 w=np.ones(len(B)) if p.weights=='uniform' else 1/target
 # Independently assembled convex quadratic gradient.
 g=2*B.T@(w*(B@x-target));lam=p.temporal_lambda if p.mode=='temporal' else 0
 for i,k in enumerate(order):
  if temporal and k in temporal:g[i]+=2*lam*(x[i]-temporal[k])
 A=np.diff(np.eye(n),axis=0);slack=A@x-p.min_spacing_delta;assert np.min(slack)>-1e-7
 active=A[slack<2e-6];columns=list(active)
 if not temporal or lam==0:columns += [np.ones(n),-np.ones(n)]
 if columns:
  M=np.array(columns).T;mu,res=nnls(M,g,maxiter=10000);res=np.linalg.norm(M@mu-g)
 else:res=np.linalg.norm(g)
 return float(res/(1+np.linalg.norm(B.T@(w*target))))

def interval_kkt(fr,order,x,s,e,p):
 n=len(order);sizes=np.array([fr.leaf_size(k)for k in order],float);target=p.total_leaf_extent_k*sizes**p.alpha/np.sum(sizes**p.alpha)
 eps=min(max(p.min_spacing_delta*.1,1e-9),p.total_leaf_extent_k/(8*n),min(target)/4)
 if n>1:eps=min(eps,min(np.diff(x))/8)
 I=np.eye(n);A=[];b=[]
 for i in range(n):A += [np.r_[-I[i],np.zeros(n)],np.r_[np.zeros(n),I[i]]];b += [eps-x[i],eps+x[i]]
 for i in range(n-1):A.append(np.r_[I[i+1],-I[i]]);b.append(eps)
 A=np.array(A);b=np.array(b);z=np.r_[s,e];slack=A@z-b;assert min(slack)>-2e-6
 h=np.r_[-np.ones(n),np.ones(n)];assert abs(h@z-p.total_leaf_extent_k)<1e-6
 r=2*(e-s-target)/target**2;g=np.r_[-r,r];active=A[slack<2e-6];M=np.c_[active.T,h,-h];mu,res=nnls(M,g,maxiter=10000)
 return float(np.linalg.norm(M@mu-g)/(1+np.linalg.norm(2/target)))

def topology(fr,ids,col,anchors,kind):
 result=0.
 for i,j in combinations(range(len(ids)),2):
  a,b=sorted([int(anchors[i]),int(anchors[j])]);level=(np.max if kind=='join'else np.min)(col[a:b+1]);result=max(result,abs(level-fr.values[fr.lca(ids[i],ids[j])]))
 return float(result)

def official_check(sc,layouts,decisions,exe):
 trees=sc['trees'];lines=[str(len(trees)-1)]
 for t in range(1,len(trees)):
  old,new=trees[t-1:t+1];oldlayout=layouts[t-1];nodes=list(new.nodes);remap={k:i for i,k in enumerate(nodes)};arcs=list(new.arcs);assert arcs==list(range(len(arcs)))
  lines.append(f'{len(old.arcs)} {len(arcs)} {len(nodes)} {remap[new.root]} {new.sample_count}')
  for a in old.arcs:lines.append(' '.join(map(str,oldlayout.subtree_intervals[a])))
  for v in nodes:lines.append(' '.join(map(str,[len(new.nodes[v].child_arcs),*new.nodes[v].child_arcs])))
  for a in arcs:
   arc=new.arcs[a];lines.append(f'{remap[arc.child]} {len(arc.regular_vertices)+1+int(arc.parent==new.root)} {new.subtree_size(a)}')
  for a in old.arcs:lines.append(' '.join(str(len(old.subtree_vertices(a)&new.subtree_vertices(b)))for b in arcs))
 output=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True).stdout
 branches=0;intervals=0;mismatches=[]
 for line in output.splitlines():
  v=line.split();t=int(v[0])+1;rows=np.array(v[2:],int).reshape(-1,4);tree=trees[t]
  for a,arc in tree.arcs.items():
   decision,lo,hi,anchor=rows[a];branches+=len(tree.nodes[arc.child].child_arcs)>=2;intervals+=1
   if bool(decision)!=bool(decisions[t].get(arc.child,False))or (lo,hi)!=layouts[t].subtree_intervals[a]or anchor!=layouts[t].position_of_vertex[arc.child]:mismatches.append(dict(frame=t,arc=a))
 assert not mismatches,mismatches[:10]
 return dict(adjacent_pairs=len(trees)-1,branch_decisions=branches,arc_intervals_and_anchors=intervals,mismatches=mismatches)

def run():
 import replicate as rp,general_method as gm
 OUT.mkdir(exist_ok=True);temp=ROOT/'tmp/baseline_audit';temp.mkdir(exist_ok=True);exe=temp/'official_core_fixture';cpp=Path(__file__).with_name('official_core_fixture.cpp')
 subprocess.run(['clang++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
 report=dict(scope='Actual existing ERA5 118 and Wildfire 30 frames; no Gaussian or new synthetic data; algorithms and saved results audited separately from paper dataset settings.',official_tmtm_commit='2c75a10ed2cd55177a25ff751e0c0a8261200717',official_harness_sha256=sha(cpp),datasets={},source_sha256={str(p.relative_to(ROOT)):sha(p)for p in [ROOT/'src/rgmtm/baselines/tmtm.py',ROOT/'src/rgmtm/baselines/stmtm.py',ROOT/'experiments/era5.py',Path(__file__)]})
 for name in ['era5','wildfire']:
  print('Audit real input',name,flush=True);ds=rp.LOADERS[name]();sc=ds['sc'];trees=sc['trees'];dec,layouts,_=tm.optimize_temporal_order(trees);off=official_check(sc,layouts,dec,exe);max_top=0.;perm=0
  for tr,fr,ids,lin in zip(trees,sc['frames'],sc['ids'],layouts):
   assert np.array_equal(np.sort(lin.vertex_at_position),np.arange(tr.sample_count));perm+=1
   for a in tr.arcs:
    ix=lin.position_of_vertex[list(tr.subtree_vertices(a))];assert max(ix)-min(ix)+1==len(ix)
   col=tr.values[lin.vertex_at_position];max_top=max(max_top,topology(fr,ids,col,lin.position_of_vertex[ids],tr.kind))
  print(name,'TMTM official core equivalent',off,flush=True)
  span=ds['native_span'];p=gm.Parameters(canvas=span,canvas_origin=float(min(ds['lo'][0],0)),width_scale=.5*span/ds['domain_area'],gap=span/240,extra_budget=span/120,rho=.5)
  b=ep.run_method(sc,'ST-MTM',p,canvas=span,length=ds['nominal'],refine_raster=False,strict_checks=False);rec=b['records'];params=st.LayoutParameters(**rec['parameters']);continuous=rec['continuous'];discrete=rec['discrete'];worst1=0.;worst2=0.;olo_worst=0.;olo_exhaustive_discrepancies=[];scores=[];max_top_st=0.;bad_signatures=[];cases={k:0 for k in ['siblings','direct_deep','deep_deep','border']}
  for t,(fr,ids,c,s) in enumerate(zip(sc['frames'],sc['ids'],continuous,discrete)):
   order=tuple(c['ordering']);assert order in all_orders(fr)
   # Brute force the hierarchy-constrained adjacency objective on every actual tree.
   centroids={v:fr.leaf_centroid(v)for v in ids}
   cost=lambda o:sum(np.linalg.norm(centroids[i]-centroids[j])for i,j in zip(o[:-1],o[1:]))
   olo=st.optimal_hierarchical_leaf_order(fr);best=min(cost(o)for o in all_orders(fr));olo_worst=max(olo_worst,float(abs(cost(olo)-best)))
   if abs(cost(olo)-best)>1e-7:olo_exhaustive_discrepancies.append(dict(frame=t,scipy_cost=float(cost(olo)),exhaustive_cost=float(best),scipy_order=list(olo)))
   temporal=None
   if t:
    prev=continuous[t-1];matches=sc['matches'][t];rank={v:j for j,v in enumerate(prev['ordering'])}
    temporal={v:prev['anchors'][rank[matches[v]]]for v in order if v in matches}
    score=lambda o:sum(rank[matches[a]]<rank[matches[b]]for a,b in combinations(o,2)if a in matches and b in matches)
    concordant=st.temporally_concordant_order(fr,prev['ordering'],matches);opt_score=max(score(o)for o in all_orders(fr));assert score(concordant)==opt_score
    oriented=olo if score(olo)>=score(olo[::-1])else olo[::-1];ratio=cost(oriented)/cost(concordant)if cost(concordant)>0 else 1
    expected=oriented if ratio<=params.reorder_threshold_r else concordant;assert order==expected
   # Runner shifts frame zero by a constant after Eq.(1); distances/KKT are invariant.
   worst1=max(worst1,stress_kkt(fr,order,np.array(c['anchors']),params,temporal));worst2=max(worst2,interval_kkt(fr,order,np.array(c['anchors']),np.array(c['starts']),np.array(c['ends']),params))
   anchor=np.array([s['anchors'][list(s['ordering']).index(v)]for v in ids])
   if b['gauge']['scale']<0:anchor=b['maps'].shape[0]-1-anchor
   max_top_st=max(max_top_st,topology(fr,ids,b['maps'][:,t],anchor,trees[t].kind))
   if not b['checks'][t]['topology_equal']:bad_signatures.append(t)
   assert np.allclose(b['maps'][anchor,t],fr.values[ids])
   for left,right in zip(order[:-1],order[1:]):
    lc=fr.lca(left,right);a=fr.nonleaf_path_to_ancestor(left,lc);bb=fr.nonleaf_path_to_ancestor(right,lc);key='siblings'if not a and not bb else'deep_deep'if a and bb else'direct_deep';cases[key]+=1
   cases['border']+=2
  assert max_top<1e-6 and max_top_st<1e-6 and not bad_signatures
  assert worst1<2e-6,(name,'Eq1 KKT',worst1)
  assert worst2<2e-5,(name,'Eq2 KKT',worst2)
  print(name,'ST Eq1/Eq2 KKT',worst1,worst2,'topology',max_top_st,flush=True)
  # Exercise paper inverse-distance weights and base/temporal modes on actual trees.
  variants=[]
  for t in sorted(set([0,len(trees)//2,len(trees)-1])):
   fr=sc['frames'][t];o=st.optimal_hierarchical_leaf_order(fr)
   for weights in ['uniform','inverse']:
    for mode in ['base','temporal']:
     pp=st.LayoutParameters(weights,params.total_leaf_extent_k,params.reorder_threshold_r,params.temporal_lambda,params.layout_length,0,mode=mode,min_spacing_delta=params.min_spacing_delta,optimizer_tolerance=1e-11)
     temporal={v:float(sc['centers'][t][sc['ids'][t].index(v),0])for v in o}if mode=='temporal'else None
     x=st.project_leaf_anchors(fr,o,pp,temporal);s,e=st.allocate_leaf_intervals(fr,o,x,pp);k1=stress_kkt(fr,o,x,pp,temporal);k2=interval_kkt(fr,o,x,s,e,pp);assert k1<2e-6 and k2<2e-5
     variants.append(dict(frame=t,weights=weights,mode=mode,eq1_kkt_relative_residual=k1,eq2_kkt_relative_residual=k2))
  report['datasets'][name]=dict(frames=len(trees),TMTM_official_core=off,TMTM_exact_permutations=perm,TMTM_all_leaf_pair_merge_error_max=max_top,STMTM=dict(actual_parameters=rec['parameters'],scipy_OLO_exhaustive_cost_gap_max=olo_worst,scipy_OLO_exhaustive_discrepancies=olo_exhaustive_discrepancies,OLO_scope='Paper Sec.4.1.1 explicitly uses SciPy OLO as a heuristic. This audit preserves that routine; it does not silently substitute an exhaustive sorter. Nonzero gaps disclose actual heuristic outcomes, not a claim of exhaustive optimality.',concordance_exhaustive_optimum=True,threshold_and_orientation=True,eq1_kkt_relative_residual_max=worst1,eq2_kkt_relative_residual_max=worst2,actual_raster_all_leaf_pair_merge_error_max=max_top_st,topology_signature_failed_frames=bad_signatures,filling_cases_exercised=cases,other_equation_settings=variants))
  write(OUT/'algorithm_audit.json',report)
 # Validate existing full201 byte bindings, without rerunning trees or optimizers.
 from experiments.volume3d.verify_saved import verify
 report['Tangaroa_saved_evidence']=verify()
 report['paper_parameter_comparison']={name:dict(vars(st.PAPER_PRESETS[name]))for name in ['storms','wildfires']}
 report['status']='passed_algorithm_checks_with_declared_protocol_differences';report['ST_author_code_equivalence_claimed']=False
 report['limits']=['No author ST-MTM executable supplied: equation/structure verification, not byte-for-byte author-code equivalence.','Shared-input experiments use their recorded Start=0 and generic weights/K/r/lambda/L, not the dataset-specific paper presets.','Tangaroa supports verified TMTM and a declared nonbinary extension; no completed real-3-D ST-MTM result.','Tangaroa derived tree node counts remain 36-186 vs paper 50-186.']
 write(OUT/'algorithm_audit.json',report);print('Baseline algorithm audit complete',flush=True)
if __name__=='__main__':run()
