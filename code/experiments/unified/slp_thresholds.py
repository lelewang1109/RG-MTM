"""ERA5 0/10/20% topology budgets, with an exhaustive feasibility audit.

Standalone follow-up; does not overwrite the published unified20261025 run.
Exact enumeration certifies feasibility, NOT global optimality of the QP
objective over all orders. Every setting uses the same augmented candidate pool.
"""
from pathlib import Path
from dataclasses import asdict
import csv
import hashlib
import json
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'src'), str(ROOT/'analysis')]
from rgmtm.error_budget import Parameters
from rgmtm.framework import cost_table
from rgmtm.unified import Controls, solve_unified_sequence
from experiments.unified.run import clean, dump, render, summary
import replicate

OUT = ROOT/'results/slp_thresholds20261026'
OLD = ROOT/'results/unified20261025/era5.json'
EPS = [0., .1, .2]
CAPS = [np.inf, .05]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_and_pools(j, p):
    pools, diagnostics = [], []
    for t, x in enumerate(j['frame_inputs']):
        tab = cost_table(p.width_scale*np.array(x['measures']), x['reference'],
                         x['merge_values'], p)
        assert tab['exact']
        original = set(map(tuple, x['candidate_orders']))
        pool = set(original)
        pos_ok = tab['tau'] <= .05*p.canvas+1e-9
        inverse = float(tab['delta'][pos_ok].min()/j['scalar_range']) if pos_ok.any() else np.inf
        if pos_ok.any():
            ix = np.flatnonzero(pos_ok)
            k = int(ix[np.argmin(tab['delta'][ix])])
            pool.add(tuple(tab['orders'][k]))
        for eps in EPS:
            admissible = tab['delta'] <= eps*j['scalar_range']+1e-9
            ix = np.flatnonzero(admissible)
            k = int(ix[np.argmin(tab['tau'][ix])])
            pool.add(tuple(tab['orders'][k]))
            old_ok = [i for i in ix if tuple(tab['orders'][i]) in original]
            old_tau = float(tab['tau'][old_ok].min()/p.canvas)
            best_tau = float(tab['tau'][k]/p.canvas)
            diagnostics.append(dict(frame=t, topology_budget=eps, features=len(x['reference']),
                exhaustive_orders=len(tab['orders']), original_pool_orders=len(original),
                min_position_budget=best_tau, original_pool_min_position_budget=old_tau,
                min_topology_for_position_5pct=inverse,
                free_packing_min_position=float(tab['tau'].min()/p.canvas),
                exact_feasible_at_5pct=best_tau <= .05+1e-9,
                original_pool_feasible_at_5pct=old_tau <= .05+1e-9,
                optimal_position_order=tab['orders'][k].tolist()))
        pools.append(sorted(pool))
    return pools, diagnostics


def key(eps, cap):
    return f'epsilon_{eps:g}_position_{cap:g}'


def render_with_gaps(sc, rows, p, nominal):
    if all(r is not None for r in rows):
        return render(sc, rows, p, nominal)
    # Render each witnessed column at its required resolution. No interpolation
    # across time and no previous-frame carry. Retain NaNs for absent witnesses.
    columns, checks = {}, {}
    for t, row in enumerate(rows):
        if row is None:
            continue
        sub = dict(frames=[sc['frames'][t]], ids=[sc['ids'][t]],
                   trees=[sc['trees'][t]], fields=sc['fields'])
        col, check = render(sub, [row], p, nominal)
        columns[t], checks[t] = col[:, 0], check
    length = max([nominal]+[len(v) for v in columns.values()])
    result = np.full((length, len(rows)), np.nan)
    for t, col in columns.items():
        if len(col) != length:
            # Re-render, rather than resampling a column at a different resolution.
            sub = dict(frames=[sc['frames'][t]], ids=[sc['ids'][t]],
                       trees=[sc['trees'][t]], fields=sc['fields'])
            col, checks[t] = render(sub, [rows[t]], p, length)
            col = col[:, 0]
        assert len(col) == length
        result[:, t] = col
    return result, dict(length=length, per_frame=checks,
                        missing='NaN columns; temporal history restarts after each missing frame')


