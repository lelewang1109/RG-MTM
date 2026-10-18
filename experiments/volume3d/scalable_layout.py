"""Large-tree RG layout with explicit numerical certificates and solver gaps.

The primary continuous interval problem is unchanged. Binary/low-arity trees
use exact earliest-finish Pareto functions, bracketed by bisection. Large-arity
and unconstrained problems use HiGHS MILP and retain both primal and dual
bounds if a time limit is reached. The secondary convex objective is solved on
a declared finite candidate-order set, never described as globally optimized
over every admissible order.
"""
from itertools import combinations
from math import factorial
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint,linprog,minimize
from scipy.sparse import coo_matrix
from rgmtm.error_budget import constraints
from analysis.certificate_core import order_tau


def leaves(tree):
    return [int(tree)] if isinstance(tree,(int,np.integer)) else sum((leaves(c) for c in tree),[])


def legal(tree,order):
    positions={v:i for i,v in enumerate(order)}
    def visit(t):
        ids=leaves(t);p=[positions[i] for i in ids]
        return max(p)-min(p)+1==len(p) and (isinstance(t,(int,np.integer)) or all(visit(c) for c in t))
    return sorted(order)==sorted(leaves(tree)) and visit(tree)


def preferred(tree,q):
    if isinstance(tree,(int,np.integer)):return [int(tree)]
    children=sorted(tree,key=lambda c:(float(np.mean(q[leaves(c)])),min(leaves(c))))
    return sum((preferred(c,q) for c in children),[])


def _prune(states):
    # Each state F(s)=max(s+C,R) for s<=D. Smaller R and larger D dominate.
    states=sorted(states,key=lambda v:(-v[1],v[0],v[2]))
    out=[];best=np.inf
    for state in states:
        if state[0]<best:out.append(state);best=state[0]
    return out


def _compose(A,CA,B,CB,gap):
    out=[]
    for ra,da,oa in A:
        for rb,db,ob in B:
            if ra+gap<=db:
                out.append((max(ra+gap+CB,rb),min(da,db-CA-gap),oa+ob))
    return out


def _frontier(tree,w,q,h,tau,gap,max_arity=10):
    if isinstance(tree,(int,np.integer)):
        i=int(tree);return [(q[i]-tau-h[i]+w[i]/2,q[i]+tau+h[i]-w[i]/2,(i,))],w[i]
    m=len(tree)
    if m>max_arity:raise OverflowError('arity exceeds exact subset-frontier capacity')
    children=[_frontier(c,w,q,h,tau,gap,max_arity) for c in tree]
    if m==1:return children[0]
    F={};sizes={}
    for mask in range(1,1<<m):
        candidates=[]
        for c in range(m):
            bit=1<<c
            if not mask&bit:continue
            old=mask^bit;B,CB=children[c]
            if not old:candidates.extend(B);sizes[mask]=CB
            else:
                candidates.extend(_compose(F[old],sizes[old],B,CB,gap));sizes[mask]=sizes[old]+gap+CB
        F[mask]=_prune(candidates)
    return F[(1<<m)-1],sizes[(1<<m)-1]


def continuous_certificate(tree,w,q,p,tolerance=2e-10):
    """Continuous tau bracket and a legal order attaining the reported upper bound."""
    w=np.asarray(w,float);q=np.asarray(q,float);n=len(w)
    if w.sum()+(n-1)*p.gap>p.canvas+1e-12:raise ValueError('fixed widths/gaps exceed canvas')
    def witness(tau):
        states,C=_frontier(tree,w,q,p.rho*w/2,tau,p.gap)
        feasible=[(max(p.canvas_origin+C,R),o) for R,D,o in states
            if p.canvas_origin<=D and max(p.canvas_origin+C,R)<=p.canvas_origin+p.canvas]
        return min(feasible)[1] if feasible else None
    order=preferred(tree,q);upper=float(order_tau(order,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0])
    # Roundoff can put an exact boundary just outside the floating-point test.
    hi=upper+1e-12*p.canvas;lo=0.
    zero=witness(0.)
    if zero is not None:return dict(lower=0.,upper=0.,order=list(zero),exact_to_tolerance=True,solver='continuous Pareto earliest-finish DP')
    while hi-lo>tolerance*p.canvas:
        mid=(hi+lo)/2;o=witness(mid)
        if o is None:lo=mid
        else:hi=mid;order=list(o)
    attained=float(order_tau(order,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0])
    return dict(lower=max(0.,min(lo,attained)),upper=attained,order=list(order),exact_to_tolerance=True,
        solver='continuous Pareto earliest-finish DP',bracket_width=max(0.,attained-lo))


