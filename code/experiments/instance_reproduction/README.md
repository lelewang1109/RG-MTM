# N3: TMTM and ST-MTM as instances; TMTM's own objective (2026-10-27)

The manuscript states TMTM and ST-MTM as instances of one problem with exact
topology and no position term (Table 1). This experiment supports that statement
on the inputs whose scalar data ship with the repository (Ring, OLR, PM2.5),
using the audited routines of `experiments/baseline_audit` (which covered
Storms and Wildfires on 2026-10-19, `results/baseline_audit_20261019/`):

1. **TMTM layout from the order.** The linearization rebuilt from the native
   branch decisions is compared with the pinned official C++ core (arc
   intervals and anchors); contiguity of every subtree and zero merge error are
   asserted.
2. **ST-MTM layout from the order.** For the native order, the native anchors
   and intervals satisfy the KKT conditions of ST-MTM Eq. 1 and Eq. 2, i.e.
   they are the exact optimum of the instance. The order itself comes from
   SciPy optimal leaf ordering (ST-MTM Sec. 4.1.1); its adjacency cost is
   compared with exhaustive enumeration over all tree-consistent orders.
3. **TMTM's objective.** At every step all 2^k branch decisions of the next tree
   (k <= 12) are enumerated against the same previous greedy layout; the greedy
   choice is compared with this per-step optimum of TMTM Eqs. 2-3. This is not
   a sequence-wide optimum.

Volumetric ST-MTM KKT residuals are read from
`results/stmtm_completion20261026/*/solver_checks.json`. Volumetric TMTM uses a
separate compact implementation and is not covered here.

```sh
cd code
PYTHONPATH=src python experiments/instance_reproduction/run.py            # ring, olr, pm25
```

Requires `clang++` (compiles `experiments/baseline_audit/official_core_fixture.cpp`
into `code/tmp/`). Outputs: `results/instance_reproduction20261027/<name>.json`
and `volumetric_stmtm.json`.
