# N1: certified orders inside the interval-layout QP (2026-10-27)

For each topology budget eps in {0, 2%, 5%, 10%} the leaf order comes from
`rgmtm.order_certificate.budget_order` (exact merge cost <= eps0 + eps,
eps0 = 1e-7 of the scalar range). The unchanged four-term QP of
`rgmtm.unified` places the anchors sequentially, in two variants:

- `certified order`: no position cap (B = infinity);
- `certified order + cap`: per-frame cap B_t = tau_t(order) + beta, where tau_t is
  the attained minimax interval position cost of the order and beta the saved
  `extra_budget`. E_inf <= max_t B_t / L is asserted.

```sh
cd code
PYTHONPATH=src python experiments/order_layout/run.py             # all 7 datasets
PYTHONPATH=src python experiments/order_layout/run.py Tangaroa    # about 3 minutes
```

Inputs (read-only): planar `results/unified20261025/*.json` (`frame_inputs`,
`parameters` and the old candidate-pool layouts used for comparison);
volumetric `features.json`, `parameters.json`, Tangaroa `reference.json`
and `positions.json`, Cylinder `frame_metrics.json` (kappa P/R layouts).
Outputs: `results/order_layout20261027/<dataset>.json`.

Metrics are continuous (no raster): E_pool, E_inf, NROE, layout-induced jump
|du - dq| / L for matched tracks (mean, p95, max), plain anchor motion |du| / L,
geometry RMS and exact merge error delta* / range (NMLE).
