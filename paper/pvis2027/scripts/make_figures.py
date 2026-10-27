"""Figures and tables of the PacificVis 2027 manuscript, from saved experiment results.

Reads code/results/{order_budget,order_layout,order_width}20261027 and the
unified20261025 maps; recomputes only what the results do not store:
N1b layouts for the rendered maps (Ring, OLR: inputs ship with the repository)
and per-frame tau on Tangaroa. Derived data are cached in figures/data/.

    cd paper/pvis2027 && PYTHONPATH=../../code/src python scripts/make_figures.py
"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parents[1]; CODE = HERE.parents[1] / 'code'
FIG = HERE / 'figures'; DATA = FIG / 'data'; TAB = HERE / 'tables'
sys.path[:0] = [str(CODE.parent), str(CODE / 'src'), str(CODE / 'analysis'), str(CODE)]
from rgmtm.error_budget import Parameters
from rgmtm.order_certificate import budget_order
from rgmtm.interval_order import interval_scores, width_order


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


n1 = module('n1', CODE / 'experiments/order_layout/run.py')
RES = CODE / 'results'
NAMES = ['Storms', 'Wildfires', 'OLR', 'PM2.5', 'Ring', 'Tangaroa', 'Cylinder']
FILE = {n: n.replace('.', '').lower() for n in NAMES}
LABEL = {n: (r'PM$_{2.5}$' if n == 'PM2.5' else n) for n in NAMES}
BUDGET = {n: json.loads((RES / f'order_budget20261027/{FILE[n]}.json').read_text()) for n in NAMES}
WIDTH = {n: json.loads((RES / f'order_width20261027/{FILE[n]}.json').read_text()) for n in NAMES}
EPS = [0, .02, .05, .1]
C = dict(A='#0072B2', B='#D55E00', C='#009E73', D='#CC79A7', base='#7B8790', grid='#DFE4E8', light='#56B4E9')
plt.rcParams.update({'font.family': 'Arial', 'font.size': 7, 'pdf.fonttype': 42, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': .6, 'xtick.major.width': .6, 'ytick.major.width': .6,
                     'legend.frameon': False, 'axes.titlesize': 7})


def save(fig, stem):
    fig.savefig(FIG / f'{stem}.pdf', bbox_inches='tight', pad_inches=.02); plt.close(fig)


def wm(n, e): return WIDTH[n]['methods'][f'width order + cap, eps={e:g}']


def params(d): return Parameters(**{k: v for k, v in d['parameters'].items() if k in n1.PARAM_FIELDS})


def n1b_rows(d, e):
    p = params(d); R = d['scalar_range']; L = p.canvas; orders = []
    for V, q, m in zip(d['merge'], d['references'], d['measures']):
        pt = budget_order(V, q, L, e * R, n1.TIE * R)
        orders.append(width_order(V, q, p.width_scale * np.asarray(m, float), p, e * R, n1.TIE * R, point=pt))
    return n1.capped_sequence(d, orders, R, e, p), orders


# ---------------------------------------------------------------- Fig. 2: concept of Theorem A
def fig_concept():
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.25), sharey=True)
    X = [1.0, 3.2, 5.6]; Y = [2.4, 4.4]          # reference positions of two sibling subtrees
    for ax, (first, title) in zip(axes, [('X', 'X before Y'), ('Y', 'Y before X')]):
        seq = [(q, 'X') for q in X] + [(q, 'Y') for q in Y] if first == 'X' else [(q, 'Y') for q in Y] + [(q, 'X') for q in X]
        pos = np.linspace(.6, 6.2, 5)
        for (q, g), x in zip(seq, pos):
            col = C['A'] if g == 'X' else C['B']
            ax.plot([q, x], [1, 0], color=col, lw=.8); ax.plot(q, 1, 'o', ms=3.2, color=col); ax.plot(x, 0, 's', ms=3.2, color=col)
        ax.hlines([1.25], min(X), max(X), color=C['A'], lw=2); ax.hlines([1.4], min(Y), max(Y), color=C['B'], lw=2)
        cost = (max(X) - min(Y)) if first == 'X' else (max(Y) - min(X))
        ax.set_title(f'{title}: cost {cost:.1f}/2', pad=1, fontsize=6.5)
        ax.set_yticks([0, 1]); ax.set_yticklabels(['map', 'reference']); ax.set_xticks([]); ax.set_ylim(-.2, 1.5)
        ax.spines['bottom'].set_visible(False); ax.tick_params(length=0)
    axes[0].text(min(X) - .15, 1.25, 'X', color=C['A'], fontsize=6, ha='right', va='center'); axes[0].text(min(Y) - .15, 1.4, 'Y', color=C['B'], fontsize=6, ha='right', va='center')
    save(fig, 'fig_concept')


# ---------------------------------------------------------------- Fig. 3: necessary vs avoidable order error
def fig_bound():
    fig, ax = plt.subplots(figsize=(3.5, 1.55))
    x = np.arange(len(NAMES)); w = .26
    for k, (m, col, lab) in enumerate([('TMTM', C['base'], 'TMTM'), ('ST-MTM', C['D'], 'ST-MTM'), (None, C['A'], r'Ours, $\varepsilon=0$')]):
        vals = np.array([100 * (BUDGET[n]['methods'][m]['NROE_mean'] if m else wm(n, 0)['NROE']) for n in NAMES])
        nu = np.array([100 * BUDGET[n]['nu_mean'] for n in NAMES])
        ax.bar(x + (k - 1) * w, np.minimum(vals, nu), w, color=col, edgecolor='white', lw=.3)
        ax.bar(x + (k - 1) * w, np.maximum(vals - nu, 0), w, bottom=np.minimum(vals, nu), color=col, alpha=.38, edgecolor='white', lw=.3, label=lab)
    ax.set_xticks(x); ax.set_xticklabels([LABEL[n] for n in NAMES], fontsize=6.0)
    ax.set_xlim(-.55, len(NAMES) - .45)
    ax.set_ylabel('Order error NROE (%)'); ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
    ax.legend(ncol=3, fontsize=6, loc='upper left', handlelength=1, columnspacing=.8, bbox_to_anchor=(0, 1.13))
    ax.text(.995, .97, r'solid: necessary ($\nu^*$); light: avoidable', transform=ax.transAxes, ha='right', va='top', fontsize=5.6, color='#333')
    save(fig, 'fig_bound')


# ---------------------------------------------------------------- Fig. 5: budget response
def fig_tradeoff():
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 1.6))
    cols = dict(zip(NAMES, [C['B'], '#E69F00', C['A'], C['D'], C['C'], '#000000', C['base']]))
    for n in NAMES:
        ms = [wm(n, e) for e in EPS]; xs = [100 * e for e in EPS]
        for ax, key in zip(axes, ['E_pool', 'E_inf', 'NMLE_max']):
            ax.plot(xs, [100 * m[key] for m in ms], '-o', ms=2.4, lw=1, color=cols[n], label=LABEL[n])
        pool = {e: WIDTH[n]['n1'].get(f'unified pool, eps={e:g}') for e in (0, .02, .1)}
        if all(pool.values()):
            for ax, key in zip(axes[:2], ['E_pool', 'E_inf']):
                ax.plot([0, 2, 10], [100 * pool[e][key] for e in (0, .02, .1)], ':', lw=.9, color=cols[n])
    axes[2].plot([0, 10], [0, 10], color='#000', lw=.6, ls='--'); axes[2].text(6.8, 8.3, r'cap $\varepsilon$', fontsize=6, rotation=33)
    for ax, t in zip(axes, ['Mean displacement $E_{pool}$ (%)', 'Worst displacement $E_\\infty$ (%)', 'Worst merge error (%)']):
        ax.set_xlabel(r'Topology budget $\varepsilon$ (%)'); ax.set_title(t, pad=3); ax.set_xticks([0, 2, 5, 10])
        ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=7, fontsize=6, loc='upper center', bbox_to_anchor=(.5, 1.1), handlelength=1.4, columnspacing=1.2)
    axes[1].text(.98, .97, 'dotted: earlier candidate pool', transform=axes[1].transAxes, ha='right', va='top', fontsize=5.6)
    fig.subplots_adjust(wspace=.32); save(fig, 'fig_tradeoff')


# ---------------------------------------------------------------- Fig. 6: Tangaroa per-frame tau
def tangaroa_frames():
    cache = DATA / 'tangaroa_tau.json'
    if cache.exists(): return json.loads(cache.read_text())
    d = n1.DATASETS['Tangaroa'](); p = params(d); R = d['scalar_range']; L = p.canvas; out = {}
    kp = d['old']['kappa RG-MTM-P']
    out['kappa_P'] = [float(interval_scores([np.argsort(x, kind='stable')], p.width_scale * np.asarray(m, float), q, p)[0][0]) / L
                      for x, m, q in zip(kp, d['measures'], d['references'])]
    for e in (0, .05):
        rows = dict(n1=[], n1b=[], lower=[])
        for V, q, m in zip(d['merge'], d['references'], d['measures']):
            pt = budget_order(V, q, L, e * R, n1.TIE * R); w = p.width_scale * np.asarray(m, float)
            r = width_order(V, q, w, p, e * R, n1.TIE * R, point=pt)
            rows['n1'].append(r['point_tau'] / L); rows['n1b'].append(r['tau'] / L); rows['lower'].append(r['lower'] / L)
        out[f'eps={e:g}'] = rows
    DATA.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(out)); return out


def fig_tangaroa():
    T = tangaroa_frames(); t = np.arange(len(T['kappa_P']))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 1.45), sharey=True)
    for ax, e in zip(axes, ['0', '0.05']):
        r = T[f'eps={e}']
        ax.fill_between(t, 0, 100 * np.array(r['lower']), color=C['grid'], lw=0, label='lower bound')
        if e == '0': ax.plot(t, 100 * np.array(T['kappa_P']), lw=.8, color='#444444', ls=(0, (2, 1)), label=r'$\kappa$ construction P')
        ax.plot(t, 100 * np.array(r['n1']), lw=.7, color=C['B'], label='point-model order (N1)')
        ax.plot(t, 100 * np.array(r['n1b']), lw=.9, color=C['A'], label='width-aware order (ours)')
        ax.set_title(r'$\varepsilon=%s$%%' % ('0' if e == '0' else '5'), pad=2); ax.set_xlabel('Time step')
        ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True); ax.set_xlim(0, t[-1])
    axes[0].set_ylabel(r'Interval cost $\tau_t/L$ (%)')
    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, ncol=4, fontsize=6, loc='upper center', bbox_to_anchor=(.5, 1.13))
    fig.subplots_adjust(wspace=.06); save(fig, 'fig_tangaroa')


# ---------------------------------------------------------------- Fig. 1/4: rendered maps
def maps_for(name, key):
    """Saved unified maps (same renderer) plus newly rendered N1b layouts at eps 0 and 10%."""
    cache = DATA / f'maps_{key}.npz'
    if cache.exists(): return dict(np.load(cache))
    un = module('un', CODE / 'experiments/unified/run.py'); import replicate
    d = n1.DATASETS[name](); ds = replicate.LOADERS[key](); p = params(d); out = {}
    saved = np.load(RES / f'unified20261025/{key}_maps.npz')
    out['topology_time'] = saved['topology_time']; out['topology_geometry'] = saved['topology_geometry']
    for e in (0, .1):
        rows, _ = n1b_rows(d, e); m, chk = un.render(ds['sc'], rows, p, ds['nominal']); out[f'ours_{e:g}'] = m
    out['q'] = np.array([(np.asarray(q) - p.canvas_origin) / p.canvas for q in d['references']], dtype=object)
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, **{k: v for k, v in out.items() if k != 'q'})
    (DATA / f'q_{key}.json').write_text(json.dumps([list(map(float, v)) for v in out['q']]))
    return dict(np.load(cache))


def fig_maps():
    sets = [('OLR', 'olr', 'RdBu_r'), ('Ring', 'ring', 'magma')]
    fig = plt.figure(figsize=(7.0, 2.9)); g = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 1, .05], hspace=.42, wspace=.12)
    titles = [('topology_time', 'TMTM-type objective'), ('topology_geometry', 'ST-MTM-type objective'),
              ('ours_0', r'Ours, $\varepsilon=0$'), ('ours_0.1', r'Ours, $\varepsilon=10\%$')]
    for row, (name, key, cmap) in enumerate(sets):
        M = maps_for(name, key); qs = json.loads((DATA / f'q_{key}.json').read_text())
        vmin = min(np.nanmin(M[k]) for k, _ in titles); vmax = max(np.nanmax(M[k]) for k, _ in titles)
        for col, (k, title) in enumerate(titles):
            ax = fig.add_subplot(g[row, col]); F = M[k].shape[1]
            im = ax.imshow(M[k], origin='lower', aspect='auto', interpolation='nearest', cmap=cmap, vmin=vmin, vmax=vmax,
                           extent=[-.5, F - .5, 0, 1], rasterized=True)
            for t, q in enumerate(qs):
                ax.plot([t] * len(q), q, '.', ms=1.3, color='k', mec='none')
            ax.set_xticks([0, F - 1]); ax.set_yticks([0, .5, 1] if col == 0 else []); ax.tick_params(labelsize=5.8, length=2)
            if row == 0: ax.set_title(title, pad=3)
            if col == 0: ax.set_ylabel(f'{name}\nreference axis', fontsize=6.5)
            if row == 1: ax.set_xlabel('Time step', fontsize=6.3, labelpad=1)
        cb = fig.colorbar(im, cax=fig.add_subplot(g[row, 4])); cb.ax.tick_params(labelsize=5.5, length=2)
        cb.set_label('OLR (W m$^{-2}$)' if key == 'olr' else 'Scalar', fontsize=6)
    save(fig, 'fig_maps')


# ---------------------------------------------------------------- Tables
def tables():
    TAB.mkdir(exist_ok=True); rows = []
    for n in NAMES:
        b = BUDGET[n]; w0, w2, w10 = wm(n, 0), wm(n, .02), wm(n, .1)
        rows.append(f"{LABEL[n]} & {b['frames']} & {b['leaves'][0]}--{b['leaves'][1]} & {100 * b['nu_mean']:.2f} & "
                    f"{100 * b['methods']['TMTM']['NROE_mean']:.2f} & {100 * b['methods']['ST-MTM']['NROE_mean']:.2f} & "
                    f"\\textbf{{{100 * w0['NROE']:.2f}}} & {100 * w0['E_pool']:.2f} & {100 * w0['E_inf']:.2f} & "
                    f"{100 * w2['E_inf']:.2f} & {100 * w2['NMLE_max']:.2f} & {100 * w10['E_inf']:.2f} & {100 * w10['NMLE_max']:.2f} \\\\")
        if n == 'Ring': rows.append(r'\midrule')
    (TAB / 'tab_main.tex').write_text('\n'.join(rows) + '\n')
    rows = []
    for n in ['Tangaroa', 'Cylinder']:
        k = WIDTH[n]['n1']
        for lab, m, e in [(r'$\kappa$ P', k['kappa RG-MTM-P'], None), (r'N1, $\varepsilon=0$', k['certified order + cap, eps=0'], None),
                          (r'Ours, $\varepsilon=0$', wm(n, 0), 0), (r'$\kappa$ R2', k['kappa RG-MTM-R 0.02'], None),
                          (r'N1, $\varepsilon=2\%$', k['certified order + cap, eps=0.02'], None), (r'Ours, $\varepsilon=2\%$', wm(n, .02), .02)]:
            nm = f"{100 * m['NMLE_max']:.2f}" if 'NMLE_max' in m else ('0' if lab.endswith(' P') else 'no cap')
            rows.append(f"{n} & {lab} & {100 * m['E_pool']:.2f} & {100 * m['E_inf']:.2f} & {100 * m['NROE']:.2f} & {100 * m['jump_mean']:.2f} & {nm} \\\\")
        rows.append(r'\midrule')
    (TAB / 'tab_volume.tex').write_text('\n'.join(rows[:-1]) + '\n')


if __name__ == '__main__':
    FIG.mkdir(exist_ok=True)
    for f in [tables, fig_concept, fig_bound, fig_tradeoff, fig_tangaroa, fig_maps]:
        print(f.__name__, flush=True); f()
