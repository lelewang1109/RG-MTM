"""Export common-model figures and tables from saved results."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'results/unified20261025';P=ROOT.parent/'paper';L=P/'manuscript/latex'
NAMES={'ring':'Ring','era5':'Storms','wildfire':'Wildfires','olr':'OLR','pm25_2000':r'PM$_{2.5}$'}
KEYS=['topology_time','topology_geometry','reference_0','reference_2','reference_10']
LABELS=['Topology--time','Topology--geometry',r'Reference, 0\%',r'Reference, 2\%',r'Reference, 10\%']
J={n:json.loads((R/(n+'.json')).read_text()) for n in NAMES}
M={n:np.load(R/(n+'_maps.npz')) for n in NAMES}
for n,j in J.items():
 # Include corrected scalar values rather than clipping them to the source
 # range. One range is shared by every displayed map for that input.
 j['display']['vmin']=min(float(np.nanmin(M[n][k])) for k in M[n].files)
 j['display']['vmax']=max(float(np.nanmax(M[n][k])) for k in M[n].files)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})


def save(fig,stem):
 for ext in ['pdf','svg','png']:
  fig.savefig(P/'figures_export'/f'{stem}.{ext}',dpi=220,bbox_inches='tight',pad_inches=.035)
 shutil.copy2(P/'figures_export'/f'{stem}.pdf',L/'figures'/f'{stem}.pdf')
 plt.close(fig)


def panel(ax,data,j,title):
 cmap=plt.get_cmap(j['display']['cmap']).copy();cmap.set_bad('#cfd4da')
 im=ax.imshow(data,origin='lower',aspect='auto',interpolation='nearest',extent=[0,j['frames']-1,0,1],
       cmap=cmap,vmin=j['display']['vmin'],vmax=j['display']['vmax'],rasterized=True)
 ax.set_title(title,fontsize=6.5,pad=5);ax.set_yticks([0,.5,1]);ax.tick_params(labelsize=5.8,length=2)
 ax.set_xticks([0,j['frames']-1]);ax.set_xlabel('Frame',fontsize=6.2,labelpad=1)
 return im


fig=plt.figure(figsize=(7.2,4.0));g=fig.add_gridspec(2,8,width_ratios=[1]*7+[.12],hspace=.55,wspace=.45)
cols=[('native_TMTM','Native\nTMTM'),('topology_time','Inspired\ntopology/time'),
      ('native_ST-MTM','Native\nST-MTM'),('topology_geometry','Inspired\ntopology/geometry'),
      ('reference_0','Reference\n'+r'$\varepsilon=0$'),('reference_2','Reference\n'+r'$\varepsilon=2\%$'),
      ('reference_10','Reference\n'+r'$\varepsilon=10\%$')]
for row,n in enumerate(['ring','era5']):
 j=J[n]
 for k,(key,title) in enumerate(cols):
  ax=fig.add_subplot(g[row,k]);data=M[n][key]
  if key.startswith('native_') and j['native_controls'][key[7:]]['similarity']['global_affine_scale']<0:data=data[::-1]
  im=panel(ax,data,j,title)
  if k==0:ax.set_ylabel(NAMES[n]+'\nNormalized axis',fontsize=6.8)
  else:ax.set_yticklabels([])
 cb=fig.colorbar(im,cax=fig.add_subplot(g[row,7]));cb.ax.tick_params(labelsize=5.5,length=2)
 cb.set_label('Scalar value',fontsize=6.2,labelpad=2)
save(fig,'Fig16')

j=J['ring'];fig=plt.figure(figsize=(7.2,5.1));g=fig.add_gridspec(3,4,width_ratios=[1,1,1,.045],wspace=.25,hspace=.52)
for i,eps in enumerate([0,.02,.1]):
 for k,b in enumerate([np.inf,.1,.05]):
  key=f'epsilon_{eps:g}_position_{b:g}';r=j['budget_grid'][key];s=r['summary'];ax=fig.add_subplot(g[i,k])
  bt=r'$B=\infty$' if np.isinf(b) else f'$B={100*b:g}\\%$'
  title=bt+f"; {s['feasible_frames']}/{j['frames']} columns"
  im=panel(ax,M['ring'][key],j,title)
  if k==0:ax.set_ylabel(f'$\\varepsilon={100*eps:g}\\%$\nNormalized axis',fontsize=7)
  else:ax.set_yticklabels([])
  if i<2:ax.set_xlabel('')
cb=fig.colorbar(im,cax=fig.add_subplot(g[:,3]));cb.ax.tick_params(labelsize=6);cb.set_label('Scalar value',fontsize=7)
save(fig,'Fig17')

rows=[]
for n,j in J.items():
 for key,label in zip(KEYS,LABELS):
  s=j['regimes'][key]['summary']
  values=[s['reference_mae'],s['geometry_rms'],s['stationary_rms'],s['motion_rms'],s['max_topology']]
  rows.append(f"{NAMES[n]} & {label} & "+' & '.join(f'{100*x:.2f}' for x in values)+r' \\')
table=r'''\begin{table*}[t]
\caption{New common-model results on all 614 planar frames, with five settings each (3070 layouts). All numbers are percentages: pooled absolute reference error (R-MAE), root mean framewise geometry/temporal squared residual (G-RMS, stationary S-RMS and projected-motion M-RMS), and worst continuous labelled merge error (Top-max). Geometry and temporal quantities use the common fixed canvas, not native-baseline scales. Empty pair/match terms contribute zero. First-frame temporal terms are zero. Different components express competing priorities; lower reference error need not improve every score.}\label{tab:unified_regimes}
\centering\small
\begin{tabular}{llrrrrr}\toprule
Input & Regime & R-MAE & G-RMS & S-RMS & M-RMS & Top-max\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{table*}
'''
(L/'tables/unified_regimes.tex').write_text(table)
rows=[]
for n in ['ring','era5']:
 for method in ['TMTM','ST-MTM']:
  s=J[n]['native_controls'][method]['similarity']
  rows.append(f"{NAMES[n]} & {method} & {100*s['pair_order_agreement']:.1f} & {100*s['anchor_rmse']:.2f} & {s['pairs']}"+r' \\')
(L/'tables/unified_similarity.tex').write_text(r'''\begin{table}[t]
\caption{Descriptive similarity of inspired regimes to their native comparison methods. One sequence-wide least-squares affine transform, including reflection, aligns native anchors to the inspired anchors; no framewise fit is used. Agreement counts non-tied labelled feature pairs. RMSE is a percentage of the common inspired canvas. Values measure similarity, not algorithm recovery.}\label{tab:unified_similarity}
\centering\small
\begin{tabular}{llrrr}\toprule
Input & Native & Order (\%) & RMSE (\%) & Pairs\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{table}
''')

(L/'unified_results.tex').write_text(r'''\section{Operating Regimes and Two-Budget Maps}\label{sec:unified_maps}
\begin{figure*}[t]
\centering\includegraphics[width=\linewidth]{figures/Fig16.pdf}
\caption{Native methods and operating regimes of one model on Ring (top) and Storms (bottom). Within each row all columns use the same fields, time steps and scalar colours; the colour range includes corrected barrier values, which are constructed values rather than source observations. Columns 2, 4 and 5--7 share interval widths, canvas, QP and renderer; only the controls change. Native methods use their own layouts and scalar filling. All display axes are normalized to $[0,1]$; one global native reflection follows the similarity fit, with no per-frame warping. The topology/time and topology/geometry columns express inspired design principles, not native-output equality. All reference columns use $B=\infty$ and vary the true topology allowance.}\label{fig:unified_regimes}
\end{figure*}

\begin{figure*}[t]
\centering\includegraphics[width=\linewidth]{figures/Fig17.pdf}
\caption{Ring maps across topology allowances (rows) and reference-position caps (columns), using the same reference-guided objective, candidate pool and scalar renderer. Position allowances are fractions of the common canvas; topology allowances are fractions of the fixed scalar range. Gray columns denote frames for which no candidate meets both budgets, not zero scalar values. A history restarts after such a missing frame. Counts report witnessed feasible columns, rather than full-space feasibility on candidate-only frames. Finite maps include measured strict-extremum clearance and anchor rounding, which are separate from the continuous constraints.}\label{fig:unified_budget_grid}
\end{figure*}

The operating-regime views expose the difference between a topology-preserving temporal emphasis, a relative-distance emphasis, and an absolute reference target. They also show why output resemblance must be measured rather than inferred from the name of a regime. The native methods allocate widths and arrange internal samples differently. The common-model columns deliberately retain one representation so that changes can be attributed to the declared controls. The two-budget matrix additionally makes incompatible requests visible as missing witnesses instead of silently widening a tolerance.
''')

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=dict(date='2026-10-26',run_id='unified20261025',frames=sum(j['frames'] for j in J.values()),settings=5,
             layouts=sum(j['frames']*5 for j in J.values()),grid_queries=len(J['ring']['budget_grid'])*40,
             native_similarity_frames=2*(J['ring']['frames']+J['era5']['frames']),
             source_sha256={s:sha(ROOT/s) for s in ['src/rgmtm/unified.py','src/rgmtm/error_budget.py','experiments/unified/run.py','experiments/unified/export.py']},
             results_sha256={p.name:sha(p) for p in R.glob('*') if p.suffix in ['.json','.npz'] and not p.name.endswith('_progress.json') and p.name!='manifest.json'},
             interpretation='same-model design-principle regimes, not exact native special cases; sequential candidate QPs',
             historical_results='unchanged numerical files in framework20261025 and earlier folders')
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for dst in [P/'evidence/unified20261025',L/'evidence/unified20261025']:
 dst.mkdir(parents=True,exist_ok=True)
 for f in R.glob('*.json'):
  if not f.name.endswith('_progress.json'):shutil.copy2(f,dst/f.name)
catalog=json.loads((P/'FIGURE_INDEX.json').read_text());vectors=catalog['additional_vector_figures']
for f in vectors:
 if f['number']==15:f.update(latex_source='budget_threshold_response.tex',source='../code/experiments/framework/export.py')
for num,label,title in [(16,'fig:unified_regimes','One-model operating regimes and native comparisons'),(17,'fig:unified_budget_grid','Topology and position budget matrix')]:
 f=dict(number=num,stem=f'Fig{num}',title=title,asset=f'manuscript/latex/figures/Fig{num}.pdf',export=f'figures_export/Fig{num}.pdf',
       label=label,source='../code/experiments/unified/export.py',editable_master=f'figures_export/Fig{num}.svg',ppt=None,
       latex_source='unified_results.tex',asset_sha256=sha(P/'figures_export'/f'Fig{num}.pdf'))
 vectors[:]=[x for x in vectors if x['number']!=num];vectors.append(f)
catalog['main_figure_count']=17
catalog['updated']='2026-10-26'
catalog['combined_ppt_scope']='Existing Figures 1--14 only; Figures 15--17 are reproducible code/SVG vector masters.'
(P/'FIGURE_INDEX.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
print('Exported Figures 16--17, operating/similarity tables, evidence and manifest.')