def verify(rows, j, p, eps, cap, maps):
    """Reconstruct geometry and merge measurements from selected coordinates."""
    checks = []
    for t, row in enumerate(rows):
        x = j['frame_inputs'][t]
        if row is None:
            assert np.isnan(maps[:, t]).all()
            continue
        u, z, w, q = (np.array(row[k], float) for k in ['x', 'z', 'w', 'reference'])
        order = np.array(row['order'], int)
        V = np.array(x['merge_values'], float)
        b = np.array(row['barriers'], float)
        delta = max([abs(max(b[i:k])-V[order[i], order[k]])
                     for i in range(len(order)) for k in range(i+1, len(order))]+[0.])
        pos = float(np.max(abs(u-q))/p.canvas)
        assert delta <= eps*j['scalar_range']+1e-7
        assert pos <= cap+1e-7
        assert np.all(z-w/2 >= p.canvas_origin-1e-7)
        assert np.all(z+w/2 <= p.canvas_origin+p.canvas+1e-7)
        assert np.all(abs(u-z) <= p.rho*w/2+1e-7)
        assert np.all(np.diff(z[order]) >= (w[order][:-1]+w[order][1:])/2+p.gap-1e-7)
        assert np.isfinite(maps[:, t]).all()
        checks.append(dict(frame=t, reconstructed_topology=delta/j['scalar_range'],
                           reconstructed_position=pos))
    return dict(checked_frames=len(checks), max_topology=max(r['reconstructed_topology'] for r in checks),
                max_position=max(r['reconstructed_position'] for r in checks))


def export_figures(result, maps):
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'pdf.fonttype':42, 'svg.fonttype':'none'})
    T = result['frames']
    ticks = np.arange(0, 101, 10)
    cmap = plt.get_cmap('RdBu_r').copy()
    cmap.set_bad('#b8bec7')
    finite = [v[np.isfinite(v)] for v in maps.values()]
    vmin, vmax = min(a.min() for a in finite), max(a.max() for a in finite)
    result['display'] = dict(vmin=float(vmin), vmax=float(vmax), cmap='RdBu_r',
                             missing_color='#b8bec7', units='hPa')

    def panel(ax, eps, cap):
        k = key(eps, cap)
        r = result['settings'][k]
        im = ax.imshow(maps[k], origin='lower', aspect='auto', interpolation='nearest',
                       extent=[-50/(T-1), 100+50/(T-1), 0, 1],
                       cmap=cmap, vmin=vmin, vmax=vmax, rasterized=True)
        ax.set_xlim(-50/(T-1), 100+50/(T-1))
        ax.set_xticks(ticks)
        ax.set_xticklabels([f'{t}%' for t in ticks], fontsize=8)
        ax.set_yticks([0, .5, 1])
        ax.set_ylabel('Reference axis\n(normalized)', fontsize=9)
        ax.set_xlabel('Time progress (all 118 frames retained)', fontsize=9)
        btext = r'$B=\infty$' if np.isinf(cap) else r'$B=5\%$'
        ax.set_title(rf'$\varepsilon={eps:.0%}$'.replace('%',r'\%')+
                     f'   |   {btext}   |   {r["summary"]["feasible_frames"]}/{T} frames',
                     loc='left', fontsize=11, pad=6)
        return im

    def save(fig, stem):
        for ext in ['png', 'svg', 'pdf']:
            fig.savefig(OUT/f'{stem}.{ext}', dpi=220, bbox_inches='tight', pad_inches=.13)
        plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(13, 8.5), layout='constrained')
    fig.suptitle('Sea-level pressure: topology budgets in 10-percentage-point increments\n'
                 f'{result["dates"][0][:10]} to {result["dates"][-1][:10]}  |  shared geometry, objective and colour scale',
                 fontsize=13)
    for ax, eps in zip(axes, EPS):
        im = panel(ax, eps, np.inf)
    fig.colorbar(im, ax=axes, label='Rendered pressure (hPa)', shrink=.9, pad=.02)
    save(fig, 'slp_thresholds_0_10_20')

    fig, axes = plt.subplots(2, 3, figsize=(17, 7.3), layout='constrained')
    fig.suptitle('Sea-level pressure: the same topology budgets with two position caps\n'
                 'Top: no hard position cap. Bottom: every feature must stay within 5% of its reference. Gray = infeasible.',
                 fontsize=13)
    for row, cap in enumerate(CAPS):
        for col, eps in enumerate(EPS):
            im = panel(axes[row, col], eps, cap)
    fig.colorbar(im, ax=axes, label='Rendered pressure (hPa)', shrink=.9, pad=.015)
    save(fig, 'slp_position_budget_comparison')

    fig, axes = plt.subplots(2, 1, figsize=(13, 6.6), sharex=True, layout='constrained')
    for eps, color in zip(EPS, ['#333333', '#0072b2', '#d55e00']):
        r = [x for x in result['feasibility_audit'] if x['topology_budget'] == eps]
        axes[0].plot(np.arange(T), [100*x['min_position_budget'] for x in r],
                     label=rf'$\varepsilon={eps:.0%}$'.replace('%',r'\%'), c=color, lw=1.5)
    axes[0].axhline(5, color='#8e44ad', ls='--', lw=1.4, label='Position cap B = 5%')
    axes[0].set_ylabel('Minimum required\nposition allowance (%)')
    axes[0].legend(ncol=4, fontsize=9)
    axes[0].set_title('Exact feasibility over all feature permutations; QP objective optimization uses a shared candidate pool', fontsize=11)
    inverse = [x['min_topology_for_position_5pct']*100 for x in result['feasibility_audit'] if x['topology_budget'] == 0]
    axes[1].plot(np.arange(T), inverse, color='#8e44ad', lw=1.5)
    for y, color in zip([0, 10, 20], ['#333333', '#0072b2', '#d55e00']):
        axes[1].axhline(y, color=color, ls='--', lw=.9)
    axes[1].set_ylabel('Minimum topology\nallowance for B = 5% (%)')
    axes[1].set_xlabel('Frame (zero-based; 12 hours per step)')
    axes[1].set_xlim(0, T-1)
    save(fig, 'slp_missing_frame_diagnostics')


