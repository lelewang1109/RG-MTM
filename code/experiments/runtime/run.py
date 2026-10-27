"""Runtime of the certified pipeline on the 917 frames, with the machine it ran on.

Bounds (Theorems A, C, A_w, C_w) are timed here on every frame for
eps in {0, 2, 5, 10}%. Ordering and QP times are read from the saved N1b run
(results/order_width20261027, same machine): ``search_seconds`` covers
budget_order + width_order (which also evaluate the bounds), and the QP time is
the remaining part of ``seconds`` (capped sequential QP plus metric evaluation).
"""
import importlib.util, json, platform, subprocess, sys, time
from pathlib import Path
import numpy as np, scipy
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from rgmtm.error_budget import Parameters
from rgmtm.order_certificate import certificate, chain_certificate
from rgmtm.interval_order import width_certificate, width_chain_certificate

spec = importlib.util.spec_from_file_location('order_layout_run', ROOT / 'experiments/order_layout/run.py')
n1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(n1)
OUT = ROOT / 'results/runtime20261027'
EPS = [0, .02, .05, .1]


def sysctl(key):
    try: return subprocess.run(['sysctl', '-n', key], capture_output=True, text=True, check=True).stdout.strip()
    except Exception: return None


def machine():
    memory = sysctl('hw.memsize')
    return dict(cpu=sysctl('machdep.cpu.brand_string') or platform.processor(), cores=sysctl('hw.ncpu'),
                performance_cores=sysctl('hw.perflevel0.physicalcpu'), efficiency_cores=sysctl('hw.perflevel1.physicalcpu'),
                memory_gb=int(memory) / 2**30 if memory else None, os=f'{platform.system()} {platform.mac_ver()[0] or platform.release()}',
                python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                qp_solver='SciPy SLSQP from a HiGHS LP feasible start (rgmtm.error_budget)', threads='single process, no parallelism')


def run(name):
    d = n1.DATASETS[name](); p = Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS})
    R = d['scalar_range']; L = p.canvas; frames = len(d['references']); leaves = [len(q) for q in d['references']]
    bounds = {}
    for e in EPS:
        t0 = time.perf_counter()
        for V, q, m in zip(d['merge'], d['references'], d['measures']):
            w = p.width_scale * np.asarray(m, float); b, tie = e * R, n1.TIE * R
            certificate(V, q, L, 2 * (b + tie)); chain_certificate(V, q, L, b, tie)
            width_certificate(V, q, w, p, 2 * (b + tie)); width_chain_certificate(V, q, w, p, b, tie)
        bounds[f'eps={e:g}'] = time.perf_counter() - t0
    saved = json.loads((ROOT / f'results/order_width20261027/{name.replace(".", "").lower()}.json').read_text())['methods']
    steps = {}
    for e in EPS:
        m = saved[f'width order + cap, eps={e:g}']
        steps[f'eps={e:g}'] = dict(ordering_seconds=m['search_seconds'], qp_seconds=m['seconds'] - m['search_seconds'],
                                   total_seconds=m['seconds'], bounds_seconds=bounds[f'eps={e:g}'])
    out = dict(dataset=name, frames=frames, leaves=[min(leaves), max(leaves)], steps=steps,
               per_frame_ms={k: {s: 1000 * v / frames for s, v in r.items()} for k, r in steps.items()})
    print(name, {k: {s: round(v, 2) for s, v in r.items()} for k, r in out['per_frame_ms'].items()}, flush=True)
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    result = dict(machine=machine(), protocol=__doc__.strip(), datasets=[run(n) for n in (sys.argv[1:] or n1.DATASETS)])
    tot = {k: sum(d['steps'][f'eps={e:g}'][k] for d in result['datasets'] for e in EPS)
           for k in ['bounds_seconds', 'ordering_seconds', 'qp_seconds', 'total_seconds']}
    result['totals_all_eps'] = tot
    (OUT / 'runtime.json').write_text(json.dumps(result, indent=1)); print(result['machine']); print(tot)
