"""Publication-size export from frozen event-case maps; no scientific stages.

Reflows the three existing large figures for a seven-inch conference column span.
Requires the local workspace's frozen NPZs and original geographic context.
Packaged PDF figures are sufficient for compiling the paper without this script.
"""
from pathlib import Path
from datetime import datetime,timezone
from itertools import combinations
import sys,json,hashlib
import numpy as np
HERE=Path(__file__).resolve().parents[1]
WORKSPACE=next(p for p in HERE.parents if (p/'code').is_dir())
SCI=WORKSPACE/'code'
sys.path[:0]=[str(SCI/'analysis'),str(SCI/'src'),str(SCI)]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from real_case_large import map_style,spatial,ERA_EVENTS,PALETTE
from real_case_evidence import load,feature_index
DATA=SCI/'results/real_case_studies/evidence'
RECORD=json.loads((DATA.parent/'event_correspondence.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.3,'axes.titlesize':8,'axes.labelsize':7.3,'axes.linewidth':.55,'xtick.labelsize':7,'ytick.labelsize':7,'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'rgmtm-paper-event-20261019'})

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def make(name):
 d,meta=load(name);events=RECORD[name]['events'];frames=RECORD[name]['snapshots'];T=len(d['track']);cmap,norm=map_style(name,d)
 fig=plt.figure(figsize=(7.05,3.10));axes=[]
 for mode,y in [('P',.687),('R',.379)]:
  ax=fig.add_axes([.067,y,.823,.248]);axes.append(ax)
  ax.imshow(d['map'+mode],origin='lower',aspect='auto',extent=(-.5,T-.5,0,1),cmap=cmap,norm=norm,interpolation='nearest')
  ax.set(xlim=(-.5,T-.5),ylim=(0,1),yticks=[0,.5,1],ylabel='Reference position')
  ax.set_title('(a) RG-MTM-P' if mode=='P' else '(b) RG-MTM-R, $\\kappa/\\Delta_F=0.20$',loc='left',fontsize=8,pad=3)
  ax.tick_params(length=2,pad=2)
  for e,color in zip(events,PALETTE):
   x=e['frame_time'];ax.axvline(x,color=color,lw=.7,ls='--');ax.text(x,.985,e['id'],transform=ax.get_xaxis_transform(),va='top',ha='center',color=color,fontsize=7.3,weight='bold',bbox=dict(fc='white',alpha=.92,ec='none',pad=.5))
   if name=='era5' and e.get('candidate') is not None:
    j=feature_index(d,e['snapshot'],e['candidate']);ax.plot(e['snapshot'],d['norm'+mode][e['snapshot'],j],'o',mec=color,mfc='none',ms=4.7,mew=.85)
  if name=='wildfire':
   chosen=json.loads((DATA/'wildfire_selection.json').read_text())['chosen']
   for tr,color in zip(chosen['tracks'],PALETTE[:3]):
    ys=[d['norm'+mode][t,feature_index(d,t,tr)] if feature_index(d,t,tr) is not None else np.nan for t in range(T)]
    ax.plot(range(T),ys,color='white',lw=1.5,alpha=.85);ax.plot(range(T),ys,color=color,lw=.7)
  ticks=[0,28,48,68,88,117] if name=='era5' else [0,5,10,15,20,25,29] if name=='wildfire' else [0,25,50,75,100,125,150,175,200]
  ax.set_xticks(ticks)
  if mode=='P':ax.tick_params(labelbottom=False)
  else:ax.set_xlabel('Frame index',labelpad=1.5)
 cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=fig.add_axes([.915,.405,.014,.48]),extend='min' if name=='wildfire' else 'neither')
 cb.ax.tick_params(length=2,pad=2,labelsize=7)
 cb.set_label('Pressure [hPa]' if name=='era5' else 'Processed log(1 + FRP [MW])' if name=='wildfire' else 'Processed speed',labelpad=2,fontsize=7)
 n=len(frames);gap=.018;width=(.823-gap*(n-1))/n
 if name=='tangaroa':
  with np.load(DATA/'tangaroa_event_volumes.npz') as z: vol={k:z[k] for k in z.files}
 for j,t in enumerate(frames):
  ax=fig.add_axes([.067+j*(width+gap),.025,width,.198])
  if name=='tangaroa':
   ax.imshow(vol['images'][j],origin='lower',extent=(-1,1,-1,1),aspect='auto')
   corners,xy=vol['corners'],vol['projected']
   for a,b in combinations(range(8),2):
    if np.count_nonzero(corners[a]!=corners[b])==1:ax.plot(xy[[a,b],0],xy[[a,b],1],c='.75',lw=.3)
   ax.set(xticks=[],yticks=[],xlim=(-1,1),ylim=(-1,1));prefix=next((e['id']+'; ' for e in events if e['frame_time']==t),'')
   ax.set_title(prefix+f'$t={t}$\nsource {t*.01:.2f}',fontsize=6.8,pad=2)
  else:
   spatial(ax,d,name,t,events[j] if name=='era5' else None)
   prefix=events[j]['id']+'; ' if name=='era5' else ''
   ax.set_title(prefix+f'$t={t}$\n'+str(d['dates'][t])[5:10],fontsize=6.8,pad=2)
   for txt in ax.texts:txt.set_fontsize(6.5)
 if name=='wildfire':
  cbraw=fig.colorbar(ScalarMappable(norm=Normalize(0,d['raw_field'].max()),cmap='inferno'),cax=fig.add_axes([.915,.025,.014,.198]))
  cbraw.ax.tick_params(length=2,pad=2,labelsize=6.5);cbraw.set_label('Raw log(1 + FRP)',fontsize=6.5,labelpad=2)
 file_stem={'era5':'storms','wildfire':'wildfires'}.get(name,name)
 target=HERE/'figures'/f'rgmtm_event_{file_stem}.pdf'
 fig.savefig(target,dpi=450,facecolor='white',metadata={'Title':f'RG-MTM {name} event-linked case','Creator':'Existing-evidence publication export','CreationDate':datetime(2026,10,19,tzinfo=timezone.utc)})
 fig.savefig(target.with_suffix('.png'),dpi=180,facecolor='white');plt.close(fig)
 return {'dataset':name,'frames':T,'events':events,'snapshots':frames,'methods':['RG-MTM-P','RG-MTM-R'],'frozen_inputs':{str(p.relative_to(WORKSPACE)):sha(p) for p in [DATA/f'{name}.npz',DATA/f'{name}.json']+([DATA/'tangaroa_event_volumes.npz'] if name=='tangaroa' else [])},'output':str(target.relative_to(HERE)),'sha256':sha(target),'display_only_changes':'7.05 x 3.10 inch reflow, readable labels, caption text externalized; unchanged arrays, extrema, full axes, event positions, source snapshots and colour scales'}

if __name__=='__main__':
 rows=[make(n) for n in ['era5','wildfire','tangaroa']]
 manifest={'scientific_stages_run':False,'layout_or_metrics_changed':False,'volume_rerendered':False,'rows':rows,'exporter_sha256':sha(Path(__file__))}
 (HERE/'figures/rgmtm_event_export_20261019.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'event_figures':[r['output'] for r in rows],'scientific_stages_run':False}))
