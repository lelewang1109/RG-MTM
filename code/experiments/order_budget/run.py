"""Order-level budget experiment on all 917 temporal frames (5 planar + 2 volumetric).

1. Theorem A: exact-topology methods (TMTM, ST-MTM, RG-MTM-P, fixed-X) have NROE >= nu*.
2. Theorem B: saved relaxed outputs have NROE >= nu*(T^(2 e_t)), e_t their measured merge error.
3. Budget sweep: best of threshold and conflict-driven selective flattening at each
   epsilon; exact optimum by enumeration on frames with at most 8 leaves; Theorem B
   and chain-aware Theorem C lower bounds on every frame.
5. Resolution sweep (tie = 0): tiny epsilons expose near-degenerate merge levels,
   i.e. positional cost caused by hierarchy decisions below data precision.
4. Matched-cost comparison on volumetric inputs: each kappa output's own per-frame
   merge error is given as epsilon to the budgeted ordering.
Order-only metrics: widths, gaps and the secondary QP are not involved.
"""
import json, sys, time
from itertools import permutations
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from rgmtm.framework import merge_costs
from rgmtm.order_certificate import certificate, budget_order, order_errors

OUT = ROOT / 'results/order_budget20261027'
EPS = [0, .005, .01, .02, .05, .1, .2, .5, 1]
RESOLUTION = [0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]
TIE = 1e-7          # merge levels within TIE * scalar range are one level
ENUMERATE = 8
EXACT_METHODS = {'TMTM', 'ST-MTM', 'A', 'RG-MTM-P', 'fixed-X anchored'}


def read(path): return json.loads(Path(path).read_text())


def planar(name, perf_path, key):
    d = read(ROOT / f'results/framework20261025/{name}.json')
    perf = read(ROOT / perf_path)
    perf = perf[key] if key else (perf if 'methods' in perf else next(iter(perf.values())))
    methods = {m: dict(nroe=v['per_frame'], nmle=None) for m, v in perf['methods'].items()
               if len(v['per_frame']) == len(d['frame_inputs'])}
    frames = [(np.asarray(f['merge_values'], float), np.asarray(f['reference'], float)) for f in d['frame_inputs']]
    return dict(frames=frames, extent=d['canvas'], range=d['scalar_range'], methods=methods, dimension=2)


def volume(src, st, scalar_range, reference):
    src = ROOT / src; feats = read(src / 'features.json')['frames']
    frames = [(np.asarray(f['source_lca_values'], float), np.asarray(reference(src, f, t), float))
              for t, f in enumerate(feats)]
    methods = {}
    for r in read(src / 'frame_metrics.json') + read(ROOT / st / 'frame_metrics.json'):
        methods.setdefault(r['method'], []).append(r)
    methods = {m: dict(nroe=[r['NROE'] for r in sorted(rs, key=lambda r: r['index'])],
                       nmle=[r['NMLE'] for r in sorted(rs, key=lambda r: r['index'])]) for m, rs in methods.items()}
    return dict(frames=frames, extent=read(src / 'parameters.json')['canvas'], range=scalar_range,
                methods=methods, dimension=3)


def tangaroa_reference(src, f, t):
    return read(src / 'reference.json')['qs'][t]


DATASETS = {
    'Storms': lambda: planar('era5', 'results/final_performance.json', 'era5'),
    'Wildfires': lambda: planar('wildfire', 'results/final_performance.json', 'wildfire'),
    'OLR': lambda: planar('olr', 'results/final_performance.json', 'olr'),
    'PM2.5': lambda: planar('pm25_2000', 'results/pm25_2000/final_performance.json', None),
    'Ring': lambda: planar('ring', 'results/final_performance.json', 'ring'),
    'Tangaroa': lambda: volume('results/volume3d/tangaroa-paper-p10-full201',
                               'results/stmtm_completion20261026/tangaroa', 2.0, tangaroa_reference),
    'Cylinder': lambda: volume('results/paper1_suite/square-cylinder3d',
                               'results/stmtm_completion20261026/square-cylinder3d', 1.0,
                               lambda src, f, t: np.asarray(f['extrema'])[:, 0]),
}


