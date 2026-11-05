"""Extend the incomplete Ring sweep past its fixed-leaf barrier threshold."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'output/paper_curves_20261105/source'))
from build import *
from itertools import permutations
from rgmtm.framework import interval_costs,merge_costs

with threadpool_limits(limits=1):
 name='Ring';root=BASE/'results'/name;prep=root/'preparation'
 F=np.load(prep/'fields.npy');xy=np.load(prep/'coordinates.npy');meta=protocol.read(prep/'protocol.json')
 d=protocol.load(name,F,xy,meta['sample_measure'],prep/'trees')
 rows=readcsv(OUT/'data/full_sequence_sweep.csv')
 for eps in [.4,.5,.6,.62,.63,.7,1.]:
  dest=OUT/'data'/name/f'epsilon_{eps:g}'
  if (dest/'summary.json').exists():sm=protocol.read(dest/'summary.json');per=readcsv(dest/'per_frame.csv')
  else:
   print(name,'EXTEND',eps,flush=True);res=protocol.solve(d,eps);sm,per=protocol.evaluate(name,d,res)
   sm.update(epsilon=eps,t_opt=res['t_opt'],method_seconds=res['seconds'])
   protocol.dump(dest/'summary.json',sm);protocol.dump(dest/'status.json',dict(success=res['success'],failures=res.get('failures',[])))
   assert sm['success'];protocol.table(dest/'per_frame.csv',per);protocol.dump(dest/'layouts.json',res['layouts'])
  assert sm['frames']==40 and sm['continuous_budget_violations']==0 and sm['rendered_budget_violations']==0
  assert sm['topology_max']<=eps+1.1e-7
  row=dict(dataset=name,epsilon=eps,NPE=sm['NPE'],E_inf=max(float(p['NPE']) for p in per),NMLE_max=sm['topology_max'],SNS=sm['SNS'],frames=40,balanced=False,source=str(dest.relative_to(ROOT)))
  rows=[r for r in rows if not(r['dataset']==name and abs(float(r['epsilon'])-eps)<1e-12)]+[row]
  print(eps,sm['NPE'],row['E_inf'],sm['topology_max'],flush=True)
 rows.sort(key=lambda r:(list(protocol.PARAMS).index(r['dataset']),float(r['epsilon'])))
 protocol.table(OUT/'data/full_sequence_sweep.csv',rows)
 t=39;q=d['reference']['qs'][t];w=d['parameters'].width_scale*d['scene']['areas'][t]
 O=np.array(list(permutations(range(len(q)))));tau=interval_costs(O,w,q,d['parameters'])/d['parameters'].canvas
 delta=merge_costs(O,d['merge_values'][t])/d['scalar_range']
 threshold=float(min(delta[tau<.0915048]))
 protocol.dump(ROOT/'output/paper_fig5_single_column_20261105/ring_threshold_audit.json',dict(frame=t,leaves=len(q),enumerated_orders=len(O),threshold_to_reduce_selected_tau=threshold,
  best_tau_at_30_percent=float(min(tau[delta<=.3+1e-7])),best_tau_at_100_percent=float(min(tau[delta<=1+1e-7])),
  method='enumerate all 120 orders; continuous minimax position and fixed-leaf optimal barrier costs'))
