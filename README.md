# AnchorMTM

Spatially anchored merge-tree maps for time-varying scalar fields, with topology budgets and certified position bounds.

## Current paper — November 7, 2026

- [Latest paper (PDF)](paper/pvis2027/最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX source](paper/pvis2027/drafts/method_anchor_figures_updated_en.tex)
- [Hourly PM2.5 case: figure, PowerPoint, plotting cache and checks](paper/pvis2027/pm25_hourly_20261107/README.md)
- [Formal four-input evaluation and provenance](paper/pvis2027/experiments_ratio_p_20261104/REPORT_zh.md)
- [Method and baseline code](code/) · [Data documentation](data/) · [Research documentation](docs/)

The revised manuscript presents the position bounds, construction and evaluation separately. Two-dimensional cases (Ring, Storms and hourly PM2.5) precede the exploratory three-dimensional Cylinder case. The new PM2.5 single-column figure places its temporal map above five source snapshots, with compact spacing and consistent date/time labels.

![Hourly PM2.5 case](paper/pvis2027/pm25_hourly_20261107/PM25_single_column.png)

## Evidence and reproduction

The formal comparison uses Gaussian, Ring, Wildfires and Storms with disclosed local input conventions. Wildfires' local reconstruction is **not** the original author-processed 32-frame input. Published baseline scores and local measurements are distinguished; reconstruction differences limit identical-input claims.

The PM2.5 case uses the ChinaVis2021 CAQRA hourly archive for January 2017, with maxima handled as join trees of negated concentration. It is an additional exploratory case, reported as an additional fixed-configuration row in the results and parameter tables. The displayed window is January 22 00:00–27 12:00 (Beijing time), at a 5% layout allowance; persistence simplification is a separate parameter. Compact derived data and the replot script are included; nationwide source archives and large intermediate trees remain external.

[Paper build instructions and supporting material](paper/pvis2027/README.md). Historical reports and figure indexes describe earlier versions; the latest PDF and current case page above take precedence.

PM2.5 metrics are recomputed on all 744 shared-input frames: Balanced (fixed 5% case budget) has best SNS (0.1636) and NPE (0.0468); Exact has second NPE (0.1390). Hilbert has best TW (0.8887). Local ST-MTM uses the declared Storms preset with start frame 0; no author PM2.5 baseline scores are claimed. Uncached one-thread remeasurement gives optimization 199.975 s and full pipeline 231.177 s; scientific metrics exactly match the original run. Stage times are recorded in timing.json.
