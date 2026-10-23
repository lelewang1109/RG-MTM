"""Stream an anti-aliased temporal display from complete saved scalar profiles.

The reconstruction is exact at integer frames before pixel integration. Knots
follow common extrema only when their order is unchanged and motion <= 0.2 L.
Crossings and large jumps use fixed-coordinate convex blending. Every native
row contributes to the final vertical area filter, rather than a row subset.
"""
import hashlib
import numpy as np
from PIL import Image

def rules_for(G, tracks, anchors):
    N, T = G.shape
    out = []
    for t in range(T-1):
        common=sorted((set(tracks[t])&set(tracks[t+1]))-{-1})
        i0=[int(np.flatnonzero(tracks[t]==tr)[0]) for tr in common]
        i1=[int(np.flatnonzero(tracks[t+1]==tr)[0]) for tr in common]
        p0=anchors[t,i0];p1=anchors[t+1,i1];order=np.argsort(p0);p0=p0[order];p1=p1[order]
        k0=np.r_[0,np.rint(p0*(N-1))/(N-1),1]
        k1=np.r_[0,np.rint(p1*(N-1))/(N-1),1]
        reason='aligned'
        if not common:reason='no common extrema'
        elif np.any(np.diff(p1)<=0):reason='crossing extrema order'
        elif np.any(abs(p0-p1)>.2):reason='large position jump'
        elif np.any(np.diff(k0)<=0) or np.any(np.diff(k1)<=0):reason='non-strict sample knots'
        out.append(dict(frames=[t,t+1],aligned=reason=='aligned',reason=reason,
                        knots0=k0.tolist(),knots1=k1.tolist()))
    return out

def column_at(G, rules, time, u):
    t=int(np.floor(time));alpha=time-t
    if alpha==0 or t==G.shape[1]-1:return G[:,t]
    rule=rules[t]
    if not rule['aligned']:return (1-alpha)*G[:,t]+alpha*G[:,t+1]
    k0=np.asarray(rule['knots0']);k1=np.asarray(rule['knots1']);km=(1-alpha)*k0+alpha*k1
    p0=np.interp(u,km,k0);p1=np.interp(u,km,k1)
    return (1-alpha)*np.interp(p0,u,G[:,t])+alpha*np.interp(p1,u,G[:,t+1])

def render(G, tracks, anchors, cm, norm, path, factor, window, rows, aspect):
    assert factor%2==1
    N,T=G.shape;lo,hi=window;r0,r1=rows;rules=rules_for(G,tracks,anchors)
    times=lo+np.clip((np.arange((hi-lo)*factor)+.5)/factor-.5,0,hi-lo-1)
    height=round(len(times)/aspect);output=np.empty((height,len(times),4),np.uint8)
    u=np.linspace(0,1,N);mn=float(G.min());mx=float(G.max());observed=[np.inf,-np.inf];exact=[]
    for j,time in enumerate(times):
        col=column_at(G,rules,float(time),u)
        if time==int(time):
            assert np.array_equal(col,G[:,int(time)])
            if int(time) not in exact:exact.append(int(time))
        v=col[r0:r1];observed[0]=min(observed[0],float(v.min()));observed[1]=max(observed[1],float(v.max()))
        rgba=np.rint(np.clip(cm(norm(v[::-1])),0,1)*255).astype(np.uint8)
        image=Image.fromarray(rgba[:,None,:]).resize((1,height),Image.Resampling.BOX)
        output[:,j,:]=np.asarray(image)[:,0,:]
    assert exact==list(range(lo,hi))
    assert observed[0]>=mn-1e-10 and observed[1]<=mx+1e-10
    Image.fromarray(output).save(path)
    return dict(method='monotone anchor-aligned convex temporal reconstruction and vertical area antialiasing',
                display_samples_per_frame=factor,native_rows=N,rows_displayed=[r0,r1],
                source_frames=list(range(lo,hi)),all_original_frame_profiles_exact_before_pixel_integration=True,
                original_profiles_sha256=hashlib.sha256(np.ascontiguousarray(G).tobytes()).hexdigest(),
                no_scalar_overshoot=True,source_scalar_range=[mn,mx],reconstructed_scalar_range=observed,
                aligned_intervals=sum(r['aligned']for r in rules[lo:hi-1]),intervals=rules[lo:hi-1],
                image_pixels=[len(times),height],pixel_filter='vertical BOX integration in RGBA, no horizontal blur',
                scientific_frames=T,scientific_arrays_modified=False,
                scope='Intermediate columns are display interpolation only. They are not observations, new trees, new layouts or additional evaluation samples.')
