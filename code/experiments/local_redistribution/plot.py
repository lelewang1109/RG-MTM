"""Paper figures for descriptive local budget response and an exact counterexample."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/local_redistribution20261030';FIG=ROOT.parent/'paper/pvis2027/figures'
BLUE='#0072B2';ORANGE='#D55E00';GREY='#89939b'
plt.rcParams.update({'font.family':'Arial','font.size':7,'axes.titlesize':7,'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6,'svg.fonttype':'none','pdf.fonttype':42,'legend.frameon':False})

def save(fig,name):
 for ext in ['pdf','svg','png']:fig.savefig(OUT/f'{name}.{ext}',dpi=260,bbox_inches='tight',pad_inches=.025)
 (FIG/f'{name}.pdf').write_bytes((OUT/f'{name}.pdf').read_bytes())

def build():
 D=json.loads((OUT/'results.json').read_text());C=json.loads((OUT/'controlled.json').read_text());S=D['transitions'];fig,axes=plt.subplots(1,2,figsize=(7,2.15),gridspec_kw={'width_ratios':[1.3,1]})
 x=np.arange(5);labels=['0–2','2–5','5–10','10–20','20–30']
 for name,offset,color in [('Vortex',-.18,BLUE),('Storms-hourly',.18,ORANGE)]:
  ss=[r for r in S if r['dataset']==name];xx=x[:len(ss)]+offset;yy=[100*r['worsened_ge_0p5pp']/r['samples'] for r in ss];axes[0].bar(xx,yy,width=.34,color=color,label='Vortex (90)' if name=='Vortex' else 'Hourly Storms (744)')
 axes[0].text(4.18,2.8,'n/a',ha='center',fontsize=6,color=GREY);axes[0].set(xticks=x,xticklabels=labels,ylim=(0,45),ylabel='Worsened samples (%)',xlabel='Budget change ε (%)');axes[0].set_title('(a) Local increase ≥ 0.5 percentage points',loc='left',pad=7);axes[0].legend(fontsize=6,loc='upper right');axes[0].yaxis.grid(alpha=.18);axes[0].set_axisbelow(True)
 ss=C['states'];e=[0,30];globalerr=[100*s['tau'] for s in ss];local=[100*s['errors'][2] for s in ss]
 axes[1].plot(e,globalerr,'o-',color=BLUE,lw=1.4,ms=4,label='Optimal worst error');axes[1].plot(e,local,'s-',color=ORANGE,lw=1.4,ms=4,label='Leaf C error')
 axes[1].set(yscale='log',ylim=(.05,35),xlim=(-2,32),xticks=e,yticks=[.1,1,10],yticklabels=['0.1','1','10'],ylabel='Displacement (% of L, log scale)',xlabel='Budget ε (%)');axes[1].set_title('(b) Exact four-leaf control',loc='left',pad=7);axes[1].legend(fontsize=6,loc='upper right');axes[1].annotate('22%',(0,22),xytext=(5,0),textcoords='offset points',color=BLUE,fontsize=6);axes[1].annotate('0.087%',(0,local[0]),xytext=(5,-3),textcoords='offset points',color=ORANGE,fontsize=6);axes[1].annotate('1%',(30,1),xytext=(-15,8),textcoords='offset points',color=ORANGE,fontsize=6);axes[1].grid(alpha=.18,which='major');fig.subplots_adjust(left=.08,right=.985,bottom=.23,top=.84,wspace=.35);save(fig,'fig_local_redistribution')
 # Retain the figure object for the editable PPT export wrapper.
 global MAIN_FIG;MAIN_FIG=fig
 fig2,axes=plt.subplots(1,3,figsize=(7,2.25));data=np.load(OUT/'inputs/vortex.npz');V={k:data[k] for k in data.files};err=abs(V['x']-V['q']);E=V['epsilon'];ex=D['example'];t=ex['frame'];j=list(E).index(.2);k=list(E).index(.3);n=V['count'][t]
 axes[0].plot(100*E,[100*np.nanmean(a) for a in err],'o-',color=BLUE,ms=3,lw=1,label='Pooled mean');axes[0].plot(100*E,[100*np.nanmax(a) for a in err],'s-',color=GREY,ms=3,lw=1,label='Sequence maximum');axes[0].set(xlabel='Budget ε (%)',ylabel='Position error (% of L)',ylim=(0,56));axes[0].set_title('(a) Vortex, all 90 frames',loc='left');axes[0].legend(fontsize=6)
 a=100*err[j,t,:n];b=100*err[k,t,:n];worse=b-a>=.5;axes[1].plot([0,40],[0,40],':',lw=.8,color=GREY);axes[1].plot(a[~worse],b[~worse],'o',color=BLUE,ms=2.5,alpha=.65);axes[1].plot(a[worse],b[worse],'o',color=ORANGE,ms=2.5,alpha=.8);axes[1].set(xlabel='Error at ε=20% (% of L)',ylabel='Error at ε=30% (% of L)',xlim=(0,max(a.max(),b.max())+2),ylim=(0,max(a.max(),b.max())+2));axes[1].set_title(f'(b) Frame {t}, all {n} features',loc='left')
 mean0,mean1=a.mean(),b.mean();max0,max1=a.max(),b.max();axes[1].text(.04,.97,f'Mean {mean0:.2f}% to {mean1:.2f}%\nMax {max0:.2f}% to {max1:.2f}%',transform=axes[1].transAxes,va='top',fontsize=6)
 i=list(V['tracks'][t,:n]).index(ex['track']);other=int(np.argmin(b-a))
 for idx,col in [(i,ORANGE),(other,BLUE)]:
  axes[2].plot(100*E,100*err[:,t,idx],'-o',lw=1,ms=3,color=col,label=f'Track {V["tracks"][t,idx]}')
 axes[2].set(xlabel='Budget ε (%)',ylabel='Feature error (% of L)');axes[2].set_title('(c) Two features in that frame',loc='left');axes[2].legend(fontsize=6)
 for ax in axes:ax.grid(alpha=.15);ax.set_axisbelow(True)
 fig2.subplots_adjust(left=.065,right=.99,bottom=.23,top=.85,wspace=.45);save(fig2,'fig_local_redistribution_detail');plt.close(fig2)
 detail=dict(frame=int(t),worsening_track=int(ex['track']),improving_track=int(V['tracks'][t,other]),frame_mean_from=float(mean0/100),frame_mean_to=float(mean1/100),frame_max_from=float(max0/100),frame_max_to=float(max1/100),features=int(n),worsening_from=float(a[i]/100),worsening_to=float(b[i]/100),selected_maximum=True);(OUT/'figure_case.json').write_text(json.dumps(detail,indent=2));print(detail)
 return fig
if __name__=='__main__':build()
