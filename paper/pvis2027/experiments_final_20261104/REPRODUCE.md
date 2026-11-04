# Reproduction

Run from `/Users/lele/Desktop/MergeTreeMaps` with `.venv/bin/python`.

1. `python paper/pvis2027/experiments_final_20261104/source/run.py`
2. Retry only failed baseline NPE after the numerical fix if needed: `python paper/pvis2027/experiments_final_20261104/source/run.py --baseline-npe-only`.
3. `python paper/pvis2027/experiments_final_20261104/source/assemble.py`
4. `python paper/pvis2027/experiments_final_20261104/source/verify.py`
5. `python paper/pvis2027/experiments_final_20261104/source/write_report_paper.py`
6. `python paper/pvis2027/build_main.py`

Use `--dataset Gaussian|Ring|Wildfires|Storms` to resume one dataset. Existing successful measured runs are retained. To explicitly remeasure a successful mode, archive that mode's output directory first; the script will then rebuild its source and trees rather than reusing intermediates. OS page caches are not cleared. Numerical warnings remain in logs; final finite-value, KKT and topology checks are mandatory.

Dependencies: NumPy, SciPy (milp/HiGHS), netCDF4, OSQP, Clarabel, threadpoolctl; pinned project TTK 0.9.9 binary at `RG-MTM/code/tmp/volume3d/native-build/rgmtm_ttk_volume` (source in `code/experiments/volume3d/native`). Existing baseline/Anchor algorithm files are imported from `RG-MTM/code`, not modified. Their exact hashes are in `config/core_sha256.json`; `source/core_snapshot` is a read-only reference copy, not an alternate implementation. Input paths and hashes are recorded in each preparation protocol. Do not reinterpret archived10.5% runs as0.105%.

Exact Python versions are in `source/requirements.txt`, `config/package_versions.json`, and the full `config/python_environment.txt`. The extraction binary used is also preserved as `source/native/rgmtm_ttk_volume_macos_arm64`, with SHA256 in `config/reference_and_binary_provenance.json`. It is platform-specific. To rebuild elsewhere, use the archived native CMakeLists/main.cpp with verified TTK0.9.9 sources, for example `cmake -S source/native -B native-build -DTTK_SOURCE_DIR=/path/to/ttk-0.9.9 -DCMAKE_BUILD_TYPE=Release`, then `cmake --build native-build --target rgmtm_ttk_volume`; the driver currently expects the project binary path above. Raw source data remain in the project and are not downloaded or replaced by the script.

SNS/TW/TD baseline cells are literal Table1 transcriptions in `source/assemble.py`; baseline computation executes NPE only. Local TD is a full-canvas-normalized sum. Published TD units are unverified: actual normalized local TD is shown in the main cells with an n header, and no cross-unit TD ranking is applied. SNS/TW/NPE best and second are computed across the four methods per dataset, with SNS/TW labelled a descriptive numeric summary of potentially different processed inputs. Each Anchor method has separate t_opt/t_total columns; there is no separate runtime table. Parameter rows have white backgrounds.

Selection rule v3: positive candidates1..10% at1% increments, first chronological25% validation, actual topology maximum<=each nominal epsilon. Minmax-normalize validation NPE/SNS over legal positive candidates (constant components0 only in the score), J=.5NPE_norm+.5SNS_norm. Within Jmin+.01 prefer smaller epsilon then smaller attained topology error. NEVER fallback0; do not manufacture a changed output. Freeze positive budgets and run final Balanced cold pipelines. Full-sequence statistics contain validation; suffix statistics are separate. Earlier outputs were already observed, so this is not claimed as a new blind test.
