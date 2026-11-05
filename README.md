# AnchorMTM

Spatial anchoring, topology-budgeted merge-tree layouts, and certified position bounds for temporal maps of scalar fields.

## Current paper — 2026-11-05

- [Main paper (PDF)](paper/pvis2027/最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX](paper/pvis2027/drafts/method_anchor_figures_updated_en.tex)
- [Current eight figures and five editable PowerPoints](paper/pvis2027/figures/FIGURE_INDEX.md)
- [Figure 5: Storms parameter profiles and event maps](paper/pvis2027/figures/anchor_storms_budget_profiles.pdf) · [editable PPT](paper/pvis2027/最新论文与三张PPT/Fig5_Storms参数剖面.pptx)
- [Figures 6–7: NROE/NMLE budget diagnostics, CSV and plotting script](paper/pvis2027/order_scalar_budget_20261105/README_zh.md)
- [Formal quantitative results and input protocol](paper/pvis2027/experiments_ratio_p_20261104/REPORT_zh.md)
- [Supplement and build instructions](paper/pvis2027/README.md)

The main body ends on page 9; the PDF has 10 pages including references. Captions and experiment prose are condensed without reducing body font size or margins. The double-column Storms parameter study is Figure 5 at the top of page 8, before the volumetric diagnostics and Figure 8 Cylinder visualization. Gray reference lines are darker. The 30% column is omitted because it coincides with 20%; no artificial offsets are used.

The formal four-input comparison uses Exact and Balanced budgets of 1%, 1%, 5%, and 10% for Gaussian, Ring, Wildfires, and Storms. Published TMTM/ST-MTM SNS/TW and locally measured metrics retain explicit input provenance and coverage limits. The qualitative Storms archive and exploratory Cylinder variant are distinguished from the quantitative comparison.

Full source fields and large intermediate archives remain external under the existing data distribution policy. Curated CSVs, plotting sources, compact figure caches and editable scenes are included. Historical budget-study materials remain available but are superseded by the current manuscript and figure index.

## Research materials

- [Method and baseline code](code/)
- [Data documentation](data/)
- [Research documentation](docs/)
- [References](references/)

This publication update synchronizes the current method source and curated formal experiment outputs. Historical reports under `docs/` describe earlier research stages and may refer to paper paths available only in Git history.
