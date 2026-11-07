from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
O=Path(__file__).resolve().parent;P=O.parents[2];W=P.parents[1];S=P/'figures/source/storms_budget_profiles';A=W/'output/storms_hourly_anomaly_fine_20261030'
E=json.loads((O/'original_position_evidence.json').read_text());sel=[next(x for x in E if x['epsilon']==e) for e in [0,.05,.1,.2]]
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':9,'axes.titlesize':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.linewidth':.55})
f=plt.figure(figsize=(7.15,2.5));canvas=f.add_axes([0,0,1,1]);canvas.set(xlim=(0,1),ylim=(0,1));canvas.axis('off')
# Use the original scalar backgrounds, preserving their approved blue/orange transfer function.
from PIL import Image
for k,e in enumerate([0,.02,.05,.1,.2]):
 ax=f.add_axes([.035+k*.195,.535,.175,.365]);img=Image.open(O/f'assets/Storms_{e:g}_main_aspect_215_140.png');ax.imshow(img,aspect='auto');ax.set(xticks=[],yticks=[]);ax.set_title(f'({k+1}) ε = {100*e:g}%',pad=4)
# The lower row explains modules; it does not fabricate baseline maps.
baseline=np.load(O/'baseline_maps.npz')
protocol=json.loads((O/'baseline_protocol.json').read_text());source=json.loads((O/'reference_input_meta.json').read_text());assert protocol['field_sha256']==source['field_sha256']
for x,key,title in [(.25,'TMTM','(6) TMTM'),(.70,'STMTM','(7) ST-MTM')]:
 ax=f.add_axes([x,.085,.28,.265]);ax.imshow(baseline[key][:,355:461],origin='lower',aspect='auto',extent=[355,460,0,1],cmap='RdBu_r',vmin=-35,vmax=35,interpolation='bilinear',interpolation_stage='data',rasterized=True);ax.set(xticks=[355,460],yticks=[]);ax.tick_params(length=2,pad=1);ax.set_title(title,pad=4)
canvas.annotate('',xy=(.25,.22),xytext=(.19,.535),arrowprops=dict(arrowstyle='->',lw=.9,connectionstyle='angle,angleA=-90,angleB=180,rad=0'))
canvas.text(.025,.29,'(8) Replace placement\nby overlap alignment',fontsize=9,ha='left',va='center');canvas.text(.025,.17,'Fixed spatial anchoring off',fontsize=8,color='#555555')
canvas.annotate('',xy=(.70,.22),xytext=(.53,.22),arrowprops=dict(arrowstyle='->',lw=.9))
canvas.text(.615,.45,'(9) Replace / add',ha='center',fontsize=9);canvas.text(.615,.34,'Geometry ordering\n+ spatial/temporal\nplacement',ha='center',va='center',fontsize=8)
canvas.text(.50,.006,'Time step: shared window 355–460; common scalar scale −35 to 35 hPa.',ha='center',fontsize=8,color='#555555')
for ext in ['pdf','png','svg']:f.savefig(P/f'figures/anchor_storms_budget_maps.{ext}',dpi=400,facecolor='white')
(O/'evidence.json').write_text(json.dumps(dict(budgets=[0,.02,.05,.1,.2],frame_window=[355,460],curve_panel=False,baseline_protocol='baseline_protocol.json',same_input=True,scalar_scale=[-35,35],lower_panels='actual TMTM/ST-MTM maps from local implementations with disclosed adapters',module_arrows='actual layout-stage replacements/additions; not exact algebraic equivalence'),indent=2))
