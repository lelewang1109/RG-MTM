"""Generate provenance-aware CSVs and booktabs tables; ranks are automatic."""
from pathlib import Path
import json,csv,hashlib,math
import numpy as np
O=Path(__file__).resolve().parents[1];W=O.parents[2]
DATASETS=['Gaussian','Ring','Wildfires','Storms']
METHODS=['TMTM','ST-MTM Temporal','AnchorMTM Exact','AnchorMTM Balanced']
PUB={
 'Gaussian':[(.25,.77,55.56),(.06,1.,32.56),(.06,1.,31.87)],
 'Ring':[(.28,.68,12.23),(.20,.92,48.64),(.21,.88,27.92)],
 'Wildfires':[(.44,.88,7487.67),(.25,.91,7249.03),(.24,.91,3895.33)],
 'Storms':[(.34,.71,164.14),(.19,.89,85.44),(.21,.94,36.24)]}

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def table(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r));p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:('N/A' if v is None else v) for k,v in r.items()} for r in rows])

def rank(rows):
 out={};audit=[]
 for ds in DATASETS:
  for metric in ['SNS','TW','TD','NPE']:
   groups={}
   for r in rows:
    if r['Dataset']!=ds:continue
    value=r[metric];group=r[metric+'_rank_group']
    if value is not None and group is not None:groups.setdefault(group,[]).append(r)
   for group,rr in groups.items():
    if len(rr)<2:continue
    precision=2 if metric=='TD' else 3 if metric in ['SNS','TW'] else 4
    distinct=sorted(set(round(r[metric],precision) for r in rr),reverse=metric=='TW')
    for r in rr:
     value=round(r[metric],precision);place=distinct.index(value)+1;style='best' if place==1 else 'second' if place==2 else 'normal'
     out[(ds,r['Method'],metric)]=style;audit.append(dict(Dataset=ds,Method=r['Method'],Metric=metric,Group=group,DisplayedValue=value,Rank=place,Style=style))
 return out,audit

def display(row,metric,styles):
 value=row[metric]
 if value is None:return r'\mathrm{N/A}'
 digits=2 if metric=='TD' else 3 if metric in ['SNS','TW'] else 4
 s=f'{value:.{digits}f}';style=styles.get((row['Dataset'],row['Method'],metric),'normal')
 if style=='best':s=r'\mathbf{'+s+'}'
 elif style=='second':s=r'\underline{'+s+'}'
 return s

