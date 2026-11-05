"""Reproducible vector PDF/SVG and 400-dpi PNG figures in manuscript style."""
from build import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import font_manager
from itertools import permutations
from scipy.optimize import linprog
from rgmtm.error_budget import Parameters, constraints
from rgmtm.framework import merge_costs,interval_costs
from rgmtm.interval_order import width_order,width_certificate,width_chain_certificate
from rgmtm.order_certificate import certificate

BLUE='#0072b2';LIGHT='#56b4e9';ORANGE='#d55e00';GREEN='#009e73';PURPLE='#8c6bb1';GRAY='#777777'
FIG=OUT/'figures';FIG.mkdir(parents=True,exist_ok=True)
font=Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf')
if font.exists():font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':'Times New Roman','font.size':8,'axes.titlesize':8.5,
    'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
    'mathtext.fontset':'stix','axes.linewidth':.6,'lines.linewidth':1.1,
    'xtick.major.width':.6,'ytick.major.width':.6,'xtick.major.size':2.5,'ytick.major.size':2.5,
    'pdf.fonttype':42,'svg.fonttype':'none','savefig.dpi':400})

def tidy(ax,title):
    ax.set_title(title,loc='left',pad=6,fontweight='bold',bbox=dict(facecolor='#f1f1f1',edgecolor='none',pad=2))
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color='#dedede',lw=.45);ax.set_axisbelow(True)

def save(fig,name):
    for ext in ['pdf','png','svg']:fig.savefig(FIG/f'{name}.{ext}',facecolor='white',dpi=400)
    plt.close(fig)

def sensitivity():
    allrows=readcsv(OUT/'data/full_sequence_sweep.csv')
    for actual in [False,True]:
        fig,axes=plt.subplots(2,2,figsize=(7,3.8))
        for idx,(name,ax) in enumerate(zip(protocol.PARAMS,axes.flat)):
            rr=[r for r in allrows if r['dataset']==name]
            x=np.array([float(r['NMLE_max' if actual else 'epsilon'])*100 for r in rr])
            npe=np.array([float(r['NPE'])*100 for r in rr]);worst=np.array([float(r['E_inf'])*100 for r in rr])
            ax.plot(x,worst,'o-',color=BLUE,ms=2.7,label=r'Worst $E_\infty$')
            ax.plot(x,npe,'s--',color=LIGHT,ms=2.4,label='NPE (mean frame maximum)')
            k=next(i for i,r in enumerate(rr) if r['balanced']=='True')
            ax.scatter(x[k],npe[k],s=55,marker='*',facecolor=ORANGE,edgecolor='white',lw=.3,zorder=5)
            ax.scatter(x[0],npe[0],s=25,facecolor='white',edgecolor=BLUE,lw=.8,zorder=4)
            if actual:
                span=float(np.ptp(x))
                if span<1e-10:
                    ax.set_xlim(-.025,1.0);ax.set_xticks([0,.5,1.])
                    ax.text(.08,.82,r'All $\varepsilon=0$--$30\%$ coincide',transform=ax.transAxes,fontsize=7)
                else:
                    ax.set_xlim(-.03*span,max(x)+.12*span)
                    groups={}
                    for j in sorted(set([0,k,len(rr)-1])):
                        key=(round(float(x[j]),7),round(float(worst[j]),7))
                        groups.setdefault(key,[]).append(j)
                    previous=None
                    for (xx,yy),indices in groups.items():
                        label=', '.join(f"{100*float(rr[j]['epsilon']):g}%" for j in indices)
                        close=previous is not None and abs(xx-previous)<.09*span
                        ax.annotate(label,(xx,yy),xytext=(8,-12) if close else (3,5),textcoords='offset points',fontsize=6.5)
                        previous=xx
            else:
                xmax=max(x);ax.set_xticks([0,5,10,15,20,25,30] if xmax<=30 else [0,20,40,60,80,100]);ax.set_xlim(-.02*xmax,1.02*xmax)
            ax.set_ylim(0,max(worst)*1.22+.15)
            ax.set_xlabel('Actual worst merge error NMLE (%)' if actual else r'Requested merge budget $\varepsilon$ (%)')
            ax.set_ylabel('Position error (%)');tidy(ax,f'({chr(97+idx)}) {name}')
        handles=[Line2D([],[],color=BLUE,marker='o',ms=3,label=r'Worst $E_\infty$'),
            Line2D([],[],color=LIGHT,ls='--',marker='s',ms=3,label='NPE'),
            Line2D([],[],color=BLUE,marker='o',mfc='white',ls='none',ms=4,label='Exact'),
            Line2D([],[],color=ORANGE,marker='*',ls='none',ms=7,label='Selected Balanced')]
        fig.legend(handles=handles,loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,.005))
        fig.subplots_adjust(left=.08,right=.985,top=.94,bottom=.17,hspace=.58,wspace=.28)
        save(fig,'fig_position_topology_frontier' if actual else 'fig_budget_sensitivity')

