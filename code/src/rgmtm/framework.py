"""Budgeted merge-tree-map family.

Native sample/skeleton profiles retain their original algorithms. The new
fixed-world interval profile enumerates orders under an actual labelled
merge-error budget. A topology budget alone does not recover a native method.
All exact claims refer to the non-strict, fixed-extremum, continuous model.
"""
from itertools import permutations
from math import factorial
import numpy as np
from .error_budget import Parameters, constraints, checked_lp, InfeasibleLayout


def native_profile(profile, *, fields=None, frames=None, parameters=None, **options):
    """Compatibility profiles: preserve the native domain, solver and renderer."""
    if profile == 'TMTM':
        from .baselines.tmtm import compute_temporal_merge_tree_map
        if fields is None or frames is not None or parameters is not None:
            raise ValueError('TMTM takes fields and its original keyword options')
        return compute_temporal_merge_tree_map(fields, **options)
    if profile == 'ST-MTM':
        from .baselines.stmtm import compute_spatiotemporal_merge_tree_map
        if frames is None or parameters is None or fields is not None or options:
            raise ValueError('ST-MTM takes augmented frames and native parameters')
        return compute_spatiotemporal_merge_tree_map(frames, parameters)
    raise ValueError('unknown native profile')


def merge_costs(orders, merge_values):
    """Exact minimum labelled merge error, including fixed leaf-value constraints."""
    O=np.asarray(orders,dtype=int);V=np.asarray(merge_values,float)
    if O.ndim!=2 or V.shape!=(O.shape[1],)*2 or not np.isfinite(V).all():
        raise ValueError('finite square merge matrix and matrix of orders required')
    n=O.shape[1]
    if n<2:return np.zeros(len(O))
    i,j=np.triu_indices(n,1);k=np.arange(n-1)
    cross=(i[:,None]<=k)&(k<j[:,None])
    targets=V[O[:,i],O[:,j]]
    ceilings=np.where(cross[None],targets[:,:,None],np.inf).min(axis=1)
    maxima=np.where(cross[None],ceilings[:,None,:],-np.inf).max(axis=2)
    leaves=np.diag(V)[O];floor=np.maximum(leaves[:,:-1],leaves[:,1:])
    return np.maximum.reduce([np.zeros(len(O)),((targets-maxima)/2).max(1),(floor-ceilings).max(1)])


def interval_costs(orders,widths,reference,p):
    O=np.asarray(orders,int);W=np.asarray(widths,float)[O];Q=np.asarray(reference,float)[O]
    m,n=O.shape;H=p.rho*W/2
    D=np.cumsum(W,1)-W/2+p.gap*np.arange(n)
    E=W.sum(1,keepdims=True)-np.cumsum(W,1)+W/2+p.gap*(n-1-np.arange(n))
    pair=(Q[:,:,None]-Q[:,None,:]+D[:,None,:]-D[:,:,None]-H[:,:,None]-H[:,None,:])/2
    i,j=np.triu_indices(n,1)
    return np.maximum.reduce([np.zeros(m),(p.canvas_origin+D-Q-H).max(1),
        (Q-H-(p.canvas_origin+p.canvas-E)).max(1),pair[:,i,j].max(1) if n>1 else np.zeros(m)])


def cost_table(widths,reference,merge_values,p=Parameters(),*,max_orders=1_000_000,candidate_orders=None):
    w=np.asarray(widths,float);q=np.asarray(reference,float);V=np.asarray(merge_values,float)
    n=len(w)
    if not n or q.shape!=(n,) or V.shape!=(n,n) or not np.isfinite(q).all():
        raise ValueError('one reference and a square merge matrix per leaf required')
    if not np.isfinite(V).all() or not np.allclose(V,V.T,rtol=0,atol=1e-12):
        raise ValueError('merge matrix must be finite and symmetric')
    if n>1 and np.any(V+np.eye(n)*1e300 < np.maximum.outer(np.diag(V),np.diag(V))-1e-10):
        raise ValueError('join-convention merge levels must be above their leaves')
    constraints(w,tuple(range(n)),p) # validates widths and packing capacity
    if candidate_orders is None:
        if factorial(n)>max_orders:
            raise RuntimeError(f'exact search requires {factorial(n)} orders; limit is {max_orders}')
        O=np.array(list(permutations(range(n))),dtype=int)
    else:
        O=np.array(sorted(set(tuple(map(int,o)) for o in candidate_orders)),dtype=int)
        if not len(O) or any(sorted(o)!=list(range(n)) for o in O):
            raise ValueError('candidate rows must be complete leaf permutations')
    tau=interval_costs(O,w,q,p);delta=merge_costs(O,V)
    return dict(orders=O,tau=tau,delta=delta,widths=w,reference=q,merge_values=V,parameters=p,exact=len(O)==factorial(n))


def select_budget(table,epsilon,reference_budget=np.inf,*,tolerance=1e-9):
    """Minimize actual minimax position error subject to a hard scalar budget.

    An infeasible reference cap raises instead of silently enlarging either cap.
    Ties use scalar cost then lexicographic order. No heuristic fallback.
    """
    if np.isnan(epsilon) or epsilon<0 or np.isnan(reference_budget) or reference_budget<0:
        raise ValueError('budgets must be nonnegative; infinity disables a cap')
    idx=np.flatnonzero((table['delta']<=epsilon+tolerance)&(table['tau']<=reference_budget+tolerance))
    if not len(idx):raise InfeasibleLayout('no order meets both declared budgets')
    k=int(idx[np.lexsort((idx,table['delta'][idx],table['tau'][idx]))[0]])
    order=table['orders'][k];tau=float(table['tau'][k]);delta=float(table['delta'][k])
    w,q,V,p=(table[n] for n in ['widths','reference','merge_values','parameters']);n=len(w)
    A,b,bounds=constraints(w,order,p)
    bounds=[(max(lo,q[i]-tau),min(hi,q[i]+tau)) for i,(lo,hi) in enumerate(bounds[:n])]+bounds[n:]
    witness=checked_lp(np.zeros(2*n),-A,-b,bounds)
    if witness is None:raise RuntimeError('closed-form optimum has no LP witness')
    C=np.array([min(V[order[i],order[j]] for i in range(k+1) for j in range(k+1,n)) for k in range(n-1)])
    barriers=C+delta
    measured=max([abs(max(barriers[i:j])-V[order[i],order[j]]) for i in range(n) for j in range(i+1,n)]+[0.])
    actual=float(np.max(abs(witness.x[:n]-q)))
    assert actual<=tau+1e-7 and measured<=epsilon+tolerance+1e-7
    return dict(order=order.tolist(),x=witness.x[:n].tolist(),z=witness.x[n:].tolist(),w=w.tolist(),
        tau=tau,delta=delta,barriers=barriers.tolist(),measured_merge_error=float(measured),
        actual_position_error=actual,epsilon=None if np.isinf(epsilon) else float(epsilon),
        reference_budget=None if np.isinf(reference_budget) else float(reference_budget),
        evaluated_orders=len(table['orders']),optimality='exhaustive continuous non-strict model' if table['exact'] else 'candidate-set feasible upper bound')


def minimum_topology_budget(table,reference_budget):
    """Inverse query: least scalar error that permits the requested position cap."""
    if np.isnan(reference_budget) or reference_budget<0:raise ValueError('invalid position budget')
    idx=np.flatnonzero(table['tau']<=reference_budget+1e-9)
    if not len(idx):raise InfeasibleLayout('position cap is below the free-packing optimum')
    return float(table['delta'][idx].min())
