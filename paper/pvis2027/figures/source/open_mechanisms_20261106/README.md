# Figures 4–6: direction, conflict and selective relaxation

The three final open-composition PNGs are embedded unchanged into a three-slide PowerPoint (one figure per slide). This preserves the image-generation artwork. Slides contain movable/replacable pictures, not individually editable diagram lines or labels. No mapping figure is included.

Canonical PPT: `../../../最新论文与三张PPT/Fig4-6_方向_冲突_放松.pptx`. Paper PDFs: `../../anchor_direction_open.pdf`, `../../anchor_conflict_open.pdf`, `../../anchor_relaxation_open.pdf`. Each is included with `width=\columnwidth` in a regular `figure` environment. Source PNGs retain their full resolution.

Former Figures 4–6 (leaf correspondence, projection conflict, selective relaxation) are temporarily withdrawn from the manuscript; original assets remain in place and their figure environments are preserved in `temporarily_removed_figures_4_6.tex`. This revision does not change the Storms or Cylinder evidence.

## Rebuild

Run `export_paper_pdf.py` with PyMuPDF to generate the paper PDF wrappers. Set `RUNTIME_NODE_MODULES`, `RUNTIME_PYTHON` and `PRESENTATIONS_SKILL_DIR` to the bundled workspace runtime and presentation-skill paths, optionally set `ANCHORMTM_FIGURE_OUTPUT_DIR` to a fresh output directory, then run `node build_ppt.mjs`. Final PPTX outputs are never overwritten by the validator.

The figures are conceptual schematics, not experimental measurements. Figure 5 uses target order A,C,D,B, matching the updated local manuscript example. Heights in Figure 6 are schematic, without numeric error claims.


## Current manuscript export

Original PNG artwork is preserved without redraw, recoloring or background replacement. The current export script embeds these original PNGs directly into PDF. The original three-slide PPT likewise retains the original artwork. Approximate native reconstructions are excluded from publication.
