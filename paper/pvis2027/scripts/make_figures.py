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


# ---------------------------------------------------------------- Fig. 4: position--topology frontier (N2)
def fig_frontier():
    F = {n: json.loads((RES / f'frontier20261027/{FILE[n]}.json').read_text())['methods'] for n in NAMES}
    fig, axes = plt.subplots(2, 4, figsize=(7.0, 3.0)); axes = axes.ravel()
    keys = [k for k in F['Ring'] if k.startswith('eps=')] + ['projection']
    for ax, n in zip(axes, NAMES):
        ms = [F[n][k] for k in keys]; x = [100 * m['NMLE_max'] for m in ms]
        for key, col, mk, lab in [('E_inf', C['A'], 'o', r'worst $E_\infty$'), ('E_pool', C['light'], 's', r'mean $E_{pool}$')]:
            y = [100 * m[key] for m in ms]
            ax.plot(x[:-1], y[:-1], '-', marker=mk, ms=2.6, lw=1, color=col, label=lab)
            ax.plot(x[-2:], y[-2:], ':', lw=.9, color=col)
            ax.plot(x[-1], y[-1], marker='*', ms=6, color=col, mec='k', mew=.3, ls='none')
        for k, xi, yi in zip(keys, x, [100 * m['E_inf'] for m in ms]):
            if k in ('eps=0', 'eps=0.02', 'eps=0.1', 'projection') and (k == 'projection' or abs(xi - x[-1]) + abs(yi - 100 * ms[-1]['E_inf']) > .3):
                lab = r'$\infty$' if k == 'projection' else '%g' % (100 * float(k[4:]))
                ax.annotate(lab, (xi, yi), xytext=(2, 2.5), textcoords='offset points', fontsize=5.4, color='#333')
        pool = [WIDTH[n]['n1'].get(f'unified pool, eps={e:g}') for e in (0, .02, .1)]
        if all(pool):
            ax.plot([100 * m['NMLE_max'] for m in pool], [100 * m['E_inf'] for m in pool], 'x:', ms=3, lw=.8, color=C['base'],
                    label='earlier pool, worst')
        ax.set_title(LABEL[n], pad=2); ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
        ax.set_ylim(bottom=0); ax.set_xlim(left=-1)
        ax.tick_params(labelsize=5.8)
    for ax in axes[4:7]: ax.set_xlabel('Worst merge error NMLE (%)', fontsize=6.2)
    for ax in (axes[0], axes[4]): ax.set_ylabel('Displacement (%)', fontsize=6.4)
    h, l = axes[0].get_legend_handles_labels(); axes[7].axis('off')
    h += [plt.Line2D([], [], marker='*', ms=6, color=C['A'], mec='k', mew=.3, ls='none')]
    l += [r'projection ($\varepsilon=\infty$)']
    axes[7].legend(h, l, loc='center', fontsize=6.2, handlelength=1.6)
    axes[7].text(.5, .1, r'labels: $\varepsilon$ in %', transform=axes[7].transAxes, ha='center', fontsize=6)
    fig.subplots_adjust(hspace=.45, wspace=.28); save(fig, 'fig_frontier')


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


# ---------------------------------------------------------------- Storms case (N5)
def barrier_marks(row, V, R, canvas, origin, threshold=1e-3):
    """Normalized positions of barriers whose displayed merge differs from the source by > threshold*R."""
    o = list(row['order']); b = np.asarray(row['barriers'], float); n = len(o)
    z = np.asarray(row['z'], float)[o]; w = np.asarray(row['w'], float)[o]; V = np.asarray(V, float)
    err = np.zeros(max(n - 1, 0))
    for i in range(n):
        for j in range(i + 1, n):
            g = i + int(np.argmax(b[i:j])); err[g] = max(err[g], abs(b[g] - V[o[i], o[j]]))
    return [((z[g] + w[g] / 2 + z[g + 1] - w[g + 1] / 2) / 2 - origin) / canvas for g in range(n - 1) if err[g] > threshold * R]


