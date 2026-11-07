# 当前正文八张图（2026-11-06）

[最新论文 PDF](../最新论文与三张PPT/AnchorMTM_最新论文.pdf)。正文至第9页，含参考文献共10页。原图2暂撤，Ring结果新增为图7。PPT文件沿用既有文件名，正文编号以下表为准。

| 编号 | 内容 | 排布 | 文件 |
|---|---|---|---|
| Figure 1 | Storms 空间支持与时序地图 | 双栏，第1页 | [PDF](anchor_storms_overview.pdf) · [PNG](anchor_storms_overview.png) · [PPT](../最新论文与三张PPT/Fig1_Storms.pptx) |
| Figure 2 | AnchorMTM 完整方法框架 | 双栏，第3页 | [PDF](anchor_framework.pdf) · [PNG](anchor_framework.png) · [PPT](../最新论文与三张PPT/Fig2_系统框架.pptx) |
| Figure 3 | 运动导出的固定方向与空间参考 | 单栏，第4页 | [PDF](anchor_direction_open.pdf) · [PNG](anchor_direction_open.png) · [PPT第1页](../最新论文与三张PPT/Fig4-6_方向_冲突_放松.pptx) |
| Figure 4 | 参考位置与拓扑连续块冲突 | 单栏，第5页 | [PDF](anchor_conflict_open.pdf) · [PNG](anchor_conflict_open.png) · [PPT第2页](../最新论文与三张PPT/Fig4-6_方向_冲突_放松.pptx) |
| Figure 5 | 选择性拓扑放松与剖面变化 | 单栏，第6页 | [PDF](anchor_relaxation_open.pdf) · [PNG](anchor_relaxation_open.png) · [PPT第3页](../最新论文与三张PPT/Fig4-6_方向_冲突_放松.pptx) |
| Figure 6 | Storms 完整事件地图参数对比 | 双栏，第8页 | [PDF](anchor_storms_budget_maps.pdf) · [PNG](anchor_storms_budget_maps.png) · [PPT](../最新论文与三张PPT/Fig6_Storms参数剖面.pptx) |
| Figure 7 | Ring：AnchorMTM两种配置、Hilbert/Morton与源场快照 | 单栏，第8页 | [PDF](anchor_ring_result.pdf) · [PNG](anchor_ring_result.png) · [源码](source/ring_result_20261106/make_figure.py) |
| Figure 8 | Cylinder 中心树变体与源三维快照 | 双栏，第9页 | [PDF](anchor_cylinder_centered_blue.pdf) · [PNG](anchor_cylinder_centered_blue.png) |

暂撤的原Figure 2保留原横向结构，横向压缩20%，Spatiotemporal map为一行；黑框、直角树形、居中二分和对称连接箭头。A/B/C及d1/d2/d3是身份与点对示意，不表示二维距离可在一维全部精确保留。

Figure 6采用与首图相同的定性Storms档案，非主表定量输入。Figure 8为独立探索性配置，不替换四数据集主表。已撤预算曲线仍保留为历史资产。

本轮以三张开放式机制图替换原正文图3–5，均为单栏；映射图暂不纳入。旧图文件保留，旧浮动体源码见[暂撤记录](source/open_mechanisms_20261106/temporarily_removed_figures_4_6.tex)。PPT已改为原生可编辑形状，三页共632个对象，零图片；[重建源码与说明](source/open_mechanisms_native_20261106/README.md)。正文图3–5已替换为新版PPT导出的3072×2048高清截图。说明文字统一Times New Roman正体，数学符号保留斜体，两个子树根节点等高。

图4–6已覆盖为纯白背景版本，保持原始构图和1536×1024尺寸；对应PPT媒体同步替换。原浅灰底备份及背景处理脚本位于source/open_mechanisms_20261106/。

原图2的浮动体及修订前论文保留在[source/ring_result_20261106](source/ring_result_20261106/)。Ring采用四数据集主表的Balanced 1%实际输出，上方40帧结果，下方0、20、39帧快照，统一YlOrBr色标、Times New Roman字体和细黑边框。

最新：Ring只保留20%位置引导单图，采用指定−128.7°方向、196位置、40帧，附0/20/39帧源场快照；正文说明其与主表自动方向不同。原流程图（图2）按用户要求恢复原文件，图3缩为0.85栏宽。其余图主要字体统一Times New Roman并按实际印刷尺寸增大至约10.5–11 pt。最新复核见[source/readability_20261106](source/readability_20261106/README.md)。

2026-11-06最新：图7采用无黑框紧凑单栏布局，左列0%居中与20%靠上，右列用户附件Hilbert/Morton，下排0/20/39帧源场。正式图与图注已同步；详见[source/ring_compact_comparison_20261106](source/ring_compact_comparison_20261106/README.md)。
