"""Joint integer rounding for the SAME continuous layout and fixed raster length.

No reference, width, order, objective weight or topology budget is changed.
Integer coordinates jointly minimize raster rounding error while retaining a
barrier pixel. First keep nearest-rounded anchors fixed; only if impossible
allow joint anchor rounding. The continuous layout is never modified.
"""
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy import sparse
from rgmtm.baselines.stmtm import DiscreteSkeleton,fill_frame


def integer_skeleton(x,s,e,length):
 n=len(x);target=np.r_[s,x,e];size=3*n
 # q=(starts,anchors,ends), abs-error auxiliaries. Minimize rounding error,
 # independently of the reference NPE and all benchmark rankings.
 rows=[];low=[];high=[]
 def add(coeff,l=-np.inf,h=np.inf):
  row=np.zeros(2*size+1)
  for k,v in coeff.items():row[k]=v
  rows.append(row);low.append(l);high.append(h)
 for i in range(n):
  add({n+i:1,i:-1},0);add({2*n+i:1,n+i:-1},0)
  if i+1<n:add({i+1:1,2*n+i:-1},2)
 for i,t in enumerate(target):
  add({i:1,size+i:-1},h=t);add({i:-1,size+i:-1},h=-t);add({size+i:1,2*size:-1},h=0)
 A=sparse.csc_matrix(np.array(rows));objective=np.r_[np.zeros(2*size),1.]
 base_lo=np.zeros(size);base_hi=np.full(size,length-1.)
 attempts=[]
 for fixed_anchors in [True,False]:
  lo=base_lo.copy();hi=base_hi.copy()
  if fixed_anchors:lo[n:2*n]=hi[n:2*n]=np.rint(x)
  lower=np.r_[lo,np.zeros(size+1)];upper=np.r_[hi,np.full(size+1,np.inf)]
  result=milp(objective,integrality=np.r_[np.ones(size),np.zeros(size+1)],bounds=Bounds(lower,upper),constraints=LinearConstraint(A,low,high),options={'mip_rel_gap':0.0})
  attempts.append(dict(anchors_fixed_to_nearest=fixed_anchors,status=int(result.status),message=result.message))
  if not result.success:continue
  optimum=float(result.x[-1]);upper[-1]=optimum+1e-7
  tie=milp(np.r_[np.zeros(size),np.ones(size),0.],integrality=np.r_[np.ones(size),np.zeros(size+1)],bounds=Bounds(lower,upper),constraints=LinearConstraint(A,low,high),options={'mip_rel_gap':0.0})
  if tie.success:result=tie
  q=np.rint(result.x[:size]).astype(int);ss,aa,ee=q[:n],q[n:2*n],q[2*n:];error=float(max(abs(q-target)))
  assert np.all(ss<=aa) and np.all(aa<=ee) and np.all(ss[1:]-ee[:-1]>=2)
  return ss,aa,ee,dict(repaired=True,anchors_fixed_to_nearest=fixed_anchors,optimal_max_rounding_error_pixels=optimum,max_coordinate_rounding_error_pixels=error,total_absolute_rounding_error_pixels=float(sum(abs(q-target))),attempts=attempts)
 raise ValueError('no integer skeleton at original fixed raster length; layout not repaired')


def render_sequence(frames,feature_ids,layouts,canvas=120.,length=2048,*,canvas_origin=0.):
 scale=(length-1)/canvas;maps=[];skeletons=[];errors=[]
 for t,(fr,ids,row) in enumerate(zip(frames,feature_ids,layouts)):
  order=np.array(row['order'],int);x=(np.asarray(row['x'])[order]-canvas_origin)*scale;z=(np.asarray(row['z'])[order]-canvas_origin)*scale;w=np.asarray(row['w'])[order]*scale;s=z-w/2;e=z+w/2
  ss=np.rint(s).astype(int);aa=np.rint(x).astype(int);ee=np.rint(e).astype(int);diag=dict(repaired=False,anchors_fixed_to_nearest=True,max_coordinate_rounding_error_pixels=float(max(abs(np.r_[ss,aa,ee]-np.r_[s,x,e]))))
  if np.any(ss<0) or np.any(ee>=length) or np.any(aa<ss) or np.any(aa>ee) or np.any(ss[1:]-ee[:-1]<2):ss,aa,ee,diag=integer_skeleton(x,s,e,length)
  sk=DiscreteSkeleton(tuple(ids[i] for i in order),aa,ss,ee);col=fill_frame(fr,sk,length);assert np.isfinite(col).all()
  maps.append(col);skeletons.append(sk);errors.append(dict(anchor_error=float(max(abs(aa/scale+canvas_origin-np.asarray(row['x'])[order]))),interval_extent_error=float(max(abs((ee-ss)/scale-np.asarray(row['w'])[order]))),integer_rounding=diag))
 return np.column_stack(maps),skeletons,errors
