# Figure 6: Storms parameter profiles and event maps

`scene.json` stores the final editable line, marker, frame and text coordinates; `assets/` contains scalar backgrounds only. The canonical editable PowerPoint is in `../../../最新论文与三张PPT/Fig6_Storms参数剖面.pptx`.

Run `python3 export_images.py` with NumPy/Matplotlib/Pillow installed to render PDF/PNG into `delivery/`. Times New Roman must be installed for matching typography. This is a plot-only reproduction from the final scene, not a rerun of the scientific method.

Budgets: 0/2/5/10/20%; common profile frame 433, track 260; event window 355–460 and common local crop. True outputs are retained without artificial offsets. The profile is a column of the rendered temporal map, not a geographic transect. Curves use display-only RDP simplification with tolerance 0.18 px. `evidence.json` records the actual/reference positions; `final_verification.json` records the paper layout checks.

Scientific sources (external local archives): `output/storms_hourly_anomaly_fine_20261030/input.json`, `coherent/maps.npz`, and per-budget `coherent/eps_*/result.json`. These qualitative archives differ from the main quantitative input. Full recomputation requires those original archives. The separately verified 30% result coincides with 20% and was omitted.