def storms_case():
    cache = DATA / 'storms_case.json'
    if cache.exists(): return json.loads(cache.read_text())
    d = n1.DATASETS['Storms'](); p = params(d); R = d['scalar_range']; L = p.canvas
    saved = json.loads((RES / 'unified20261025/era5.json').read_text())['regimes']
    q = [np.asarray(v, float) for v in d['references']]
    worst = lambda xs: [float(np.max(np.abs(np.asarray(x, float) - qq)) / L) for x, qq in zip(xs, q)]
    out = dict(worst={k: worst([r['x'] for r in saved[k]['rows']]) for k in ('topology_time', 'topology_geometry')})
    rows10 = None
    for e in (0, .1):
        rows, _ = n1b_rows(d, e); out['worst'][f'ours_{e:g}'] = worst([r['x'] for r in rows])
        if e: rows10 = rows
    out['nmle_10'] = [float(r['delta']) / R for r in rows10]
    out['marks_10'] = [barrier_marks(r, V, R, L, p.canvas_origin) for r, V in zip(rows10, d['merge'])]
    DATA.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(out)); return out


def fig_storms():
    M = maps_for('Storms', 'era5'); qs = json.loads((DATA / 'q_era5.json').read_text()); S = storms_case()
    titles = [('topology_time', 'TMTM-type objective'), ('topology_geometry', 'ST-MTM-type objective'),
              ('ours_0', r'Ours, $\varepsilon=0$'), ('ours_0.1', r'Ours, $\varepsilon=10\%$, relaxed barriers marked')]
    vmin = min(np.nanmin(M[k]) for k, _ in titles); vmax = max(np.nanmax(M[k]) for k, _ in titles)
    fig = plt.figure(figsize=(7.0, 3.35))
    g = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 1, .045], height_ratios=[1, .42], hspace=.32, wspace=.12)
    for col, (k, title) in enumerate(titles):
        ax = fig.add_subplot(g[0, col]); F = M[k].shape[1]
        im = ax.imshow(M[k], origin='lower', aspect='auto', interpolation='nearest', cmap='RdBu_r', vmin=vmin, vmax=vmax,
                       extent=[-.5, F - .5, 0, 1], rasterized=True)
        for t, qq in enumerate(qs): ax.plot([t] * len(qq), qq, '.', ms=1.3, color='k', mec='none')
        if k == 'ours_0.1':
            for t, ms in enumerate(S['marks_10']):
                if ms: ax.plot([t] * len(ms), ms, '_', ms=3.2, mew=1.1, color='#FFD000')
        ax.set_title(title, pad=3, fontsize=6.6); ax.set_xticks([0, F - 1]); ax.tick_params(labelsize=5.8, length=2)
        ax.set_yticks([0, .5, 1] if col == 0 else [])
        if col == 0: ax.set_ylabel('Storms\nreference axis', fontsize=6.5)
    cb = fig.colorbar(im, cax=fig.add_subplot(g[0, 4])); cb.ax.tick_params(labelsize=5.5, length=2); cb.set_label('MSLP (hPa)', fontsize=6)
    t = np.arange(len(qs))
    gb = g[1, :4].subgridspec(1, 2, wspace=.22)
    ax = fig.add_subplot(gb[0])
    for k, col, lab in [('topology_time', C['base'], 'TMTM-type'), ('topology_geometry', C['D'], 'ST-MTM-type'),
                        ('ours_0', C['A'], r'ours $\varepsilon=0$'), ('ours_0.1', C['C'], r'ours $\varepsilon=10\%$')]:
        ax.plot(t, 100 * np.array(S['worst'][k]), lw=.8, color=col, label=lab)
    ax.set_ylabel('Worst displacement (%)', fontsize=6.2); ax.set_xlabel('Time step', fontsize=6.2, labelpad=1)
    ax.legend(fontsize=5.6, ncol=4, loc='upper left', bbox_to_anchor=(0, 1.3), handlelength=1.2, columnspacing=.8)
    ax.set_xlim(0, t[-1]); ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True); ax.tick_params(labelsize=5.8)
    ax = fig.add_subplot(gb[1])
    ax.bar(t, 100 * np.array(S['nmle_10']), width=1, color='#E0A800')
    ax.axhline(10, color='k', lw=.6, ls='--'); ax.text(t[-1], 10.3, r'cap $\varepsilon$', ha='right', va='bottom', fontsize=5.6)
    ax.set_ylabel('Merge error (%)', fontsize=6.2); ax.set_xlabel(r'Time step ($\varepsilon=10\%$)', fontsize=6.2, labelpad=1)
    ax.set_xlim(-.5, t[-1] + .5); ax.set_ylim(0, 11.5); ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
    ax.tick_params(labelsize=5.8)
    save(fig, 'fig_storms')


