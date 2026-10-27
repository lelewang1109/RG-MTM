# N1b: width-aware certified orders inside the interval-layout QP (2026-10-27)

N1 chose the leaf order by point-model order error (NROE). On Tangaroa this
left the worst displacement above the kappa P construction, because wide
features push their neighbours away. N1b keeps everything of N1 (inputs, eps
grid {0, 2%, 5%, 10%}, eps0 = 1e-7 of the scalar range, the four-term QP with
per-frame cap B_t = tau_t + beta, continuous metrics) and changes only the order:

- `rgmtm.interval_order.width_order` minimizes the interval position cost tau
  (attained minimax |x - q| under widths, gaps and anchor eccentricity) subject
  to exact merge cost <= eps0 + eps. It refines the candidate structures of
  `budget_order` (exact tree, threshold and selective flattenings) by local
  search over child permutations and keeps the N1 order as a candidate, so
  tau_t never exceeds N1's.
- `rgmtm.interval_order.width_certificate` (Theorem A_w) is a lower bound on tau
  for every map with zero merge error, or merge error <= eps after Theorem B
  flattening. With zero widths and gap it equals Theorem A (tau = L nu*).

```sh
cd code
PYTHONPATH=src python experiments/order_width/run.py             # all 7 datasets
PYTHONPATH=src python experiments/order_width/run.py Tangaroa
```

Inputs: the same as `experiments/order_layout/` plus its saved results
`results/order_layout20261027/*.json` (N1 and kappa metrics for comparison).
Outputs: `results/order_width20261027/<dataset>.json`; each file holds
`methods` (N1b) and `n1` (copied N1/kappa entries, with tau of the kappa
orders added for the volumetric data).
