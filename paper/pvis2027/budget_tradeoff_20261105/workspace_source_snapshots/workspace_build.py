"""Paper-style curves. Full-sequence sweeps reuse the current frozen protocol."""
from pathlib import Path
import os, sys, json, csv
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
W=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
BASE=W/'paper/pvis2027/experiments_ratio_p_20261104'
sys.path.insert(0,str(BASE/'source'))
import run as protocol
from threadpoolctl import threadpool_limits

def readcsv(p):
    with p.open() as f:return list(csv.DictReader(f))

def sweep():
    epsilons=[0.]+[i/100 for i in range(1,11)]+[.15,.20,.30]
    rows=[]
    for name in protocol.PARAMS:
        root=BASE/'results'/name;prep=root/'preparation'
        F=np.load(prep/'fields.npy');xy=np.load(prep/'coordinates.npy')
        meta=protocol.read(prep/'protocol.json')
        d=protocol.load(name,F,xy,meta['sample_measure'],prep/'trees')
        selected=protocol.read(root/'selection.json')['epsilon']
        for eps in epsilons+([.4,.5,.6,.62,.63,.7,1.] if name=='Ring' else []):
            dest=OUT/'data'/name/f'epsilon_{eps:g}'
            jp=dest/'summary.json'
            archived=root/('Exact' if eps==0 else 'Balanced')
            if eps in [0.,selected]:
                sm=protocol.read(archived/'summary.json');per=readcsv(archived/'per_frame.csv')
                origin=str(archived.relative_to(W))
            elif jp.exists():
                sm=protocol.read(jp);per=readcsv(dest/'per_frame.csv');origin=str(dest.relative_to(W))
            else:
                print(name,'FULL SWEEP',eps,len(F),flush=True)
                res=protocol.solve(d,eps);sm,per=protocol.evaluate(name,d,res)
                sm.update(epsilon=eps,t_opt=res['t_opt'],method_seconds=res['seconds'])
                protocol.dump(jp,sm)
                protocol.dump(dest/'status.json',dict(success=res['success'],failures=res.get('failures',[])))
                if not sm['success']:raise RuntimeError((name,eps,sm))
                protocol.table(dest/'per_frame.csv',per)
                # Metrics and layout records suffice; avoid duplicating large map rasters.
                protocol.dump(dest/'layouts.json',res['layouts'])
                origin=str(dest.relative_to(W))
            assert sm['frames']==len(F)
            assert sm['continuous_budget_violations']==0 and sm['rendered_budget_violations']==0
            assert sm['topology_max']<=eps+1.1e-7
            rows.append(dict(dataset=name,epsilon=eps,NPE=sm['NPE'],E_inf=max(float(p['NPE']) for p in per),
                NMLE_max=sm['topology_max'],SNS=sm['SNS'],frames=sm['frames'],balanced=eps==selected,source=origin))
            protocol.table(OUT/'data/full_sequence_sweep.csv',rows)
            print(name,eps,'NPE',round(sm['NPE'],6),'NMLE',round(sm['topology_max'],6),flush=True)
    protocol.dump(OUT/'data/protocol.json',dict(epsilons=epsilons,ring_additional_epsilons=[.4,.5,.6,.62,.63,.7,1.],source=str(BASE),
        reference='one offline direction and extent per complete input, frozen across budgets',
        parameters='current manuscript protocol, all weights/widths/raster lengths fixed',
        exact_balanced='reuse archived complete runs; all other budgets independently solve complete sequence',
        timing='cached preparation, not a new cold-runtime benchmark',
        topology='full fixed-leaf matrix including diagonal; check continuous and rendered errors',
        selection='existing Balanced selection retained; new sweep does not reselect it'))

if __name__=='__main__':
    with threadpool_limits(limits=1):sweep()
