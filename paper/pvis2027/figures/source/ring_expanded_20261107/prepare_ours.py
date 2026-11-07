from pathlib import Path
import sys,numpy as np,json
from itertools import product
O=Path(__file__).resolve().parent;P=O.parents[2];sys.path.insert(0,str(P/'experiments_ratio_p_20261104/source'));import run as r
D=P/'experiments_ratio_p_20261104/results/Ring';prep=D/'preparation'
archive=P.parents[1]/'output/github/RG-MTM-latest-20261027/code/results/unified20261025/ring.json'
original=r.read(archive);a=np.array(original['reference']['candidates']['direction']['a']);xy=np.load(prep/'coordinates.npy');F=np.load(prep/'fields.npy')
with r.threadpool_limits(limits=1):
 d=r.load('Ring',F,xy,225,prep/'trees');old=d['reference'];corners=np.array(list(product(*zip(xy.min(0),xy.max(0)))))@a;o=float(corners.min());L=float(np.ptp(corners))
 d['reference']=dict(kind='direction',origin=o,extent=L,qs=[e@a for e in d['extrema']],label='fixed archive direction',candidates=dict(direction=dict(a=a.tolist(),manual=True,angle_deg=float(np.degrees(np.arctan2(a[1],a[0]))))))
 d['parameters']=r.gm.universal_parameters(o,L,len(xy)*225)
 physical_reference=d['reference']
 for e in [0.,.02,.05,.1,.2]:
  solve_data=dict(d)
  if True:
   solve_data['reference']=dict(physical_reference,qs=[(1-e/.2)*np.full(len(q),o+.5*L)+(e/.2)*np.asarray(q) for q in physical_reference['qs']],label='neutral central layout targets; spatial guidance off')
  res=r.solve(solve_data,e);s,per=r.evaluate('Ring',d,res);assert s['success'] and not s['continuous_budget_violations'] and not s['rendered_budget_violations'];np.savez_compressed(O/f'ring_reference_{e:g}.npz',map=res['map']);r.dump(O/f'ring_reference_{e:g}_summary.json',s);r.dump(O/f'ring_reference_{e:g}_layouts.json',res['layouts']);print(e,s,flush=True)
 r.dump(O/'ring_reference_protocol.json',dict(direction=a,angle_deg=np.degrees(np.arctan2(a[1],a[0])),reference_origin=o,reference_extent=L,choice='User supplied archive reference; explicit fixed direction, not re-estimated from current tracks',previous_main_table_reference={k:v for k,v in old.items() if k!='qs'},raster_length=196,source_fields=str(prep/'fields.npy'),source_direction=str(archive),parameters=r.asdict(d['parameters']),normalization='(projection-origin)/extent, fixed across frames and budgets; no image translation',epsilons=[0,.02,.05,.1,.2],guidance_strengths=[0,.1,.25,.5,1],layout_targets='(1-alpha)*canvas_midpoint + alpha*physical_projection; alpha=epsilon/.2; continuous joint guidance-budget sweep',physical_reference_fixed=True,comparison='paired topology-only and guided settings; NOT an epsilon-only ablation',main_tables_unchanged=True))
