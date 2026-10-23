"""Replace January rows by verified annual records in current numeric tables."""
import json,math,numpy as np

def apply(result,load):
 base='results/pm25_2000/';r=load(base+'replicate_pm25_2000.json');c=r['certificate'];e=load(base+'eval_projection.json')['pm25_2000'];p=load(base+'final_performance.json')['pm25_2000'];f=load(base+'filling.json')['pm25_2000'];a=load(base+'attainable_pm25_2000.json');std=load(base+'standard_metrics.json')['results'];tasks=load(base+'reference_tasks.json')
 def replace_rows(name,rows):
  lines=result['tables/'+name+'.tex'].splitlines();out=[];done=False
  for line in lines:
   if line.startswith('PM2.5 &'):
    if not done:out.extend(rows);done=True
   else:out.append(line)
  assert done,name;result['tables/'+name+'.tex']='\n'.join(out)+'\n'
 def row(v):return ' & '.join(map(str,v))+r'\\'
 replace_rows('datasets_supp',[row(['PM2.5','2000-01-01--2000-12-31',366,r'$49\times49$','1--7','Split','100 km'])])
 result['tables/datasets_supp.tex']=result['tables/datasets_supp.tex'].replace('278 frames','614 frames').replace('January PM2.5 is exploratory.','PM2.5 uses the full year; January remains an exploratory historical control.')
 F=100*np.mean(c['F_per_frame']);H=100*np.mean(c['H_per_frame']);replace_rows('certificates_supp',[row(['PM2.5',366,'1--7',f'{F:.2f}',f'{H:.2f}',f'{F+H:.2f}','36/366'])])
 methods=[('TMTM','TMTM'),('ST-MTM','ST-MTM'),('Hilbert','Hilbert'),('Morton','Morton'),('Packed sort','q-sort (packed)'),('RG-MTM-P','A'),('RG-MTM-R, $20\\%$','R 20%'),('RG-MTM-R, $\\infty$','R inf'),('Exact projection','oracle q')]
 replace_rows('hidden_quality_supp',[row(['PM2.5',label,*[f"{e['hidden'][key][k]:.3f}"for k in ['order_flip_rate','jitter','stress','nn_preservation']]])for label,key in methods])
 proxy={x['method']:x for x in e['proxy']if x['k']==2 and x['eps']==.02};fill20=next(x for x in f if x['cap']==.2)
 replace_rows('motion_supp',[row(['PM2.5',95,*[f"{100*proxy[k]['error']:.1f}"for k in ['TMTM','ST-MTM','Hilbert','Morton','q-sort (packed)','A','R 20%']],f"{100*fill20['D_opt_share']:.1f}"])])
 replace_rows('standard_metrics_supp',[row(['PM2.5',x['method'],f"{x['SNS']:.4f}",f"{x['TW1']:.4f}",f"{x['TD']:.4f}",x['SNS_frames'],x['TW1_frames']])for x in std])
 rs={x['method']:x for x in tasks['ranks']};ms={x['method']:x for x in tasks['motion']if x['scope']=='all_three_classes'}
 replace_rows('standard_tasks_supp',[row(['PM2.5',x['method'],f"{x['Kendall_tau_b']:.4f}",f"{x['Spearman_rho']:.4f}",f"{100*ms[x['method']]['balanced_accuracy']:.1f}",f"{100*ms[x['method']]['macro_F1']:.1f}",ms[x['method']]['events']])for x in tasks['ranks']])
 result['tables/standard_tasks_supp.tex']=result['tables/standard_tasks_supp.tex'].replace('PM2.5 has only ten windows.','Annual PM2.5 has 123 windows (95 clear).')
 # The expanded table includes several distinct diagnostics and historical controls.
 lines=result['tables/supplement_generated.tex'].splitlines();section='';output=[];done=set()
 for line in lines:
  if line.startswith('\\caption'):section=line
  if not line.startswith('PM2.5 &'):output.append(line);continue
  if 'Expanded numerical' in section:
   if section in done:continue
   done.add(section)
   for label,key in [('TMTM','TMTM'),('ST-MTM','ST-MTM'),('Hilbert','Hilbert'),('Morton','Morton'),('RG-MTM-P (ours)','A'),('RG-MTM-R (ours)','R 20%'),('Packed sort','q-sort (packed)'),('Fixed X (control)','fixed-X anchored'),('Exact projection','oracle q')]:
    d=e['dstar'].get(key);output.append(row(['PM2.5',label,f"{100*p['methods'][key]['mean']:.2f}",f"{100*d['mean_share']:.2f}"if d else('--'if key=='oracle q'else'0.00'),f"{100*d['max_share']:.2f}"if d else('--'if key=='oracle q'else'0.00'),f"{e['hidden'][key]['stress']:.3f}",95,f"{100*proxy[key]['error']:.1f}"]))
  elif 'exact-frontier' in section:
   t=a['tightness'];output.append(row(['PM2.5',7,f"{t['tight_within_half_pixel']}/{t['breakpoints']}",f"{100*t['gap_max']:.2f}",'366/366','0.00']))
  elif 'scalar filling' in section:
   if section in done:continue
   done.add(section)
   for x in f:output.append(row(['PM2.5',r'$\infty$'if math.isinf(x['cap'])else x['cap'],f"{100*x['D_lca_share']:.2f}",f"{100*x['D_opt_share']:.2f}",f"{x['measured_vs_closed_form_max']:.1e}"]))
  else:output.append(line.replace('PM2.5 &','PM2.5 Jan &'))
 result['tables/supplement_generated.tex']='\n'.join(output)+'\n'
 result['tables/supplement_generated.tex']=result['tables/supplement_generated.tex'].replace('January was selected for display after this comparison.','This historical 30-day pilot guided earlier displays; current primary results use all 366 days.').replace('Retained direction sensitivity:','Retained exploratory direction sensitivity (PM2.5 January pilot):')
 return result
