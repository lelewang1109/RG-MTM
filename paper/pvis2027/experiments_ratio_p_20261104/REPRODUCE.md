# Reproduce ratio-p experiment

From the MergeTreeMaps workspace root, use `.venv/bin/python` with the package versions in `source/requirements.txt`. The same scripts also resolve the published repository's `code/` layout. Source data are external; paths and hashes are recorded per preparation protocol. TTK0.9.9 native source/binary and core snapshots are preserved in source/. The native binary is macOS arm64-specific.

Run in order:

1. `python paper/pvis2027/experiments_ratio_p_20261104/source/run.py`
2. `python paper/pvis2027/experiments_ratio_p_20261104/source/assemble.py`
3. `python paper/pvis2027/experiments_ratio_p_20261104/source/verify.py`
4. `python paper/pvis2027/experiments_ratio_p_20261104/source/write_report_paper.py`
5. `python paper/pvis2027/build_main.py`

`--dataset Gaussian|Ring|Wildfires|Storms` resumes one dataset. Successful measured configurations are retained. Archive a final mode directory to explicitly remeasure; it will rebuild preprocessing and trees. All p numbers are FRACTIONS: .001,.001,.15,.105, never divided by100 before threshold multiplication. Cache metadata and every tree's actual threshold are checked. Raw source fields/coordinates may be reused only when unchanged; no old simplified trees/layouts/scores are reused. The old percentage-interpretation directory remains untouched.

Positive Balanced selection remains first-quarter validation, epsilon1..10% in1% steps, normalized J=.5NPE+.5SNS, near-optimal tolerance.01 and smaller-epsilon tie rule. No test-metric retuning, no zero fallback. Baseline SNS/TW/TD are verbatim published scores; only NPE is recomputed on the new shared input. Main numerical rankings are per dataset across the four displayed methods; published TD units remain unverified against local normalized units. No Base row, no separate Table3; both Anchor modes have t_opt/t_total columns. TW coverage appears in notes only.
