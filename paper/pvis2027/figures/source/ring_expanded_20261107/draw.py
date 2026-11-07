from pathlib import Path
import json,hashlib,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LinearSegmentedColormap
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[2];D=P/'experiments_ratio_p_20261104/results/Ring';F=np.load(D/'preparation/fields.npy');eps=[0,.02,.05,.1,.2];ours=[-np.load(O/f'ring_reference_{e:g}.npz')['map'] for e in eps];B=np.load(O/'baseline_maps.npz');ref=np.asarray(Image.open(P/'figures/source/ring_compact_comparison_20261106/supplied_hilbert_morton.png').convert('RGB'))
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':9,'axes.titlesize':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'axes.linewidth':.55,'pdf.fonttype':42,'svg.fonttype':'none'})
cm=LinearSegmentedColormap.from_list('ring_white_brown',['#ffffff','#fffbd5','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506']);norm=Normalize(0,float(F.max()));fig=plt.figure(figsize=(3.5,3.6))
for k,(e,m,y) in enumerate(zip(eps,ours,[.81,.675,.54,.405,.27])):
 ax=fig.add_axes([.155,y,.33,.09]);im=ax.imshow(m,origin='lower',extent=[-.5,39.5,0,1],aspect='auto',cmap=cm,norm=norm,interpolation='bilinear',interpolation_stage='data',rasterized=True);ax.set_title(f'ε = {100*e:g}%',loc='left',pad=3);ax.set(yticks=[0,1],xticks=[0,39] if k==4 else [],ylim=(0,1));ax.tick_params(length=1.5,pad=1)
from matplotlib.patches import Rectangle
fig.add_artist(Rectangle((.11,.22),.40,.74,transform=fig.transFigure,fill=False,ec='black',lw=.65,ls='--'))
fig.text(.32,.955,'AnchorMTM',ha='center',fontsize=9,bbox=dict(fc='white',ec='none',pad=1))
right=[('Hilbert',ref[35:374,40:315],True),('Morton',ref[35:374,378:653],True),('TMTM',B['TMTM'],False),('ST-MTM',B['STMTM'],False)]
for k,((name,m,screenshot),y) in enumerate(zip(right,[.81,.63,.45,.27])):
 ax=fig.add_axes([.615,y,.33,.09]);ax.imshow(m,origin='upper' if screenshot else 'lower',extent=[-.5,39.5,0,1],aspect='auto',cmap=None if screenshot else cm,norm=None if screenshot else norm,interpolation='nearest' if screenshot else 'bilinear',rasterized=True)
 if screenshot:
  from matplotlib.patches import Rectangle
  ax.add_patch(Rectangle((-.5,.905),14.8,.095,fc='white',ec='none',lw=0))
 ax.set(yticks=[],xticks=[0,39] if k==3 else [],ylim=(0,1));ax.tick_params(length=1.5,pad=1);ax.set_title(name,loc='left',pad=3)
fig.text(.025,.59,'Normalized position',rotation=90,va='center',fontsize=9)
cax=fig.add_axes([.64,.979,.30,.01]);cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[0,6,12]);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=8,length=1.5,pad=1)
for k,t in enumerate([0,10,20,30,39]):
 ax=fig.add_axes([.10+k*.178,.025,.16,.15]);ax.imshow(F[t],origin='lower',extent=[0,210,0,210],cmap=cm,norm=norm,interpolation='nearest',rasterized=True);ax.set(xticks=[],yticks=[]);ax.set_title(f't = {t}',pad=3)
fig.text(.97,.235,'t',ha='right',fontsize=8)
for ext in ['pdf','png','svg']:fig.savefig(P/f'figures/anchor_ring_result.{ext}',dpi=500,facecolor='white')
(O/'provenance.json').write_text(json.dumps(dict(ours_epsilons=eps,zero_configuration='guidance off, neutral central targets; exact topology',positive_configuration='fixed physical reference direction -128.7356 degrees; guidance on',right_panels=['supplied Hilbert','supplied Morton','same-input local TMTM','same-input local ST-MTM'],same_field_hash=hashlib.sha256((D/'preparation/fields.npy').read_bytes()).hexdigest(),frames=40,raster_length=196,snapshots=[0,20,39],font='Times New Roman 9pt',main_tables_unchanged=True,color_key_scope='computed maps and snapshots; supplied curve screenshots retain original colors'),indent=2))
