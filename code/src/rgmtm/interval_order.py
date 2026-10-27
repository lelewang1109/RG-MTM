"""Width-aware order certificate and leaf ordering for the interval layout (N1b).

The interval model gives leaf k an interval of width W_k, consecutive intervals
``gap`` apart, and lets its anchor sit within H_k = rho W_k / 2 of the interval
centre; tau(order) is the attained minimax |x - q| (``framework.interval_costs``).
Point-model order error ignores W, so a low-NROE order can still have a large tau
when features are wide (Tangaroa, N1).

Theorem A_w: with lo_k = q_k - W_k/2 - H_k, hi_k = q_k + W_k/2 + H_k and
s_k = W_k + gap, if block X precedes block Y then for any S_X in X and S_Y in Y
the first leaf a of S_X and the last leaf b of S_Y have centres at least
sum_{S_X + S_Y} s - gap - W_a/2 - W_b/2 apart, hence

    tau >= (A(X) + B(Y) - gap) / 2,
    A(X) = max_alpha [alpha + sum_{k in X, lo_k >= alpha} s_k],
    B(Y) = max_beta  [sum_{k in Y, hi_k <= beta} s_k - beta].

A map with zero merge error keeps every subtree contiguous, so tau is at least
the maximum over sibling pairs of the smaller orientation. The canvas ends give
the order-free packing terms origin - gap + B(all) and A(all) - gap - origin -
canvas. With W = gap = 0 this is Theorem A in canvas units (tau = L nu*).
Flattening every gap <= 2 eps (Theorem B) makes it valid for merge error <= eps.
"""
import numpy as np
from .framework import merge_costs
from .order_certificate import hierarchy, _blocks, _parents, _expand, budget_order, order_error


def _ends(widths, reference, p):
    W = np.asarray(widths, float); q = np.asarray(reference, float); H = p.rho * W / 2
    return q - W / 2 - H, q + W / 2 + H, W + p.gap


def _packing(lo, hi, s):
    """A and B of Theorem A_w for one leaf set (every sorted prefix is a valid subset)."""
    a = np.argsort(-lo, kind='stable'); b = np.argsort(hi, kind='stable')
    return float(np.max(lo[a] + np.cumsum(s[a]))), float(np.max(np.cumsum(s[b]) - hi[b]))


def interval_scores(orders, widths, reference, p):
    """tau of each order (as ``interval_costs``) and the sum of squared positive terms.

    The second value breaks plateaus of the minimax objective in local search.
    """
    O = np.asarray(orders, int); W = np.asarray(widths, float)[O]; Q = np.asarray(reference, float)[O]
    m, n = O.shape; H = p.rho * W / 2
    D = np.cumsum(W, 1) - W / 2 + p.gap * np.arange(n)
    E = W.sum(1, keepdims=True) - np.cumsum(W, 1) + W / 2 + p.gap * (n - 1 - np.arange(n))
    left = p.canvas_origin + D - Q - H; right = Q - H - (p.canvas_origin + p.canvas - E)
    i, j = np.triu_indices(n, 1)
    pair = ((Q[:, i] - Q[:, j] + D[:, j] - D[:, i] - H[:, i] - H[:, j]) / 2) if n > 1 else np.zeros((m, 0))
    terms = np.concatenate([left, right, pair], 1)
    return np.maximum(0., terms.max(1)), (np.maximum(0., terms) ** 2).sum(1)


def width_certificate(merge_values, reference, widths, p, gap=0.0, tie=0.0):
    """Theorem A_w on T^(gap): lower bound on tau for any map splitting only gaps <= gap."""
    nodes, root = hierarchy(merge_values)
    if root is None: return 0.
    lo, hi, s = _ends(widths, reference, p)
    A, B = _packing(lo, hi, s)
    best = max(0., p.canvas_origin - p.gap + B, A - p.gap - p.canvas_origin - p.canvas)
    for _, ch in _blocks(nodes, root, max(gap, 2 * tie)):
        ab = [_packing(lo[L], hi[L], s[L]) for L in (nodes[c]['leaves'] for c in ch)]
        for x in range(len(ab)):
            for y in range(x + 1, len(ab)):
                best = max(best, (min(ab[x][0] + ab[y][1], ab[y][0] + ab[x][1]) - p.gap) / 2)
    return best