# ---------------------------------------------------------------- Teaser and pipeline: one real Storms frame
T_STAR = 61
LETTERS = 'ABCDEFGH'
PAL = [C['A'], C['B'], C['C'], C['D'], '#E69F00', C['light']]


def storms_frame():
    cache = DATA / 'storms_frame.json'
    if cache.exists(): return json.loads(cache.read_text())
    import replicate
    ds = replicate.LOADERS['era5'](); sc = ds['sc']; d = n1.DATASETS['Storms'](); p = params(d)
    t = T_STAR; ids = list(sc['ids'][t]); coords = np.asarray(sc['coords'])
    saved = json.loads((RES / 'unified20261025/era5.json').read_text())['regimes']
    rows0, _ = n1b_rows(d, 0); rows10, _ = n1b_rows(d, .1)
    pick = lambda r: dict(order=[int(v) for v in r['order']], x=list(map(float, r['x'])), z=list(map(float, r['z'])),
                          w=list(map(float, r['w'])), barriers=list(map(float, r['barriers'])), delta=float(r['delta']),
                          cap=float(r.get('cap', np.nan)))
    out = dict(t=t, date=str(sc['dates'][t]), canvas=p.canvas, origin=p.canvas_origin, scalar_range=d['scalar_range'],
               field=np.asarray(sc['fields'][t]).tolist(), x=sorted(set(coords[:, 0].tolist())), y=sorted(set(coords[:, 1].tolist())),
               extrema=coords[ids].tolist(), q=list(map(float, d['references'][t])), V=np.asarray(d['merge'][t]).tolist(),
               measures=list(map(float, d['measures'][t])), tmtm_x=list(map(float, saved['topology_time']['rows'][t]['x'])),
               ours0=pick(rows0[t]), ours10=pick(rows10[t]), direction=[0.9998129355353527, -0.019341508115477836])
    DATA.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(out)); return out


def _labels(F):
    """Letters by reference order (A = westmost)."""
    rank = np.argsort(np.argsort(F['q'])); return [LETTERS[r] for r in rank], [PAL[r % len(PAL)] for r in rank]


def _field(ax, F, letters, cols, proj=True):
    X, Y = np.array(F['x']), np.array(F['y']); Z = np.array(F['field'])
    ax.imshow(Z, origin='lower', extent=[X[0], X[-1], Y[0], Y[-1]], cmap='RdBu_r', vmin=975, vmax=1040, interpolation='bilinear')
    ax.contour(X, Y, Z, levels=np.arange(960, 1050, 8), colors='k', linewidths=.25, alpha=.45)
    ybase = Y[0] - .1 * (Y[-1] - Y[0])
    for (ex, ey), l, c in zip(F['extrema'], letters, cols):
        ax.plot(ex, ey, 'o', ms=4.5, mfc=c, mec='white', mew=.6)
        ax.text(ex + 2, ey + 2, l, fontsize=6.5, color='k', weight='bold')
        if proj: ax.plot([ex, ex], [ey, ybase], ':', lw=.6, color=c, clip_on=False)
    if proj:
        ax.annotate('', xy=(X[-1], ybase), xytext=(X[0], ybase), arrowprops=dict(arrowstyle='->', lw=.8), annotation_clip=False)
        ax.text(X[-1], ybase - 5.5, 'reference axis $q$ (west $\\to$ east)', ha='right', va='top', fontsize=5.8)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(X[0], X[-1]); ax.set_ylim(Y[0], Y[-1])
    for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(.5)


