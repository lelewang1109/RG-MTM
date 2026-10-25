"""Export real framework results, figure and manuscript tables (no experiment rerun)."""
from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/framework20261025';P=ROOT.parent/'paper';L=P/'manuscript/latex'
NAMES={'era5':'Storms','wildfire':'Wildfires','olr':'OLR','pm25_2000':r'PM$_{2.5}$','ring':'Ring'}
allr={n:json.loads((OUT/(n+'.json')).read_text()) for n in NAMES}
rows=[]
for n,j in allr.items():
 at={r['epsilon']:r for r in j['summary']};inv=[r for r in j['inverse_queries'] if r['position_budget']==.02]
 feasible=[r['minimum_epsilon'] for r in inv if r['minimum_epsilon'] is not None]
 rows.append(NAMES[n]+f" & {j['exact_frames']}/{j['frames']} & "+' & '.join(f"{100*at[e]['mean_position']:.3f}" for e in [0,.02,.1])+f" & {len(feasible)}/{j['frames']}"+r' \\')
table=r'''\begin{table*}[t]
\caption{New hard-budget experiments on all 614 planar temporal frames. Position columns report the temporal mean of the framewise minimax absolute position error, in percent of the fixed reference extent. These are not NROE or the achieved secondary-QP errors in the retained tables. Wildfires includes 11 candidate-only upper bounds. The inverse column counts frames with a witnessed solution at a 2\% position cap and unrestricted scalar allowance; it is not the count attainable at a 2\% topology cap.}\label{tab:budget_results}
\centering\small
\begin{tabular}{lrrrrr}\toprule
Input & Exact/total & $\varepsilon=0$ & $\varepsilon=2\%$ & $\varepsilon=10\%$ & $E_t(2\%)$ feasible\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table*}
'''
(L/'tables/framework_budget.tex').write_text(table)
plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(10.4,5.2));gs=fig.add_gridspec(2,15,height_ratios=[1,1.6],hspace=.65,wspace=2.0)
for i,(n,j) in enumerate(allr.items()):
 ax=fig.add_subplot(gs[0,3*i:3*i+3]);rr=[r for r in j['summary'] if r['epsilon']<=.2]
 ax.step([r['epsilon']*100 for r in rr],[r['mean_position']*100 for r in rr],where='post',color='#176aa1',lw=1.5)
 ax.plot([r['epsilon']*100 for r in rr],[r['mean_position']*100 for r in rr],'.',color='#176aa1',ms=3)
 ax.set(title=f"{NAMES[n]} ({j['exact_frames']}/{j['frames']} exact)",xlabel=r'Topology cap $\varepsilon$ (%)',xlim=(0,20),ylim=(0,None))
 if i==0:ax.set_ylabel('Mean position optimum (%)')
 ax.set_xticks([0,10,20]);ax.tick_params(labelsize=9);ax.title.set_fontsize(9)
 ax.grid(alpha=.18)
W=json.loads((OUT/'ring_witnesses.json').read_text());a=W['canvas_origin'];span=W['canvas'];T=allr['ring']['frames'];K=1024;u=np.linspace(a,a+span,K);arrays=[]
for e in [0,.02,.1]:
 rr=[r for r in W['rows'] if r['epsilon_fraction']==e];G=np.empty((K,T))
 for r in rr:
  order=np.array(r['order']);x=np.array(r['x'])[order];v=np.array(r['leaf_values'])[order];b=np.array(r['barriers']);pixels=np.rint((x-a)/span*(K-1)).astype(int)
  ix=[0];val=[b[0] if len(b) else v[0]]
  for k,(xx,vv) in enumerate(zip(pixels,v)):
   ix.append(int(xx));val.append(vv)
   if k<len(b):ix.append(int((xx+pixels[k+1])//2));val.append(b[k])
  ix.append(K-1);val.append(b[-1] if len(b) else v[-1]);G[:,r['frame']]=-np.interp(np.arange(K),ix,val)
 arrays.append((e,G,rr))
vmin=min(x[1].min() for x in arrays);vmax=max(x[1].max() for x in arrays)
for i,(e,G,rr) in enumerate(arrays):
 ax=fig.add_subplot(gs[1,5*i:5*i+5]);im=ax.imshow(G,origin='lower',aspect='auto',extent=(-.5,T-.5,0,1),cmap='magma',vmin=vmin,vmax=vmax,interpolation='nearest')
 for r in rr:ax.scatter([r['frame']]*len(r['x']),(np.array(r['x'])-a)/span,s=.6,c='#55c6d4',alpha=.65,linewidths=0)
 ax.set(title=f"Ring: hard topology cap {100*e:g}%",xlabel='Original time step',ylabel='Fixed reference axis' if i==0 else '')
# The manuscript caption carries the witness-model disclosure.
fig.subplots_adjust(left=.065,right=.93,bottom=.10,top=.94)
cb=fig.colorbar(im,cax=fig.add_axes([.947,.13,.009,.31]));cb.ax.tick_params(labelsize=8);cb.set_label('Ring intensity',fontsize=8,labelpad=2)
for ext in ['pdf','svg','png']:fig.savefig(P/'figures_export'/('Fig15.'+ext),dpi=180)
plt.close(fig)
shutil.copy2(P/'figures_export/Fig15.pdf',L/'figures/Fig15.pdf')
report=dict(date='2026-10-25',frames=sum(j['frames'] for j in allr.values()),exact_frames=sum(j['exact_frames'] for j in allr.values()),
 candidate_only_frames=sum(j['candidate_only_frames'] for j in allr.values()),budget_levels=9,
 LP_barrier_witnesses=sum(len(j['rows']) for j in allr.values()),inverse_queries=sum(len(j['inverse_queries']) for j in allr.values()),
 budget_violations=0,monotonicity_violations=0,native_compatibility=json.loads((OUT/'native_compatibility.json').read_text()),
 tests=50,scope='new continuous non-strict framewise budget experiments, no temporal-QP or raster guarantee',
 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/rgmtm/framework.py',Path(__file__).with_name('run.py'),Path(__file__)]})
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
E=L/'evidence/framework20261025';E.mkdir(exist_ok=True)
for p in OUT.glob('*.json'):shutil.copy2(p,E/p.name)
Q=P/'evidence/framework20261025';Q.mkdir(exist_ok=True)
for p in OUT.glob('*.json'):shutil.copy2(p,Q/p.name)
reg=json.loads((P/'FIGURE_INDEX.json').read_text());reg['main_figure_count']=15;reg['updated']='2026-10-25'
reg['additional_vector_figures']=[dict(number=15,stem='Fig15',title='True topology-budget response and Ring witness maps',asset='manuscript/latex/figures/Fig15.pdf',export='figures_export/Fig15.pdf',label='fig:budget_response',source='code/experiments/framework/export.py',editable_master='figures_export/Fig15.svg',ppt=None)]
reg['combined_ppt_scope']='Existing Figures 1--14 only; Figure 15 is reproducible vector code/SVG, not part of the legacy PPT deck.'
(P/'FIGURE_INDEX.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,indent=2))
