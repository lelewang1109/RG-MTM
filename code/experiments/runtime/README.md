# Runtime of the certified pipeline (2026-10-27)

Records the machine and the time of the three steps on all 917 frames at
eps in {0, 2, 5, 10}%:

- **bounds** (Theorems A, C, A_w, C_w): timed by this script on every frame;
- **ordering** (`budget_order` + `width_order`): `search_seconds` of the saved
  N1b run, `results/order_width20261027/` (same machine, same day);
- **QP**: the rest of that run's `seconds` (capped sequential QP plus metric
  evaluation), solved with SciPy SLSQP from a HiGHS LP feasible start.

Single Python process, no parallelism. Machine and library versions are stored
in the output.

```sh
cd code
PYTHONPATH=src python experiments/runtime/run.py     # about 30 seconds
```

Output: `results/runtime20261027/runtime.json` (machine, per-dataset totals and
per-frame milliseconds, totals over all budgets).
