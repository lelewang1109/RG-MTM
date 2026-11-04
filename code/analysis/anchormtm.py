"""Automatic-reference adapter; existing order search and QP remain unchanged.

The low-level adapter returns continuous layouts. anchor_mtm adds reconstruction. Existing experiment drivers
and their recorded reference protocols are deliberately not redirected here.
"""
from dataclasses import replace

import numpy as np
import general_method as gm
from rgmtm.error_budget import Parameters, reference_unit_direction
from rgmtm.unified import solve_budgeted_frame, DEFAULT_EPSILON0
from rgmtm.interval_order import width_order


def solve_anchored_sequence(centers, measures, hierarchies, extrema, merge_values,
                            tracks, lo, hi, scalar_range, p=Parameters(), *,
                            eta=None, direction=None, epsilon=None, epsilon0=DEFAULT_EPSILON0, reference=None, periodic_lengths=None):
    """Fit once, then use the existing heuristic order search and capped QP.

    Prefer epsilon (normalized extra budget). eta is the legacy absolute-budget
    compatibility argument, with epsilon0=0; it cannot be combined with epsilon.

    eta is an absolute continuous merge budget (zero for Exact Mode). Numerical
    solver tolerances are not folded into it. References and returned positions
    use raw projected coordinates on [origin, origin + extent]; subtract origin
    once, only when converting them to the paper's [0,L] convention.
    Width scale, gap, rho, beta and objective weights are caller supplied in the
    projected coordinate units. No experimental scale rule is changed here.
    """
    sizes = [len(v) for v in (centers, measures, hierarchies, extrema, merge_values, tracks)]
    if not sizes[0] or len(set(sizes)) != 1:
        raise ValueError('nonempty aligned sequences required')
    if eta is not None:
        if epsilon is not None: raise ValueError('choose epsilon, not both epsilon and legacy eta')
        epsilon, epsilon0 = eta/scalar_range, 0.
    epsilon = 0. if epsilon is None else epsilon
    eta = (epsilon0 + epsilon)*scalar_range
    if not np.isfinite(eta) or eta < 0 or epsilon < 0 or not np.isfinite(scalar_range) or scalar_range <= 0:
        raise ValueError('finite nonnegative eta and positive scalar range required')
    for c, e, ids in zip(centers, extrema, tracks):
        if np.asarray(e).shape != np.asarray(c).shape or len(ids) != len(c) or len(set(ids)) != len(ids):
            raise ValueError('aligned extrema, centers and distinct track IDs required')
    if reference is not None:
        ref = reference
    elif direction is None:
        ref = gm.auto_reference({'tracks': tracks,'centers':centers,'periodic_lengths':periodic_lengths}, extrema, np.asarray(lo), np.asarray(hi))
    else:
        from itertools import product
        a = reference_unit_direction(len(lo), direction)
        corners = np.array(list(product(*zip(lo, hi)))) @ a
        ref = dict(qs=[np.asarray(e) @ a for e in extrema], origin=float(corners.min()),
                   extent=float(np.ptp(corners)), kind='direction',
                   candidates={'direction': {'a': a.tolist(), 'manual': True}})
    p = replace(p, canvas=ref['extent'], canvas_origin=ref['origin'])
    rows = []
    for t, q in enumerate(ref['qs']):
        candidates = []
        order = width_order(merge_values[t], q, p.width_scale * np.asarray(measures[t]), p, eta, tie=0., collector=candidates)
        previous = previous_q = matched = None
        if t:
            old = {k: i for i, k in enumerate(tracks[t-1])}
            matched = np.array([k in old for k in tracks[t]])
            previous = np.array([rows[-1]['x'][old[k]] if k in old else 0. for k in tracks[t]])
            previous_q = np.array([ref['qs'][t-1][old[k]] if k in old else 0. for k in tracks[t]])
        row = solve_budgeted_frame(centers[t], measures[t], hierarchies[t], q,
            merge_values[t], scalar_range, epsilon, p, epsilon0=epsilon0,
            candidate_orders=candidates, previous=previous, previous_q=previous_q, matched=matched)
        order = dict(order, order=list(row['order']), tau=row['tau'], delta=row['delta'], nroe=row['nroe'])
        row['order_search'] = order
        rows.append(row)
    return dict(reference=ref, parameters=p, layouts=rows, rendered=False)


from dataclasses import dataclass
from time import perf_counter


@dataclass(frozen=True)
class FixedConfiguration:
    """Fixed per-sequence settings; epsilon is not stored in this configuration."""
    epsilon0: float = DEFAULT_EPSILON0
    parameters: Parameters | None = None
    raster_length: int = 2048


