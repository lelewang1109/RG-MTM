# AnchorMTM construction overview (Figure 2)

Only the middle construction panel (b) of the independent concept is retained. The four stages preserve every internal component: scalar-field thumbnails; matched augmented trees and Track IDs; motion vectors, global direction and projected references; three candidate orders; width-aware refinement; separate displacement and merge-error evaluations; admission and rejection; selected order and heuristic-search label; reference targets, interval anchors and displacement cap; weighted four-term QP; valid history and projected motion; reconstructed profile; leaf/LCA filling and barrier correction; stacked profiles and map assembly; temporal map, axes and scalar key.

The style matches the current paper: Times New Roman, white panels, gray headers, dark outlines, and feature colors A blue `#0066CC`, B orange `#FF8800`, C teal `#009E91`, D violet `#9656AD`.

All labels, trees, curves, nodes, intervals and arrows in the PowerPoint are native editable objects. `assets/storms_map.png` is a raster background copied byte-for-byte from the current qualitative Storms output at epsilon=10%, formerly used in Figure 5 (now Figure 6). The remaining schematics are conceptual, without measured layout values. The scalar key indicates relative value order; it is not a calibrated numeric legend.

## Rebuild

`build.mjs` contains the full native object geometry. It uses the bundled `@oai/artifact-tool` runtime and presentation validators. Set `RUNTIME_NODE_MODULES`, `RUNTIME_PYTHON`, and `PRESENTATIONS_SKILL_DIR` to the paths returned by the workspace-dependencies tool. Optionally set `ANCHORMTM_FIGURE_OUTPUT_DIR` to a new output directory. Create `.build/` before running. The finalizer does not overwrite an existing final PPTX.

```sh
node build.mjs
```

Export the resulting PPTX with LibreOffice/PowerPoint to PDF. For the published PDF, LibreOffice was run with a private Fontconfig configuration including `/System/Library/Fonts/Supplemental`, ensuring that Times New Roman is embedded. The final PDF is `../../anchor_framework.pdf`; the editable PPTX is in the canonical paper delivery directory. The PDF is vector except for the scalar map. The current LaTeX uses a full-text-width `figure*`.

The content follows the current method section. The candidate search is heuristic; tau and delta* are exact evaluations only for a fixed order. Feasible continuous barriers do not unconditionally certify the rendered map.