def fig_teaser():
    F = storms_frame(); M = maps_for('Storms', 'era5'); letters, cols = _labels(F); t = F['t']
    L, o = F['canvas'], F['origin']
    fig = plt.figure(figsize=(7.0, 2.35))
    g = fig.add_gridspec(1, 4, width_ratios=[1.05, 1.25, 1.25, .04], wspace=.16)
    ax = fig.add_subplot(g[0]); _field(ax, F, letters, cols)
    ax.set_title(f'(a) Pressure minima, {F["date"][:10]} 12 UTC', fontsize=6.6, pad=3)
    for k, (key, title, xs) in enumerate([('topology_time', '(b) Hierarchy-first layout (TMTM-type)', F['tmtm_x']),
                                          ('ours_0', r'(c) Ours: exact hierarchy, position certified', F['ours0']['x'])]):
        ax = fig.add_subplot(g[k + 1]); Mk = M[key]; T = Mk.shape[1]
        im = ax.imshow(Mk, origin='lower', aspect='auto', interpolation='nearest', cmap='RdBu_r', vmin=975, vmax=1040,
                       extent=[-.5, T - .5, 0, 1], rasterized=True)
        ax.axvspan(t - .5, t + .5, color='k', alpha=.18, lw=0)
        us = [(x - o) / L for x in xs]; ys = _spread(us, .075)
        for u, yl, q, l, c in zip(us, ys, F['q'], letters, cols):
            v = (q - o) / L
            ax.plot([t - 7, t], [v, u], lw=.7, color=c, zorder=3)
            ax.plot(t - 7, v, '>', ms=3, color=c, mec='white', mew=.3, zorder=4)
            ax.plot(t, u, 'o', ms=3.6, mfc=c, mec='white', mew=.5, zorder=4)
            ax.plot([t + 1.5, t + 8], [u, yl], lw=.5, color='k'); ax.text(t + 9, yl, l, fontsize=6, va='center', weight='bold')
        ax.set_title(title, fontsize=6.6, pad=3); ax.set_xticks([0, t, T - 1]); ax.set_xticklabels(['0', f'{t}', f'{T - 1}'], fontsize=5.6)
        ax.set_yticks([0, .5, 1] if k == 0 else []); ax.tick_params(labelsize=5.6, length=2); ax.set_xlabel('Time step (12 h)', fontsize=6, labelpad=1)
        if k == 0: ax.set_ylabel('Map axis', fontsize=6.2)
    cb = fig.colorbar(im, cax=fig.add_subplot(g[3])); cb.ax.tick_params(labelsize=5.3, length=2); cb.set_label('MSLP (hPa)', fontsize=5.8)
    save(fig, 'fig_teaser')


def _spread(vals, gap):
    """Label positions at least ``gap`` apart, as close as possible to ``vals`` (within [0, 1])."""
    idx = np.argsort(vals); pos = np.array(vals, float)[idx]
    for i in range(1, len(pos)): pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = max(0., pos[-1] - .97) if len(pos) else 0.; pos -= shift
    for i in range(len(pos) - 2, -1, -1): pos[i] = min(pos[i], pos[i + 1] - gap)
    out = np.empty_like(pos); out[idx] = pos; return list(out)


def _critical_pair(V, q):
    from rgmtm.order_certificate import hierarchy, _blocks
    nodes, root = hierarchy(V); q = np.asarray(q); best = (0, None, None, None)
    for k, ch in _blocks(nodes, root, 0.):
        for a in range(len(ch)):
            for b in range(a + 1, len(ch)):
                X, Y = nodes[ch[a]]['leaves'], nodes[ch[b]]['leaves']
                c = min(q[X].max() - q[Y].min(), q[Y].max() - q[X].min())
                if c > best[0]: best = (c, X, Y, k)
    return best, nodes, root


def _tree(ax, V, order, letters, cols, nodes, root, highlight=()):
    pos = {leaf: i for i, leaf in enumerate(order)}; xy = {}
    def place(k):
        if not nodes[k]['children']:
            xy[k] = (pos[k], nodes[k]['level']); return xy[k]
        pts = [place(c) for c in nodes[k]['children']]
        xy[k] = (np.mean([p[0] for p in pts]), nodes[k]['level']); return xy[k]
    place(root)
    for k, d in nodes.items():
        for c in d['children']:
            ax.plot([xy[c][0], xy[c][0], xy[k][0]], [xy[c][1], xy[k][1], xy[k][1]], lw=.9, color='#555' if k not in highlight else C['B'])
    for leaf, i in pos.items():
        ax.plot(i, nodes[leaf]['level'], 'D', ms=4, color=cols[leaf], mec='white', mew=.4)
        ax.text(i, nodes[leaf]['level'] - 1.6, letters[leaf], ha='center', va='top', fontsize=6, weight='bold')
    top = nodes[root]['level']; ax.plot([xy[root][0]] * 2, [top, top + 2.5], lw=.9, color='#555')
    ax.set_xticks([]); ax.set_xlim(-.6, len(order) - .4); ax.tick_params(labelsize=5.5, length=2)


def _marked(r, V, R, threshold=1e-3):
    o = r['order']; b = np.asarray(r['barriers']); n = len(o); err = np.zeros(max(n - 1, 0))
    for i in range(n):
        for j in range(i + 1, n):
            g = i + int(np.argmax(b[i:j])); err[g] = max(err[g], abs(b[g] - V[o[i], o[j]]))
    return {g for g in range(n - 1) if err[g] > threshold * R}