def build():
 params=read(O/'config/paper_parameters.json');rows=[];measured=[];npe=[];topology=[];runtime=[];aparams=[];selection=[];source_audit=[]
 for ds in DATASETS:
  root=O/'results'/ds;inp=read(root/'input_audit.json');sel=read(root/'selection.json');cfg=params[ds];p=inp['parameters']
  source_audit.append(dict(Dataset=ds,nx=cfg['nx'],ny=cfg['ny'],T=cfg['T'],p_number=cfg['p'],p_percent=cfg['p'],p_fraction=cfg['p']/100,L=cfg['L'],TW_k=cfg['k'],features_min=inp['features_min'],features_max=inp['features_max'],author_input_identical_confirmed=False,protocol=inp['protocol']['reconstruction']))
  for s in sel['candidates']:
   selection.append(dict(Dataset=ds,epsilon=s['epsilon'],validation_frames=len(sel['validation_frames']),success=s['success'],NPE=s.get('NPE'),SNS=s.get('SNS'),TW=s.get('TW'),TD=s.get('TD'),topology_mean=s.get('topology_mean'),topology_max=s.get('topology_max'),rendered_budget_violations=s.get('rendered_budget_violations'),eligible=s.get('eligible',False),validation_gain=s.get('validation_gain'),NPE_norm=s.get('NPE_norm'),SNS_norm=s.get('SNS_norm'),J=s.get('J'),J_min=sel['J_min'],near_optimal_J_tolerance=sel['near_optimal_J_tolerance'],selected=bool(s['epsilon']==sel['epsilon']),error=json.dumps(s.get('error',''),ensure_ascii=False)))
  for i,name in [(0,'TMTM'),(2,'ST-MTM Temporal')]:
   mode=['tmtm','base','temporal'][i];s=read(root/'baseline_npe'/(mode+'.json'));sns,tw,td=PUB[ds][i]
   row=dict(Dataset=ds,Method=name,SNS=sns,TW=tw,TD=td,NPE=s.get('NPE'),t_opt=None,t_total=None,TD_measured_local=None,metrics_source='published',NPE_source='local reconstructed shared input',SNS_rank_group='dataset_reported_numeric_summary',TW_rank_group='dataset_reported_numeric_summary',TD_rank_group='published_TD',NPE_rank_group='local_shared_input',TW_k=cfg['k'],TW_valid_frames=None,NPE_valid_frames=s.get('frames'),cross_source_comparison='descriptive numeric summary; author inputs not verified identical',TD_unit='as reported, unconfirmed; NOT cross-ranked',epsilon=None,success=s.get('success'),note=s.get('error',s.get('note','')));rows.append(row);npe.append(s)
  for label in ['Exact','Balanced']:
   path=root/label;s=read(path/'summary.json');success=s['success'];epsilon=s.get('epsilon');name='AnchorMTM '+label
   same=False
   if label=='Balanced' and success:
    x=np.load(root/'Exact/map.npz')['map'];y=np.load(path/'map.npz')['map'];same=bool(np.array_equal(x,y))
    if same:same=all(np.array_equal(a['pixel_x'],b['pixel_x']) for a,b in zip(read(root/'Exact/layouts.json'),read(path/'layouts.json')))
   row=dict(Dataset=ds,Method=name,SNS=s.get('SNS'),TW=s.get('TW'),TD=s.get('TD'),NPE=s.get('NPE'),t_opt=s.get('t_opt'),t_total=s.get('t_total'),TD_measured_local=s.get('TD'),metrics_source='local',NPE_source='local reconstructed shared input',SNS_rank_group='dataset_reported_numeric_summary',TW_rank_group='dataset_reported_numeric_summary',TD_rank_group='local_normalized_TD',NPE_rank_group='local_shared_input',TW_k=cfg['k'],TW_valid_frames=s.get('TW_valid_frames'),NPE_valid_frames=s.get('frames'),cross_source_comparison='descriptive numeric summary; author inputs not verified identical',TD_unit='full_canvas_normalized_sum; NOT cross-ranked with quote',epsilon=epsilon,success=success,note='positive budget reserved; identical output to Exact' if label=='Balanced' and same else '' if success else json.dumps(s.get('error'),ensure_ascii=False));rows.append(row)
   measured.append(dict(Dataset=ds,Method=name,SNS=s.get('SNS'),TW=s.get('TW'),TD=s.get('TD'),NPE=s.get('NPE'),TW_k=cfg['k'],TW_valid_frames=s.get('TW_valid_frames'),SNS_valid_frames=s.get('SNS_valid_frames'),frames=cfg['T'],epsilon=epsilon,validation_NPE=s.get('validation_NPE'),assessment_NPE=s.get('assessment_NPE'),selection_status=sel['status'] if label=='Balanced' else 'strict endpoint',same_output_as_Exact=same if label=='Balanced' else None,success=success))
   lay=read(path/'layouts.json') if (path/'layouts.json').exists() else [];repaired=sum(r.get('raster_error',{}).get('integer_rounding',{}).get('repaired',False) for r in lay);maxround=max([r.get('raster_error',{}).get('integer_rounding',{}).get('max_coordinate_rounding_error_pixels',0.) for r in lay]+[0.])
   topo=dict(Dataset=ds,Method=name,epsilon=epsilon,success=success,frames=cfg['T'],actual_topology_mean=s.get('topology_mean'),actual_topology_max=s.get('topology_max'),continuous_budget_violations=s.get('continuous_budget_violations'),rendered_budget_violations=s.get('rendered_budget_violations'),collapsed_anchor_frames=s.get('collapsed_anchor_frames'),repaired_raster_frames=repaired,max_joint_rounding_error_pixels=maxround,scope='full fixed leaf-label merge matrix incl diagonal; no full augmented-root-height certificate');topology.append(topo)
   runtime.append(dict(Dataset=ds,Method=name,epsilon=epsilon,t_opt=s.get('t_opt') if success else None,t_total=s.get('t_total'),t_preprocess=s.get('t_preprocess'),t_topology=s.get('t_topology'),t_features_reference=s.get('t_features_reference'),method_seconds=s.get('method_seconds'),failure_elapsed=s.get('failure_elapsed'),repeats=s.get('repeats',0),cache_used_for_timing=s.get('cache_used_for_reported_timing'),BLAS_threads=1,native_TTK_threads=1,native_workers=1,HiGHS_threads='auto/default',hardware='Apple M4',success=success))
  bs=read(root/'Balanced/summary.json');chosen=next(x for x in sel['candidates'] if x['epsilon']==sel['epsilon']);bm=next(x for x in measured if x['Dataset']==ds and x['Method']=='AnchorMTM Balanced')
  aparams.append(dict(Dataset=ds,epsilon_Balanced=sel['epsilon'],actual_NMLEmax=bs.get('topology_max'),actual_NMLEmean=bs.get('topology_mean'),selection_status=sel['status'],maximum_allowed_actual_topology_error=sel['epsilon'],J_validation=chosen['J'],NPE_norm_validation=chosen['NPE_norm'],SNS_norm_validation=chosen['SNS_norm'],near_optimal_J_tolerance=.01,same_output_as_Exact=bm['same_output_as_Exact'],L_pixels=cfg['L'],p_percent=cfg['p'],canvas_extent=p['canvas'],width_scale=p['width_scale'],gap=p['gap'],rho=p['rho'],beta0=p['extra_budget'],reference_weight=p['reference_weight'],geometry_weight=p['geometry_weight'],motion_weight=p['motion_weight'],eccentricity_weight=p['eccentricity_weight'],validation_frames=len(sel['validation_frames']),assessment_frames=len(sel['assessment_frames'])))
 table(O/'comparison_final.csv',rows);table(O/'anchor_metrics_measured.csv',measured);table(O/'anchor_parameters.csv',aparams);table(O/'anchor_runtime.csv',runtime);table(O/'baseline_npe.csv',npe);table(O/'topology_validation.csv',topology);table(O/'balanced_selection.csv',selection);table(O/'input_audit.csv',source_audit)
 styles,rank_audit=rank(rows);table(O/'ranking_audit.csv',rank_audit)
 table(O/'ranking_exclusions.csv',[dict(Dataset=r['Dataset'],Method=r['Method'],Metric='TD',Reason='TD ranked within published or normalized-local unit group only, not across units') for r in rows])
 # Four methods; both Anchor modes have separate optimization/total time columns.
 tex=[r'\begin{table*}[t]',r'\centering',r'\caption{Quantitative comparison. Headers p denote published Table~1 scores; n denotes local full-canvas-normalized TD. SNS/TW/NPE best and second values are computed over the four displayed methods per dataset, with ties. These are descriptive numerical comparisons because author and reconstructed inputs are not verified identical. TD best/second are marked separately within the published and local unit groups; cross-unit TD ranking is not established. Both time columns are measured seconds (one run).}',r'\label{tab:quantitative-final}',r'\setlength{\tabcolsep}{1.5pt}',r'\renewcommand{\arraystretch}{1.2}',r'\scriptsize',r'\resizebox{\textwidth}{!}{%',r'\begin{tabular}{l'+'r'*20+'}',r'\toprule',r'\multirow{2}{*}{Dataset} & '+ ' & '.join(r'\multicolumn{'+str(4 if i<2 else 6)+r'}{c}{'+m.replace('AnchorMTM ','AnchorMTM~')+'}' for i,m in enumerate(METHODS))+r' \\',r'\cmidrule(lr){2-5} \cmidrule(lr){6-9} \cmidrule(lr){10-15} \cmidrule(lr){16-21}', ' & '+' & '.join((r'SNS$\downarrow^{\rm p}$ & TW$\uparrow^{\rm p}$ & TD$\downarrow^{\rm p}$ & NPE$\downarrow$' if i<2 else r'SNS$\downarrow$ & TW$\uparrow$ & TD$\downarrow^{\rm n}$ & NPE$\downarrow$ & $t_{\rm opt}$ & $t_{\rm total}$') for i in range(4))+r' \\',r'\midrule']
 for ds in DATASETS:
  cells=[]
  for m in METHODS:
   row=next(r for r in rows if r['Dataset']==ds and r['Method']==m)
   cells += ['$'+display(row,metric,styles)+'$' for metric in ['SNS','TW','TD','NPE']]
   if row['metrics_source']=='local':
    tf=lambda v:f'{v:.3f}' if v<10 else f'{v:.2f}'
    cells += [tf(row['t_opt']),tf(row['t_total'])]
  tex.append(ds+' & '+' & '.join(cells)+r' \\')
 tex +=[r'\midrule',r'\multicolumn{21}{p{\dimexpr\textwidth-3pt\relax}}{Ring: both local TW values use only 1 eligible frame out of 40 ($k=3$); other local TW values cover all frames. No coverage count is appended to a metric cell. TD$^{\rm n}$ sums matched-anchor displacement divided by the fixed full canvas span.} \\',r'\bottomrule',r'\end{tabular}',r'}',r'\end{table*}'];(O/'tables').mkdir(exist_ok=True);(O/'tables/quantitative_comparison.tex').write_text('\n'.join(tex)+'\n')
 tex=[r'\begin{table*}[t]',r'\centering',r'\caption{AnchorMTM parameter settings. Exact uses $\varepsilon=0$ and $\varepsilon_0=0$; Balanced always reserves a positive budget, chosen by the fixed validation score $J$. Attained NMLEmax is checked against nominal $\varepsilon$; the fixed internal numerical allowance $10^{-7}$ does not relax that final check. A zero attained error is not a zero reserved budget. $N$ is raster length and $L$ the physical projection span. Width scale $s$, gap $g$ and slack $\beta_0$ follow fixed rules. Objective weights $(w_q,w_g,w_m,w_e)=(4,1,0.5,0.1)$ and $\rho=0.5$.}',r'\label{tab:anchor-parameters-final}',r'\small',r'\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{lrrrrrrrl}',r'\toprule',r'Dataset & $\varepsilon_{\mathrm{Bal}}$ & Attained max & $N$ & $L$ & $s$ & $g$ & $\beta_0$ & Output \\',r'\midrule']
 for i,x in enumerate(aparams):
  status='Same as Exact' if x['same_output_as_Exact'] else 'J selected'
  tex.append(f"{x['Dataset']} & {100*x['epsilon_Balanced']:g}\\% & {100*x['actual_NMLEmax']:.4f}\\% & {x['L_pixels']} & {x['canvas_extent']:.3f} & {x['width_scale']:.5g} & {x['gap']:.4g} & {x['beta0']:.4g} & {status}"+r' \\')
 tex +=[r'\bottomrule',r'\end{tabular}',r'\end{table*}'];(O/'tables/anchor_parameter_settings.tex').write_text('\n'.join(tex)+'\n')
 # Runtime CSV retained; timings are columns of Table1, not a separate table.
 dump(O/'assembled.json',dict(comparison=rows,measured=measured,parameters=aparams,runtime=runtime,topology=topology,input_audit=source_audit))
 return rows,measured,aparams,runtime,topology,source_audit

if __name__=='__main__':build()
