# AnchorMTM — 当前论文与大纲

- [正文 PDF](最新论文与三张PPT/AnchorMTM_最新论文.pdf) · [LaTeX](drafts/method_anchor_figures_updated_en.tex)
- [完整中文大纲（重点修订第五节）](OUTLINE_zh.md)
- [当前八张正文配图](figures/FIGURE_INDEX.md)
- [补充材料](drafts/method_anchor_single_parameter_supplement.pdf)

## 当前修订（2026-11-06）

图6只保留原第二行的事件地图与局部放大，保留五个预算列标题。正文暂撤原图7、8预算诊断曲线，源文件保留；原图9 Cylinder变体自动顺延为图7。图6两行原始资产与PPT仍保留，正文使用独立的anchor_storms_budget_maps.pdf。

第五节调整为：数据与评估协议、参考定位与空间质量、拓扑有效性与放松效果、Storms案例、参数与计算成本、三维探索案例。正文删除被撤曲线的引用与密集趋势叙述，保持四数据集主表和所有测量值不变。完整写作逻辑与证据边界见中文大纲。

从仓库根目录运行 `python3 paper/pvis2027/build_main.py` 编译正文。历史章节生成器 `section5_revision_20261105/source/update.py` 尚未迁移本轮结构，不应直接运行覆盖当前正文。

正式四数据集结果见[比例p实验](experiments_ratio_p_20261104/REPORT_zh.md)。Gaussian、Ring、Wildfires、Storms的Balanced预算分别为1%、1%、5%、10%。完整原始数据和大型中间数组仍保留在本地。

## 最新排版（2026-11-06）

使用 IEEE VGTC Conference review 模式，保留模板字体、双栏尺寸、页边距及原图细节。正文9页，含参考文献共10页。图4–6沿用原图构图，已将浅灰背景清理为纯白并覆盖原PNG、配图PDF和PPT内嵌图片，不采用近似重绘版本。清理仅作用于近白色区域，使用平滑过渡保留渐变边缘，文字、深色线条及饱和颜色保持原像素。

| 页码 | 图表与对应内容 |
|---|---|
| 1 | 图1：Storms概览与研究动机 |
| 2 | 图2：既有TMTM / ST-MTM流程与相关工作 |
| 3 | 图3：AnchorMTM完整流程框架；本页无其他图 |
| 4 | 图4：运动方向与固定空间参考 |
| 5 | 图5：参考顺序与拓扑连续块冲突 |
| 6 | 图6：选择性拓扑放松与理论分析 |
| 7 | 表1、2：四数据集比较、参数与运行时间 |
| 8 | 图7：Storms预算案例 |
| 9 | 图8：Cylinder三维探索案例 |
| 10 | 参考文献 |

正文每页均至少包含一张图或表。图2、3保留已有可编辑PPT；图4–6的原生形状重建暂不纳入本版，以确保原图一致。

后续PPT更新：图4–6的PPT已替换为619个原生可编辑对象组成的三页版本，见[重建说明](figures/source/open_mechanisms_native_20261106/README.md)。本次只更换PPT，正文PDF配图继续保留已批准的原始图面；原生重绘的平滑纹理及字体渲染与栅格原图存在细微差异。

[图件索引](figures/FIGURE_INDEX.md)列出当前编号及对应资产。格式依据：[PacificVis 2027 submission guidelines](https://pacificvis2027.github.io/contribute/paper-submission-guidelines/)。


最新同步：三图说明文字统一为Times New Roman正体、32 px；数学标签保留斜体。第二图AB/CD根节点等高，第三图圈出放松节点。正式PPT共632个原生对象，正文图4–6现使用该PPT经办公软件渲染的3072×2048截图，替代上一版图面。
