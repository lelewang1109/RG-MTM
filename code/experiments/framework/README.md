# Budgeted map-family experiments (2026-10-25)

The family declares a representation/solver profile and separate normalized topology and position caps. Native TMTM/ST-MTM retain their own algorithms; a topology threshold alone does not recover either one. `src/rgmtm/framework.py` supplies native compatibility entry points and a new fixed-world hard-budget order solver.

From the MergeTreeMaps workspace root:

```sh
.venv/bin/python RG-MTM/code/experiments/framework/run.py
.venv/bin/python RG-MTM/code/experiments/framework/export.py
```

In a standalone code checkout, run `PYTHONPATH=src python experiments/framework/run.py` and `PYTHONPATH=src python experiments/framework/export.py`. Prepared original data are required; full-year PM2.5 uses the saved trusted local scene at `results/pm25_2000/dataset.pkl`.

Results live only in `results/framework20261025/`: five sequence summaries, every per-frame LP/barrier witness, inverse queries, original-field hashes, native compatibility and validation records. The loader can re-emit its unchanged dataset protocol metadata; historical scientific results are not rerun or overwritten.

614 frames and nine topology settings produce 5526 continuous witnesses. Search is exhaustive through 40320 permutations (603 frames). The other 11 Wildfires frames use the original legal orders, reference order/reverse and single-insertion variants, fixed across thresholds. Their costs are feasible upper bounds. They are not global optima; a missing candidate is not an infeasibility proof.

The continuous solver uses non-strict extrema and minimax position error. Rendered illustrations do not carry an unmeasured raster guarantee. No previous motion or temporal-QP metrics are assigned to these new framewise witnesses. Independent baseline reproduction evidence remains separate from native dispatch compatibility.
