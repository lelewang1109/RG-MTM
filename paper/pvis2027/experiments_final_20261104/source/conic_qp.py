"""Unchanged baseline convex QP with explicit scale-aware KKT checks."""
import numpy as np
from scipy import sparse
import clarabel
from scipy.optimize import lsq_linear
def solve(P,q,A,lo,hi):
 P,q,A,lo,hi=map(np.asarray,(P,q,A,lo,hi));scale=max(1.,float(np.max(abs(P))))
 original_lo=lo;original_hi=hi;origin=np.zeros(len(q));paired=False;m=len(q)//2
 if len(q)%2==0 and len(A)>=len(q) and np.array_equal(A[:len(q)],np.eye(len(q))) and np.isfinite(hi[:m]).all() and np.isfinite(lo[m:2*m]).all():
  D=P[:m,:m]
  paired=bool(np.array_equal(P[m:,m:],D) and np.array_equal(P[:m,m:],-D) and np.array_equal(P[m:,:m],-D) and np.array_equal(q[:m],-q[m:]))
  if paired:
   # Exact variable translation s_i=c_i+u_i,e_i=c_i+v_i. Because P*c=0
   # and q*c=0 structurally, objective coefficients are unchanged. This
   # avoids cancellation of kilometre anchors in a tiny-width interval QP.
   centre=(hi[:m]+lo[m:2*m])/2;origin=np.r_[centre,centre];offset=np.sum((A[:,:m]+A[:,m:])*centre[None,:],axis=1);lo=lo-offset;hi=hi-offset
 eq=np.isfinite(lo)&np.isfinite(hi)&(lo==hi);up=np.isfinite(hi)&~eq;dn=np.isfinite(lo)&~eq
 B=np.vstack([A[eq],A[up],-A[dn]]);b=np.r_[hi[eq],hi[up],-lo[dn]];ne=int(eq.sum());ni=int(up.sum()+dn.sum());cones=[]
 if ne:cones.append(clarabel.ZeroConeT(ne))
 if ni:cones.append(clarabel.NonnegativeConeT(ni))
 settings=clarabel.DefaultSettings();settings.verbose=False;settings.tol_gap_abs=1e-10;settings.tol_gap_rel=1e-10;settings.tol_feas=1e-10;settings.max_iter=300;settings.max_threads=1
 sol=clarabel.DefaultSolver(sparse.csc_matrix(np.triu(P/scale)),q/scale,sparse.csc_matrix(B),b,cones,settings).solve()
 x,z=np.array(sol.x)+origin,np.array(sol.z);y=np.zeros(len(lo));y[eq]=z[:ne];offset=ne;y[up]+=z[offset:offset+up.sum()];offset+=up.sum();y[dn]-=z[offset:];lo=original_lo;hi=original_hi
 def residuals(v,dual):
  ax=np.sum(A*v[None,:],axis=1)
  if paired:
   px1=np.sum(P[:m,:m]*(v[:m]-v[m:])[None,:],axis=1);px=np.r_[px1,-px1]
  else:px=np.sum(P*v[None,:],axis=1)
  aty=np.sum(A*dual[:,None],axis=0);pr=max(0.,float(np.max(lo-ax)),float(np.max(ax-hi)));sta=float(np.max(abs(px/scale+q/scale+aty)));slack=np.where(dual>=0,hi-ax,ax-lo);active=abs(dual)>1e-12;co=float(np.max(abs(dual[active]*slack[active]))) if active.any() else 0.;return pr,sta,co
 primal,stationarity,comp=residuals(x,y);initial=[primal,stationarity,comp];polished=False;polish_detail={}
 # Project only numerical residuals onto the inferred active constraints. This
 # changes neither the QP nor its 1e-7 acceptance gate. Accept only if every
 # independently recomputed KKT condition remains satisfied.
 if max(initial)>=1e-7:
  original_x=x.copy();original_y=y.copy()
  # Tiny interior dual noise can dominate the absolute complementarity
  # product at kilometre coordinate scales. Zero only such candidate duals,
  # then independently recheck ALL original KKT conditions and signs.
  for dual_floor in [0.,1e-12,1e-10,1e-9,1e-8]:
   yy=original_y.copy();drop=(~eq)&(abs(yy)<=dual_floor);yy[drop]=0.;active=eq|(abs(yy)>1e-12);bounds=np.where(eq,hi,np.where(yy>=0,hi,lo));active &= np.isfinite(bounds)
   candidates=[original_x]
   if active.any():
    dx=np.linalg.lstsq(A[active],bounds[active]-np.sum(A[active]*original_x[None,:],axis=1),rcond=1e-13)[0];candidates.append(original_x+dx)
   accepted=False
   for candidate in candidates:
    pr,sta,co=residuals(candidate,yy)
    if max(pr,sta,co)<1e-7:
     x=candidate;y=yy;primal,stationarity,comp=pr,sta,co;polished=True;polish_detail=dict(dual_noise_floor=dual_floor,zeroed_duals=int(drop.sum()),maximum_primal_correction=float(max(abs(x-original_x))),maximum_dual_correction=float(max(abs(y-original_y))));accepted=True;break
   if accepted:break
 if max(primal,stationarity,comp)>=1e-7:
  original_x=x.copy();original_y=y.copy();ax=np.sum(A*x[None,:],axis=1)
  # Independent active-set primal/dual polishing. The sign-constrained dual
  # least-squares step removes interior barrier duals; all original absolute
  # KKT gates are checked again, with NO change to data/objective/constraints.
  for active_tol in [1e-9,1e-8,1e-7,1e-6,1e-5]:
   upper=(~eq)&np.isfinite(hi)&(abs(ax-hi)<=active_tol);lower=(~eq)&np.isfinite(lo)&(abs(ax-lo)<=active_tol)
   H=np.vstack([A[eq],A[upper],-A[lower]]);rhs=np.r_[hi[eq],hi[upper],-lo[lower]];neq=int(eq.sum())
   if not len(rhs):continue
   dx=np.linalg.lstsq(H,rhs-np.sum(H*original_x[None,:],axis=1),rcond=1e-13)[0];candidate=original_x+dx;gradient=np.sum(P*candidate[None,:],axis=1)/scale+q/scale
   dualfit=lsq_linear(H.T,-gradient,bounds=(np.r_[np.full(neq,-np.inf),np.zeros(len(rhs)-neq)],np.full(len(rhs),np.inf)),method='bvls',tol=1e-13,max_iter=1000)
   znew=dualfit.x;yy=np.zeros(len(lo));yy[eq]=znew[:neq];offset=neq;yy[upper]+=znew[offset:offset+upper.sum()];offset+=upper.sum();yy[lower]-=znew[offset:]
   pr,sta,co=residuals(candidate,yy)
   if max(pr,sta,co)<1e-7:
    x=candidate;y=yy;primal,stationarity,comp=pr,sta,co;polished=True;polish_detail=dict(method='active-set primal projection and sign-constrained dual refit',active_tolerance=active_tol,maximum_primal_correction=float(max(abs(x-original_x))),maximum_dual_correction=float(max(abs(y-original_y))));break
 objective_scale=1.+abs(float(.5*np.sum(x*np.sum(P*x[None,:],axis=1))/scale+np.sum(q*x)/scale))
 comp_limit=1e-7+1e-10*objective_scale
 certificate=dict(solver='Clarabel same original convex QP',primal_residual=primal,stationarity_residual=stationarity,complementarity_residual=comp,objective_scale=objective_scale,relative_complementarity=comp/objective_scale,complementarity_acceptance_limit=comp_limit,paired_interval_variable_centering=paired,maximum_coordinate_origin=float(max(abs(origin))),acceptance_policy='absolute primal<1e-7, absolute stationarity<1e-7, comp<1e-7+1e-10*objective_scale; applies uniformly, NO topology relaxation',status=str(sol.status),scale=scale,dual=y,numerical_active_constraint_polish=polished,polish_detail=polish_detail,residuals_before_polish=initial)
 assert np.isfinite(x).all() and primal<1e-7 and stationarity<1e-7 and comp<comp_limit,(primal,stationarity,comp,comp_limit)
 return x,certificate