def _moves(ch):
    """Child permutations one insertion away (all of them up to 8 children, else within 3)."""
    m = len(ch); out = set()
    for i in range(m):
        rest = ch[:i] + ch[i + 1:]
        for j in range(m):
            if j != i and (m <= 8 or abs(i - j) <= 3):
                out.add(tuple(rest[:j] + [ch[i]] + rest[j:]))
    out.discard(tuple(ch))
    return [list(c) for c in sorted(out)]


def _search(nodes, root, flat, q, w, V, p, limit, passes):
    """Local search over child permutations of T^flat on (tau, squared terms).

    Starts from midpoint order; every accepted move keeps merge cost <= limit.
    On the exact tree (empty ``flat``) every child permutation is legal.
    """
    key = lambda c: (q[nodes[c]['leaves']].min() + q[nodes[c]['leaves']].max()) / 2
    state = {}; stack = [root]
    while stack:
        k = stack.pop()
        if nodes[k]['children']:
            state[k] = sorted(_expand(nodes, k, flat), key=key); stack += state[k]
    def emit(st):
        def go(k): return sum((go(c) for c in st[k]), []) if nodes[k]['children'] else [k]
        return go(root)
    order = emit(state)
    if flat and merge_costs([order], V)[0] > limit: return None
    t, soft = (float(v[0]) for v in interval_scores([order], w, q, p))
    blocks = [k for k in state if len(state[k]) > 1]
    for _ in range(passes):
        improved = False
        for k in blocks:
            cands = _moves(state[k])
            orders = np.array([emit({**state, k: c}) for c in cands])
            T, S = interval_scores(orders, w, q, p)
            for i in np.lexsort((S, T)):
                better = T[i] < t - 1e-12 or (T[i] <= t + 1e-12 and S[i] < soft - 1e-12 * max(1., soft))
                if not better: break
                if flat and merge_costs([orders[i]], V)[0] > limit: continue
                state[k] = cands[i]; t, soft = float(T[i]), float(S[i]); order = list(orders[i]); improved = True
                break
        if not improved: break
    return dict(order=[int(v) for v in order], tau=t, soft=soft, flattened=len(flat))


def width_order(merge_values, reference, widths, p, budget, tie=0.0, *, point=None, keep=4, passes=8):
    """Order with exact merge cost <= budget + tie that minimizes tau (ties: NROE).

    Candidate structures are those of ``budget_order``: the exact tree, every
    threshold flattening up to 2(budget + tie) and the selective flattening. The
    ``keep`` best structures by initial tau (always including the exact tree) are
    refined by local search. ``point`` (the ``budget_order`` result, computed if
    omitted) is kept as a candidate, so tau never exceeds that of the N1 order.
    """
    V = np.asarray(merge_values, float); q = np.asarray(reference, float); w = np.asarray(widths, float)
    L = p.canvas; limit = budget + tie
    point = point or budget_order(V, q, L, budget, tie)
    lower = width_certificate(V, q, w, p, 2 * limit)
    t0 = float(interval_scores([point['order']], w, q, p)[0][0])
    best = dict(order=list(point['order']), tau=t0, delta=float(point['delta']), source='point order', flattened=None)
    nodes, root = hierarchy(V)
    if root is not None and len(V) > 1:
        parent = _parents(nodes)
        inner = [k for k, d in nodes.items() if d['children'] and k in parent]
        gap = {k: nodes[parent[k]]['level'] - nodes[k]['level'] for k in inner}
        levels = {0.} | {g for g in gap.values() if 0 < g <= 2 * limit}
        structures = {frozenset(k for k in inner if gap[k] <= s) for s in levels}
        structures |= {frozenset(), frozenset(point.get('selective_flat', ()))}
        start = []
        for f in structures:
            r = _search(nodes, root, f, q, w, V, p, limit, 0)
            if r: start.append((r['tau'], r['soft'], len(f), f))
        start.sort(key=lambda r: r[:3])
        chosen = [r[3] for r in start[:keep]] + ([frozenset()] if frozenset() not in [r[3] for r in start[:keep]] else [])
        for f in chosen:
            r = _search(nodes, root, f, q, w, V, p, limit, passes)
            if not r: continue
            if r['tau'] < best['tau'] - 1e-12 or (r['tau'] <= best['tau'] + 1e-12 and
                                                    order_error(r['order'], q, L) < order_error(best['order'], q, L) - 1e-15):
                best = dict(order=r['order'], tau=r['tau'], delta=float(merge_costs([r['order']], V)[0]),
                            source='width search', flattened=r['flattened'])
    best.update(nroe=order_error(best['order'], q, L), lower=lower, point_tau=t0, point_nroe=float(point['nroe']))
    return best
