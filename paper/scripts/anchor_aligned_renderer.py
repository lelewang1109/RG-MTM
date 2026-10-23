"""Conservative display reconstruction; never changes saved scientific frames.

Only same-order common extrema with <=0.2L inter-frame displacement are used.
Other intervals retain fixed-position linear interpolation. The mapping is
strictly monotone, no scalar overshoot is introduced, and integer frames match
the frozen 4096-row output exactly. Intermediate columns are display samples.
"""
import numpy as np

def render_display(a,factor=41):
    assert factor%2==1
    G=a['mapR'];N,T=G.shape;u=np.linspace(0,1,N)
    times=np.clip((np.arange(T*factor)+.5)/factor-.5,0,T-1)
    output=np.empty((N,len(times)),dtype=np.float64)
    rules=[]
    for t in range(T-1):
        common=sorted((set(a['track'][t])&set(a['track'][t+1]))-{-1})
        ids0=[int(np.flatnonzero(a['track'][t]==tr)[0]) for tr in common]
        ids1=[int(np.flatnonzero(a['track'][t+1]==tr)[0]) for tr in common]
        p0=a['normR'][t,ids0];p1=a['normR'][t+1,ids1]
        order=np.argsort(p0);p0=p0[order];p1=p1[order]
        k0=np.r_[0,np.rint(p0*(N-1))/(N-1),1]
        k1=np.r_[0,np.rint(p1*(N-1))/(N-1),1]
        reason='aligned'
        if not common:reason='no common extrema'
        elif np.any(np.diff(p1)<=0):reason='crossing extrema order'
        elif np.any(abs(p0-p1)>.2):reason='large position jump'
        elif np.any(np.diff(k0)<=0) or np.any(np.diff(k1)<=0):reason='non-strict sample knots'
        rules.append(dict(frames=[t,t+1],aligned=reason=='aligned',reason=reason,
            common_tracks=[int(common[j]) for j in order],knots0=k0.tolist(),knots1=k1.tolist()))
    for j,tt in enumerate(times):
        t=int(np.floor(tt));alpha=tt-t
        if alpha==0 or t==T-1:
            output[:,j]=G[:,t];continue
        rule=rules[t]
        if not rule['aligned']:
            output[:,j]=(1-alpha)*G[:,t]+alpha*G[:,t+1];continue
        k0=np.array(rule['knots0']);k1=np.array(rule['knots1']);km=(1-alpha)*k0+alpha*k1
        y0=np.interp(u,km,k0);y1=np.interp(u,km,k1)
        output[:,j]=(1-alpha)*np.interp(y0,u,G[:,t])+alpha*np.interp(y1,u,G[:,t+1])
    assert np.array_equal(output[:,factor//2::factor],G)
    assert output.min()>=G.min()-1e-10 and output.max()<=G.max()+1e-10
    report=dict(method='anchor-aligned piecewise linear display reconstruction',
        display_samples_per_frame=factor,original_frames_exact=True,original_rows=N,
        no_scalar_overshoot=True,aligned_intervals=sum(r['aligned'] for r in rules),
        interval_count=T-1,fallback_intervals=[r['frames'] for r in rules if not r['aligned']],
        jump_threshold_L=.2,intervals=rules,
        scope='Intermediate columns are display reconstruction, not observations or new RG-MTM layout/optimization results. Scientific metrics use original saved frames.')
    return output,report
