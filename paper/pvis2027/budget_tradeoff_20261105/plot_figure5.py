"""Compact single-column Figure 5: three planar and two volumetric sequences."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import font_manager
OUT=Path(__file__).resolve().parent
FIG=OUT.parent/'figures'
FIG.mkdir(parents=True,exist_ok=True)
def readcsv(p):
 with p.open() as f:return list(csv.DictReader(f))
records=readcsv(OUT/'figure5_metrics.csv')
font_path=Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf')
if font_path.exists():font_manager.fontManager.addfont(str(font_path))
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':7,
 'axes.titlesize':7.5,'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,
 'axes.linewidth':.55,'lines.linewidth':1.,'xtick.major.size':2,'ytick.major.size':2,
 'xtick.major.width':.5,'ytick.major.width':.5,'pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(3,2,figsize=(3.4,2.95))
cmap=matplotlib.colors.LinearSegmentedColormap.from_list('budget',['#004b87','#0085bd','#b9dced'])
for index,(ax,name) in enumerate(zip(axes.flat,['Storms','Wildfires','Ring','Tangaroa','Cylinder'])):
 points=[r for r in records if r['dataset']==name]
 x=np.array([float(r['NMLE_max'])*100 for r in points]);y=np.array([float(r['E_inf'])*100 for r in points]);mean=np.array([float(r['E_pool'])*100 for r in points]);eps=np.array([float(r['epsilon']) for r in points])
 colors=cmap(np.sqrt(eps))
 ax.plot(x,y,color='#0085bd',lw=1.1,zorder=2)
 ax.plot(x,mean,color='#56b4d9',ls='--',lw=.85,zorder=2)
 ax.scatter(x,y,c=colors,s=11,edgecolor='white',linewidth=.3,zorder=3)
 ax.scatter(x,mean,c=colors,s=7,edgecolor='white',linewidth=.25,zorder=3)
 span=max(x);ax.set_xlim(-.025*span,span*1.08)
 ax.set_ylim(0,max(y)*1.19)
 chosen=[j for j,e in enumerate(eps) if any(abs(e-target)<1e-10 for target in [0,.02,.1,.63])]
 chosen=sorted(set(chosen+[len(points)-1]));seen=[]
 for j in chosen:
  if any(abs(x[j]-v)<.075*span for v in seen):continue
  seen.append(x[j]);end=x[j]>.85*span
  ax.annotate(f'{100*eps[j]:g}',(x[j],y[j]),xytext=(-2 if end else 2,3),ha='right' if end else 'left',textcoords='offset points',fontsize=5.6)
 ax.set_title(name+(' (3D)' if name in ['Tangaroa','Cylinder'] else ''),pad=2.5)
 ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dfe3e6',lw=.4);ax.set_axisbelow(True)
 ax.tick_params(pad=1.4)
legend=axes.flat[-1];legend.axis('off')
handles=[Line2D([],[],color='#0085bd',marker='o',mec='white',mew=.3,ms=3,label=r'Worst $E_\infty$'),
 Line2D([],[],color='#56b4d9',ls='--',label=r'Mean $E_{\mathrm{pool}}$')]
legend.legend(handles=handles,loc='upper left',bbox_to_anchor=(.0,1.04),frameon=False,fontsize=6.7,handlelength=2,borderaxespad=0,labelspacing=.65)
legend.text(.0,.44,r'Dot shade / labels: $\varepsilon$ (%)'+'\nDark = zero budget\nAll frames; fixed reference',transform=legend.transAxes,fontsize=6.1,va='top',linespacing=1.4)
fig.subplots_adjust(left=.12,right=.985,top=.955,bottom=.13,hspace=.49,wspace=.27)
fig.supylabel('Displacement (%)',x=.006,y=.56,fontsize=7)
fig.supxlabel('Worst merge error NMLE (%)',y=.015,fontsize=7)
for ext in ['pdf','svg','png']:
 fig.savefig(FIG/f'anchor_budget_tradeoff_single_column.{ext}',dpi=450,facecolor='white',bbox_inches='tight',pad_inches=.015)
plt.close(fig)
assert len({r['dataset'] for r in records})==5 and not any(r['dataset']=='Gaussian' for r in records)
print(FIG/'anchor_budget_tradeoff_single_column.pdf')