def fig_pipeline():
    F = storms_frame(); letters, cols = _labels(F); q = np.array(F['q']); L, o = F['canvas'], F['origin']
    V = np.array(F['V']); R = F['scalar_range']; n = len(q)
    (cost, X, Y, node), nodes, root = _critical_pair(V, q)
    fig = plt.figure(figsize=(7.0, 2.5))
    g = fig.add_gridspec(1, 5, width_ratios=[1.25, 1.05, .95, 1.15, 1.1], wspace=.6)
    # (a) input
    ax = fig.add_subplot(g[0]); _field(ax, F, letters, cols, proj=True)
    ax.set_title('(a) Field, extrema,\nreferences $q_i$', fontsize=6.4, pad=2)
    # (b) merge tree and bound
    ax = fig.add_subplot(g[1]); mid = F['ours0']['order']
    _tree(ax, V, mid, letters, cols, nodes, root, highlight=(node,))
    lo = min(nodes[k]['level'] for k in nodes) - 4
    ax.set_ylabel('Merge level (hPa)', fontsize=5.8); ax.set_ylim(lo - 7, nodes[root]['level'] + 4)
    yh = lo - 1
    ax2 = ax.inset_axes([0, -.02, 1, .2]); ax2.set_xlim(0, 1); ax2.set_ylim(-1, 2.2); ax2.axis('off')
    for S, c, yy in [(X, C['A'], 1.2), (Y, C['B'], 0)]:
        a, b = (q[S].min() - o) / L, (q[S].max() - o) / L
        ax2.plot([a, b], [yy, yy], lw=2.2, color=c, solid_capstyle='butt')
        ax2.plot([a, b], [yy, yy], '|', ms=5, mew=1.2, color=c)
        ax2.text(b + .03, yy, ''.join(sorted(letters[i] for i in S)), fontsize=5.4, ha='left', va='center', color=c)
    ax2.text(.5, -1.2, r'hull overlap $\Rightarrow\ \nu^*=%.1f\%%$' % (100 * cost / (2 * L)), ha='center', va='top', fontsize=5.8)
    ax.set_title('(b) Merge tree and\ncertified bound', fontsize=6.4, pad=2)
    # (c) budgeted orders
    ax = fig.add_subplot(g[2]); ax.set_xlim(-.2, 1.2); ax.set_ylim(-.35, 2.5); ax.axis('off')
    for yy, key, lab in [(2.0, 'ours0', r'$\varepsilon=0$'), (.9, 'ours10', r'$\varepsilon=10\%$')]:
        r = F[key]; d = r['delta'] / R
        for k, leaf in enumerate(r['order']):
            u = k / (n - 1)
            ax.add_patch(plt.Rectangle((u - .07, yy - .18), .14, .36, color=cols[leaf], lw=0))
            ax.text(u, yy, letters[leaf], ha='center', va='center', fontsize=6, color='white', weight='bold')
        ax.text(.5, yy + .36, lab + r', $\delta^*=%.1f\%%$' % (100 * d), fontsize=5.6, ha='center')
    ax.text(.5, -.25, 'exact merge cost checked\nfor every candidate order', ha='center', fontsize=5.6, color='#333')
    ax.set_title('(c) Budgeted\nleaf order', fontsize=6.4, pad=2)
    # (d) barriers + anchored layout
    ax = fig.add_subplot(g[3]); M = maps_for('Storms', 'era5'); col = M['ours_0.1'][:, F['t']]
    u = np.linspace(0, 1, len(col)); ax.plot(u, col, lw=.9, color='#333')
    r = F['ours10']
    for leaf in range(n):
        x = (r['x'][leaf] - o) / L; qq = (q[leaf] - o) / L; z0 = (r['z'][leaf] - r['w'][leaf] / 2 - o) / L; z1 = (r['z'][leaf] + r['w'][leaf] / 2 - o) / L
        ax.add_patch(plt.Rectangle((z0, 966), z1 - z0, 3.2, color=cols[leaf], lw=0, clip_on=False))
        ax.plot(x, V[leaf, leaf], 'o', ms=3.6, mfc=cols[leaf], mec='white', mew=.4, zorder=4)
        ax.plot(qq, 962, '^', ms=3, color=cols[leaf], clip_on=False)
    oo = r['order']
    for k, bv in enumerate(r['barriers']):
        xm = ((r['z'][oo[k]] + r['w'][oo[k]] / 2 + r['z'][oo[k + 1]] - r['w'][oo[k + 1]] / 2) / 2 - o) / L
        ax.plot([xm - .03, xm + .03], [bv, bv], lw=1.6, color=C['B'] if k in _marked(r, V, R) else '#333')
    ax.text(.02, 1033, 'bars: intervals; ticks: barriers\n(orange: relaxed)', fontsize=5, va='top')
    ax.set_ylim(960, 1036); ax.set_xlim(0, 1); ax.set_xticks([0, .5, 1]); ax.tick_params(labelsize=5.5, length=2)
    ax.set_xlabel(r'map axis (triangles: $q_i$)', fontsize=5.8, labelpad=1); ax.set_ylabel('Profile $\\psi$ (hPa)', fontsize=5.8)
    ax.set_title('(d) Optimal barriers and\ncapped anchor placement', fontsize=6.4, pad=2)
    # (e) map with disclosure
    ax = fig.add_subplot(g[4]); S = storms_case(); t = F['t']; w0, w1 = t - 14, t + 14
    ax.imshow(M['ours_0.1'][:, w0:w1 + 1], origin='lower', aspect='auto', interpolation='nearest', cmap='RdBu_r', vmin=975, vmax=1040,
              extent=[w0 - .5, w1 + .5, 0, 1], rasterized=True)
    for tt in range(w0, w1 + 1):
        if S['marks_10'][tt]: ax.plot([tt] * len(S['marks_10'][tt]), S['marks_10'][tt], '_', ms=3.2, mew=1.1, color='#FFD000')
    ax.axvspan(t - .5, t + .5, color='k', alpha=.18, lw=0)
    ax.set_yticks([]); ax.set_xticks([w0, t, w1]); ax.tick_params(labelsize=5.5, length=2)
    ax2 = ax.inset_axes([0, -.36, 1, .17]); ax2.bar(range(w0, w1 + 1), [100 * v for v in S['nmle_10'][w0:w1 + 1]], width=1, color='#E0A800')
    ax2.set_xlim(w0 - .5, w1 + .5); ax2.set_ylim(0, 10); ax2.set_xticks([]); ax2.set_yticks([0, 10]); ax2.tick_params(labelsize=5, length=1.5)
    ax2.text(w1 + .5, 10, r'$d_{top}$ %', fontsize=5, ha='right', va='bottom')
    ax.set_title('(e) Map with marked\nrelaxed barriers', fontsize=6.4, pad=2)
    save(fig, 'fig_pipeline')


