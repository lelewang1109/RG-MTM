# Numerical evidence

All JSON/CSV files are unchanged copies of saved results. `manifest.json` records original workspace-relative paths and SHA-256 hashes. `数值与来源.json` connects the primary table to unrounded source values; the original method keys A and R 20% map to RG-MTM-P and RG-MTM-R.

- `final_performance.json`, `eval_projection.json`, `filling.json`: primary reference order, anchor-based motion, and measured rendered barriers.
- `replicate_*.json`: certificate decomposition and continuous anchor displacements.
- `attainable_*.json`: sequence-mean exact per-frame frontiers and selected-order checks. The plotted points combine mean positional optima with maximum scalar cost.
- `publication2027/figure_data/domain_filling_example.json`: archived five-leaf scalar profiles and node-to-pixel trace.
- `publication2027/bisector_control/`: the separate 64-frame reference control; excluded from the main 342-frame suite.
- `public_metrics_20261016/`: standard raster-based geometry, stability, rank and motion-classification results.

The retained primary anchor-based ME and separate raster cross-check use their declared protocols. Ring RG-MTM-R has 16/124 primary errors and 15/124 in the raster cross-check. No experiment or parameter sweep was run for this manuscript integration. Processed field/render NPZ arrays, raw observations and the full scientific implementation remain in the original workspace; they are not required to compile the manuscript.
