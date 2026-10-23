# 图1最终候选：五时刻紧凑版

保留目录：figure1_revision_v3_20261023。前两版候选目录已按用户要求删除；本目录中的三时刻旧导出已更新为五时刻最终版，不另存历史版本。原图、正文、母版PPT和原始实验数据未改动，40个原有文件的保护哈希见 original_hashes.json。

## 最终内容

- 左侧五列：1999年12月26日01:00、02:00、03:00、05:00、07:00 UTC。每列为源场、完整分支拓扑、参考q/P/R位置映射。列距和行距已压缩。
- 右侧改为RG-MTM-P和RG-MTM-R20的真实标量时间图，范围均为01:00—07:00，每幅包含全部七个逐小时输出，未把五个不等间隔快照当成等间隔序列。
- 位置映射与右侧两幅图共享0.10—0.52 L显示范围；所有标量场共享[-35,35]hPa配色。右侧虚线标出左侧五个选择时刻。
- A=track127、B=113、C=130；灰点完整保留其他极值。五个时刻的完整树分别有3、3、3、6、5个叶，未裁成三叶树。
- 拓扑纵向间距为示意排版，不代表标量高度。q/P/R间细线表示身份对应，不是运动轨迹。
- 全部内容来自独立744小时异常值实验，未混用118帧定量实验。

## 文件和复现

Fig1_RG_MTM_v3.png为高清预览，PDF为论文排版候选，SVG包含可编辑文字、拓扑和映射。positions.npz只保留本最终图需要的七小时P图及位置；R和原始源场直接读取原有冻结数据。evidence.json保留五个时刻的全部叶位置和逐对实测误差，图内不再放指标表。

使用工作区Python运行本目录build_figure.py即可重新导出。compute_positions.py可从原始冻结输入重算本最终图所需的P缓存（为保持时间正则项，仍计算完整744小时P布局，但仅保存最终需要的七小时）。本轮只裁取已有计算结果，没有重跑优化。

## 英文图注

**Figure 1. Changing spatial-order conflicts in hourly Storms data.** Five columns show source fields, complete branching topologies and the corresponding reference (q), topology-preserving (P), and locally relaxed (R20) positions at 01:00, 02:00, 03:00, 05:00 and 07:00 UTC on 26 December 1999. The right panels show P and R20 scalar temporal maps over the same seven-hour window, with guides at the five selected times. A=127, B=113 and C=130 denote computed feature correspondences; gray dots retain all other extrema. Branching is exact, unary nodes are suppressed, and tree heights are schematic. Lines between q/P/R rows indicate correspondence rather than temporal motion. Position views share the range 0.10–0.52 L, and all scalar fields share the pressure-anomaly color scale. The original tree groups A/B during the early conflict; subsequent topology changes alter the need for relaxation. These hourly data and track IDs are independent of the 118-frame quantitative Storms experiment.