def milp_certificate(tree,w,q,p,time_limit=3.,candidate_orders=()):
    """Same continuous problem; keep the dual bound when HiGHS is interrupted."""
    w=np.asarray(w,float);q=np.asarray(q,float);n=len(w);groups=[]
    def visit(t):
        if isinstance(t,(int,np.integer)):return [int(t)]
        child=[visit(c) for c in t]
        for A,B in combinations(child,2):groups.append((A,B))
        return sum(child,[])
    visit(tree);m=len(groups)
    candidates=[preferred(tree,q)]+[list(o) for o in candidate_orders if legal(tree,o)]
    scores=[float(order_tau(o,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0]) for o in candidates]
    best=int(np.argmin(scores));upper=scores[best];order=candidates[best]
    if upper<=1e-13*p.canvas:return dict(lower=0.,upper=upper,order=order,exact_to_tolerance=True,solver='feasible zero-error witness')
    rows=[];cols=[];data=[];lower=[];upper_rows=[]
    def add(terms,lo=-np.inf,hi=np.inf):
        k=len(lower)
        for c,v in terms:rows.append(k);cols.append(c);data.append(v)
        lower.append(lo);upper_rows.append(hi)
    for i in range(n):
        add([(i,1),(n,-1)],hi=q[i]+p.rho*w[i]/2)
        add([(i,-1),(n,-1)],hi=-q[i]+p.rho*w[i]/2)
    M=2*p.canvas+p.gap
    for b,(A,B) in enumerate(groups):
        for i in A:
            for j in B:
                sep=(w[i]+w[j])/2+p.gap
                add([(j,1),(i,-1),(n+1+b,-M)],lo=sep-M)
                add([(i,1),(j,-1),(n+1+b,M)],lo=sep)
    mat=coo_matrix((data,(rows,cols)),shape=(len(lower),n+1+m)).tocsc()
    lb=np.r_[p.canvas_origin+w/2,0.,np.zeros(m)]
    ub=np.r_[p.canvas_origin+p.canvas-w/2,upper+1e-10*p.canvas,np.ones(m)]
    result=milp(np.r_[np.zeros(n),1.,np.zeros(m)],integrality=np.r_[np.zeros(n+1),np.ones(m)],
        bounds=Bounds(lb,ub),constraints=LinearConstraint(mat,lower,upper_rows),
        options=dict(time_limit=time_limit,mip_rel_gap=1e-8))
    if result.x is not None:
        trial=np.argsort(result.x[:n],kind='stable').tolist()
        if legal(tree,trial):
            score=float(order_tau(trial,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0])
            if score<upper:upper=score;order=trial
    dual=getattr(result,'mip_dual_bound',None)
    low=max(0.,float(dual)) if dual is not None and np.isfinite(dual) else 0.
    low=min(low,upper)
    return dict(lower=low,upper=upper,order=order,exact_to_tolerance=upper-low<=2e-7*p.canvas,
        solver='HiGHS MILP',status=int(result.status),message=str(result.message),seconds_limit=time_limit,
        absolute_gap=upper-low,binary_variables=m)


def free_bounds(w,q,p):
    """Sound workload lower bound over every occupied-window interval subset.

    For S, demand=sum(w_S)+(len(S)-1)*gap must fit between
    min(q-h-w/2)-tau and max(q+h+w/2)+tau. Prefix/suffix subsets
    also give one-sided bounds against the canvas. A feasible reference-sorted
    order is an upper witness; equality certifies the unrestricted optimum.
    """
    w=np.asarray(w,float);q=np.asarray(q,float);n=len(w);radius=(1+p.rho)*w/2
    left=q-radius;right=q+radius;lower=0.
    for L in left:
        ids=np.flatnonzero(left>=L);ids=ids[np.argsort(right[ids],kind='stable')]
        demand=np.cumsum(w[ids]+p.gap)-p.gap
        lower=max(lower,float(np.max((demand-(right[ids]-L))/2)),
            float(demand[-1]+L-p.canvas_origin-p.canvas))
    ids=np.argsort(right,kind='stable');demand=np.cumsum(w[ids]+p.gap)-p.gap
    lower=max(lower,float(np.max(demand+p.canvas_origin-right[ids])))
    order=np.argsort(q,kind='stable').tolist()
    upper=float(order_tau(order,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0])
    return dict(lower=max(0.,min(lower,upper)),upper=upper,order=order,
        exact_to_tolerance=upper-lower<=2e-7*p.canvas,solver='interval workload lower bound and feasible reference-sort upper witness',
        absolute_gap=max(0.,upper-lower))


