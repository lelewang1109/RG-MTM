# N1c: geometry, stability, motion and raster metrics of the new layouts (2026-10-27)

Scores the width-aware certified layouts with the capped QP (as in
`experiments/frontier`) at eps in {0, 2, 10}% and the projection baseline with the
unchanged protocol of the completed nine-input table
(`results/stmtm_completion20261026/unified_metrics.csv`):

- SNS, TW (k=1) and TD from `experiments/stmtm_completion/run.py: geometry`
  (unweighted support centroids, positions on the full [0,1] canvas);
- motion error ME from `motion` there (original extrema and tracks, lag 2,
  source threshold 2% of the domain diagonal; occupied-range display threshold,
  fixed canvas for Cylinder). Planar domain diagonals are not stored; the script
  takes the midpoint of the interval that reproduces the stored event count.
  Thresholds are nested, so the whole interval selects the same events.
- raster errors of the rendered map (barrier discrepancy, anchor rounding) for
  Ring, OLR and PM2.5, whose scalar inputs ship with the repository.

Before scoring, the script re-evaluates the saved anchors of the stored methods
(planar TMTM/ST-MTM/P/R, volumetric kappa P/R) and records stored versus
recomputed values in `reproduction`. SNS and TD agree exactly except on
Cylinder (relative 1e-5). TW differs in the third or fourth decimal on Tangaroa
P/R and Cylinder P/R, and ME by one event on PM2.5 P, Ring R and Cylinder P;
everything else agrees exactly. The stored values were taken from rendered
anchors, these from continuous ones.

```sh
cd code
PYTHONPATH=src python experiments/metrics_n1c/run.py           # all 7 datasets
PYTHONPATH=src python experiments/metrics_n1c/run.py Ring      # about a minute
```

Outputs: `results/metrics_n1c20261027/<dataset>.json` with `settings`
(eps=0, eps=0.02, eps=0.1, projection), `baselines` (stored native TMTM/ST-MTM
and kappa rows) and `reproduction`.
