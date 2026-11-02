# AnchorMTM — current paper

Only the current manuscript, companion supplement, two figures, and their editable PowerPoint sources are retained here.

- [Main paper (PDF)](drafts/method_anchor_figures_updated_en.pdf) · [LaTeX](drafts/method_anchor_figures_updated_en.tex)
- [Supplement (PDF)](drafts/method_anchor_single_parameter_supplement.pdf) · [LaTeX](drafts/method_anchor_single_parameter_supplement.tex)
- Figure 1: [PDF](figures/anchor_storms_overview.pdf) · [editable PPTX](figures/editable/Storms_feature_support_improved.pptx)
- Figure 2: [vector PDF](figures/anchor_leaf_correspondence.pdf) · [PNG](figures/anchor_leaf_correspondence.png) · [editable PPTX](figures/editable/AnchorMTM_cross_frame_solid_editable.pptx)

The first figure uses the current editable central-Storms sequence figure: five snapshots (frames 363, 385, 408, 430, 452), one matched extremum (stored Track 260), mapped profiles at the saved 5% budget, twelve colored intermediate profiles with dashed borders, and the complete 744-frame map. Date labels come from the original saved timestamps. The matching identity endpoints do not establish physical storm genesis or dissipation. The source is `output/storms_central_lifecycle_real_20261102/ppt/Storms_central_lifecycle_editable.pptx`; scientific data come from `output/storms_hourly_anomaly_fine_20261030/coherent/maps.npz` (`eps_0.05`). The correspondence figure retains the updated supports and compact full-column layout. The main paper has 7 pages; the companion supplement has 8 pages. Experiments, Discussion, and Conclusion remain placeholders.

## Build

Run from `drafts/`, using a TeX installation with `algorithm2e` and the standard AMS, graphics, font, and hyperlink packages:

```sh
tectonic -X compile method_anchor_figures_updated_en.tex
tectonic -X compile method_anchor_single_parameter_supplement.tex
```

The bundled `vgtc.cls`, bibliography style, and `../refs.bib` are required. Generated compiler caches and logs are excluded. This cleanup changes no method implementation or experimental results. Historical paper files remain available in Git history.
