"""N1b: width-aware certified leaf orders inside the interval-layout QP, 917 frames.

Same inputs, eps grid, data resolution eps0, capped QP (B_t = tau_t + beta) and
continuous metrics as N1 (experiments/order_layout); only the leaf order
changes. ``width_order`` minimizes the interval position cost tau (point-model
NROE breaks ties) under the exact merge cost <= eps0 + eps and keeps the N1
order as a candidate, so tau_t never exceeds N1's. Per frame it reports tau of
the N1 order, of the new order and of the kappa P order (volumetric), and the
width-aware lower bound of Theorem A_w (Theorem B flattening for eps > 0).
"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from rgmtm.error_budget import Parameters
from rgmtm.order_certificate import budget_order
from rgmtm.interval_order import interval_scores, width_order

spec = importlib.util.spec_from_file_location('order_layout_run', ROOT / 'experiments/order_layout/run.py')
n1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(n1)
OUT = ROOT / 'results/order_width20261027'
N1 = ROOT / 'results/order_layout20261027'


def tau_of(order, d, t, p):
    return float(interval_scores([order], p.width_scale * np.asarray(d['measures'][t], float), d['references'][t], p)[0][0])


def run(name):
    d = n1.DATASETS[name](); R = d['scalar_range']
    p = Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS}); L = p.canvas
    saved = json.loads((N1 / f'{name.replace(".", "").lower()}.json').read_text())['methods']
    result = dict(dataset=name, frames=len(d['references']), canvas=L, scalar_range=R, eps0=n1.TIE, methods={}, n1={})
    for label, m in saved.items():
        if label.startswith('kappa') or label.startswith('unified pool') or '+ cap' in label: result['n1'][label] = m
    for label, xs in d['old'].items():
        if label.startswith('kappa'):
            taus = [tau_of(np.argsort(x, kind='stable'), d, t, p) for t, x in enumerate(xs)]
            result['n1'][label]['order_tau_mean'] = float(np.mean(taus)) / L
            result['n1'][label]['order_tau_max'] = float(np.max(taus)) / L
    for e in n1.EPS:
        t0 = time.perf_counter(); orders = []
        for t, (V, q) in enumerate(zip(d['merge'], d['references'])):
            w = p.width_scale * np.asarray(d['measures'][t], float)
            pt = budget_order(V, q, L, e * R, n1.TIE * R)
            orders.append(width_order(V, q, w, p, e * R, n1.TIE * R, point=pt))
        search = time.perf_counter() - t0
        rows = n1.capped_sequence(d, orders, R, e, p)
        m = n1.metrics([r['x'] for r in rows], d, L, [r['delta'] for r in rows])
        assert m['E_inf'] <= max(r['cap'] for r in rows) + 1e-7
        assert max(o['delta'] for o in orders) <= (e + n1.TIE) * R * (1 + 1e-12)
        tau = np.array([o['tau'] for o in orders]) / L; ptau = np.array([o['point_tau'] for o in orders]) / L
        low = np.array([o['lower'] for o in orders]) / L
        m.update(cap_mean=float(np.mean([r['cap'] for r in rows])), cap_max=float(max(r['cap'] for r in rows)),
                 order_tau_mean=float(tau.mean()), order_tau_max=float(tau.max()),
                 n1_order_tau_mean=float(ptau.mean()), n1_order_tau_max=float(ptau.max()),
                 width_lower_mean=float(low.mean()), width_lower_max=float(low.max()),
                 frames_at_lower=int(np.sum(tau <= low + 1e-9)), frames_improved=int(np.sum(tau < ptau - 1e-9)),
                 order_NROE=float(np.mean([o['nroe'] for o in orders])),
                 geometry_rms=float(np.sqrt(np.mean([r['terms']['geometry'] for r in rows]))),
                 max_normalized_qp_gap=float(max(r['normalized_qp_gap'] for r in rows)),
                 search_seconds=search, seconds=time.perf_counter() - t0)
        result['methods'][f'width order + cap, eps={e:g}'] = m
        old = result['n1'][f'certified order + cap, eps={e:g}']
        print(name, f'eps={e:g}', 'N1 -> N1b  E_pool %.2f->%.2f  E_inf %.2f->%.2f  NROE %.2f->%.2f  jump %.2f->%.2f  tau_max %.2f->%.2f (lower %.2f)  improved %d/%d  %.0fs' % (
            100 * old['E_pool'], 100 * m['E_pool'], 100 * old['E_inf'], 100 * m['E_inf'], 100 * old['NROE'], 100 * m['NROE'],
            100 * old['jump_mean'], 100 * m['jump_mean'], 100 * ptau.max(), 100 * tau.max(), 100 * low.max(),
            m['frames_improved'], len(orders), m['seconds']), flush=True)
    return result


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or n1.DATASETS:
        r = run(name)
        (OUT / f'{name.replace(".", "").lower()}.json').write_text(json.dumps(r, indent=1))
