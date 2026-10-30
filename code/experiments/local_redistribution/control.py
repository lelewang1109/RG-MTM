"""Exact four-leaf minimax control with independent LPs and convex QP certificates."""
from pathlib import Path
import itertools,json
import numpy as np
from scipy.optimize import linprog
from scipy import sparse
import osqp
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/local_redistribution20261030'
q=np.array([.2,.8,.18,.6]);centers=np.c_[q,[.144,.156,.146,.052]];w=np.full(4,.06);g=.01;rho=.5
V=np.ones((4,4));np.fill_diagonal(V,0);V[0,1]=V[1,0]=V[2,3]=V[3,2]=.4

def constraints(order):
 A=[];b=[]
 def add(v,r):
  a=np.zeros(8)
  for i,s in v:a[i]+=s
  A.append(a);b.append(r)
 for i in range(4):add([(i,1),(4+i,-1)],rho*w[i]/2);add([(i,-1),(4+i,1)],rho*w[i]/2)
 for i,j in zip(order,order[1:]):add([(4+i,1),(4+j,-1)],-(w[i]+w[j])/2-g)
 return np.array(A),np.array(b)
def lp(o):
 A,b=constraints(o);A=np.c_[A,np.zeros(len(A))];B=b.tolist()
 for i in range(4):
  a=np.zeros(9);a[i]=1;a[-1]=-1;A=np.vstack([A,a]);B.append(q[i]);a=np.zeros(9);a[i]=-1;a[-1]=-1;A=np.vstack([A,a]);B.append(-q[i])
 c=np.zeros(9);c[-1]=1;r=linprog(c,A_ub=A,b_ub=B,bounds=[(0,1)]*4+[(v/2,1-v/2) for v in w]+[(0,None)],method='highs');assert r.success;return float(r.fun)
def qp(o,tau):
 A,b=constraints(o);D=[];y=[]
 for i in range(4):
  a=np.zeros(8);a[i]=np.sqrt(4/4);D.append(a);y.append(q[i]*np.sqrt(4/4));a=np.zeros(8);a[i]=np.sqrt(.1/4);a[4+i]=-np.sqrt(.1/4);D.append(a);y.append(0)
 for i,j in itertools.combinations(range(4),2):
  # Orient positive source distance by this candidate leaf order.
  if o.index(i)>o.index(j):i,j=j,i
  a=np.zeros(8);a[j]=np.sqrt(1/6);a[i]=-np.sqrt(1/6);D.append(a);y.append(np.linalg.norm(centers[i]-centers[j])*np.sqrt(1/6))
 D=np.array(D);y=np.array(y);H=2*np.sum(D[:,:,None]*D[:,None,:],axis=0);c=-2*np.sum(D*y[:,None],axis=0);bounds=[(max(0,a-tau-1e-9),min(1,a+tau+1e-9)) for a in q]+[(v/2,1-v/2) for v in w]
 AA=sparse.vstack([sparse.csc_matrix(A),sparse.eye(8)],format='csc');solver=osqp.OSQP();solver.setup(P=sparse.triu(sparse.csc_matrix(H),format='csc'),q=c,A=AA,l=np.r_[np.full(len(A),-np.inf),[v[0] for v in bounds]],u=np.r_[b,[v[1] for v in bounds]],verbose=False,eps_abs=1e-11,eps_rel=1e-11,max_iter=100000,polishing=True)
 r=solver.solve(raise_error=False);assert r.info.status_val==1;z=r.x;assert np.max(np.sum(A*z,axis=1)-b)<1e-8;grad=np.sum(H*z,axis=1)+c;oracle=linprog(grad,A_ub=A,b_ub=b,bounds=bounds,method='highs');assert oracle.success;gap=max(0,float(np.sum(grad*(z-oracle.x))));assert gap<1e-8
 return dict(x=z[:4].tolist(),z=z[4:].tolist(),errors=abs(z[:4]-q).tolist(),objective=float(np.sum((np.sum(D*z,axis=1)-y)**2)),convex_gap=gap)
def main(out=OUT):
 records=[]
 for o in itertools.permutations(range(4)):
  exact=abs(o.index(0)-o.index(1))==1 and abs(o.index(2)-o.index(3))==1
  delta=0 if exact else .3;records.append(dict(order=list(o),tau=lp(o),delta=delta))
 states=[]
 for e in [0,.3]:
  eligible=[r for r in records if r['delta']<=e+1e-10];best=min(r['tau'] for r in eligible);tied=[r for r in eligible if abs(r['tau']-best)<1e-10];solutions=[dict(**r,**qp(r['order'],best)) for r in tied];s=min(solutions,key=lambda r:(r['objective'],r['order']));states.append(dict(epsilon=e,eligible_orders=len(eligible),optimal_order_ties=len(tied),**s))
 assert abs(states[0]['tau']-.22)<1e-10 and abs(states[1]['tau']-.01)<1e-10
 assert states[1]['errors'][2]-states[0]['errors'][2]>.005
 for s in states:
  # Closed-form optimal barriers .4,1,.4 (exact) or .7,.7,.7 (mixed); remeasure every pair.
  o=s['order'];barriers=[float(V[o[k],o[k+1]]) for k in range(3)] if s['delta']==0 else [.7]*3
  actual=max(abs(max(barriers[a:b])-V[o[a],o[b]]) for a in range(4) for b in range(a+1,4));assert abs(actual-s['delta'])<1e-12;s['barriers']=barriers;s['measured_merge_error']=actual
 d=dict(q=q.tolist(),centers=centers.tolist(),widths=w.tolist(),gap=g,rho=rho,scalar_range=1,leaf_values=[0]*4,sibling_level=.4,root_level=1,parameters=dict(reference_weight=4,geometry_weight=1,eccentricity_weight=.1,temporal_weight=0,beta=0,numerical_cap_allowance=1e-9),states=states,all_orders=records,independent_LP_solves=24,all_orders_enumerated=True,analytic_minimax_bounds=[.22,.01],validation_passed=True,scope='one constructed static counterexample, not prevalence; exact lexicographic minimax order followed by the same fixed convex secondary objective; does not rely on a heuristic order or a temporal history')
 (out/'controlled.json').write_text(json.dumps(d,indent=2));print('CONTROL',[(s['tau'],s['errors'][2],s['order']) for s in states])
if __name__=='__main__':main()
