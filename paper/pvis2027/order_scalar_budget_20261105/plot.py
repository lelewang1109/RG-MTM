"""Two single-column NROE/NMLE figures. CSV-only reproduction; no motion metrics."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import font_manager,ticker
HERE=Path(__file__).resolve().parent;FIG=HERE.parent/'figures'
with (HERE/'metrics.csv').open() as f:rows=list(csv.DictReader(f))
font=Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf')
if font.exists():font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':6.5,
 'axes.labelsize':6.5,'axes.titlesize':6.8,'xtick.labelsize':5.7,'ytick.labelsize':5.7,
 'axes.linewidth':.5,'xtick.major.size':2,'ytick.major.size':2,'xtick.major.width':.5,'ytick.major.width':.5,
 'pdf.fonttype':42,'svg.fonttype':'none'})
BLUE='#0086ad';TEAL='#00ad9a';ORANGE='#f37b21'
for names,stem,height in [(['Storms','Wildfires','Ring'],'anchor_planar_order_scalar',2.65),(['Tangaroa','Cylinder'],'anchor_volume_order_scalar',1.90)]:
 fig,axes=plt.subplots(len(names),2,figsize=(3.4,height),sharex=True,squeeze=False)
 for i,name in enumerate(names):
  rr=sorted([r for r in rows if r['dataset']==name],key=lambda r:float(r['epsilon']));assert len(rr)==5
  x=np.arange(5);v=lambda k:np.array([float(r[k])*100 for r in rr])
  a,b=axes[i]
  a.plot(x,v('NROE_mean'),'-o',color=BLUE,lw=.9,ms=2.3,mec='#33687a',mew=.3)
  b.plot(x,v('NMLE_mean'),'-o',color=TEAL,lw=.9,ms=2.3,mec='#33687a',mew=.3)
  b.plot(x,v('NMLE_max'),'--s',color=ORANGE,lw=.9,ms=2.3,mew=.3)
  a.set_ylim(0,max(v('NROE_mean'))*1.18+.025);b.set_ylim(0,max(v('NMLE_max'))*1.16+.025)
  a.set_ylabel('NROE (%)',labelpad=2);b.set_ylabel('NMLE (%)',labelpad=2)
  a.set_title(f'{name} ({int(float(rr[0]["frames"]))} frames)',loc='left',pad=2)
  for ax in [a,b]:
   ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dfe3e6',lw=.35);ax.set_axisbelow(True)
   ax.set_xlim(-.18,4.18);ax.set_xticks(x,['Exact','2%','5%','10%','20%']);ax.tick_params(pad=1.5)
   ax.yaxis.set_major_locator(ticker.MaxNLocator(3,min_n_ticks=3))
 fig.text(.29,.998,'(a) Reference order',ha='center',va='top',fontsize=7)
 fig.text(.79,.998,'(b) Scalar cost',ha='center',va='top',fontsize=7)
 handles=[Line2D([],[],color=TEAL,marker='o',ms=2.5,lw=.9,label='NMLE: mean over frames'),Line2D([],[],color=ORANGE,ls='--',marker='s',ms=2.5,lw=.9,label='maximum')]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.52,-.005),frameon=False,ncol=2,fontsize=5.9,handlelength=1.7,columnspacing=1,borderaxespad=0)
 fig.subplots_adjust(left=.115,right=.99,top=.87 if len(names)==2 else .91,bottom=.18 if len(names)==2 else .13,wspace=.42,hspace=.51)
 for ext in ['pdf','svg','png']:fig.savefig(FIG/f'{stem}.{ext}',dpi=450,facecolor='white',bbox_inches='tight',pad_inches=.015)
 plt.close(fig)
 print(FIG/f'{stem}.pdf')
