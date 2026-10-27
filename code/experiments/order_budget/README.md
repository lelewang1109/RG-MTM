# Order-level budget experiment (2026-10-27)

Tests the closed-form order certificate and budgeted midpoint ordering
(`src/rgmtm/order_certificate.py`) on all 917 temporal frames: five planar
sequences (614 frames) and Tangaroa/Cylinder (303 volumes).

```sh
cd code
PYTHONPATH=src python experiments/order_budget/run.py            # all datasets
PYTHONPATH=src python -m unittest tests.test_order_certificate   # brute-force checks
```

Inputs are read-only saved results: `results/framework20261025/*.json`
(planar merge matrices and references), `results/final_performance.json` and
`results/pm25_2000/final_performance.json` (per-frame NROE of TMTM, ST-MTM,
RG-MTM-P, fixed-X), `results/volume3d/tangaroa-paper-p10-full201`,
`results/paper1_suite/square-cylinder3d` and `results/stmtm_completion20261026`.
Outputs go to `results/order_budget20261027/<dataset>.json`.

What each output section means:

| Key | Content |
|---|---|
| `nu_per_frame`, `nu_mean` | Theorem A bound nu*(T) for every frame |
| `methods` | every saved method: NROE, violations of Theorem A (exact topology) or B (measured merge error), frames at bound |
| `budget_sweep` | budgeted midpoint order at epsilon in {0,...,1}: NROE, Theorem B lower bound, achieved merge cost, exact optimum on frames with at most 8 leaves |
| `matched_cost` | volumetric kappa outputs vs budgeted ordering given each frame's own measured merge error |

Scope: order-only (NROE). Widths, gaps, canvas, the secondary QP and raster
rendering are not involved; positional layouts are a separate next step.
Merge levels within 1e-7 of the scalar range are treated as one level.