# ---------------------------------------------------------------- Cross-method comparison
def compare_data():
    import csv
    rows = list(csv.DictReader((RES / 'stmtm_completion20261026/unified_metrics.csv').open()))
    st = lambda n, m: next(r for r in rows if r['dataset'] == n and r['method'] == m)
    out = {}
    for n in NAMES:
        F = json.loads((RES / f'frontier20261027/{FILE[n]}.json').read_text())['methods']
        Q = json.loads((RES / f'metrics_n1c20261027/{FILE[n]}.json').read_text())['settings']
        me = lambda c: 100 * c['ME_errors'] / c['ME_clear']
        d = {}
        for m, key in [('TMTM', 'TMTM'), ('ST-MTM', 'ST-MTM'), (r'$\kappa$ R20 (earlier)', 'RG-MTM-R')]:
            r = st(n, key)
            d[m] = dict(NROE=float(r['NROE']), NMLE=float(r['NMLE_max']), ME=100 * int(r['motion_errors']) / int(r['N_clear']),
                        SNS=float(r['SNS']), TW=float(r['TW1']))
        for m, fk, qk in [('Projection', 'projection', 'projection'), (r'Ours, $\varepsilon=0$', 'eps=0', 'eps=0'),
                          (r'Ours, $\varepsilon=10\%$', 'eps=0.1', 'eps=0.1')]:
            d[m] = dict(NROE=100 * F[fk]['NROE'], NMLE=100 * F[fk]['NMLE_max'], ME=me(Q[qk]), SNS=Q[qk]['SNS'], TW=Q[qk]['TW1'])
        out[n] = d
    return out