def lp_tau(w,q,o,p):
    n=len(w);A,b,bounds=constraints(w,o,p)
    E=np.c_[np.eye(n),np.zeros((n,n)),-np.ones(n)]
    F=np.c_[-np.eye(n),np.zeros((n,n)),-np.ones(n)]
    res=linprog(np.r_[np.zeros(2*n),1.],A_ub=np.vstack([np.c_[-A,np.zeros(len(A))],E,F]),b_ub=np.r_[-b,q,-q],bounds=bounds+[(0,None)],method='highs')
    assert res.success,res.message
    return float(res.fun)

def theory():
    p=Parameters(canvas=1.,canvas_origin=0.,gap=.01,rho=.5)
    w=np.full(4,.06);O=np.array(list(permutations(range(4))))
    def matrix(h):
        V=np.ones((4,4));np.fill_diagonal(V,0);V[0,1]=V[1,0]=V[2,3]=V[3,2]=1-h
        return V
    V=matrix(.6);delta=merge_costs(O,V);records=[]
    for d in np.linspace(-.12,.30,43):
        q=np.array([.2,.5,.5-d,.8-d]);vals=np.array([lp_tau(w,q,o,p) for o in O])
        np.testing.assert_allclose(vals,interval_costs(O,w,q,p),atol=1e-9)
        optimum=vals[delta<=1e-10].min();alg=width_order(V,q,w,p,0.)['tau']
        lower=width_certificate(V,q,w,p);point=certificate(V,q,1.)
        assert lower<=optimum+1e-9 and abs(alg-optimum)<1e-9
        records.append(dict(overlap=d,point_bound=point,width_bound=lower,exhaustive_LP=optimum,algorithm=alg))
    protocol.table(OUT/'data/controlled_overlap.csv',records)
    budgetrows=[];q=np.array([.2,.5,.26,.56])
    for h in [.2,.4,.6,.8]:
        V=matrix(h);cost=merge_costs(O,V);vals=np.array([lp_tau(w,q,o,p) for o in O])
        for eps in np.linspace(0,.45,91):
            optimum=vals[cost<=eps+1e-10].min();alg=width_order(V,q,w,p,float(eps))['tau']
            lower=width_chain_certificate(V,q,w,p,float(eps))
            assert lower<=optimum+1e-9 and abs(alg-optimum)<1e-9
            budgetrows.append(dict(parent_gap=h,epsilon=eps,lower_bound=lower,exhaustive_LP=optimum,algorithm=alg))
    protocol.table(OUT/'data/controlled_budget.csv',budgetrows)
    fig,axes=plt.subplots(1,2,figsize=(7,2.65));a,b=axes
    x=np.array([r['overlap']*100 for r in records])
    a.plot(x,[r['point_bound']*100 for r in records],ls='--',color=LIGHT,label=r'Point bound $\nu^*$')
    a.plot(x,[r['exhaustive_LP']*100 for r in records],color=ORANGE,label='Optimum (24 orders; LP)')
    a.plot(x[::3],[r['width_bound']*100 for r in records][::3],ls='none',marker='o',mfc='white',color=BLUE,ms=4,label='Width bound')
    a.plot(x[1::6],[r['algorithm']*100 for r in records][1::6],ls='none',marker='x',color='#111111',ms=4,label='Order search')
    a.set(xlabel=r'Signed subtree overlap $d$ (%)',ylabel='Minimax displacement (%)',ylim=(-.3,19));tidy(a,'(a) Overlap forces displacement')
    a.legend(frameon=False,loc='upper left',fontsize=6.5,handlelength=1.7)
    for h,c in zip([.2,.4,.6,.8],[LIGHT,GREEN,ORANGE,PURPLE]):
        rr=[r for r in budgetrows if r['parent_gap']==h]
        b.step([r['epsilon']*100 for r in rr],[r['exhaustive_LP']*100 for r in rr],where='post',color=c,label=f'$h={100*h:g}\\%$')
        b.plot(h*50,0,'o',mfc='white',color=c,ms=4)
    b.set(xlabel=r'Merge budget $\varepsilon$ (%)',ylabel='Minimax displacement (%)',ylim=(-.4,17),xlim=(0,45));tidy(b,r'(b) Conflict releases at $\varepsilon=h/2$')
    b.legend(frameon=False,ncol=2,loc='upper right',fontsize=6.5)
    fig.subplots_adjust(left=.075,right=.985,bottom=.19,top=.89,wspace=.28)
    save(fig,'fig_controlled_bounds')

