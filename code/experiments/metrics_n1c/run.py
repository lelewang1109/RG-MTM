"""N1c: geometry, stability, motion and raster metrics of the new layouts, 917 frames.

Recomputes the width-aware certified layouts with the capped QP (experiments/
frontier) at eps in {0, 2, 10}% and the projection baseline, and scores them with
the unchanged protocol of the completed nine-input table
(results/stmtm_completion20261026/unified_metrics.csv):

- SNS, TW (k=1), TD: ``geometry`` of experiments/stmtm_completion on unweighted
  support centroids, positions on the full [0,1] canvas;
- ME: ``motion`` there (original extrema and tracks, lag 2, source threshold 2%
  of the domain diagonal; occupied-range display threshold, fixed canvas for
  Cylinder). Planar domain diagonals are not stored; we use the midpoint of the
  interval that reproduces the stored event count. Thresholds are nested, so
  every value in it selects the same events.

Before scoring, the script re-evaluates the saved anchors of the stored methods
(planar u0..u3, volumetric kappa P/R) and records the agreement. Raster errors
(barrier discrepancy and anchor rounding of the rendered map) need the scalar
inputs and are computed for Ring, OLR and PM2.5 only.
"""
import csv, importlib.util, json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT.parent), str(ROOT / 'src'), str(ROOT / 'analysis'), str(ROOT)]
from rgmtm.error_budget import Parameters
from rgmtm.framework import merge_costs
from rgmtm.order_certificate import budget_order
from rgmtm.interval_order import interval_scores, width_order


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


n1 = module('order_layout_run', ROOT / 'experiments/order_layout/run.py')
sc = module('stmtm_completion_run', ROOT / 'experiments/stmtm_completion/run.py')
OUT = ROOT / 'results/metrics_n1c20261027'
SETTINGS = [0, .02, .1, 'projection']
STORED = list(csv.DictReader((ROOT / 'results/stmtm_completion20261026/unified_metrics.csv').open()))
PLANAR = {'Storms': 'era5', 'Wildfires': 'wildfire', 'OLR': 'olr', 'PM2.5': 'pm25', 'Ring': 'ring'}
VOLUME = {'Tangaroa': ('results/volume3d/tangaroa-paper-p10-full201', 'tangaroa', True),
          'Cylinder': ('results/paper1_suite/square-cylinder3d', 'square-cylinder3d', False)}
RASTER = {'Ring': 'ring', 'OLR': 'olr', 'PM2.5': 'pm25_2000'}
METHODS = ['TMTM', 'ST-MTM', 'RG-MTM-P', 'RG-MTM-R']


def stored(name, method):
    return next(r for r in STORED if r['dataset'] == name and r['method'] == method)


def landmarks(name):
    key = PLANAR[name]
    path = ROOT / ('results/pm25_2000/landmarks.npz' if key == 'pm25' else f'results/public_metrics_20261016/{key}_landmarks.npz')
    z = np.load(path, allow_pickle=True); n = z['count']
    return z, n, [dict(extrema=z['extrema'][t][:n[t]]) for t in range(len(n))]


def planar_diagonal(name, z, n, feats, tracks):
    """Midpoint of the diagonals that reproduce the stored motion event count."""
    want = int(stored(name, 'TMTM')['N_clear']); pos = [np.asarray(z['u0'][t][:n[t]], float) for t in range(len(n))]
    hits = [g for g in np.geomspace(5, 5000, 4000) if sc.motion(feats, tracks, pos, None, g, 1.)['clear'] == want]
    assert hits, f'no diagonal reproduces {want} events on {name}'
    return float((min(hits) + max(hits)) / 2), [float(min(hits)), float(max(hits))]


def score(d, xs, p, feats, diag, occupied):
    u = [(np.asarray(x, float) - p.canvas_origin) / p.canvas for x in xs]
    g, _ = sc.geometry(d['centers'], u, d['tracks'], True)
    m = sc.motion(feats, d['tracks'], u, None, diag, 1., occupied=occupied)
    return dict(SNS=g['SNS'], TW1=g['TW1'], TD=g['TD'], ME_errors=m['errors'], ME_clear=m['clear'],
                ME_fraction=m['error_fraction'], SNS_frames=g['SNS_frames'], TW1_frames=g['TW1_frames'])


