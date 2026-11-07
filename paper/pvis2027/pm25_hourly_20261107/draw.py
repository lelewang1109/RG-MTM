from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from datetime import datetime,timedelta
C=np.load(Path(__file__).with_name('figure_cache.npz'));A=np.zeros((4096,744));A[:,504:637]=C['map'];F=dict(zip(C['frames'],C['snapshots']));dates=[datetime(2017,1,1)+timedelta(hours=i) for i in range(744)];cm=LinearSegmentedColormap.from_list('pollution',plt.get_cmap('RdYlGn_r')(np.linspace(0,1,256)**.6));norm=Normalize(0,400)
OUT=Path(__file__).resolve().parent;plt.rcParams.update({'font.size':6,'axes.labelsize':6,'xtick.labelsize':5,'ytick.labelsize':5,'font.family':'serif'})
start=504;stop=637;frames=[504,540,576,612,636];fig=plt.figure(figsize=(3.35,2.20));ax=fig.add_axes([.12,.55,.83,.39]);im=ax.imshow(A[:,start:stop],origin='lower',aspect='auto',extent=[start-.5,stop-.5,0,1],cmap=cm,norm=norm,interpolation='bilinear');ax.set_ylabel('Mapped position');ax.set_yticks([0,.5,1]);ax.set_xticks([504,576,636],[dates[t].strftime('%Y-%m-%d')+' '+dates[t].strftime('%H:%M') for t in [504,576,636]]);ax.tick_params(pad=1,length=2);ax.get_xticklabels()[-1].set_ha('right');ax.get_xticklabels()[0].set_ha('left')

geo=json.loads((OUT/'china_admin1.geojson').read_text())
for i,t in enumerate(frames):
 a=fig.add_axes([.12+i*.168,.25,.158,.23]);a.imshow(F[t],origin='lower',extent=[110,120,32,41],cmap=cm,norm=norm,interpolation='bilinear',aspect='auto')
 for ft in geo['features']:
  g=ft['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for poly in polys:
   q=np.array(poly[0]);a.plot(q[:,0],q[:,1],color='#444444',lw=.22)
 a.set(xlim=(110,120),ylim=(32,41),xticks=[],yticks=[]);a.text(.5,-.08,dates[t].strftime('%Y-%m-%d')+' '+dates[t].strftime('%H:%M'),transform=a.transAxes,ha='center',va='top',fontsize=3.6)
cb=fig.colorbar(im,cax=fig.add_axes([.19,.13,.65,.025]),orientation='horizontal',extend='max');cb.set_label('PM2.5 [µg/m³]',labelpad=1);cb.ax.tick_params(pad=1,length=2);ax.get_xticklabels()[-1].set_ha('right');ax.get_xticklabels()[0].set_ha('left')
cb.set_ticks([0,100,200,300,400])
for panel in [ax]+[a for a in fig.axes if a not in [ax,cb.ax]]:
 for spine in panel.spines.values():spine.set_visible(True);spine.set_color('black');spine.set_linewidth(.45)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'PM25_single_column.{ext}',dpi=600,bbox_inches='tight',pad_inches=.02)