def temporal():
    root=BASE/'results/Storms';fig,axes=plt.subplots(2,1,figsize=(7,3.6),sharex=True,gridspec_kw={'height_ratios':[1.7,1]})
    curves=[('baseline_npe/tmtm_per_frame.csv','TMTM adapter',GRAY,'-'),
        ('baseline_npe/temporal_per_frame.csv','ST-MTM adapter',PURPLE,'-'),
        ('Exact/per_frame.csv','AnchorMTM Exact',LIGHT,'-'),('Balanced/per_frame.csv','AnchorMTM Balanced',BLUE,'-')]
    export=[]
    for file,label,color,ls in curves:
        rr=readcsv(root/file);x=np.array([int(r['frame']) for r in rr])/24
        axes[0].plot(x,[float(r['NPE'])*100 for r in rr],color=color,lw=.7 if 'adapter' in label else 1.,ls=ls,label=label)
        export.extend(dict(method=label,frame=r['frame'],NPE=r['NPE']) for r in rr)
    rr=readcsv(root/'Balanced/per_frame.csv');x=np.array([int(r['frame']) for r in rr])/24
    nm=np.array([float(r['topology_max'])*100 for r in rr])
    axes[1].fill_between(x,nm,color=LIGHT,alpha=.25,lw=0);axes[1].plot(x,nm,color=BLUE,lw=.8,label='Actual per-frame NMLE')
    eps=100*protocol.read(root/'selection.json')['epsilon'];axes[1].axhline(eps,color=ORANGE,ls='--',lw=.9,label=f'Requested budget ({eps:g}%)')
    tidy(axes[0],'(a) Storms: position error over the complete sequence');tidy(axes[1],'(b) Where the topology budget is used')
    axes[0].set_ylabel('Frame-max position error (%)');axes[0].set_ylim(0,105)
    axes[0].legend(frameon=False,ncol=4,fontsize=6.5,loc='upper center')
    axes[1].set(ylabel='Merge error (%)',ylim=(0,14),xlabel='December 1999 (UTC)')
    axes[1].legend(frameon=False,ncol=2,fontsize=6.5,loc='upper center')
    axes[1].set_xticks([0,7,14,21,30],['Dec 1','Dec 8','Dec 15','Dec 22','Dec 31']);axes[1].set_xlim(0,743/24)
    fig.subplots_adjust(left=.095,right=.985,top=.94,bottom=.13,hspace=.32)
    protocol.table(OUT/'data/storms_temporal.csv',export);save(fig,'fig_storms_temporal_diagnostics')

def motion():
    root=BASE/'results/Storms';prep=root/'preparation';F=np.load(prep/'fields.npy');xy=np.load(prep/'coordinates.npy');meta=protocol.read(prep/'protocol.json')
    d=protocol.load('Storms',F,xy,meta['sample_measure'],prep/'trees');L=d['parameters'].canvas
    tracks=d['scene']['tracks'];qs=d['reference']['qs']
    layouts={label:protocol.read(root/rel) for label,rel in [('TMTM adapter','baseline_npe/tmtm_anchors.json'),('ST-MTM adapter','baseline_npe/temporal_anchors.json')]}
    for label,mode in [('AnchorMTM Exact','Exact'),('AnchorMTM Balanced','Balanced')]:layouts[label]=[r['pixel_x'] for r in protocol.read(root/mode/'layouts.json')]
    rows=[]
    for name,U in layouts.items():
        for t in range(1,len(U)):
            old={k:i for i,k in enumerate(tracks[t-1])}
            for i,k in enumerate(tracks[t]):
                if k not in old:continue
                j=old[k];dq=(qs[t][i]-qs[t-1][j])/L;dx=(U[t][i]-U[t-1][j])/L
                rows.append(dict(method=name,frame=t,track=k,delta_reference=dq,delta_display=dx,residual=abs(dx-dq)))
    protocol.table(OUT/'data/storms_projected_motion.csv',rows)
    fig,axes=plt.subplots(1,4,figsize=(7,2.2),sharex=True,sharey=True)
    colors=[GRAY,PURPLE,LIGHT,BLUE];summ=[]
    lim=max(max(abs(r['delta_reference']),abs(r['delta_display'])) for r in rows)*100*1.04
    for i,(ax,(name,U),c) in enumerate(zip(axes,layouts.items(),colors)):
        rr=[r for r in rows if r['method']==name];x=np.array([r['delta_reference'] for r in rr])*100;y=np.array([r['delta_display'] for r in rr])*100
        ax.plot([-lim,lim],[-lim,lim],color='#aaaaaa',ls='--',lw=.7)
        ax.scatter(x,y,s=3,color=c,alpha=.3,edgecolors='none',rasterized=False)
        mae=np.mean([r['residual'] for r in rr])*100
        ax.text(.04,.95,f'Mean residual: {mae:.2f}%\n$n={len(rr)}$',transform=ax.transAxes,va='top',fontsize=6.5)
        title=name.replace('AnchorMTM ','');tidy(ax,f'({chr(97+i)}) {title}')
        ax.set(xlim=(-lim,lim),ylim=(-lim,lim),xlabel=r'Projected motion $\Delta q/L$ (%)');ax.set_aspect('equal')
        summ.append(dict(method=name,matched_steps=len(rr),mean_absolute_residual=mae/100))
    axes[0].set_ylabel(r'Displayed motion $\Delta x/L$ (%)')
    fig.subplots_adjust(left=.075,right=.99,top=.85,bottom=.23,wspace=.18)
    protocol.table(OUT/'data/storms_motion_summary.csv',summ);save(fig,'fig_storms_projected_motion')

if __name__=='__main__':
    with threadpool_limits(limits=1):
        theory();temporal();motion();sensitivity()