def run(name):
    d = DATASETS[name](); L, R = d['extent'], d['range']; tie = TIE * R; frames = d['frames']
    nu = np.array([certificate(V, q, L, 0, tie) for V, q in frames])
    out = dict(dataset=name, dimension=d['dimension'], frames=len(frames), extent=L, scalar_range=R, tie=tie,
               leaves=[min(len(V) for V, _ in frames), max(len(V) for V, _ in frames)],
               nu_mean=float(nu.mean()), nu_max=float(nu.max()), nu_per_frame=nu.tolist(),
               nu_tie_sensitivity={str(x): float(np.mean([certificate(V, q, L, 0, x * R) for V, q in frames]))
                                   for x in (0, 1e-8, 1e-7, 1e-6, 1e-5)}, methods={})
    for m, v in d['methods'].items():
        nroe = np.asarray(v['nroe'], float)
        if v['nmle'] is None:
            if m not in EXACT_METHODS: continue      # planar relaxed outputs lack per-frame merge error
            nmle = np.zeros(len(nroe))
        else:
            nmle = np.asarray(v['nmle'], float)
        exact = nmle * R <= tie
        bound = np.array([certificate(V, q, L, 2 * e * R, tie) for (V, q), e in zip(frames, nmle)])
        out['methods'][m] = dict(NROE_mean=float(nroe.mean()), exact_topology_frames=int(exact.sum()),
            theorem_violations=int(np.sum(nroe + 1e-8 < bound)),
            frames_at_bound=int(np.sum(np.abs(nroe - bound) < 1e-6)),
            avoidable_mean=float(np.mean(nroe - bound)))
    small = [i for i, (V, _) in enumerate(frames) if len(V) <= ENUMERATE]
    exact = {}
    for i in small:
        V, q = frames[i]; P = np.array(list(permutations(range(len(V)))))
        exact[i] = (merge_costs(P, V), order_errors(P, q, L))
    sweep = []
    for e in EPS:
        rows = [budget_order(V, q, L, e * R, tie) for V, q in frames]
        opt = np.array([exact[i][1][exact[i][0] <= e * R + tie].min() for i in small])
        ours = np.array([rows[i]['nroe'] for i in small])
        nroe = np.array([r['nroe'] for r in rows]); low = np.array([r['lower'] for r in rows])
        delta = np.array([r['delta'] for r in rows]) / R
        assert np.all(delta <= e + TIE + 1e-12) and np.all(nroe + 1e-12 >= low)
        mean = lambda k: float(np.mean([r[k] for r in rows if k in r] or [0.]))
        sweep.append(dict(epsilon=e, NROE_mean=float(nroe.mean()), lower_mean=float(low.mean()),
            lower_b_mean=mean('lower_b'), lower_c_mean=mean('lower_c'),
            threshold_NROE_mean=mean('threshold_nroe'), selective_NROE_mean=mean('selective_nroe'),
            frames_selective=int(sum(r.get('source') == 'selective' for r in rows)),
            topology_mean=float(delta.mean()), topology_max=float(delta.max()),
            frames_at_lower_bound=int(np.sum(nroe - low < 1e-9)),
            enumerated_frames=len(small),
            enumerated_optimum_mean=float(opt.mean()) if small else None,
            enumerated_gap_mean=float(np.mean(ours - opt)) if small else None,
            enumerated_frames_optimal=int(np.sum(ours - opt < 1e-9)) if small else None))
    out['budget_sweep'] = sweep
    resolution = []
    for e in RESOLUTION:
        rows = [budget_order(V, q, L, e * R, 0.) for V, q in frames]
        resolution.append(dict(epsilon=e, NROE_mean=float(np.mean([r['nroe'] for r in rows])),
            lower_c_mean=float(np.mean([r['lower_c'] for r in rows])),
            topology_max=float(max(r['delta'] for r in rows) / R)))
    out['resolution_sweep'] = resolution
    matched = {}
    for m, v in d['methods'].items():
        if v['nmle'] is None or m in EXACT_METHODS: continue
        rows = [budget_order(V, q, L, e * R, tie) for (V, q), e in zip(frames, v['nmle'])]
        ours = np.array([r['nroe'] for r in rows]); theirs = np.asarray(v['nroe'], float)
        matched[m] = dict(kappa_NROE_mean=float(theirs.mean()), kappa_NMLE_mean=float(np.mean(v['nmle'])),
            budget_NROE_mean=float(ours.mean()),
            budget_NMLE_mean=float(np.mean([r['delta'] for r in rows]) / R),
            frames_budget_better=int(np.sum(ours < theirs - 1e-9)),
            frames_budget_worse=int(np.sum(ours > theirs + 1e-9)))
    out['matched_cost'] = matched
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or DATASETS:
        t = time.perf_counter(); r = run(name); r['seconds'] = time.perf_counter() - t
        (OUT / f'{name.replace(".", "").lower()}.json').write_text(json.dumps(r, indent=1))
        print(name, f"{r['seconds']:.1f}s nu*={100 * r['nu_mean']:.3f}%",
              {m: (v['theorem_violations'], round(100 * v['NROE_mean'], 2)) for m, v in r['methods'].items()},
              flush=True)
