"""Closed-form reference-order certificate and budgeted midpoint ordering.

Theorem A: every map with zero labelled merge error keeps each subtree
contiguous, so its reference-order error (NROE) is at least

    nu*(T) = max_v max_{X != Y in ch(v)} min(M_X - m_Y, M_Y - m_X)^+ / (2L),

where [m_X, M_X] is the reference hull of child subtree X. Sorting children by
hull midpoint at every node attains it in O(n log n).

Theorem B: a map with merge error <= eps can only split subtrees whose parent
gap is <= 2 eps, so NROE >= nu*(T^(2 eps)) with those nodes flattened.

Theorem C (chain-aware, at least as strong as B): let A_eps(u) be the highest
ancestor of u with level <= f(u) + 2 eps. With merge error <= eps no leaf
outside A_eps(u) lies between two leaves of u: the displayed (i,j) merge is
<= f(u) + eps but would be >= f(lca(i,k)) - eps > f(u) + eps. Hence each such
leaf, and each node w with w outside A_eps(u) and u outside A_eps(w), lies
wholly on one side of u, which gives the bound in ``chain_certificate``.
B flattens every gap <= 2 eps at once; C charges chains by their summed gap.

``tie`` is the merge error treated as zero (float32 round-off). By Theorem B a
map with merge error <= tie may split any node whose parent gap is <= 2 tie, so
those nodes are flattened; exactly equal levels always form a multifurcation.
Join convention: off-diagonal merge values lie above leaf values.
"""
import numpy as np
from .framework import merge_costs


def hierarchy(merge_values):
    """Labelled hierarchy of a join-convention merge matrix; equal levels merge."""
    V = np.asarray(merge_values, float); n = len(V)
    parent = list(range(n)); cluster = list(range(n))
    nodes = {i: dict(level=float(V[i, i]), leaves=[i], children=[]) for i in range(n)}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    pairs = sorted((V[i, j], i, j) for i in range(n) for j in range(i + 1, n))
    k = 0; nid = n
    while k < len(pairs):
        level = pairs[k][0]
        while k < len(pairs) and pairs[k][0] == level:
            _, i, j = pairs[k]; a, b = find(i), find(j)
            if a != b: parent[b] = a
            k += 1
        groups = {}
        for r in range(n): groups.setdefault(find(r), set()).add(cluster[r])
        for root, members in groups.items():
            if len(members) > 1:
                nodes[nid] = dict(level=float(level), children=sorted(members),
                                  leaves=sorted(sum((nodes[m]['leaves'] for m in members), [])))
                for r in range(n):
                    if find(r) == root: cluster[r] = nid
                nid += 1
    root = max(nodes) if n else None
    return nodes, root


def _flattened_children(nodes, k, gap):
    out = []
    for c in nodes[k]['children']:
        if nodes[c]['children'] and nodes[k]['level'] - nodes[c]['level'] <= gap:
            out += _flattened_children(nodes, c, gap)
        else:
            out.append(c)
    return out


def _blocks(nodes, root, gap):
    """Internal nodes of T^(gap) with their (flattened) children."""
    stack = [root]; out = []
    while stack:
        k = stack.pop()
        if not nodes[k]['children']: continue
        ch = _flattened_children(nodes, k, gap); out.append((k, ch)); stack += ch
    return out


def order_error(order, reference, extent):
    """NROE of one leaf order: minimax displacement after monotone calibration."""
    x = np.asarray(reference, float)[list(order)]
    return max(0., float(np.max(np.maximum.accumulate(x) - x))) / (2 * extent) if len(x) else 0.


def order_errors(orders, reference, extent):
    x = np.asarray(reference, float)[np.asarray(orders, int)]
    return np.maximum(0., (np.maximum.accumulate(x, axis=1) - x).max(axis=1)) / (2 * extent)


