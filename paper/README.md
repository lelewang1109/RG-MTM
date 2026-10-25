# 当前论文：统一位置—拓扑框架

2026-10-26 当前副标题为 **A Unified Position–Topology Framework**。在原有四项公式、共同区间表示、QP和绘制流程内，通过权重、时间目标和双预算表达不同设计原则。

| 入口 | 内容 |
|---|---|
| [正文](manuscript/Revised_RG-MTM.pdf) / [附录](manuscript/Revised_Supplement.pdf) | 当前改稿，25页正文、50页附录 |
| [LaTeX项目](manuscript/latex/README.md) / [源码ZIP](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26/RG-MTM_LaTeX.zip) | 当前TeX、图与证据，可独立编译 |
| [贡献说明](../docs/统一体系贡献说明_20261025.md) / [论证大纲](MANUSCRIPT_OUTLINE.md) | 统一模型、冲突解释、受控实验三项贡献 |
| [新实验](../code/experiments/unified/README.md) / [新结果](../code/results/unified20261025/) | 614帧×5设置、15,141个QP、双预算矩阵和原生相似性 |
| [图16](figures_export/Fig16.svg) / [图17](figures_export/Fig17.svg) | 原生/统一工作区域对照；拓扑×位置阈值矩阵 |
| [图件索引](FIGURE_INDEX.json) / [核验范围](COMPREHENSIVE_REVIEW.md) | 17张正文图的身份与来源 |
| [原PPT合集](figures_ppt/All_Figures.pptx) / [附录PPT](figures_ppt/All_Supplementary_Figures.pptx) | 分别覆盖原图1—14、附图1—18；图15—17使用代码/SVG |

新QP实验有496帧穷举、118帧候选搜索；独立前沿实验framework20261025保留其603/11的覆盖身份，不能混用。七项新增检查后完整套件为57项。

维护：统一实验run.py → export.py → 编译正文/附录并检查渲染 → scripts/package_delivery.py → scripts/verify_unified_revision.py。当前检查器独立重建目标、约束、QP间隙、标量与位置误差，核对旧证据、图件、PDF和ZIP。

TMTM-inspired和ST-MTM-inspired是设计原则的参数区域，不宣称原生算法等价。连续预算、候选覆盖、严格极值栅格误差和全时序最优性各自声明。

重构前稿保存在../../其他/归档/思想统一重构前_20261025/；更早完整归档仍保留。当前PDF与TeX是唯一活跃改稿。
