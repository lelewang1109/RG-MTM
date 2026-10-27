"""N1: certified leaf orders inside the shared interval-layout QP, 917 temporal frames.

For each topology budget eps, the order is fixed by ``budget_order`` (minimum
reference-order error with exact merge cost <= eps0 + eps, see
experiments/order_budget). The unchanged four-term interval QP of
``rgmtm.unified`` (widths, gaps, canvas, eccentricity, reference, geometry and
projected-motion terms, B = infinity) then places the anchors sequentially.

Compared with the saved layouts of the same inputs: the earlier common-model
candidate-pool QP (planar, unified20261025) and the kappa construction P/R
(volumetric). Metrics are continuous (no raster): E_pool, E_inf, NROE,
layout-induced jump |du - dq|/L of matched tracks, plain anchor motion |du|/L,
geometry residual and exact merge error delta*/range. A second variant adds the
per-frame position cap B_t = tau_t + beta of the earlier P/R construction.
"""
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from rgmtm.error_budget import Parameters
from rgmtm.unified import Controls, solve_unified_frame, solve_unified_sequence
from rgmtm.framework import interval_costs
from rgmtm.order_certificate import budget_order, order_error

OUT = ROOT / 'results/order_layout20261027'
EPS = [0, .02, .05, .1]
TIE = 1e-7                       # data resolution eps0, fraction of the scalar range
PARAM_FIELDS = set(Parameters.__dataclass_fields__)


def read(path): return json.loads(Path(path).read_text())


def planar(name):
    d = read(ROOT / f'results/unified20261025/{name}.json')
    fi = d['frame_inputs']
    old = {f'unified pool, eps={e:g}': [r['x'] for r in d['regimes'][k]['rows']]
           for e, k in [(0, 'reference_0'), (.02, 'reference_2'), (.1, 'reference_10')]}
    old_delta = {f'unified pool, eps={e:g}': [r['delta'] for r in d['regimes'][k]['rows']]
                 for e, k in [(0, 'reference_0'), (.02, 'reference_2'), (.1, 'reference_10')]}
    return dict(centers=[f['centers'] for f in fi], measures=[f['measures'] for f in fi],
                hierarchies=[f['hierarchy'] for f in fi], references=[f['reference'] for f in fi],
                merge=[f['merge_values'] for f in fi], tracks=[f['tracks'] for f in fi],
                scalar_range=d['scalar_range'], parameters=d['parameters'], old=old, old_delta=old_delta)


def volume(folder, measure_key, reference, old_positions):
    src = ROOT / folder; f = read(src / 'features.json'); frames = f['frames']
    par = read(src / 'parameters.json'); rng = {'volume3d': 2.0}.get(folder.split('/')[1], 1.0)
    return dict(centers=[fr['centers'] for fr in frames], measures=[fr.get(measure_key, fr['support_counts']) for fr in frames],
                hierarchies=[fr['hierarchy'] for fr in frames], references=[reference(src, fr, t) for t, fr in enumerate(frames)],
                merge=[fr['source_lca_values'] for fr in frames], tracks=f['tracks'],
                scalar_range=rng, parameters=par, old=old_positions(src), old_delta={})


def tangaroa_old(src):
    pos = read(src / 'positions.json')
    return {f'kappa {m}': pos[m] for m in ['RG-MTM-P', 'RG-MTM-R 0.02', 'RG-MTM-R 0.2']}


def cylinder_old(src):
    rows = read(src / 'frame_metrics.json'); out = {}
    for m in ['RG-MTM-P', 'RG-MTM-R 0.02', 'RG-MTM-R 0.2']:
        rs = sorted([r for r in rows if r['method'] == m], key=lambda r: r['index'])
        out[f'kappa {m}'] = [r['layout']['x'] for r in rs]
    return out


DATASETS = {
    'Storms': lambda: planar('era5'), 'Wildfires': lambda: planar('wildfire'), 'OLR': lambda: planar('olr'),
    'PM2.5': lambda: planar('pm25_2000'), 'Ring': lambda: planar('ring'),
    'Tangaroa': lambda: volume('results/volume3d/tangaroa-paper-p10-full201', 'volumes',
                               lambda src, fr, t: read(src / 'reference.json')['qs'][t], tangaroa_old),
    'Cylinder': lambda: volume('results/paper1_suite/square-cylinder3d', 'support_counts',
                               lambda src, fr, t: list(np.asarray(fr['extrema'])[:, 0]), cylinder_old),
}


