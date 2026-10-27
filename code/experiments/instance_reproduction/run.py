"""N3: TMTM and ST-MTM as instances of the formulation, and TMTM's own objective.

Problem (3) of the manuscript lists TMTM (eps=0, B=inf, objective E_O, layout
fully determined by the leaf order) and ST-MTM (eps=0, B=inf, E_G + lambda E_M
then E_W for a fixed order) as instances. For each input whose scalar data ship
with the repository (Ring, OLR, PM2.5) this script checks, with the audited
routines of experiments/baseline_audit (which covered Storms and Wildfires):

1. TMTM: the layout rebuilt from the native branch decisions equals the pinned
   official C++ core (arc intervals and anchors), and keeps the tree exactly;
2. ST-MTM: for the native order, the native anchors and intervals satisfy the
   KKT conditions of Eq. 1 and Eq. 2 (they are the exact optimum of the
   instance); the order heuristic (SciPy OLO, Sec. 4.1.1) is compared with
   exhaustive enumeration of its own adjacency objective;
3. TMTM's objective: for every step, all 2^k branch decisions of the next tree
   are enumerated against the same previous layout; the greedy choice is
   compared with this per-step optimum of Eqs. 2--3.

Volumetric ST-MTM KKT residuals are read from the stored solver checks.
"""
import json, pickle, subprocess, sys, time
from itertools import combinations, product
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'analysis'), str(ROOT / 'src')]
from rgmtm.baselines import tmtm as tm, stmtm as st
from experiments import era5 as ep
from experiments.baseline_audit import audit
import replicate as rp, general_method as gm

OUT = ROOT / 'results/instance_reproduction20261027'
MAX_DECISIONS = 12


def load(name):
    return pickle.loads((ROOT / 'results/pm25_2000/dataset.pkl').read_bytes()) if name == 'pm25' else rp.LOADERS[name]()


def tmtm_enumeration(trees, layouts, pair_objectives):
    """Per-step optimum of Eqs. 2-3 over all branch decisions, previous layout fixed."""
    steps = []
    for t in range(len(trees) - 1):
        target = trees[t + 1]
        nodes = sorted(k for k, node in target.nodes.items() if len(node.child_arcs) >= 2)
        if len(nodes) > MAX_DECISIONS:
            steps.append(dict(step=t, decisions=len(nodes), enumerated=False)); continue
        overlap = tm.spatial_overlap_matrix(trees[t], target)
        best = np.inf
        for flags in product([False, True], repeat=len(nodes)):
            layout = tm.linearize_tree(target, dict(zip(nodes, flags)))
            best = min(best, tm.objective_between(trees[t], layouts[t], target, layout, overlap))
        greedy = float(pair_objectives[t])
        steps.append(dict(step=t, decisions=len(nodes), enumerated=True, greedy=greedy, optimum=float(best),
                          gap=greedy - float(best), relative_gap=(greedy - best) / greedy if greedy > 0 else 0.))
    done = [s for s in steps if s['enumerated']]
    return dict(steps=len(steps), enumerated=len(done), greedy_optimal=sum(s['gap'] <= 1e-9 for s in done),
                greedy_total=float(sum(s['greedy'] for s in done)), optimum_total=float(sum(s['optimum'] for s in done)),
                max_relative_gap=float(max((s['relative_gap'] for s in done), default=0.)),
                mean_relative_gap=float(np.mean([s['relative_gap'] for s in done])) if done else 0.,
                scope='per step against the same previous greedy layout; not a sequence-wide optimum',
                per_step=steps)