def main():
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    j = json.loads(OLD.read_text())
    p = Parameters(**j['parameters'])
    pools, diagnostics = audit_and_pools(j, p)
    print('Exact feasibility audit complete; loading original processed ERA5 fields', flush=True)
    ds = replicate.LOADERS['era5']()
    sc = ds['sc']
    field_sha = hashlib.sha256(np.asarray(sc['fields'], dtype='<f8').tobytes()).hexdigest()
    assert field_sha == j['field_sha256']
    assert len(sc['frames']) == j['frames'] == 118
    for t, old in enumerate(j['frame_inputs']):
        assert np.allclose(sc['centers'][t], old['centers'], rtol=0, atol=1e-10)
        assert np.allclose(sc['areas'][t], old['measures'], rtol=0, atol=1e-10)
        assert list(sc['tracks'][t]) == old['tracks']
    arrays = lambda name: [np.asarray(x[name]) for x in j['frame_inputs']]
    result = dict(dataset='ERA5 mean sea-level pressure', frames=j['frames'],
        dates=sc['dates'], scalar_range=j['scalar_range'], field_sha256=field_sha,
        parameters=j['parameters'], reference=j['reference'],
        frame_inputs=j['frame_inputs'], candidate_orders=pools,
        feasibility_audit=diagnostics, settings={},
        original_run_sha256=sha(OLD), original_run='unified20261025/era5.json',
        protocol='Same objective, fixed geometry, tracks, reference and common augmented order pool for all six settings. '
                 'Exhaustive order enumeration certifies budget feasibility. QP objective search remains candidate-based. '
                 'No missing-column carry; history restarts after a missing frame. All time steps retained.',
        source_sha256={f:sha(ROOT/f) for f in ['experiments/unified/slp_thresholds.py',
            'experiments/unified/run.py', 'src/rgmtm/unified.py', 'src/rgmtm/framework.py',
            'src/rgmtm/error_budget.py', 'analysis/era5_expanded.py']})
    maps = {}
    for cap in CAPS:
        for eps in EPS:
            k = key(eps, cap)
            print('SOLVE', k, flush=True)
            ctrl = Controls(topology_budget=eps, position_budget=cap)
            rows = solve_unified_sequence(arrays('centers'), arrays('measures'),
                [x['hierarchy'] for x in j['frame_inputs']], arrays('reference'),
                arrays('merge_values'), [x['tracks'] for x in j['frame_inputs']],
                pools, j['scalar_range'], ctrl, p, allow_infeasible=True)
            if np.isfinite(cap):
                expected = [x['exact_feasible_at_5pct'] for x in diagnostics if x['topology_budget'] == eps]
                assert [r is not None for r in rows] == expected
            else:
                assert all(r is not None for r in rows)
            maps[k], rc = render_with_gaps(sc, rows, p, ds['nominal'])
            checked = verify(rows, j, p, eps, cap, maps[k])
            result['settings'][k] = dict(controls=asdict(ctrl), rows=rows,
                summary=summary(rows, p), render=rc, verification=checked,
                missing_frames=[t for t,r in enumerate(rows) if r is None])
            print('DONE', k, clean(result['settings'][k]['summary']), flush=True)
            dump(OUT/'progress.json', dict(completed=list(result['settings']), seconds=time.time()-start))
    export_figures(result, maps)
    result['seconds'] = time.time()-start
    np.savez_compressed(OUT/'maps.npz', **maps)
    dump(OUT/'results.json', result)
    flat = [{**r, 'date':sc['dates'][r['frame']]} for r in diagnostics]
    for r in flat:
        del r['optimal_position_order']
    with (OUT/'frame_feasibility.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader(); writer.writerows(flat)
    dump(OUT/'manifest.json', dict(files_sha256={p.name:sha(p) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name not in ['manifest.json','progress.json']},
        checked_constraints=True, exact_feasibility=True, global_QP_order_optimality=False))
    print('EXPORTED', OUT, 'seconds', result['seconds'], flush=True)


if __name__ == '__main__':
    main()
