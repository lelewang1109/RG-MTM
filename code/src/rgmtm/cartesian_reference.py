"""Offline 3-D reference axis from support-centroid motion, not extremum jitter."""
import numpy as np

def centroid_axis_reference(centers, tracks, extrema, lo, hi, periodic_lengths=None):
    lo,hi=np.asarray(lo,float),np.asarray(hi,float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.isfinite([lo,hi]).all() or not np.all(hi>lo):raise ValueError('finite positive 3-D domain bounds required')
    if len(centers)==0 or not len(centers)==len(tracks)==len(extrema):raise ValueError('aligned nonempty centroid, track and extremum sequences required')
    periods={} if periodic_lengths is None else {int(k):float(v) for k,v in periodic_lengths.items()}
    if any(k not in range(3) or not np.isfinite(v) or v<=0 for k,v in periods.items()):raise ValueError('valid periodic axis lengths required')
    energy=np.zeros(3);steps=0
    for t,(c,ids,e) in enumerate(zip(centers,tracks,extrema)):
        c=np.asarray(c,float);e=np.asarray(e,float)
        if c.shape!=(len(ids),3) or e.shape!=c.shape or len(set(ids))!=len(ids) or not np.isfinite(c).all() or not np.isfinite(e).all():raise ValueError('finite aligned 3-D points and unique track IDs required')
        if t:
            old=dict(zip(tracks[t-1],np.asarray(centers[t-1],float)))
            for p,k in zip(c,ids):
                if k not in old:continue
                d=p-old[k]
                for axis,length in periods.items():d[axis]=(d[axis]+length/2)%length-length/2
                energy+=d*d;steps+=1
    total=float(energy.sum());axis=int(np.argmax(energy)) if total>1e-20 else int(np.argmax(hi-lo));a=np.eye(3)[axis]
    capture=energy/total if total>1e-20 else np.zeros(3)
    return dict(kind='direction',qs=[np.asarray(e)@a for e in extrema],origin=float(lo[axis]),extent=float(hi[axis]-lo[axis]),
                label='position along centroid-motion Cartesian axis '+'xyz'[axis],
                candidates=dict(direction=dict(a=a.tolist(),capture=float(capture[axis]),fallback=total<=1e-20),
                                axis_capture=capture.tolist(),matched_steps=steps,periodic_lengths=periods,
                                selection_points='support centroids',reference_points='extrema',scope='complete input offline; no output metrics used'))
