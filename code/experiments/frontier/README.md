# N2: position--topology frontier and projection baseline (2026-10-27)

Extends N1b (`experiments/order_width`) to the full frontier on the same 917
frames: width-aware certified orders with the capped QP at
eps in {0, 1, 2, 5, 10, 20, 50}% (eps0 = 1e-7 of the scalar range), closed by
the **projection baseline** (eps = infinity): every frame's leaves sorted by
reference q (zero order error), the optimal barriers of that order, and the
same capped QP (B_t = tau_t + beta). The projection is the Hovmoller-like end
of the trade-off; its merge error is whatever the sorted order forces.

```sh
cd code
PYTHONPATH=src python experiments/frontier/run.py             # all 7 datasets, about 15 minutes
PYTHONPATH=src python experiments/frontier/run.py Ring        # seconds
```

Outputs: `results/frontier20261027/<dataset>.json`, one entry per budget and
`projection`, with E_pool, E_inf, NROE, jumps, NMLE mean/max, tau of the orders,
QP gaps and, for the projection, the number of frames whose sorted order keeps
the exact tree (`frames_exact_topology`).
