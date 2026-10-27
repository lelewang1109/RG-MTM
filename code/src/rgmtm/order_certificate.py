"""Closed-form reference-order certificate and budgeted midpoint ordering.

Theorem A: every map with zero labelled merge error keeps each subtree
contiguous, so its reference-order error (NROE) is at least

    nu*(T) = max_v max_{X != Y in ch(v)} min(M_X - m_Y, M_Y - m_X)^+ / (2L),

where [m_X, M_X] is the reference hull of child subtree X. Sorting children by
hull midpoint at every node attains it in O(n log n).

Theorem B: a map with merge error <= eps can only split subtrees whose parent
gap is <= 2 eps, so NROE >= nu*(T^(2 eps)) with those nodes flattened.

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


def budget_order(merge_values, reference, extent, budget, tie=0.0):
    """Best midpoint order over flattening levels whose exact merge cost <= budget.

    Candidates flatten every gap below one threshold, from 2*(budget+tie) down
    to the exact tree (threshold 0), which always qualifies. Returns the order, its exact
    cost delta*, its NROE and the Theorem B lower bound.
    """
    nodes, root = hierarchy(merge_values)
    V = np.asarray(merge_values, float)
    lower = certificate(V, reference, extent, 2 * (budget + tie))
    if root is None or len(V) < 2:
        return dict(order=list(range(len(V))), delta=0., nroe=0., lower=lower, threshold=0.)
    gaps = sorted({nodes[k]['level'] - nodes[c]['level'] for k, d in nodes.items()
                   for c in d['children'] if nodes[c]['children']})
    levels = sorted({0.} | {g for g in gaps if 0 < g <= 2 * (budget + tie)}, reverse=True)
    orders = [midpoint_order(V, reference, s) for s in levels]
    delta = merge_costs(orders, V); nroe = order_errors(orders, reference, extent)
    ok = delta <= budget + tie
    k = int(np.flatnonzero(ok)[np.argmin(nroe[ok])])
    return dict(order=orders[k], delta=float(delta[k]), nroe=float(nroe[k]), lower=lower,
                threshold=float(levels[k]), candidates=len(orders))
