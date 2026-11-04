"""Numerical fallback for unchanged ST-MTM Eq1, both weight choices."""
import numpy as np
from scipy.spatial.distance import pdist,squareform

def project(frame,order,parameters,temporal,qp):
 n=len(order);D=squareform(pdist(np.array([frame.leaf_centroid(i) for i in order])));P=np.zeros((n,n));q=np.zeros(n)
 for i in range(n):
  for j in range(i+1,n):
   if parameters.weights=='inverse' and D[i,j]==0:raise ValueError('undefined inverse-distance weight for coincident source centroids')
   w=1. if parameters.weights=='uniform' else 1./D[i,j]
   P[i,i]+=2*w;P[j,j]+=2*w;P[i,j]-=2*w;P[j,i]-=2*w;q[i]+=2*w*D[i,j];q[j]-=2*w*D[i,j]
 matched=[(i,temporal[v]) for i,v in enumerate(order) if temporal and v in temporal];lam=parameters.temporal_lambda if parameters.mode=='temporal' else 0.
 if lam:
  for i,x in matched:P[i,i]+=2*lam;q[i]-=2*lam*x
 A=np.diff(np.eye(n),axis=0);lo=np.full(n-1,parameters.min_spacing_delta);hi=np.full(n-1,np.inf)
 if not matched or lam==0:A=np.vstack([A,np.ones(n)]);lo=np.r_[lo,0.];hi=np.r_[hi,0.]
 x,certificate=qp(P,q,A,lo,hi)
 assert np.min(np.diff(x))>=parameters.min_spacing_delta-1e-7
 return x,certificate
