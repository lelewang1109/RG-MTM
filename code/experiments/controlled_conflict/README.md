# N4: controlled hierarchy conflict (2026-10-30)

This deterministic synthetic tree experiment changes only sibling reference-hull overlap, interval width, or the permitted merge error. It is not a scalar-field time series and does not measure temporal coherence or perceptual performance.

## Reproduce

From the repository root, with NumPy, SciPy and Matplotlib installed:

```sh
PYTHONPATH=code/src python code/experiments/controlled_conflict/run.py
python code/experiments/controlled_conflict/plot.py
```

The first command runs all scientific checks; the second draws only from saved results. The paper's `scripts/make_figures.py` also regenerates both figures from these results.

## Inputs and controls

- Four zero-valued leaves, sibling pairs X={A,B}, Y={C,D}; pair merge level a=0.4, root=1. Canvas L=1, scalar range=1.
- References q=(0.2,0.5,0.5-d,0.8-d). Signed overlap d ranges from -0.12 to 0.30 in increments of 0.01. Negative d separates the hulls; for this range X-before-Y is never worse than Y-before-X.
- Equal widths W in {0,0.03,0.06,0.09}; anchor slack rho=0.5. Gap=0 for the zero-width point limit, and 0.01 for all positive-width settings. Thus the point limit removes both width and gap; the three finite-width settings share the same gap.
- Total: 172 overlap/width settings. All 24 orders per setting are evaluated. For each order, a minimax LP is built directly from centre separation, canvas boundaries, anchor slack and reference deviation constraints, independently of `interval_costs`.
- Select the best zero-merge-error order for tau_exact, and best unrestricted order for tau_free. H_hier=tau_exact-tau_free isolates extra hierarchy cost and is not the per-anchor slack H_i.
- Budget sweep: fixed d=0.24, W=0.06, gap=0.01, rho=0.5; a in {0.2,0.4,0.6,0.8}; epsilon=0 to 0.45 in steps of 0.005 (364 settings). Reuse 24 independent spatial LPs, filter all orders by their exact optimal merge cost.
- No tolerance budget, no additional position slack, no QP secondary weights; epsilon_0=beta=0. All data are deterministic; there is no random seed or sampling uncertainty.

## Results and checks

- `code/results/controlled_conflict20261030/overlap.{csv,json}`: overlap, widths, bounds, optimum displacement, free packing and hierarchy excess.
- `budget.{csv,json}`: gap/budget sweep, selected order, optimum displacement and measured optimal barrier error.
- `enumeration.json`: all 24 orders, independent LP costs, anchors, centres and merge costs for each overlap/width setting.
- `witnesses.json`: selected exact and free orders, exact LP placement witnesses and verified barriers.
- `summary.json`: numerical residuals and software versions.

4152 independent LPs in total. Maximum LP/closed-form discrepancy: 1.67e-16 of the canvas. The point lower bound, width lower bound and implemented width-aware search all reach the exhaustive optimum in this controlled family. The search also reaches the exhaustive optimum at all 364 budget settings. All selected barriers are checked against every pairwise source merge level.

For exact hierarchy, nu*=max(0,d)/2 and tau_exact=max(0,(d+(1-rho)W+gap)/2). At d=0.24, W=0.06, point cost=0.12, interval cost=0.14, free packing cost=0. At a=0.4 the free order requires merge error 0.30. More generally, the release threshold is epsilon=(1-a)/2. At d=0.30, W=0.06, tau_exact=0.17 and tau_free=0.02, so H_hier=0.15.

## Figures and manuscript

- Main: `paper/pvis2027/figures/fig_controlled_conflict.{pdf,svg,png}` — displacement versus overlap and the budget release threshold.
- Supplement: `fig_controlled_conflict_supp.{pdf,svg,png}` — tree/hull setup, hierarchy excess for three widths, and four parent-gap thresholds.
- Main subsection: `Controlled hierarchy conflict`; supplement section: `Controlled hierarchy-conflict experiment (N4)`.

These checks establish tightness and optimality for this family only. They do not settle residual gaps in Tangaroa, general large-tree optimality, input-noise robustness or readability.
