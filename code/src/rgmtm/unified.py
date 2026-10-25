"""One interval model and QP for topology/time, geometry and reference regimes.

Inspired regimes express design principles, not native-algorithm recovery.
Scalar caps concern continuous labelled merge barriers. Candidate coverage and
QP certificates are reported separately; the renderer needs its own check.
"""
from dataclasses import dataclass, replace
from itertools import combinations
from math import factorial
import numpy as np
from .error_budget import Parameters, InfeasibleLayout, solve_frame
from .framework import cost_table


@dataclass(frozen=True)
class Controls:
    topology_budget: float = 0.0       # fraction of one fixed scalar range
    position_budget: float = np.inf   # fraction of one fixed canvas
    reference_weight: float = 4.0
    geometry_weight: float = 1.0
    temporal_weight: float = 0.5
    eccentricity_weight: float = 0.1
    motion_fraction: float = 1.0

    def validate(self):
        if any(np.isnan(x) or x < 0 for x in (self.topology_budget, self.position_budget)):
            raise ValueError('nonnegative budgets required')
        w=[self.reference_weight,self.geometry_weight,self.temporal_weight,self.eccentricity_weight]
        if not np.isfinite(w).all() or min(w)<0 or not 0<=self.motion_fraction<=1:
            raise ValueError('finite nonnegative weights and motion fraction in [0,1] required')


def objective_terms(x,z,centers,reference,p,previous=None,previous_q=None,matched=None):
    """Unweighted mean squared residuals normalized by the common canvas squared."""
    x,z,c,q=map(np.asarray,(x,z,centers,reference));n=len(x)
    pairs=list(combinations(range(n),2))
    geom=np.mean([(abs(x[j]-x[i])-np.linalg.norm(c[j]-c[i]))**2 for i,j in pairs]) if pairs else 0.
    temporal=0.;stationary=0.;motion=0.
    if previous is not None and np.any(matched):
        mask=np.asarray(matched,bool);du=x[mask]-np.asarray(previous)[mask]
        dq=q[mask]-np.asarray(previous_q)[mask]
        stationary=float(np.mean(du**2));motion=float(np.mean((du-dq)**2))
        temporal=float(np.mean((du-p.motion_fraction*dq)**2))
    return dict(reference=float(np.mean((x-q)**2)/p.canvas**2),geometry=float(geom/p.canvas**2),
                temporal=temporal/p.canvas**2,stationary=stationary/p.canvas**2,
                motion=motion/p.canvas**2,eccentricity=float(np.mean((x-z)**2)/p.canvas**2))


def solve_unified_frame(centers,measure,hierarchy,reference,merge_values,scalar_range,
                        controls=Controls(),p=Parameters(),*,candidate_orders,
                        previous=None,previous_q=None,matched=None):
    """Filter topology then solve the SAME four-term interval QP in every regime."""
    controls.validate()
    if not np.isfinite(scalar_range) or scalar_range<=0:raise ValueError('positive fixed scalar range required')
    p=replace(p,reference_budget=controls.position_budget*p.canvas,
              reference_weight=controls.reference_weight,geometry_weight=controls.geometry_weight,
              motion_weight=controls.temporal_weight,eccentricity_weight=controls.eccentricity_weight,
              motion_fraction=controls.motion_fraction,compact_tiebreak=True)
    V=np.asarray(merge_values,float);q=np.asarray(reference,float);w=p.width_scale*np.asarray(measure,float)
    table=cost_table(w,q,V,p,candidate_orders=candidate_orders)
    keep=(table['delta']<=controls.topology_budget*scalar_range+1e-9)&(table['tau']<=p.reference_budget+1e-9)
    admitted=table['orders'][keep]
    if not len(admitted):raise InfeasibleLayout('no candidate meets both budgets')
    r=solve_frame(centers,measure,hierarchy,previous,previous_q,p,matched,reference=q,
                  candidate_orders=admitted)
    o=np.asarray(r['order']);n=len(o)
    k=int(np.flatnonzero(np.all(table['orders']==o,axis=1))[0]);delta=float(table['delta'][k])
    C=np.array([min(V[o[i],o[j]] for i in range(g+1) for j in range(g+1,n)) for g in range(n-1)])
    b=C+delta
    actual=max([abs(max(b[i:j])-V[o[i],o[j]]) for i,j in combinations(range(n),2)]+[0.])
    if actual>controls.topology_budget*scalar_range+1e-7:raise RuntimeError('scalar cap violated')
    r.update(delta=delta,barriers=b,measured_topology=actual/scalar_range,
             position_error=float(np.max(abs(r['x']-q))/p.canvas),
             terms=objective_terms(r['x'],r['z'],centers,q,p,previous,previous_q,matched),
             pool_size=len(table['orders']),admitted_orders=len(admitted),
             exhaustive=bool(len(table['orders'])==factorial(n)),
             normalized_objective=float(r['objective']/p.canvas**2),
             normalized_qp_gap=float(r['global_gap_bound']/p.canvas**2))
    return r


def solve_unified_sequence(centers,measures,hierarchies,references,merge_values,tracks,pools,
                           scalar_range,controls=Controls(),p=Parameters(),*,allow_infeasible=False):
    lengths=[len(x) for x in (centers,measures,hierarchies,references,merge_values,tracks,pools)]
    if not lengths[0] or len(set(lengths))!=1:raise ValueError('nonempty aligned sequences required')
    if any(len(ids)!=len(c) or len(set(ids))!=len(ids) for ids,c in zip(tracks,centers)):
        raise ValueError('one distinct track ID per feature required')
    rows=[]
    for t in range(lengths[0]):
        previous=previous_q=mask=None
        if t and rows[-1] is not None:
            old={k:i for i,k in enumerate(tracks[t-1])};ids=tracks[t]
            mask=np.array([k in old for k in ids]);previous=np.zeros(len(ids));previous_q=np.zeros(len(ids))
            for i,k in enumerate(ids):
                if mask[i]:
                    previous[i]=rows[-1]['x'][old[k]];previous_q[i]=references[t-1][old[k]]
        try:
            r=solve_unified_frame(centers[t],measures[t],hierarchies[t],references[t],merge_values[t],
                 scalar_range,controls,p,candidate_orders=pools[t],previous=previous,
                 previous_q=previous_q,matched=mask)
        except InfeasibleLayout:
            if not allow_infeasible:raise
            r=None
        rows.append(r)
    return rows
