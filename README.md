# AnchorMTM

Spatial anchoring, topology-budgeted merge-tree layouts, and certified position bounds for temporal maps of scalar fields.

## Current paper — 2026-11-05

- [Main paper (PDF)](paper/pvis2027/最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX](paper/pvis2027/drafts/method_anchor_figures_updated_en.tex)
- [Figure 5: three planar and two volumetric budget curves](paper/pvis2027/figures/anchor_budget_tradeoff_single_column.pdf) · [PNG](paper/pvis2027/figures/anchor_budget_tradeoff_single_column.png) · [editable SVG](paper/pvis2027/figures/anchor_budget_tradeoff_single_column.svg)
- [Figure 5 metrics, independent rendering audits and portable plotting script](paper/pvis2027/budget_tradeoff_20261105/README.md)
- [Formal quantitative results and input protocol](paper/pvis2027/experiments_ratio_p_20261104/REPORT_zh.md)
- [Companion supplement, figure sources and build instructions](paper/pvis2027/README.md)

The current manuscript has nine pages. Figure 5 is a compact single-column plot on page 8 with Storms, Wildfires, Ring, Tangaroa (201 frames), and Cylinder (102 frames). Gaussian remains in the four-input method-comparison table but is omitted from the budget plot because its outputs coincide. Ring's sweep extends through 100% to resolve a transition near 62%; this diagnostic does not change its selected Balanced budget. The two volumetric curves use separately documented archived inputs and fixed references; all 1,515 rendered columns were independently rechecked, including the diagonal of each fixed-leaf merge matrix.

The formal four-input comparison uses Exact and positive-budget Balanced settings of 1%, 1%, 5%, and 10% for Gaussian, Ring, Wildfires, and Storms. Published TMTM/ST-MTM SNS/TW and locally measured metrics have explicit provenance and coverage limits. The paper includes default-orientation Hilbert/Morton baselines and separates absolute anchoring from neighborhood preservation.

Full source fields, raw volume arrays, native intermediate trees, and large map archives remain local under the existing data distribution policy. Published curve CSVs and the plot-only script reproduce Figure 5 without these large inputs; independent recomputation of the measured metrics requires the documented source archives.

## Research materials

- [Method and baseline code](code/)
- [Data documentation](data/)
- [Research documentation](docs/)
- [References](references/)

This publication update synchronizes the current method source and curated formal experiment outputs. Historical reports under `docs/` describe earlier research stages and may refer to paper paths available only in Git history.