def fig_compare():
    D = compare_data(); methods = list(D[NAMES[0]])
    style = {'TMTM': ('s', C['base']), 'ST-MTM': ('D', C['D']), r'$\kappa$ R20 (earlier)': ('^', C['light']),
             'Projection': ('*', '#000000'), r'Ours, $\varepsilon=0$': ('o', C['A']), r'Ours, $\varepsilon=10\%$': ('o', C['C'])}
    panels = [('NROE', 'Order error NROE (%)', 'lower'), ('NMLE', 'Worst merge error (%)', 'lower'),
              ('ME', 'Motion error ME (%)', 'lower'), ('SNS', 'Distance stress SNS', 'lower'), ('TW', 'Trustworthiness TW', 'higher')]
    fig, axes = plt.subplots(1, 5, figsize=(7.0, 2.05)); x = np.arange(len(NAMES)); off = np.linspace(-.3, .3, len(methods))
    for ax, (key, title, better) in zip(axes, panels):
        for k, m in enumerate(methods):
            mk, col = style[m]
            ax.plot(x + off[k], [D[n][m][key] for n in NAMES], mk, ms=3.6 if mk != '*' else 5, color=col, mec='white' if mk != '*' else col,
                    mew=.3, ls='none', label=m)
        if key == 'NROE':
            ax.hlines([100 * BUDGET[n]['nu_mean'] for n in NAMES], x - .42, x + .42, color='k', lw=1.1, zorder=1, label=r'lower bound $\nu^*$')
        ax.set_xticks(x); ax.set_xticklabels([LABEL[n] for n in NAMES], fontsize=5.2, rotation=90)
        ax.set_title(title + (r' $\downarrow$' if better == 'lower' else r' $\uparrow$'), fontsize=6.2, pad=3)
        ax.tick_params(labelsize=5.4, length=2); ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
        for v in x[:-1] + .5: ax.axvline(v, color=C['grid'], lw=.4)
        ax.axvline(4.5, color='#999', lw=.6)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=7, fontsize=6, loc='upper center', bbox_to_anchor=(.5, 1.1), handlelength=1.2, columnspacing=1.0)
    fig.subplots_adjust(wspace=.38); save(fig, 'fig_compare')


# ---------------------------------------------------------------- Reference direction in 3-D
def fig_direction():
    fig = plt.figure(figsize=(7.0, 2.1))
    g = fig.add_gridspec(1, 5, width_ratios=[.85, 1.3, .18, .85, 1.3], wspace=.42)
    for k, n in enumerate(['Tangaroa', 'Cylinder']):
        D = json.loads((RES / f'reference_direction20261027/{n.lower()}.json').read_text())
        dirs = np.array([r['direction'] for r in D['sweep']]); nu = 100 * np.array([r['nu_mean'] for r in D['sweep']])
        ax = fig.add_subplot(g[3 * k])
        th = np.arccos(np.clip(dirs[:, 2], -1, 1)); ph = np.arctan2(dirs[:, 1], dirs[:, 0]); rr = np.sqrt(2) * np.sin(th / 2)
        sc = ax.scatter(rr * np.cos(ph), rr * np.sin(ph), c=nu, s=9, cmap='viridis', lw=0)
        ax.add_patch(plt.Circle((0, 0), 1, fill=False, lw=.5, color='#999'))
        K = D['key_directions']
        for lab, mk in [('x', 'o'), ('y', 's'), ('z', '^'), ('stored', '*'), ('smallest bound', 'P')]:
            v = np.array(K[lab]['direction'], float); v = -v if v[2] < 0 else v
            t_, p_ = np.arccos(np.clip(v[2], -1, 1)), np.arctan2(v[1], v[0]); r_ = np.sqrt(2) * np.sin(t_ / 2)
            ax.plot(r_ * np.cos(p_), r_ * np.sin(p_), mk, ms=6 if mk == '*' else 4, mfc='white' if mk != '*' else C['B'], mec='k', mew=.6)
            if lab in ('x', 'y', 'z'): ax.annotate(lab, (r_ * np.cos(p_), r_ * np.sin(p_)), xytext=(3, 3), textcoords='offset points', fontsize=6)
        ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(-1.12, 1.12); ax.set_ylim(-1.12, 1.12)
        cax = ax.inset_axes([.1, -.12, .8, .05]); cb = fig.colorbar(sc, cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize=5.2, length=2); cb.set_label(r'$\nu^*$ (%)', fontsize=5.6, labelpad=1)
        ax.set_title(n, fontsize=7, pad=2)
        ax = fig.add_subplot(g[3 * k + 1]); labs = ['x', 'y', 'z', 'stored', 'smallest bound']; x = np.arange(len(labs)); w = .2
        for j, (key, col, lab) in enumerate([('nu_mean', '#000000', r'$\nu^*$'), ('ours_NROE', C['A'], r'ours, $\varepsilon=0$'),
                                              ('ST-MTM_NROE', C['D'], 'ST-MTM'), ('TMTM_NROE', C['base'], 'TMTM')]):
            ax.bar(x + (j - 1.5) * w, [100 * K[l][key] for l in labs], w, color=col, label=lab, lw=0)
        ax.set_xticks(x); ax.set_xticklabels(['x', 'y', 'z', 'stored', 'best'], fontsize=5.6)
        ax.set_ylabel('Order error NROE (%)', fontsize=5.8); ax.tick_params(labelsize=5.4, length=2)
        ax.yaxis.grid(True, color=C['grid'], lw=.5); ax.set_axisbelow(True)
        if k == 0: fig.legend(*ax.get_legend_handles_labels(), ncol=4, fontsize=6, loc='upper center', bbox_to_anchor=(.5, 1.06), handlelength=1, frameon=False)
    save(fig, 'fig_direction')


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