def stmtm_checks(ds, sc, trees):
    span = ds['native_span']
    p = gm.Parameters(canvas=span, canvas_origin=float(min(ds['lo'][0], 0)), width_scale=.5 * span / ds['domain_area'],
                      gap=span / 240, extra_budget=span / 120, rho=.5)
    b = ep.run_method(sc, 'ST-MTM', p, canvas=span, length=ds['nominal'], refine_raster=False, strict_checks=False)
    rec = b['records']; params = st.LayoutParameters(**rec['parameters']); continuous = rec['continuous']
    eq1 = eq2 = 0.; gaps = []; heuristic_order_frames = 0
    for t, (fr, ids, c) in enumerate(zip(sc['frames'], sc['ids'], continuous)):
        order = tuple(c['ordering']); orders = audit.all_orders(fr); assert order in orders
        centroids = {v: fr.leaf_centroid(v) for v in ids}
        cost = lambda o: sum(np.linalg.norm(centroids[i] - centroids[j]) for i, j in zip(o[:-1], o[1:]))
        olo = st.optimal_hierarchical_leaf_order(fr); best = min(cost(o) for o in orders)
        gaps.append(float(cost(olo) - best)); heuristic_order_frames += abs(cost(olo) - best) > 1e-7
        temporal = None
        if t:
            prev = continuous[t - 1]; matches = sc['matches'][t]; rank = {v: j for j, v in enumerate(prev['ordering'])}
            temporal = {v: prev['anchors'][rank[matches[v]]] for v in order if v in matches}
        eq1 = max(eq1, audit.stress_kkt(fr, order, np.array(c['anchors']), params, temporal))
        eq2 = max(eq2, audit.interval_kkt(fr, order, np.array(c['anchors']), np.array(c['starts']), np.array(c['ends']), params))
    return dict(frames=len(continuous), eq1_kkt_relative_residual_max=eq1, eq2_kkt_relative_residual_max=eq2,
                olo_frames_above_exhaustive=int(heuristic_order_frames), olo_gap_max=float(max(gaps)),
                parameters=rec['parameters'])


def run(name, exe):
    t0 = time.perf_counter(); ds = load(name); sc = ds['sc']; trees = sc['trees']
    decisions, layouts, pair_objectives = tm.optimize_temporal_order(trees)
    official = audit.official_check(sc, layouts, decisions, exe)
    max_top = 0.
    for tree, fr, ids, lin in zip(trees, sc['frames'], sc['ids'], layouts):
        assert np.array_equal(np.sort(lin.vertex_at_position), np.arange(tree.sample_count))
        for arc in tree.arcs:
            ix = lin.position_of_vertex[list(tree.subtree_vertices(arc))]; assert max(ix) - min(ix) + 1 == len(ix)
        col = tree.values[lin.vertex_at_position]
        max_top = max(max_top, audit.topology(fr, ids, col, lin.position_of_vertex[ids], tree.kind))
    out = dict(dataset=name, frames=len(trees),
               TMTM=dict(official_core=official, merge_error_max=max_top, objective=tmtm_enumeration(trees, layouts, pair_objectives)),
               STMTM=stmtm_checks(ds, sc, trees), seconds=None)
    out['seconds'] = time.perf_counter() - t0
    e = out['TMTM']['objective']
    print(name, 'TMTM official mismatches', len(official['mismatches']), '| greedy optimal', e['greedy_optimal'], '/', e['enumerated'],
          'max rel gap %.3f' % e['max_relative_gap'], '| ST Eq1/Eq2 KKT %.1e %.1e' % (out['STMTM']['eq1_kkt_relative_residual_max'], out['STMTM']['eq2_kkt_relative_residual_max']),
          '| OLO above exhaustive', out['STMTM']['olo_frames_above_exhaustive'], flush=True)
    return out


def volumetric():
    out = {}
    for key in ['tangaroa', 'square-cylinder3d']:
        checks = json.loads((ROOT / f'results/stmtm_completion20261026/{key}/solver_checks.json').read_text())
        out[key] = dict(frames=len(checks),
                        eq1_stationarity_max=max(c['projection']['stationarity_residual'] for c in checks),
                        eq1_primal_max=max(c['projection']['primal_residual'] for c in checks),
                        eq2_stationarity_max=max(c['intervals']['stationarity_residual'] for c in checks))
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True); tmp = ROOT / 'tmp/instance_reproduction'; tmp.mkdir(parents=True, exist_ok=True)
    exe = tmp / 'official_core_fixture'
    subprocess.run(['clang++', '-std=c++17', '-O2', str(ROOT / 'experiments/baseline_audit/official_core_fixture.cpp'), '-o', str(exe)], check=True)
    for name in sys.argv[1:] or ['ring', 'olr', 'pm25']:
        (OUT / f'{name}.json').write_text(json.dumps(run(name, exe), indent=1))
    (OUT / 'volumetric_stmtm.json').write_text(json.dumps(volumetric(), indent=1))
    print('volumetric', volumetric())
