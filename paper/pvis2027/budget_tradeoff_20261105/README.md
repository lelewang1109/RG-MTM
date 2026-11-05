# Figure 5: position--topology trade-offs

The current single-column Figure 5 contains Storms, Wildfires, Ring, Tangaroa (3D), and Cylinder (3D). Gaussian is omitted only from this plot: its configurations coincide, and its quantitative table results remain unchanged. The paper remains nine pages, with Figure 5 on page 8.

## Reproduce the figure

```sh
python3 -m pip install numpy matplotlib
python3 paper/pvis2027/budget_tradeoff_20261105/plot_figure5.py
```

The portable script reads only `figure5_metrics.csv` and writes PDF, SVG, and 450-dpi PNG to `../figures/`. Times New Roman is used in the publication; install that font for identical typography. No field arrays or archived absolute paths are needed to redraw the measured curves.

## Metrics and scope

There are 59 complete-sequence configurations: Storms and Wildfires have 14 budgets each, Ring has 21, and the two volumetric inputs have five each. Each point uses all frames with its reference, widths, gaps, objective weights and raster length fixed across budgets. Lines only connect measured samples; finite sampling does not establish unrestricted-budget endpoints.

- Horizontal coordinate: worst attained normalized merge error, measured from the rendered profile against the original fixed-leaf merge matrix, including diagonal extremum values.
- Solid curve: `E_inf`, the largest rendered reference displacement across all feature--frames, divided by the fixed physical canvas extent.
- Dashed curve: `E_pool`, the mean over all feature--frames of that displacement. This differs from table NPE, which averages the maximum error in each frame.
- Dot shade and labels: requested merge budget, in percent. The existing Balanced selections are unchanged.

Ring's original 0--30% sweep did not resolve its late transition. Additional budgets of 40%, 50%, 60%, 62%, 63%, 70%, and 100% show worst displacement dropping from 10.021% at 62% to 1.177% at 63%. Enumerating all 120 orders of the responsible five-leaf frame gives a continuous release threshold of 62.0013877%; see `ring_threshold_audit.json`. Large diagnostic budgets are not recommendations to accept that topology change.

## Volumetric provenance and independent checks

The volumetric points reuse complete rendered archives from `output/current_method_parameter_sweep_20261029/`, not the later centered-tree-guidance prototypes or partial p2 previews. Their construction uses width-aware ordering, a singleton capped four-term QP, and optimal scalar filling. Their independent preprocessing protocols are stated in the paper and `volume_protocol.json`; they do not enter the four-input baseline comparison.

| Input | Frames | Grid | Scalar / simplification | Fixed reference |
|---|---:|---|---|---|
| Tangaroa | 201 | 300 × 180 × 120 | Velocity magnitude clipped to [0,2], absolute persistence 0.2 | Matched-extremum motion direction |
| Cylinder | 102 | 135 × 64 × 48 | Normalized negative Q scalar, 2% per-frame persistence | Streamwise x axis |

Both use 8,192-position profiles and requested budgets 0%, 2%, 5%, 10%, 20%. Numerical allowance is `epsilon0=1e-7`. The zero-budget Cylinder output has a small error within this allowance; it is not claimed to be bitwise zero.

All 1,515 rendered columns and 44,785 feature--frame observations were independently rechecked. Raster anchors were recovered by the original fixed-canvas rounding rule; the complete fixed-leaf matrices, including diagonals, were recomputed directly from saved profiles. No budget violations occurred. Source feature hashes match the archived protocols. Metric values use rendered anchors, rather than the older continuous-position summaries.

To repeat the archive audit, obtain the documented original workspace archives and run:

```sh
python3 paper/pvis2027/budget_tradeoff_20261105/audit_archived_volumes.py /path/to/original/workspace
```

Raw map arrays and source volume inputs are deliberately not bundled here. The audit script writes its outputs in this directory. Source hashes and original archive paths provide provenance; they are not download links.

## Published files

| File | Purpose |
|---|---|
| `figure5_metrics.csv` | All five plotted datasets and 59 complete-sequence configurations |
| `plot_figure5.py` | Portable plot-only reproduction |
| `volume_curve_metrics.csv` | Independently measured volumetric summaries |
| `volume_per_frame_audit.csv` | All 1,515 volumetric per-frame checks |
| `volume_protocol.json`, `verification.json` | Frozen references/settings and source/raster hashes |
| `planar_per_frame/` | Per-frame metrics for every plotted planar configuration |
| `inputs/` | Current planar preprocessing/reference audits |
| `audit_archived_volumes.py` | Independent raw-archive audit, requiring external local inputs |
| `workspace_source_snapshots/` | Original workspace sweep sources for historical review; restore their original paths before use |

The workspace sweep snapshots originally lived at `output/paper_curves_20261105/source/{build,plot}.py` and `output/paper_fig5_single_column_20261105/extend_ring.py`. They are preserved as source snapshots, not as the portable plotting entry point. Formal planar reconstruction code and frozen protocols remain under `../experiments_ratio_p_20261104/`.

中文说明：图中删除Gaussian，加入201帧Tangaroa及102帧Cylinder，单栏五子图、共用图例。三维采用单独冻结的预处理和方向；按原始渲染结果重新检查完整固定叶标签合并矩阵，所有预算检查通过。主表仍为原四个二维数据集，Gaussian未从主表删除。可用绘图CSV直接重画，不能用重画代替原始数据的独立测量。
