# AnchorMTM — 当前论文与八张配图

- [正文 PDF](最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX](drafts/method_anchor_figures_updated_en.tex)
- [补充材料 PDF](drafts/method_anchor_single_parameter_supplement.pdf) · [LaTeX](drafts/method_anchor_single_parameter_supplement.tex)
- [八张图、预览及可编辑文件](figures/FIGURE_INDEX.md)

## 当前版本（2026-11-05）

正文止于第9页，参考文献延续至第10页。图表说明和实验叙述已精简，正文大小及页边距保持不变。Storms参数对比为Figure 5，在第8页顶部跨双栏，早于三维诊断Figure 7和第9页Cylinder Figure 8。

Figure 5采用首图的定性Storms档案，上行为同帧标量剖面，下行为完整事件地图及左下角放大图。预算为0%、2%、5%、10%、20%；30%复核无进一步变化，未列入图中。灰色参考线加深为#555555，字体为Times New Roman；PPT中的线、点、框和文字可编辑。数据无人工偏移，0/2/5%局部重合，10/20%更接近参考。首图定性档案与主表定量输入的区别在正文中明示。

Figure 6、7仅展示NROE与NMLE，不展示旧事件ME或旧位移曲线。[CSV及绘图入口](order_scalar_budget_20261105/README_zh.md)可独立复画。Figure 8为探索性固定树序变体，位置轴不是物理X；其结果不替换四数据集主表。

正式四数据集结果见[比例p实验](experiments_ratio_p_20261104/REPORT_zh.md)。Gaussian、Ring、Wildfires、Storms的Balanced预算分别为1%、1%、5%、10%。输入重建、SNS/TW的跨输入比较及覆盖限制保留在论文中。完整原始数据和大型中间数组仍按现有数据分发政策留在本地。

## 文件与复现

最新正文和五份可编辑PPT统一在[交付目录](最新论文与三张PPT/)；目录名沿用旧名称。八张图的PDF/PNG/SVG和源码见[图件索引](figures/FIGURE_INDEX.md)。旧预算曲线材料留作历史记录，以正文和当前索引为准。

从仓库根目录编译正文，需要Tectonic：

```sh
python3 paper/pvis2027/build_main.py
```

补充材料从drafts目录执行：

```sh
tectonic -X compile method_anchor_single_parameter_supplement.tex
```

Storms最终场景和栅格背景见[源码说明](figures/source/storms_budget_profiles/README.md)；它们支持复画已发布图件，重新运行完整科学计算仍需外部档案。Cylinder轻量缓存与源码位于figures/source/cylinder_centered_blue/。
