"""Event-centred Anatol preview from genuine hourly fields and existing P/R solvers.

Reuses the frozen full-month direction, canvas and scalar range. Solves the
forward sequence from its original start through the final displayed hour;
therefore no event-window reset or event-specific direction fit is introduced.
Outputs are isolated from the manuscript and frozen experiment evidence.
"""
from pathlib import Path
import sys, json, hashlib, time
import numpy as np

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
CODE = PAPER.parent / 'code'
sys.path[:0] = [str(CODE / 'analysis'), str(CODE), str(CODE / 'src'), str(PAPER / 'scripts')]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from netCDF4 import Dataset
from scipy.interpolate import RegularGridInterpolator
from experiments import era5 as ep
import relax_hierarchy as rh, general_method as gm, conflict_strategies as cs, filling
from geo import Era5Geo
from anchor_aligned_renderer import render_display

INPUT = PAPER / 'evidence/fig1/december1999_xaxis/fields.npz'
SAVED = PAPER / 'evidence/fig1/december1999_data_direction/results.npz'
SOURCE = CODE / 'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc'
START, END = 24, 96
SNAPSHOTS = [36, 42, 54, 66, 78, 90]
CAPS = [.5, 1, 1.5, 2, 3, 5, 20]
METHODS = ['P'] + [f'R{k:g}' for k in CAPS]
TRACK = 10
CM = plt.get_cmap('RdBu_r')
NORM = Normalize(-35, 35)
ACCENT = '#c36b13'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False,
        default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x.item()), encoding='utf-8')