def certificate(merge_values, reference, extent, gap=0.0, tie=0.0):
    """nu*(T^(gap)): lower bound on NROE for any map that splits only gaps <= gap."""
    nodes, root = hierarchy(merge_values)
    if root is None: return 0.
    q = np.asarray(reference, float); best = 0.
    for _, ch in _blocks(nodes, root, max(gap, 2 * tie)):
        hull = [(q[nodes[c]['leaves']].min(), q[nodes[c]['leaves']].max()) for c in ch]
        for a in range(len(hull)):
            for b in range(a + 1, len(hull)):
                (m1, M1), (m2, M2) = hull[a], hull[b]
                best = max(best, min(M1 - m2, M2 - m1))
    return best / (2 * extent)


def midpoint_order(merge_values, reference, gap=0.0, tie=0.0):
    """Leaf order legal in T^(gap) that attains certificate(..., gap)."""
    nodes, root = hierarchy(merge_values)
    if root is None: return []
    q = np.asarray(reference, float)
    def emit(k):
        if not nodes[k]['children']: return [k]
        ch = _flattened_children(nodes, k, gap)
        key = lambda c: (q[nodes[c]['leaves']].min() + q[nodes[c]['leaves']].max()) / 2
        return sum((emit(c) for c in sorted(ch, key=key)), [])
    return emit(root)


def _parents(nodes):
    return {c: k for k, d in nodes.items() for c in d['children']}


def _span(nodes, parent, u, slack):
    """A_eps(u): highest ancestor of u whose level is within ``slack`` of u."""
    a = u
    while a in parent and nodes[parent[a]]['level'] - nodes[u]['level'] <= slack:
        a = parent[a]
    return a


def chain_certificate(merge_values, reference, extent, budget, tie=0.0):
    """Theorem C lower bound on NROE for any map with merge error <= budget (+ tie)."""
    nodes, root = hierarchy(merge_values)
    if root is None: return 0.
    q = np.asarray(reference, float); n = len(q); parent = _parents(nodes); slack = 2 * (budget + tie)
    inner = [u for u, d in nodes.items() if d['children']]
    hull = {u: (q[nodes[u]['leaves']].min(), q[nodes[u]['leaves']].max()) for u in nodes}
    allowed = {u: set(nodes[_span(nodes, parent, u, slack)]['leaves']) for u in inner}
    best = 0.
    for u in inner:
        m, M = hull[u]
        for k in range(n):
            if k not in allowed[u]: best = max(best, min(M - q[k], q[k] - m))
        for w in inner:
            if w < u and not (set(nodes[w]['leaves']) & allowed[u]) and not (set(nodes[u]['leaves']) & allowed[w]):
                (m2, M2) = hull[w]; best = max(best, min(M - m2, M2 - m))
    return best / (2 * extent)


def _expand(nodes, k, flat):
    out = []
    for c in nodes[k]['children']:
        out += _expand(nodes, c, flat) if c in flat else [c]
    return out


def _flat_order(nodes, root, flat, q):
    key = lambda c: (q[nodes[c]['leaves']].min() + q[nodes[c]['leaves']].max()) / 2
    def emit(k):
        if not nodes[k]['children']: return [k]
        return sum((emit(c) for c in sorted(_expand(nodes, k, flat), key=key)), [])
    return emit(root)


def _critical(nodes, root, flat, q):
    """Sibling pair of T^flat with the largest unavoidable order cost."""
    best = (0., None, None); stack = [root]
    while stack:
        k = stack.pop()
        if not nodes[k]['children']: continue
        ch = _expand(nodes, k, flat); stack += ch
        hull = [(q[nodes[c]['leaves']].min(), q[nodes[c]['leaves']].max()) for c in ch]
        for a in range(len(ch)):
            for b in range(a + 1, len(ch)):
                cost = min(hull[a][1] - hull[b][0], hull[b][1] - hull[a][0])
                if cost > best[0]: best = (cost, ch[a], ch[b])
    return best


