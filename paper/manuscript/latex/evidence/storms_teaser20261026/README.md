# 当前论文图1：Storms 局部地理与阈值对照

当前论文首图由完整744小时 R20 定位图、五张真实源快照、P/R1/R2/R5 局部图组成。选择 f30–46（1999-12-02 06:00–22:00 UTC）、输出位置0.10–0.42；源快照为 f33/34/35/37/42。只有这些已展示时刻、已展示特征带标记。所有地理坐标、方向投影、标签和帧间缺失均核验；R20定位图所选原始标量列与R5完全一致。

字母 A/B/C/D/E/F 对应计算track 7/5/8/9/10/0。B在09时之后不再独立保留，C从12时开始分配新编号，不将其解释为已核实的物理气旋身份变更。阈值为既有层次放松资格比例，不是实际合并误差硬上限。

文件说明：

- `event_results.npz`：从原序列起点计算到f96的前向P/R布局、全4096行标量列、参考、地理位置、计算ID、实测误差；首图显示其中f30–46。
- `teaser_source_fields.npz`：五张快照的原供应网格气压异常场，使用相同192小时均值基线。
- `metrics.json`：完整输入/代码哈希、逐帧资格变更、73小时候选窗口指标与R20重现核验。正文附录新增的17小时指标从这些完整数组的f30–46直接计算，分母不混用。
- `teaser_layout.json`、`teaser_display_validation.json`：当前首图的布局、字体、源对应与显示重建核验。
- `Anatol_event_threshold_preview.svg`：可编辑矢量文字和标记、内嵌标量位图。正文采用同源的 `figures/Fig1.pdf`。
- `build_preview.py`、`render_teaser.py`、`render_linked.py`：工作区绘图代码的冻结副本。运行需完整RG-MTM代码/数据；这些副本供追溯，LaTeX编译不依赖它们。
- `geographic_correspondence.json/.csv`：前一完整地理版的对应记录；当前五快照精确记录以`teaser_layout.json`为准。

完整仓库重绘入口：`paper/previews/storms_anatol_20261026/build_preview.py`。更新论文应同步导出的PDF/SVG与图注，不从历史PPT页重新覆盖当前首图。此例仍是独立744小时可视化实验，不加入614帧或325输入的评价总体。
