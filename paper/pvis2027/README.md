# AnchorMTM — 当前论文与四张配图

- [正文 PDF](最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX 源文](drafts/method_anchor_figures_updated_en.tex)
- [补充材料 PDF](drafts/method_anchor_single_parameter_supplement.pdf) · [LaTeX 源文](drafts/method_anchor_single_parameter_supplement.tex)
- [四张图的索引与预览](figures/FIGURE_INDEX.md)

| 正文编号 | 内容 | 排版 | 图片文件 | 可编辑源文件 |
|---|---|---|---|---|
| Figure 1 | Storms 空间快照、标量条形与时序地图 | 跨双栏首图 | [PDF](figures/anchor_storms_overview.pdf) · [PNG](figures/anchor_storms_overview.png) | [PPTX](最新论文与三张PPT/Fig1_Storms.pptx) |
| Figure 2 | 叶特征的跨帧对应、延续、出生与消失 | 单栏 | [PDF](figures/anchor_leaf_correspondence.pdf) · [PNG](figures/anchor_leaf_correspondence.png) | [PPTX](最新论文与三张PPT/Fig2_跨帧特征对应.pptx) |
| Figure 3 | 空间投影、增强合并树与顺序冲突 | 单栏，第 4 页 | [矢量 PDF](figures/anchor_projection_conflict.pdf) · [PNG](figures/anchor_projection_conflict.png) · [SVG](figures/anchor_projection_conflict.svg) | [完整编号版 PPTX](最新论文与三张PPT/Fig3_空间映射与拓扑冲突.pptx) |
| Figure 4 | 选择性放松前后的拓扑与极值映射 | 单栏 | [矢量 PDF](figures/anchor_selective_relaxation.pdf) · [PNG](figures/anchor_selective_relaxation.png) | [PPTX](最新论文与三张PPT/Fig4_选择性放松.pptx) |

## 当前版本说明

正文共 9 页，补充材料共 8 页。第5节已按四数据集比例p实验重写，表1展示三方法及AnchorMTM两种Mode，表2为Balanced参数/时间单栏表；Discussion与Conclusion已补齐。SNS/TW原文值与本地重建输入的区别、TW覆盖率均保留说明。Figure 1、2、3保留现有科学内容，首图定性输入与新定量输入在正文中明确区分。本次未修改AnchorMTM核心算法与QP权重。

Figure 1 是当前编辑后的 Storms 首图：五个时刻（frames 363、385、408、430、452）、Track 260、保存的 5% 预算轮廓、12 个带虚线边框的中间帧条形，以及完整的 744 帧地图。历史编辑目录是 `output/storms_central_lifecycle_real_20261102/`（旧 PPT 导出已清理，当前版本见上方交付目录），科学数据来源是 `output/storms_hourly_anomaly_fine_20261030/coherent/maps.npz` 的 `eps_0.05`。匹配身份不代表经验证的物理风暴起止身份。

Figure 3 是合成的 5×7 网格示例，包含 4 个叶极值、35 个样本；合并树由同一网格标量场计算。仅极值参与所示映射。内部弧和合并节点为灰色。节点位于完整采样中心网格单元的中心；边界向外展示半格。宽度条仅为大致示意，不作为定量宽度或优化结果。论文单栏版省略小编号、放大主要标签；完整编号版保留在 PPT 中。

## 复现 Figure 3

从项目根目录执行：

```sh
.venv/bin/python paper/pvis2027/figures/source/make_projection_conflict_paper.py
```

该脚本读取同目录 `projection_conflict_scene.json`，生成论文版 PDF、PNG 和 SVG。`projection_conflict_correspondence.json` 保存支撑集合与节点对应。`projection_conflict_full_generator.py` 保存合成数据、合并树计算及完整图绘制流程，输出到项目 `output/projection_conflict_schematic_20261103/`。

## 编译论文

从 `drafts/` 执行，需可用的 Tectonic/TeX 及现有编译依赖：

```sh
python3 ../build_main.py
tectonic -X compile method_anchor_single_parameter_supplement.tex
```

保留 `vgtc.cls`、`abbrv-doi-narrow.bst` 和 `../refs.bib`。相关旧交付版及图片预览已清理；科学数据、方法代码、绘图源代码和编译依赖保留。本次仅本地更新。

## 2026-11-03 样式统一

Figure 2、3 使用白底、灰色标题底、黑色边框以及统一的 A/B/C/D 蓝、橙、青绿、紫配色。Figure 3(c) 的外框和八个色块均有黑色轮廓。字体与 Figure 1 采用 Times New Roman；按论文实际排版大小校准，主要标签约 6.7 pt，小刻度约 5.6 pt，标题/轴符号约 7.6 pt。数学空集符号可由覆盖该字符的字体渲染。Figure 2 的下标保留为原生可编辑文字。

样式修改与字体修复脚本位于 `output/paper_figure_style_20261103/source/`；PDF 采用本地 LibreOffice 导出，字体配置显式加载系统 Times New Roman。相关旧交付件与预览已清理；后续维护以交付目录中的 PPT 为准。

## 唯一交付目录

[最新论文与三张PPT](最新论文与三张PPT/) 含最新论文 PDF 与四个对应 PPT，不提供压缩包。目录名沿用旧名称。旧的三个 PPT 原路径已移除；`drafts/` 中的旧 PDF 路径仅为符号链接，不是重复副本。

Figure 2 上部网格对比区域已压缩到原高度的 78%，字体保持不变，下部对应状态整体上移；整体图高约减少 15%。

## 2026-11-04 正式定量实验

四数据集8组AnchorMTM与12组基线NPE已完成。正式目录：[experiments_final_20261104](experiments_final_20261104/REPORT_zh.md)。Gaussian/Wildfires为明确标注重建输入；Ring保持196点并通过联合整数舍入。Balanced按固定验证J选择正预算：Gaussian1%、Ring1%、Wildfires4%、Storms10%；Gaussian实际误差0、输出与Exact相同，不制造收益。SNS/TW/NPE按数据集四方法统一自动标最优/次优（SNS/TW跨输入为描述性汇总），归一化TD已直接放回主表并标单位、暂不跨单位排名；两组Anchor各有独立t_opt/t_total列，删除表3、Base行和TW覆盖率上标，参数表白底；完整指标、独立参数表（含实际NMLEmax）、冷流水线时间、全部候选、LaTeX和复现脚本均在该目录。5.1、5.2、5.5已同步；其余未完成章节不因本次定量更新被视为完成。

## 2026-11-04 按比例解释p的重算

当前正式实验为[experiments_ratio_p_20261104](experiments_ratio_p_20261104/REPORT_zh.md)。p比例为0.001、0.001、0.15、0.105，即0.1%、0.1%、15%、10.5%。四数据集8组Exact/Balanced重新计算；选中预算：Gaussian 1%、Ring 1%、Wildfires 5%、Storms 10%。旧百分数解释结果完整保存在experiments_final_20261104。四方法、四指标逐数据集自动数字排名，TD单位与输入限制明示；时间拆两列，删除表3，TW覆盖率只放表注，参数表白底。

## 2026-11-04 选择性放松示意图

新增 Figure 4，位于 Topology-Budgeted Leaf Ordering 部分，单栏排版。左侧保留 AB/CD 两个子树；右侧示意放松 AB 约束后允许 ACDB 顺序，CD 子树保留。它是机制示意，未声称真实误差数值；候选仍须通过原始合并矩阵预算检查。四张 PPT 与最新论文在同一交付文件夹。
