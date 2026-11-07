from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LinearSegmentedColormap
from matplotlib.patches import Rectangle
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[2];D=P/'experiments_ratio_p_20261104/results/Ring';R=P/'figures/source/readability_20261106';C=P/'figures/source/ring_compact_comparison_20261106'
F=np.load(D/'preparation/fields.npy');maps=[-np.load(R/f'ring_reference_{e}.npz')['map'] for e in ['0','0.2']]
# Load only the canonical curve implementation, avoiding unrelated package imports.
curve_file=P.parents[1]/'RG-MTM/code/src/rgmtm/baselines/space_filling.py';spec=importlib.util.spec_from_file_location('ring_space_filling',curve_file);sf=importlib.util.module_from_spec(spec);spec.loader.exec_module(sf)
orders={m:sf.sample_order(F.shape[1:],m) for m in ['Hilbert','Morton']}
for m in orders:assert np.array_equal(np.sort(orders[m]),np.arange(196))
baselines={m:sf.linearize(F,m) for m in orders}
assert all(m.shape==(196,40) and np.isfinite(m).all() for m in maps+list(baselines.values()))
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':9,'axes.titlesize':9,'axes.labelsize':9,'xtick.labelsize':9,'ytick.labelsize':9,'axes.linewidth':.6,'pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(3.5,2.9));norm=Normalize(0,float(F.max()));cm=LinearSegmentedColormap.from_list('ring_yellow_brown',['#ffffff','#fffbd5','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506']);stages=[0,20,39]
# Supplied baseline panels: retain the scientific image content, exclude frame pixels.
reference=np.asarray(Image.open(C/'supplied_hilbert_morton.png').convert('RGB'))
baselines={'Hilbert':reference[35:374,40:315], 'Morton':reference[35:374,378:653]}
layout=[(.16,.69,maps[0],'(a) Ours: 0%',False),(.16,.425,maps[1],'(b) Ours: 20%',True),(.615,.69,baselines['Hilbert'],'(c) Hilbert',False),(.615,.425,baselines['Morton'],'(d) Morton',True)]
for k,(x,y,m,title,bottom) in enumerate(layout):
 ax=fig.add_axes([x,y,.33,.16])
 if k<2:im=ax.imshow(m,origin='lower',aspect='auto',extent=[-.5,39.5,0,1],cmap=cm,norm=norm,interpolation='bilinear',interpolation_stage='data',rasterized=True)
 else:
  ax.imshow(m,origin='upper',aspect='auto',extent=[-.5,39.5,0,1],interpolation='nearest',rasterized=True)
  # Replace only the original printed method name; the early-time corner is white.
  ax.add_patch(Rectangle((-.5,.905),14.8,.095,fc='white',ec='none',lw=0))
 for sp in ax.spines.values():sp.set_visible(True)
 [sp.set_color('black') for sp in ax.spines.values()];[sp.set_linewidth(.55) for sp in ax.spines.values()]
 ax.set(xticks=[0,39] if bottom else [],yticks=[0,1] if k<2 else [],ylim=(0,1));ax.tick_params(length=2,pad=1)
 ax.set_title(title,loc='left',pad=4)
fig.text(.025,.64,'Normalized position',rotation=90,va='center',fontsize=9)
fig.text(.77,.34,'Time step',ha='center',fontsize=9)
cax=fig.add_axes([.58,.953,.36,.018]);cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[0,6,12]);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=9,length=2,pad=1);fig.text(.29,.949,'Scalar',fontsize=9)

for k,t in enumerate(stages):
 ax=fig.add_axes([.12+k*.295,.05,.235,.23]);ax.imshow(F[t],origin='lower',extent=[0,210,0,210],cmap=cm,norm=norm,interpolation='nearest',rasterized=True);ax.set(xticks=[],yticks=[]);[sp.set_visible(True) for sp in ax.spines.values()];ax.set_title(f't = {t}',pad=4)
for ext in ['pdf','png','svg']:fig.savefig(P/f'figures/anchor_ring_result.{ext}',dpi=500,facecolor='white')
np.savez_compressed(C/'canonical_curve_maps_not_displayed.npz',**{m:sf.linearize(F,m) for m in orders},**{m+'_order':v for m,v in orders.items()})
proto={'layout':'single column; upper left AnchorMTM pair; upper right Hilbert/Morton; snapshots below; thin individual panel frames; no outer or group frames','epsilons':[0,.2],'guidance_strengths':[0,1],'zero_mode':'neutral central targets; spatial guidance off; exact topology','positive_mode':'fixed -128.7356 degree projected targets; spatial guidance on; epsilon .2','comparison':'paired configurations, not an epsilon-only ablation','reference_protocol':str(R/'ring_reference_protocol.json'),'frames':40,'raster_length':196,'snapshots':stages,'source_grid':[14,14],'curves':'canonical complete sample permutations; x=columns,y=rows; pad to16 square then discard out-of-domain; no rotation/reflection/reversal search','curve_code_sha256':hashlib.sha256(curve_file.read_bytes()).hexdigest(),'source_fields_sha256':hashlib.sha256((D/'preparation/fields.npy').read_bytes()).hexdigest(),'common_scalar_range':[0,float(F.max())],'font':'Times New Roman','font_size_pt':9,'interpolation':'bilinear scalar interpolation for temporal display only; snapshot original samples','curve_y_axis':'normalized traversal rank; AnchorMTM y is normalized layout coordinate; neither inferred as identical physical coordinates','no_screenshot_data_tracing':True,'baseline_display_source':'supplied_hilbert_morton.png; cropped frame; original method name replaced; no numerical claims from screenshot','color_scale_scope':'ours and source snapshots share calibrated scalar scale; supplied baseline panels retain original colors'}
(O/'provenance.json').write_text(json.dumps(proto,indent=2));(C/'provenance.json').write_text(json.dumps(proto,indent=2))
print('Ring comparison figure written')
