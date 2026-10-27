"""N2: position--topology frontier from exact topology to pure projection, 917 frames.

Same inputs, data resolution eps0, width-aware certified orders, capped QP
(B_t = tau_t + beta) and continuous metrics as N1/N1b (experiments/order_width);
the budget grid is extended to eps in {0, 1, 2, 5, 10, 20, 50}% and closed by
the projection baseline (eps = infinity): leaves sorted by reference (NROE = 0)
with the optimal barriers of that order, placed by the same capped QP. The
projection is the Hovmoller-like end of the frontier; its merge error is
whatever the sorted order forces.
"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from rgmtm.error_budget import Parameters
from rgmtm.framework import merge_costs
from rgmtm.order_certificate import budget_order
from rgmtm.interval_order import interval_scores, width_order

spec = importlib.util.spec_from_file_location('order_layout_run', ROOT / 'experiments/order_layout/run.py')
n1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(n1)
OUT = ROOT / 'results/frontier20261027'
EPS = [0, .01, .02, .05, .1, .2, .5]


def summarize(d, L, R, orders, rows, p):
    m = n1.metrics([r['x'] for r in rows], d, L, [r['delta'] for r in rows])
    assert m['E_inf'] <= max(r['cap'] for r in rows) + 1e-7
    tau = np.array([o['tau'] for o in orders]) / L
    m.update(NMLE_mean=float(np.mean([r['delta'] for r in rows]) / R), order_tau_mean=float(tau.mean()),
             order_tau_max=float(tau.max()), cap_max=float(max(r['cap'] for r in rows)),
             geometry_rms=float(np.sqrt(np.mean([r['terms']['geometry'] for r in rows]))),
             max_normalized_qp_gap=float(max(r['normalized_qp_gap'] for r in rows)))
    return m


def run(name):
    d = n1.DATASETS[name](); R = d['scalar_range']
    p = Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS}); L = p.canvas
    result = dict(dataset=name, frames=len(d['references']), canvas=L, scalar_range=R, eps0=n1.TIE, methods={})
    for e in EPS:
        t0 = time.perf_counter(); orders = []
        for t, (V, q) in enumerate(zip(d['merge'], d['references'])):
            w = p.width_scale * np.asarray(d['measures'][t], float)
            pt = budget_order(V, q, L, e * R, n1.TIE * R)
            orders.append(width_order(V, q, w, p, e * R, n1.TIE * R, point=pt))
        assert max(o['delta'] for o in orders) <= (e + n1.TIE) * R * (1 + 1e-12)
        rows = n1.capped_sequence(d, orders, R, e, p)
        m = summarize(d, L, R, orders, rows, p); m['seconds'] = time.perf_counter() - t0
        result['methods'][f'eps={e:g}'] = m
        print(name, f'eps={e:g}', 'E_pool %.2f E_inf %.2f NROE %.2f NMLE mean/max %.2f/%.2f' % (
            100 * m['E_pool'], 100 * m['E_inf'], 100 * m['NROE'], 100 * m['NMLE_mean'], 100 * m['NMLE_max']), flush=True)
    t0 = time.perf_counter(); orders = []
    for t, (V, q) in enumerate(zip(d['merge'], d['references'])):
        o = [int(i) for i in np.argsort(np.asarray(q, float), kind='stable')]
        w = p.width_scale * np.asarray(d['measures'][t], float)
        orders.append(dict(order=o, delta=float(merge_costs([o], np.asarray(V, float))[0]),
                           tau=float(interval_scores([o], w, q, p)[0][0])))
    rows = n1.capped_sequence(d, orders, R, np.inf, p)
    m = summarize(d, L, R, orders, rows, p); m['seconds'] = time.perf_counter() - t0
    m['frames_exact_topology'] = int(sum(o['delta'] <= n1.TIE * R for o in orders))
    result['methods']['projection'] = m
    print(name, 'projection', 'E_pool %.2f E_inf %.2f NROE %.2f NMLE mean/max %.2f/%.2f' % (
        100 * m['E_pool'], 100 * m['E_inf'], 100 * m['NROE'], 100 * m['NMLE_mean'], 100 * m['NMLE_max']), flush=True)
    return result


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or n1.DATASETS:
        r = run(name)
        (OUT / f'{name.replace(".", "").lower()}.json').write_text(json.dumps(r, indent=1))
