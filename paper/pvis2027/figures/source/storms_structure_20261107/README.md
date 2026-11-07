# Current Figure6: original top row + editable PPT (2026-11-07)

The first row reuses the original storms_budget_profiles scene geometry: all five parameter titles, trajectories, ROI rectangles, lower-left zooms, dashed reference curves, markers and connectors. Only the row is translated vertically. The lower row retains the newly recomputed same-input TMTM/ST-MTM maps and editable module labels/arrows.

Delivered PPT: ../../../最新论文与三张PPT/Fig6_Storms_参数与方法对比_可编辑.pptx. One slide,108 native shapes (17 text boxes,34 custom editable paths),12 independent scalar-background images. No complete slide/figure screenshot is embedded. ppt_editability_audit.json records package inspection. .build/preview.png is Artifact Tool preview, .build/office_preview.png is the independent office-export render. Finalizer validation is private in .build/validation.json.

Author scene: prepare_editable.py builds editable_scene.json from original row geometry and same-input baseline scalar rasters. build_editable.mjs uses the bundled Artifact Tool and finalizer. Original pre-edit reference row remains in storms_budget_profiles/scene.json. All scalar background source arrays and configuration remain in baseline_maps.npz and baseline_protocol.json. Data rasters retain independent image layers; paths, curves, arrows and text remain editable native PPT objects.

Current paper figure is exported from the validated native PPT through office PDF export and copied to ../../anchor_storms_budget_maps.pdf. Its print layout matches the PPT. The earlier draw.py-only candidate is superseded. The compiled paper has10 pages total, conclusion on9, Figure6 on8. The teaser and method framework remain untouched.