def _valid(nodes, parent, flat, slack):
    """Every flattened node scatters only within an ancestor at most ``slack`` above it."""
    for u in flat:
        a = parent[u]
        while a in flat: a = parent[a]
        if nodes[a]['level'] - nodes[u]['level'] > slack: return False
    return True


def selective_order(merge_values, reference, extent, budget, tie=0.0):
    """Conflict-driven flattening: repeatedly release the current bottleneck pair.

    Starts from the exact tree; flattens one or both nodes of the critical
    sibling pair when the flattening respects Theorem C's chain condition and
    the exact merge cost of the resulting midpoint order stays <= budget + tie.
    """
    nodes, root = hierarchy(merge_values); V = np.asarray(merge_values, float)
    q = np.asarray(reference, float); parent = _parents(nodes); slack = 2 * (budget + tie)
    flat = set(); order = _flat_order(nodes, root, flat, q); score = order_error(order, q, extent)
    best = dict(order=order, delta=0., nroe=score, flattened=0, flat=set())
    while True:   # the flattened set only grows, so this stops
        cost, X, Y = _critical(nodes, root, flat, q)
        if cost <= 0: break
        trials = []
        for add in ({X}, {Y}, {X, Y}):
            if any(not nodes[c]['children'] or c == root for c in add): continue
            f = flat | add
            if not _valid(nodes, parent, f, slack): continue
            o = _flat_order(nodes, root, f, q); d = float(merge_costs([o], V)[0])
            if d <= budget + tie: trials.append((order_error(o, q, extent), d, len(add), f, o))
        if not trials: break
        s, d, _, f, o = min(trials, key=lambda t: t[:3])
        if s > score + 1e-15: break
        flat, score = f, s      # non-worsening steps may unlock a deeper flattening
        if s < best['nroe'] - 1e-15: best = dict(order=o, delta=d, nroe=s, flattened=len(f), flat=set(f))
    return best


def budget_order(merge_values, reference, extent, budget, tie=0.0):
    """Best order with exact merge cost <= budget + tie among two constructions.

    (i) midpoint orders after flattening every gap below one threshold, from
    2*(budget+tie) down to the exact tree, which always qualifies;
    (ii) conflict-driven selective flattening. Reports the Theorem B and the
    chain-aware Theorem C lower bounds (``lower`` is the larger).
    """
    nodes, root = hierarchy(merge_values)
    V = np.asarray(merge_values, float)
    lower_b = certificate(V, reference, extent, 2 * (budget + tie))
    lower_c = chain_certificate(V, reference, extent, budget, tie)
    if root is None or len(V) < 2:
        return dict(order=list(range(len(V))), delta=0., nroe=0., lower=max(lower_b, lower_c),
                    lower_b=lower_b, lower_c=lower_c, source='trivial', threshold_nroe=0., selective_nroe=0.)
    gaps = sorted({nodes[k]['level'] - nodes[c]['level'] for k, d in nodes.items()
                   for c in d['children'] if nodes[c]['children']})
    levels = sorted({0.} | {g for g in gaps if 0 < g <= 2 * (budget + tie)}, reverse=True)
    orders = [midpoint_order(V, reference, s) for s in levels]
    delta = merge_costs(orders, V); nroe = order_errors(orders, reference, extent)
    ok = delta <= budget + tie
    k = int(np.flatnonzero(ok)[np.argmin(nroe[ok])])
    best = dict(order=orders[k], delta=float(delta[k]), nroe=float(nroe[k]), source='threshold',
                threshold=float(levels[k]))
    sel = selective_order(V, reference, extent, budget, tie)
    best['threshold_nroe'] = best['nroe']; best['selective_nroe'] = sel['nroe']; best['selective_flat'] = sorted(sel['flat'])
    if sel['nroe'] < best['nroe'] - 1e-15:
        best.update(order=sel['order'], delta=sel['delta'], nroe=sel['nroe'], source='selective')
    best.update(lower=max(lower_b, lower_c), lower_b=lower_b, lower_c=lower_c, candidates=len(orders) + 1)
    return best
