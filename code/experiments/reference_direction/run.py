"""Reference direction in 3-D: how the certified bound and the methods depend on it.

The bounds need only the merge tree, the extremum positions (stored in 3-D) and
the feature widths. For Tangaroa and Cylinder this script sweeps 400 directions
over the hemisphere (d and -d give the same bound) and, for each, rebuilds the
references exactly as the stored ones were built: q = projection of the extremum
onto d, canvas origin and length from the projection of the 8 domain corners.

Per direction: mean order bound nu* (data resolution eps0 = 1e-7, as in the paper); mean NROE of native TMTM and ST-MTM
(stored positions, one global flip per sequence chosen in their favour, as in
the earlier protocol); violations of the bound. For the coordinate axes, the
stored direction and the direction with the smallest bound, it also computes our
exact (eps = 0) width-aware order: NROE, attained displacement tau and the
width-aware lower bound. The stored direction must reproduce the saved
references (checked).
"""
import importlib.util, json, sys, time
from itertools import product
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dataclasses import replace
from rgmtm.error_budget import Parameters
from rgmtm.order_certificate import certificate, budget_order, order_errors
from rgmtm.interval_order import width_order, width_certificate

spec = importlib.util.spec_from_file_location('order_layout_run', ROOT / 'experiments/order_layout/run.py')
n1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(n1)
OUT = ROOT / 'results/reference_direction20261027'
SETS = {
    'Tangaroa': dict(features='results/volume3d/tangaroa-paper-p10-full201/features.json', key='tangaroa',
                     box=[(-.35, .65), (-.3, .3), (-.5, -.3)],
                     stored=json.loads((ROOT / 'results/volume3d/tangaroa-paper-p10-full201/reference.json').read_text())['direction']),
    'Cylinder': dict(features='results/paper1_suite/square-cylinder3d/features.json', key='square-cylinder3d',
                     box=None, stored=[1., 0., 0.]),
}


def hemisphere(n=400):
    """Fibonacci directions with z >= 0."""
    k = np.arange(n) + .5; z = k / n; r = np.sqrt(1 - z * z); phi = np.pi * (1 + 5 ** .5) * k
    return np.c_[r * np.cos(phi), r * np.sin(phi), z]


def canvas(d, box):
    corners = np.array(list(product(*box))); s = corners @ d; return float(s.min()), float(s.max() - s.min())


def run(name):
    cfg = SETS[name]; d = n1.DATASETS[name](); p0 = Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS})
    feats = json.loads((ROOT / cfg['features']).read_text())['frames']; X = [np.asarray(f['extrema'], float) for f in feats]
    if cfg['box'] is None:
        c = np.load(ROOT / 'data/real/paper1_suite/square-cylinder3d/coordinates.npz'); cfg['box'] = [(float(c[k].min()), float(c[k].max())) for k in 'xyz']
    nat = json.loads((ROOT / f"results/stmtm_completion20261026/{cfg['key']}/landmarks.json").read_text())['positions']
    natives = {m: [np.asarray(u, float) for u in nat[m]] for m in ('TMTM', 'ST-MTM')}
    V = [np.asarray(v, float) for v in d['merge']]; R = d['scalar_range']

    def refs(direction):
        u = np.asarray(direction, float); u = u / np.linalg.norm(u); o, L = canvas(u, cfg['box'])
        return [x @ u for x in X], o, L

    q0, o0, L0 = refs(cfg['stored'])     # reproduce the stored references
    assert np.allclose(o0, p0.canvas_origin) and np.allclose(L0, p0.canvas), (o0, L0)
    assert max(float(np.max(abs(a - np.asarray(b)))) for a, b in zip(q0, d['references'])) < 1e-9 * L0

    def native_nroe(qs, L):
        best = None
        for flip in (False, True):
            vals = [float(order_errors([np.argsort(-u if flip else u, kind='stable')], q, L)[0]) for u, q in zip(nat_pos, qs)]
            best = vals if best is None or np.mean(vals) < np.mean(best) else best
        return best

    sweep = []; t0 = time.perf_counter()
    for direction in hemisphere():
        qs, o, L = refs(direction)
        nu = [certificate(v, q, L, 0., n1.TIE * R) for v, q in zip(V, qs)]
        row = dict(direction=direction.tolist(), nu_mean=float(np.mean(nu)), nu_max=float(np.max(nu)))
        for m, pos in natives.items():
            nat_pos = pos; vals = native_nroe(qs, L)
            row[f'{m}_NROE'] = float(np.mean(vals)); row[f'{m}_violations'] = int(sum(a < b - 1e-12 for a, b in zip(vals, nu)))
        sweep.append(row)
    sweep_seconds = time.perf_counter() - t0

    best = min(sweep, key=lambda r: r['nu_mean'])['direction']
    keys = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1], 'stored': cfg['stored'], 'smallest bound': best}
    key_rows = {}
    for label, direction in keys.items():
        qs, o, L = refs(direction); p = replace(p0, canvas=L, canvas_origin=o)
        orders = []
        for v, q, m in zip(V, qs, d['measures']):
            w = p.width_scale * np.asarray(m, float)
            orders.append(width_order(v, q, w, p, 0., n1.TIE * R, point=budget_order(v, q, L, 0., n1.TIE * R)))
        nu = [certificate(v, q, L, 0., n1.TIE * R) for v, q in zip(V, qs)]
        row = dict(direction=[float(a) for a in np.asarray(direction) / np.linalg.norm(direction)], nu_mean=float(np.mean(nu)),
                   ours_NROE=float(np.mean([o_['nroe'] for o_ in orders])), ours_tau_mean=float(np.mean([o_['tau'] for o_ in orders])) / L,
                   ours_tau_max=float(np.max([o_['tau'] for o_ in orders])) / L,
                   width_lower_mean=float(np.mean([o_['lower'] for o_ in orders])) / L,
                   frames_at_width_bound=int(sum(o_['tau'] <= o_['lower'] + 1e-9 * L for o_ in orders)))
        for m, pos in natives.items():
            nat_pos = pos; row[f'{m}_NROE'] = float(np.mean(native_nroe(qs, L)))
        key_rows[label] = row
        print(name, label, {k: (round(100 * v, 2) if isinstance(v, float) else v) for k, v in row.items() if k != 'direction'}, flush=True)
    nus = np.array([r['nu_mean'] for r in sweep])
    return dict(dataset=name, frames=len(V), directions=len(sweep), sweep_seconds=sweep_seconds,
                total_violations={m: sum(r[f'{m}_violations'] for r in sweep) for m in natives},
                nu_mean_range=[float(nus.min()), float(nus.max())], stored_nu_rank=int(np.sum(nus < key_rows['stored']['nu_mean'] - 1e-15)),
                key_directions=key_rows, sweep=sweep)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or SETS:
        r = run(name)
        print(name, 'violations', r['total_violations'], 'nu range %.2f-%.2f%%' % tuple(100 * x for x in r['nu_mean_range']),
              'stored direction rank', r['stored_nu_rank'], 'of', r['directions'], flush=True)
        (OUT / f'{name.lower()}.json').write_text(json.dumps(r, indent=1))
