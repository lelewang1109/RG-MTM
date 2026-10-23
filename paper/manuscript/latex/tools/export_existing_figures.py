"""Re-export saved publication drawings; no field extraction or layout optimization.
Run with the project .venv Python from the full MergeTreeMaps workspace.
The source package already includes all exported figures needed by LaTeX.
"""
from pathlib import Path
import sys,json,hashlib,runpy
ROOT=Path(__file__).resolve().parents[4]
PAPER=Path(__file__).resolve().parents[1]
CODE=ROOT/'code'
OUT=PAPER/'figures'
sys.path[:0]=[str(CODE/'src'),str(CODE/'analysis'),str(CODE/'experiments/publication2027')]
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import figstyle as fs
import layout_figures as layout
import domain_filling_figures as domain
from dataset_suite import PAPER_DATASETS,REAL_DATASETS,LABELS
from visualization import metrics
fs.apply()
plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'rgmtm-integrated-20261016','pdf.fonttype':42})
record=json.loads((CODE/'results/publication2027/figure_data/domain_filling_example.json').read_text())
profiles=[{k:np.array(v) if isinstance(v,list) else v for k,v in r.items()} for r in record['profiles']]
# Draw the archived sample profiles rather than rerunning their construction.
domain.render_checked=lambda frame:profiles
domain.node_correspondence=lambda frame,profile:record['node_correspondence']
manifest={'scope':'Existing saved data and plotting geometry; editorial labels and vector export only; no new numerical experiments','figures':[],'source_sha256':{}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(fig,stem,*args):
 stem='rgmtm_'+stem.removeprefix('fig_')
 if stem=='rgmtm_teaser_focus':
  fig.axes[2].set_title('(b) RG-MTM-P: preserve hierarchy')
  fig.axes[4].set_title('(c) RG-MTM-R: improve alignment')
  for ax in [fig.axes[2],fig.axes[4]]:ax.set_ylabel('anchor error (% L)')
 if stem=='rgmtm_diagnosis_tradeoff':
  for ax in fig.axes[4:]:ax.set_ylabel('mean optimum (% L)')
 if stem=='rgmtm_topology_motion_tradeoff':
  fig._suptitle.set_text('Motion error and merge-level cost at fixed operating settings')
 for ext in ['pdf','png','svg']:
  fig.savefig(OUT/f'{stem}.{ext}',dpi=300,bbox_inches='tight',facecolor='white')
 manifest['figures'].append({'stem':stem,'files':{ext:sha(OUT/f'{stem}.{ext}') for ext in ['pdf','png','svg']}})
 plt.close(fig)
 print(stem,flush=True)
layout.save=save;domain.save=save
arrays={}
for n in ['era5','olr']:
 f=CODE/f'results/publication2027/figure_data/{n}_render.npz'
 m=json.loads(f.with_suffix('.json').read_text());assert sha(f)==m['arrays_sha256']
 with np.load(f,allow_pickle=False) as z:arrays[n]={k:z[k] for k in z.files}
 manifest['source_sha256'][str(f.relative_to(ROOT))]=sha(f)
layout.teaser(arrays['era5'])
layout.diagnosis_frontier()
layout.motion_cost()
manifest['case_selection']=layout.cases(arrays)
frame=domain.example();np.testing.assert_allclose(frame.values,record['values'])
domain.detail(frame,profiles)
ev=json.loads((CODE/'results/eval_projection.json').read_text())
class Export:
 def save(self,*args):save(*args)
ex=Export()
metrics.motion_errors(ev,PAPER_DATASETS,LABELS,ex)
metrics.topology_motion(ev,REAL_DATASETS,LABELS,ex)
metrics.neighbourhoods(ev,PAPER_DATASETS,LABELS,ex)
metrics.motion_sensitivity(ev,PAPER_DATASETS,LABELS,ex)
# The original bisector drawing only exports PNG/SVG; add PDF from that same Figure.
original_save=Figure.savefig
def save_bisector(self,path,*args,**kwargs):
 result=original_save(self,path,*args,**kwargs)
 if str(path).endswith('.svg'):original_save(self,Path(path).with_suffix('.pdf'),*args,**kwargs)
 return result
Figure.savefig=save_bisector
old_argv=sys.argv
try:
 sys.argv=['rgmtm_bisector_figure.py','--out',str(OUT)]
 runpy.run_path(str(CODE/'experiments/publication2027/rgmtm_bisector_figure.py'),run_name='__main__')
finally:
 sys.argv=old_argv;Figure.savefig=original_save
stem='rgmtm_bisector_absolute_position'
manifest['figures'].append({'stem':stem,'files':{ext:sha(OUT/f'{stem}.{ext}') for ext in ['pdf','png','svg']}})
for f in [CODE/'tools/build_rgmtm_figures.py',CODE/'experiments/publication2027/layout_figures.py',CODE/'experiments/publication2027/domain_filling_figures.py',CODE/'experiments/publication2027/rgmtm_bisector_figure.py',CODE/'results/eval_projection.json',CODE/'results/attainable_era5.json',CODE/'results/attainable_wildfire.json',CODE/'results/publication2027/figure_data/domain_filling_example.json',CODE/'results/publication2027/bisector_control/bisector_highres_x_three_methods.npz']:
 manifest['source_sha256'][str(f.relative_to(ROOT))]=sha(f)
manifest['user_supplied_figures']=[
 {'stem':'rgmtm_pipeline_v22','source':'figures/source/RG-MTM_pipeline_v22_editable.pptx','source_sha256':sha(OUT/'source/RG-MTM_pipeline_v22_editable.pptx'),'export':'figures/rgmtm_pipeline_v22.pdf','export_sha256':sha(OUT/'rgmtm_pipeline_v22.pdf'),'conversion':'LibreOffice PDF export from original supplied PPTX; source unchanged'},
 {'stem':'rgmtm_reference_direction','source':'User attachment Unknown-20.png','export':'figures/rgmtm_reference_direction.png','sha256':sha(OUT/'rgmtm_reference_direction.png'),'conversion':'Unchanged PNG copy'}]
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