def layouts(d, p, setting):
    R = d['scalar_range']; L = p.canvas; orders = []
    for t, (V, q) in enumerate(zip(d['merge'], d['references'])):
        w = p.width_scale * np.asarray(d['measures'][t], float)
        if setting == 'projection':
            o = [int(i) for i in np.argsort(np.asarray(q, float), kind='stable')]
            orders.append(dict(order=o, delta=float(merge_costs([o], np.asarray(V, float))[0]),
                               tau=float(interval_scores([o], w, q, p)[0][0])))
        else:
            pt = budget_order(V, q, L, setting * R, n1.TIE * R)
            orders.append(width_order(V, q, w, p, setting * R, n1.TIE * R, point=pt))
    return n1.capped_sequence(d, orders, R, np.inf if setting == 'projection' else setting, p)


def run(name):
    d = n1.DATASETS[name](); p = Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS})
    out = dict(dataset=name, frames=len(d['references']), settings={}, reproduction={}, baselines={})
    if name in PLANAR:
        z, n, feats = landmarks(name); diag, interval = planar_diagonal(name, z, n, feats, d['tracks']); occupied = True
        out['diagonal'] = dict(value=diag, reproducing_interval=interval, rule='midpoint; same nested event set throughout')
        for k, method in enumerate(METHODS):
            u = [np.asarray(z[f'u{k}'][t][:n[t]], float) for t in range(len(n))]
            g, _ = sc.geometry(d['centers'], u, d['tracks'], True); m = sc.motion(feats, d['tracks'], u, None, diag, 1.)
            s = stored(name, method)
            out['reproduction'][method] = dict(SNS=[g['SNS'], float(s['SNS'])], TW1=[g['TW1'], float(s['TW1'])], TD=[g['TD'], float(s['TD'])],
                                               ME=[m['errors'], int(s['motion_errors'])])
    else:
        folder, key, occupied = VOLUME[name]
        feats = json.loads((ROOT / folder / 'features.json').read_text())['frames']
        if name == 'Tangaroa':
            diag = json.loads((ROOT / folder / 'reference.json').read_text())['domain_diagonal']
        else:
            c = np.load(ROOT / 'data/real/paper1_suite/square-cylinder3d/coordinates.npz')
            diag = float(np.linalg.norm([np.ptp(c['x']), np.ptp(c['y']), np.ptp(c['z'])]))
        out['diagonal'] = dict(value=float(diag), rule='stored domain diagonal')
        for label, method in [('kappa RG-MTM-P', 'RG-MTM-P'), ('kappa RG-MTM-R 0.2', 'RG-MTM-R')]:
            r = score(d, d['old'][label], p, feats, diag, occupied); s = stored(name, method)
            out['reproduction'][method] = dict(SNS=[r['SNS'], float(s['SNS'])], TW1=[r['TW1'], float(s['TW1'])], TD=[r['TD'], float(s['TD'])],
                                               ME=[r['ME_errors'], int(s['motion_errors'])])
    for method in METHODS:
        s = stored(name, method)
        out['baselines'][method] = dict(SNS=float(s['SNS']), TW1=float(s['TW1']), TD=float(s['TD']),
                                        ME_errors=int(s['motion_errors']), ME_clear=int(s['N_clear']))
    for setting in SETTINGS:
        t0 = time.perf_counter(); rows = layouts(d, p, setting)
        r = score(d, [row['x'] for row in rows], p, feats, out['diagonal']['value'], occupied)
        if name in RASTER:
            un = module('unified_run', ROOT / 'experiments/unified/run.py'); import pickle, replicate
            key = RASTER[name]
            ds = pickle.loads((ROOT / 'results/pm25_2000/dataset.pkl').read_bytes()) if key == 'pm25_2000' else replicate.LOADERS[key]()
            _, check = un.render(ds['sc'], rows, p, ds['nominal'])
            r['raster'] = dict(length=check['length'], max_barrier_discrepancy=check['max_barrier_discrepancy'],
                               max_anchor_rounding=check['max_anchor_rounding'],
                               max_raster_topology=float(max(row['raster_topology'] for row in rows)))
        r['seconds'] = time.perf_counter() - t0
        tag = setting if setting == 'projection' else f'eps={setting:g}'; out['settings'][tag] = r
        print(name, tag, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k in ('SNS', 'TW1', 'TD', 'ME_errors', 'ME_clear')},
              r.get('raster', ''), flush=True)
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or n1.DATASETS:
        r = run(name)
        (OUT / f'{name.replace(".", "").lower()}.json').write_text(json.dumps(r, indent=1))