def metrics(xs, d, L, deltas=None):
    qs = [np.asarray(q, float) for q in d['references']]; xs = [np.asarray(x, float) for x in xs]
    err = np.concatenate([np.abs(x - q) for x, q in zip(xs, qs)]) / L
    jumps = []; moves = []
    for t in range(1, len(xs)):
        prev = {k: i for i, k in enumerate(d['tracks'][t - 1])}
        for i, k in enumerate(d['tracks'][t]):
            if k in prev:
                j = prev[k]; du = xs[t][i] - xs[t - 1][j]; dq = qs[t][i] - qs[t - 1][j]
                jumps.append(abs(du - dq) / L); moves.append(abs(du) / L)
    jumps = np.asarray(jumps); out = dict(E_pool=float(err.mean()), E_inf=float(err.max()),
        NROE=float(np.mean([order_error(np.argsort(x, kind='stable'), q, L) for x, q in zip(xs, qs)])),
        jump_mean=float(jumps.mean()) if len(jumps) else 0., jump_p95=float(np.quantile(jumps, .95)) if len(jumps) else 0.,
        jump_max=float(jumps.max()) if len(jumps) else 0., anchor_motion_mean=float(np.mean(moves)) if moves else 0.,
        matched_steps=len(jumps))
    if deltas is not None:
        dd = np.asarray(deltas, float) / d['scalar_range']
        out.update(NMLE_mean=float(dd.mean()), NMLE_max=float(dd.max()))
    return out


def capped_sequence(d, orders, R, e, p):
    """Same QP with a per-frame position cap B_t = tau_t(order) + beta (beta = p.extra_budget).

    tau_t is the attained minimax position cost of the fixed order under the
    interval geometry, so the cap is always feasible and E_inf <= max_t B_t / L.
    """
    rows = []
    for t, o in enumerate(orders):
        q = np.asarray(d['references'][t], float); w = p.width_scale * np.asarray(d['measures'][t], float)
        tau = float(interval_costs(np.array([o['order']]), w, q, p)[0])
        previous = previous_q = mask = None
        if t:
            old = {k: i for i, k in enumerate(d['tracks'][t - 1])}
            mask = np.array([k in old for k in d['tracks'][t]])
            previous = np.array([rows[-1]['x'][old[k]] if k in old else 0. for k in d['tracks'][t]])
            previous_q = np.array([d['references'][t - 1][old[k]] if k in old else 0. for k in d['tracks'][t]])
        r = solve_unified_frame(d['centers'][t], d['measures'][t], d['hierarchies'][t], q, d['merge'][t], R,
                                Controls(topology_budget=e + TIE, position_budget=(tau + p.extra_budget) / p.canvas), p,
                                candidate_orders=[o['order']], previous=previous, previous_q=previous_q, matched=mask)
        r['cap'] = (tau + p.extra_budget) / p.canvas; rows.append(r)
    return rows


def run(name):
    d = DATASETS[name](); R = d['scalar_range']
    p = Parameters(**{k: v for k, v in d['parameters'].items() if k in PARAM_FIELDS}); L = p.canvas
    result = dict(dataset=name, frames=len(d['references']), canvas=L, scalar_range=R, eps0=TIE, methods={})
    for label, xs in d['old'].items():
        result['methods'][label] = metrics(xs, d, L, d['old_delta'].get(label))
    for e in EPS:
        t0 = time.perf_counter()
        orders = [budget_order(V, q, L, e * R, TIE * R) for V, q in zip(d['merge'], d['references'])]
        rows = solve_unified_sequence(d['centers'], d['measures'], d['hierarchies'], d['references'], d['merge'],
                                      d['tracks'], [[o['order']] for o in orders], R, Controls(topology_budget=e + TIE), p)
        m = metrics([r['x'] for r in rows], d, L, [r['delta'] for r in rows])
        m.update(order_NROE=float(np.mean([o['nroe'] for o in orders])),
                 lower_bound=float(np.mean([o['lower'] for o in orders])),
                 geometry_rms=float(np.sqrt(np.mean([r['terms']['geometry'] for r in rows]))),
                 max_normalized_qp_gap=float(max(r['normalized_qp_gap'] for r in rows)),
                 seconds=time.perf_counter() - t0)
        result['methods'][f'certified order, eps={e:g}'] = m
        t0 = time.perf_counter(); rows = capped_sequence(d, orders, R, e, p)
        c = metrics([r['x'] for r in rows], d, L, [r['delta'] for r in rows])
        c.update(cap_mean=float(np.mean([r['cap'] for r in rows])), cap_max=float(max(r['cap'] for r in rows)),
                 geometry_rms=float(np.sqrt(np.mean([r['terms']['geometry'] for r in rows]))),
                 max_normalized_qp_gap=float(max(r['normalized_qp_gap'] for r in rows)), seconds=time.perf_counter() - t0)
        assert c['E_inf'] <= c['cap_max'] + 1e-7
        result['methods'][f'certified order + cap, eps={e:g}'] = c
        for tag, v in (('free', m), ('cap', c)):
            print(name, f'eps={e:g}', tag, {k: round(100 * x, 3) for k, x in v.items() if k in ('E_pool', 'E_inf', 'NROE', 'jump_mean', 'NMLE_max')},
                  f"{v['seconds']:.1f}s", flush=True)
    return result


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or DATASETS:
        r = run(name)
        (OUT / f'{name.replace(".", "").lower()}.json').write_text(json.dumps(r, indent=1))