def table_quality():
    """N1c: SNS, TW (k=1) and motion error of baselines and our layouts."""
    rows = []
    for n in NAMES:
        Q = json.loads((RES / f'metrics_n1c20261027/{FILE[n]}.json').read_text()); b = Q['baselines']; s = Q['settings']
        cols = [b['TMTM'], b['ST-MTM'], s['eps=0'], s['eps=0.1'], s['projection']]
        me = lambda c: 100 * (c['ME_errors'] / c['ME_clear'])
        sns = [c['SNS'] for c in cols]; tw = [c['TW1'] for c in cols]; mes = [me(c) for c in cols]
        fmt = lambda v, best, f: (r'\textbf{' + f % v + '}') if v == best else f % v
        rows.append(f"{LABEL[n]} & " + ' & '.join(fmt(v, min(sns), '%.3f') for v in sns) + ' & '
                    + ' & '.join(fmt(v, max(tw), '%.3f') for v in tw) + ' & '
                    + ' & '.join(fmt(v, min(mes), '%.1f') for v in mes) + r' \\')
        if n == 'Ring': rows.append(r'\midrule')
    (TAB / 'tab_quality.tex').write_text('\n'.join(rows) + '\n')


def table_compare():
    """All values behind Fig. compare (supplement)."""
    D = compare_data(); rows = []
    for n in NAMES:
        for k, (m, v) in enumerate(D[n].items()):
            name = LABEL[n] if k == 0 else ''
            rows.append(f"{name} & {m} & {v['NROE']:.2f} & {v['NMLE']:.2f} & {v['ME']:.1f} & {v['SNS']:.3f} & {v['TW']:.3f} \\\\")
        rows.append(r'\midrule')
    (TAB / 'tab_compare.tex').write_text('\n'.join(rows[:-1]) + '\n')


def table_direction():
    rows = []
    for n in ['Tangaroa', 'Cylinder']:
        K = json.loads((RES / f'reference_direction20261027/{n.lower()}.json').read_text())['key_directions']
        for k, lab in enumerate(['x', 'y', 'z', 'stored', 'smallest bound']):
            r = K[lab]; dvec = '(' + ', '.join('%.2f' % v for v in r['direction']) + ')'
            rows.append(f"{n if k == 0 else ''} & {lab} {dvec} & {100 * r['nu_mean']:.2f} & {100 * r['ours_NROE']:.2f} & "
                        f"{100 * r['ST-MTM_NROE']:.2f} & {100 * r['TMTM_NROE']:.2f} & {100 * r['ours_tau_mean']:.2f} & {100 * r['width_lower_mean']:.2f} \\\\")
        rows.append(r'\midrule')
    (TAB / 'tab_direction.tex').write_text('\n'.join(rows[:-1]) + '\n')


if __name__ == '__main__':
    FIG.mkdir(exist_ok=True)
    for f in [tables, table_quality, table_compare, table_direction, fig_concept, fig_bound, fig_frontier, fig_tangaroa, fig_maps, fig_storms,
              fig_teaser, fig_pipeline, fig_compare, fig_direction]:
        print(f.__name__, flush=True); f()
