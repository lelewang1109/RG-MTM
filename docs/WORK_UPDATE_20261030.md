# 工作整理与发布索引（2026-10-30）

## 当前论文

入口：`paper/pvis2027/main.pdf` 和 `supplement.pdf`，LaTeX 工程在同目录。正文 9+2 页，附录 10 页。

- N4 可控冲突实验完成：172 组重叠/宽度设置、364 组预算设置，独立 LP 与全叶序验证。
- 保留新增局部预算响应实验，明确预算增大不保证每个点的位置误差都改善。
- 改进版 Storms 支撑区域图已作为首图；五组数据集六档预算总览为正文图 11。
- 旧半日 Storms 图和 OLR/Ring 对比图保留在附录；额外诊断序列不并入 917 帧横评。

## 可编辑 PPT

- 当前首图：`paper/figures_editable/20261030/Storms_feature_support_improved.pptx`
- 原二维图：`paper/figures_editable/20261030/Storms_teaser_hybrid_editable.pptx`
- `paper/figures_editable/20261030/Vortex_teaser_editable_final.pptx`

改进版另存为可编辑副本，原两份 PPT 保留。改版依据见 `docs/STORMS_FIGURE_READING_20261030.md`，实际支撑集合和核验记录见 `paper/visualizations/20261030/storms_feature_support/`。

## 五组总览图（正文图 11）

目录：`paper/visualizations/20261030/dataset_overview_extended/`。

二维 Storms/Wildfires/PM2.5、三维 Tangaroa/Vortex；六档 ε=0/2/5/10/20/30%；ε=0 条状剖面和参考 q、时间序 A1/A2/A3、快照列框选、三维包围盒。Tangaroa 与 Vortex 恢复原三维传递函数配色，PM2.5 采用固定高对比显示范围。

新增 30% 的 391 个前缀布局保留首帧起完整时间历史，独立约束与渲染检查在目录内。该总览图已插入主文。

PDF/SVG/PNG/PPT 可直接查看。可视化复现脚本依赖本地完整原始数据及既有实验工作区；设置 `MERGETREEMAPS_WORKSPACE` 指向完整 MergeTreeMaps 工作区。不要把仅含发布文件的仓库当作所有原始数据均已下载的工作区。

## 数据与复现边界

不上传原始 ERA5/野火/体数据下载包、虚拟环境、编译缓存、临时截图或微信附件。实验协议、生成源码、必要的新结果及核验记录随图件发布。用户历史提交和冻结基准结果保留。

## 本轮最终论文图替换

首图已引用 `fig_storms_support.pdf`，对应 `Storms_feature_support_improved.pptx`；正文图 11 已引用 `fig_dataset_overview_extended.pdf`，原 Vortex 大图保留为历史图件。五组总览已正式插入主文。改进首图源 PNG 冻结在 figures/，`fig_current_teaser()` 可重新封装 PDF。

远端 06dcd53 的 Near-Optimal 标题、定理定义域、保守最优性表述和 ERA5 文献条目，与本地新增实验和图件已按共同基线进行三方文本合并。

最新独立 LaTeX 包：`paper/pvis2027/export/RG-MTM_PacificVis2027_Current_20261030.zip`；包含本次图替换、当前正文和附录。
