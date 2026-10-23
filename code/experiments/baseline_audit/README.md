# Real-data baseline audit

Run `PYTHONPATH=src:analysis:. python experiments/baseline_audit/audit.py` from the repository root. Requires prepared existing ERA5/Wildfire inputs and a C++17 compiler. Reports go to `results/baseline_audit_20261019/`; original experiments are never overwritten.

The C++ harness includes verbatim `LandscapeInfo` and greedy routines from Wiebke/TemporalMergeTreeMaps commit `2c75a10ed2cd55177a25ff751e0c0a8261200717` (the original Inviwo BSD notice is retained). Stub accessors provide identical actual trees and overlap counts. This verifies the core, not the complete author Inviwo/TTK application.

ST-MTM checks use the equations and four filling cases of the supplied preprint. Independent convex KKT checks, exhaustive concordance/order diagnostics, and actual raster barriers use existing real fields. SciPy OLO is retained as specified by the paper; disagreements with exhaustive ordering are reported, not suppressed. Shared-input parameter settings are distinguished from the paper's per-dataset presets.

See the Chinese report and machine-readable evidence under `results/baseline_audit_20261019/` for conclusions and limitations.