def certificate(tree,w,q,p,**kwargs):
    try:return continuous_certificate(tree,w,q,p)
    except OverflowError:
        free=free_bounds(w,q,p)
        candidates=[preferred(tree,q)]+[o for o in kwargs.get('candidate_orders',()) if legal(tree,o)]
        score=[float(order_tau(o,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0]) for o in candidates]
        k=int(np.argmin(score))
        if score[k]-free['lower']<=2e-7*p.canvas:
            return dict(lower=min(free['lower'],score[k]),upper=score[k],order=list(candidates[k]),
                exact_to_tolerance=True,solver='workload lower bound attained by a legal hierarchy order',absolute_gap=max(0.,score[k]-free['lower']))
        result=milp_certificate(tree,w,q,p,**kwargs)
        result['lower']=max(result['lower'],min(free['lower'],result['upper']))
        result['absolute_gap']=result['upper']-result['lower']
        result['exact_to_tolerance']=result['absolute_gap']<=2e-7*p.canvas
        return result


def solve_candidates(centers,w,q,tree,p,cert,previous=None,previous_q=None,mask=None,extra_orders=(),maximum_orders=4):
    """Original reference/geometry/residual-motion QP, on declared feasible orders."""
    c=np.asarray(centers);w=np.asarray(w);q=np.asarray(q);n=len(q)
    mask=np.zeros(n,bool) if mask is None else np.asarray(mask,bool)
    budget=cert['upper']+p.extra_budget
    orders=[tuple(cert['order']),tuple(preferred(tree,q))]+[tuple(o) for o in extra_orders]
    orders=list(dict.fromkeys(o for o in orders if legal(tree,o)))
    orders=[o for o in orders if order_tau(o,w,q,p.canvas_origin,p.canvas,p.gap,p.rho)[0]<=budget+1e-10*p.canvas]
    orders=orders[:maximum_orders]
    best=None;records=[]
    for order in orders:
        A,b,bounds=constraints(w,order,p);R=np.c_[np.eye(n),np.zeros((n,n))]
        A=np.vstack([A,R,-R]);b=np.r_[b,q-budget,-q-budget]
        lp=linprog(np.zeros(2*n),A_ub=-A,b_ub=-b,bounds=bounds,method='highs')
        if not lp.success:raise RuntimeError('QP initial continuous feasibility failed '+lp.message)
        gw=p.geometry_weight/max(1,n*(n-1)//2);rw=p.reference_weight/n;ew=p.eccentricity_weight/n
        tw=p.motion_weight/max(1,int(mask.sum()))
        bg=np.zeros(n);distance_const=0.
        for ia,i in enumerate(order):
            for j in order[ia+1:]:
                d=float(np.linalg.norm(c[i]-c[j]));bg[i]-=d;bg[j]+=d;distance_const+=d*d
        H=np.zeros((2*n,2*n));I=np.eye(n)
        H[:n,:n]=2*(gw*(n*I-np.ones((n,n)))+(rw+ew)*I+tw*np.diag(mask.astype(float)))
        H[n:,n:]=2*ew*I;H[:n,n:]=-2*ew*I;H[n:,:n]=-2*ew*I
        goal=np.zeros(n) if previous is None else np.asarray(previous)+q-np.asarray(previous_q)
        linear=np.r_[-2*gw*bg-2*rw*q-2*tw*mask*goal,np.zeros(n)]
        const=gw*distance_const+rw*(q@q)+tw*np.sum(goal[mask]**2)
        mv=lambda matrix,v:np.einsum('ij,j->i',matrix,v,optimize=False)
        fun=lambda v:float((.5*np.einsum('i,ij,j->',v,H,v,optimize=False)+np.sum(linear*v)+const)/p.canvas**2)
        jac=lambda v:(mv(H,v)+linear)/p.canvas**2
        opt=minimize(fun,lp.x,jac=jac,method='SLSQP',bounds=bounds,
            constraints={'type':'ineq','fun':lambda v:mv(A,v)-b,'jac':lambda v:A},options=dict(ftol=1e-12,maxiter=1500))
        slack=float(np.min(mv(A,opt.x)-b))
        if not np.isfinite(opt.x).all() or slack < -2e-8*p.canvas:raise RuntimeError('QP violated a hard RG constraint')
        oracle=linprog(jac(opt.x),A_ub=-A,b_ub=-b,bounds=bounds,method='highs')
        if not oracle.success:raise RuntimeError('QP optimality oracle failed')
        gap=max(0.,float(jac(opt.x)@(opt.x-oracle.x)))
        records.append(dict(order=list(order),success=bool(opt.success),convex_first_order_gap=gap,objective=fun(opt.x)))
        if best is None or fun(opt.x)<best['objective']:
            best=dict(x=opt.x[:n],z=opt.x[n:],w=w,order=list(order),tau=cert['upper'],budget=budget,reference=q,
                objective=fun(opt.x),min_constraint_slack=slack,convex_first_order_gap=gap,qp_success=bool(opt.success))
    if best is None:raise RuntimeError('no primary-certificate witness in candidate QP orders')
    best['candidate_qps']=records;best['secondary_global_optimum_claimed']=False
    return best