def prepare():
    a, old = np.load(INPUT), np.load(SAVED)
    path = HERE / 'event_results.npz'
    provenance = dict(input_sha256=sha(INPUT), saved_sha256=sha(SAVED),
        solver_sha256={str(p.relative_to(CODE)): sha(p) for p in [
            CODE/'analysis/relax_hierarchy.py', CODE/'analysis/conflict_strategies.py',
            CODE/'analysis/filling.py', CODE/'src/rgmtm/error_budget.py',
            CODE/'src/rgmtm/reference_guided.py']},
        event_window=[START, END], snapshots=SNAPSHOTS, thresholds_percent=CAPS)
    if path.exists() and json.loads((HERE/'metrics.json').read_text())['provenance'] == provenance:
        return a, old, np.load(path), json.loads((HERE/'metrics.json').read_text())
    before = time.perf_counter()
    sc = ep.scene_from_fields(a['fields'][:END+1], a['coords'], float(a['geometry'][2]), 'join', max_leaves=None)
    for t, ids in enumerate(sc['ids']):
        assert np.array_equal(ids, old['leaf'][t, :len(ids)])
        assert np.array_equal(sc['tracks'][t], old['tracks'][t, :len(ids)])
    p = gm.universal_parameters(*old['geometry'], 49*49*float(a['geometry'][2]))
    qs = [old['qnorm'][t, :len(ids)]*p.canvas+p.canvas_origin for t, ids in enumerate(sc['ids'])]
    theta = gm.THETA_FRACTION*p.canvas
    scalar_range = float(np.ptp(a['fields']))
    full = [rh.node_tree(fr, ids) for fr, ids in zip(sc['frames'], sc['ids'])]
    gates = []
    for fr, ids, areas, q, struct in zip(sc['frames'], sc['ids'], sc['areas'], qs, full):
        w = p.width_scale*np.asarray(areas)
        free, _ = gm.tau_free(w, q, p)
        hier, _ = rh.best_tau(struct, w, q, p)
        gates.append((hier, free))
    arrays = dict(dates=a['dates'][:END+1], tracks=old['tracks'][:END+1],
        qnorm=old['qnorm'][:END+1], leaf=old['leaf'][:END+1],
        lonlat=old['lonlat'][:END+1], values=old['value'][:END+1],
        direction=old['direction'], geometry=old['geometry'])
    metrics = dict(provenance=provenance, methods={}, scalar_range_hPa=scalar_range,
        direction=old['direction'], canvas=old['geometry'],
        computation='Forward prefix f0..f96, with full-month frozen reference and scalar range; display f24..f96.',
        identity='Track 10 is the computed scalar feature associated with the published Anatol event region/time; no independent physical-identity validation.',
        original_results_modified=False)
    sl = slice(START, END+1)
    for method in METHODS:
        structs, logs = [], []
        for t, (fr, ids, areas, q, s0, (hier, free)) in enumerate(zip(sc['frames'], sc['ids'], sc['areas'], qs, full, gates)):
            if method != 'P' and hier-free > theta:
                st, steps, relaxed_tau = rh.relax_frame_threshold(fr, ids, p.width_scale*np.asarray(areas), q, p, theta, free, float(method[1:])/100*scalar_range)
            else:
                st, steps, relaxed_tau = s0, [], hier
            structs.append(st)
            logs.append(dict(frame=t, relaxed_nodes=len(steps), steps=steps, tau=relaxed_tau))
        print('Solving', method, flush=True)
        rows = cs.solve_weighted_sequence(sc, qs, {}, p) if method == 'P' else rh.solve_sequence_structs(sc, qs, structs, p)
        if method == 'P': cs.validate_weighted(sc, rows, p)
        else: rh.validate_relaxed(sc, rows, structs, p)
        maps, skeletons, resolution = rh.render(sc, rows, p, 4096)
        assert resolution == 4096
        if method != 'P':
            for t, (fr, sk) in enumerate(zip(sc['frames'], skeletons)):
                maps[:, t], _ = filling.optimal_fill(maps[:, t], list(sk.ordering), sk.anchors, fr, 'join')
        anchors = np.full_like(arrays['qnorm'], np.nan)
        for t, row in enumerate(rows): anchors[t, :len(row['x'])] = (row['x']-p.canvas_origin)/p.canvas
        merge = rh.merge_errors(sc, maps, skeletons, 'join')
        direct = np.array([max(e, default=0.) for e in merge])
        assert np.isfinite(maps).all()
        # Check every extremum against the actual rendered pixel, not an analytic proxy.
        for t, (fr, sk) in enumerate(zip(sc['frames'], skeletons)):
            for k, ix in zip(sk.ordering, sk.anchors):
                assert abs(maps[int(ix),t]-fr.values[k]) < 1e-7
        if method == 'P':
            assert max(direct) < 1e-7
            assert all(ep.signature(maps[:,t], 'join') == ep.signature(tree) for t,tree in enumerate(sc['trees']))
        arrays['map_'+method], arrays['norm_'+method], arrays['merge_'+method] = maps, anchors, direct
        position = np.concatenate([abs(row['x']-row['reference'])/p.canvas*100 for row in rows[START:END+1]])
        changed = np.max(abs(maps[:,sl]-arrays['map_P'][:,sl]), axis=0) > 1e-7
        metrics['methods'][method] = dict(max_position_error_percent_L=float(position.max()),
            mean_position_error_percent_L=float(position.mean()), max_merge_error_hPa=float(max(direct[sl])),
            changed_hours_vs_P=int(changed.sum()), changed_hour_indices=(np.flatnonzero(changed)+START).tolist(),
            relaxed_hours=sum(log['relaxed_nodes']>0 for log in logs[START:END+1]), frame_log=logs[START:END+1])
        print(method, {k:v for k,v in metrics['methods'][method].items() if k not in ('frame_log',)}, flush=True)
    # The recomputed R20 must reproduce the existing full-month experiment on this prefix.
    metrics['verification'] = dict(max_R20_map_difference=float(np.max(abs(arrays['map_R20']-old['mapR'][:,:END+1]))),
        max_R20_anchor_difference=float(np.nanmax(abs(arrays['norm_R20']-old['normR'][:END+1]))),
        P_topology_verified_all_prefix_hours=True, all_extremum_pixels_verified=True,
        scientific_frames=int(END-START+1), computation_seconds=time.perf_counter()-before)
    assert metrics['verification']['max_R20_map_difference'] < 1e-6
    assert metrics['verification']['max_R20_anchor_difference'] < 1e-7
    np.savez_compressed(path, **arrays)
    dump(HERE/'metrics.json', metrics)
    return a, old, np.load(path), metrics


def raw_snapshots(a):
    path = HERE/'raw_snapshots.npz'
    if path.exists(): return np.load(path)
    with Dataset(SOURCE) as ds:
        lat, lon = np.asarray(ds['latitude'][:]), np.asarray(ds['longitude'][:])
        raw = []
        for t in SNAPSHOTS:
            i = int(a['source_indices'][t])
            raw.append(np.asarray(ds['msl'][i], float)/100-np.asarray(ds['msl'][i-96:i+96], float).mean(0)/100)
    np.savez_compressed(path, lat=lat, lon=lon, fields=raw, frames=SNAPSHOTS)
    return np.load(path)


def map_image(ax, matrix, tracks, positions, start, end, factor=9):
    dense, validation = render_display(dict(mapR=matrix[:,start:end+1], track=tracks[start:end+1], normR=positions[start:end+1]), factor=factor)
    ax.imshow(dense, origin='lower', aspect='auto', extent=(start-.5,end+.5,0,1), cmap=CM, norm=NORM, interpolation='bilinear')
    ax.set(xlim=(start-.5,end+.5), ylim=(0,1))
    return validation



if __name__ == '__main__':
    from render_teaser import render_teaser
    render_teaser(*prepare())