def prepare_sequence(scene, lo, hi, domain_measure, configuration=FixedConfiguration()):
    """Budget-independent reference preparation on already extracted/matched inputs."""
    from rgmtm.reference_points import reference_points_from_frames
    if not np.isfinite(configuration.epsilon0) or configuration.epsilon0 < 0:
        raise ValueError('finite nonnegative fixed epsilon0 required')
    if not np.isfinite(domain_measure) or domain_measure <= 0:
        raise ValueError('positive fixed domain measure required')
    ext = reference_points_from_frames(scene['frames'], scene['ids'], kind='extremum')
    ref = gm.auto_reference(scene, ext, np.asarray(lo), np.asarray(hi))
    p = configuration.parameters or gm.universal_parameters(ref['origin'], ref['extent'], domain_measure)
    p = replace(p, canvas=ref['extent'], canvas_origin=ref['origin'])
    scalar_range = float(np.ptp(scene['fields']))
    if not np.isfinite(scalar_range) or scalar_range <= 0:
        raise ValueError('positive sequence-wide scalar range required')
    signs = [(-1. if tree.kind == 'split' else 1.) for tree in scene['trees']]
    matrices = [np.array([[sign*fr.values[fr.lca(i,j)] if i != j else sign*fr.values[i]
                 for j in ids] for i in ids]) for fr,ids,sign in zip(scene['frames'],scene['ids'],signs)]
    return dict(scene=scene, extrema=ext, reference=ref, parameters=p,
                merge_values=matrices, scalar_range=scalar_range, configuration=configuration)


def prepare_fields(fields, coordinates, sample_measure, *, kind='join',
                   configuration=FixedConfiguration()):
    """Existing extraction and overlap matching, once before any budget sweep."""
    from experiments.era5 import scene_from_fields
    scene = scene_from_fields(fields, coordinates, sample_measure, kind, max_leaves=None)
    return prepare_sequence(scene, np.min(coordinates,axis=0), np.max(coordinates,axis=0),
                            np.prod(np.shape(fields)[1:])*sample_measure, configuration)


def anchor_mtm(prepared, epsilon=0.):
    """Single-control public execution: fixed reference -> layout -> temporal map.

    Failures are returned explicitly. Rendered budget checks concern the fixed
    leaf labels only; no full-tree label-coverage certificate is claimed.
    """
    started = perf_counter()
    if not np.isfinite(epsilon) or epsilon < 0: raise ValueError('epsilon must be finite and nonnegative')
    sc = prepared['scene'];cfg = prepared['configuration'];p = prepared['parameters']
    result = dict(epsilon=float(epsilon), epsilon0=cfg.epsilon0,
        eta=(cfg.epsilon0+epsilon)*prepared['scalar_range'], scalar_range=prepared['scalar_range'],
        reference=prepared['reference'], parameters=p, success=False, failures=[], map=None,
        layouts=[], rendered=False, full_tree_certified=False)
    stage = 'layout'
    try:
        solved = solve_anchored_sequence(sc['centers'], sc['areas'], sc['hier'], prepared['extrema'],
            prepared['merge_values'], sc['tracks'], None, None, prepared['scalar_range'], p,
            epsilon=epsilon, epsilon0=cfg.epsilon0, reference=prepared['reference'])
        rows = result['layouts'] = solved['layouts']
        stage = 'reconstruction'
        from rgmtm.reference_guided import render_sequence
        from filling import optimal_fill
        maps, skeletons, raster = render_sequence(sc['frames'], sc['ids'], rows,
            p.canvas, cfg.raster_length, canvas_origin=p.canvas_origin)
        for t,(fr,ids,row,sk,V) in enumerate(zip(sc['frames'],sc['ids'],rows,skeletons,prepared['merge_values'])):
            kind = sc['trees'][t].kind
            maps[:,t], _ = optimal_fill(maps[:,t], list(sk.ordering), sk.anchors, fr, kind)
            values = (-1. if kind == 'split' else 1.)*maps[:,t]
            anchor_by_id = dict(zip(sk.ordering, sk.anchors))
            pix = np.array([anchor_by_id[i] for i in ids])
            displayed = np.array([[max(values[min(a,b):max(a,b)+1]) for b in pix] for a in pix])
            error = np.abs(displayed-V)
            pixel_x = p.canvas_origin + pix*p.canvas/(cfg.raster_length-1)
            row.update(rendered_position_error=float(np.max(abs(pixel_x-row['reference']))/p.canvas),
                pixel_x=pixel_x, NMLEmean=float(error.mean()/prepared['scalar_range']),
                NMLEmax=float(error.max()/prepared['scalar_range']),
                rendered_merge_error=float(error.max()), rendered_budget_ok=bool(error.max()<=result['eta']),
                ME=float(np.sqrt(row['terms']['motion'])), raster_error=raster[t],
                metric_convention='NMLE over the full fixed-label matrix including diagonal; ME is normalized RMS')
            if t:
                old = {k:i for i,k in enumerate(sc['tracks'][t-1])}
                residual = [pixel_x[i]-rows[t-1]['pixel_x'][old[k]]-
                    (row['reference'][i]-rows[t-1]['reference'][old[k]])
                    for i,k in enumerate(sc['tracks'][t]) if k in old]
                row['rendered_ME'] = float(np.sqrt(np.mean(np.square(residual)))/p.canvas) if residual else 0.
            else: row['rendered_ME'] = 0.
        result.update(map=maps, success=True, rendered=True)
    except (ValueError, RuntimeError, AssertionError) as error:
        result['failures'].append(dict(stage=stage, type=type(error).__name__, message=str(error)))
    result['seconds'] = perf_counter()-started
    return result
