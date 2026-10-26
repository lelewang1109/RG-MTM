# 目录导读：如何理解RG-MTM文件夹

本导读以2026-10-26当前稿为准。GitHub仓库根目录对应本地工作区的 `RG-MTM/`；本地外层 `其他/` 和 `output/` 是归档、汇报与发布工作区，不是算法运行的必要目录。

## 先判断你要做什么

| 任务 | 打开什么 | 得到什么 |
|---|---|---|
| 看完整叙事 | `paper/manuscript/Revised_RG-MTM.pdf` | 26页当前正文 |
| 查证明和细节 | `paper/manuscript/Revised_Supplement.pdf` | 52页当前附录 |
| 改最终稿 | `paper/manuscript/latex/main.tex` 及其input的模块 | 当前源码，无需恢复旧稿 |
| 找图件母版 | `paper/FIGURE_INDEX.json` | 正文编号、稳定文件名、编辑源和页码 |
| 查总评价数字 | `code/results/stmtm_completion20261026/unified_metrics.csv` | 九输入、四方法完整指标 |
| 看方法实现 | `code/src/rgmtm/unified.py`、`framework.py`、`error_budget.py` | 共同QP、预算/屏障与区间约束 |
| 核验或重跑 | 各 `code/experiments/*/README.md` | 输入、设置、保存结果及验证命令 |

## code：方法、实验与数值证据

`src/rgmtm/` 实现共享区间模型、参考点、误差预算、屏障与独立基线。`experiments/` 定义某次实验的输入和设置。`results/` 保存输出，文件夹后缀通常是实验身份或日期。`analysis/` 是证书、处理、指标与作图共用模块，存在互相导入关系。`tests/` 核验实现和输入契约，`provenance/` 记录冻结来源及迁移身份。

| 实验入口 | 保存结果 | 当前作用 |
|---|---|---|
| `experiments/unified/` | `results/unified20261025/` | 共同四项QP的五个设置；614帧×5，496帧全顺序覆盖、118帧候选池 |
| `experiments/framework/` | `results/framework20261025/` | 独立连续预算/位置前沿与反向查询；603/11覆盖 |
| `experiments/stmtm_completion/` | `results/stmtm_completion20261026/` | 四组共325个新增ST-MTM布局，当前总表来源 |
| `experiments/publication2027/` | `results/publication2027/`、`submission20261023/` | 既有P/R、旧运行与冻结表格的溯源，不覆盖当前稿 |
| `experiments/volume3d/` | `results/volume3d/` | Tangaroa正式三维体输入和扩展 |
| `experiments/paper1_suite/` | `results/paper1_suite/` | Nucleon、重建Benzene和三维Cylinder |

`slp_thresholds20261026/` 是独立压力预算诊断，不代替共同模型实验。Storms首图又是独立的逐小时资格阈值例子。

## paper：当前可继续修改的论文

`manuscript/` 的两份PDF是阅读入口；`manuscript/latex/` 是编辑入口。`main.tex` 用input组合章节，`supplement.tex` 组合附录。编译图件在 `latex/figures/`，冻结证据在 `latex/evidence/`；独立源码ZIP放在Release。

`figures_export/` 保存当前PDF/PNG/SVG。`FIGURE_INDEX.json` 关联正文图号与稳定资产名。重排后，例如正文图7/8对应稳定文件Fig16/Fig17，不能只根据文件名猜正文编号。

当前图1的编辑源是 `previews/storms_anatol_20261026/render_teaser.py` 和 `figures_export/Fig1.svg`。既有 `figures_ppt/Fig1.pptx` 和合并PPT对应页保留旧版；新版图1及资产Fig15—17使用代码/SVG，不从旧PPT重新覆盖。

`.build/` 是本地编译、渲染、改稿备份和检查缓存，不是当前稿入口，也不进入GitHub发布。`checks/` 是带有适用范围的核验记录。`figures_export/revisions/`、`figures_ppt/revisions/` 和previews中的旧版供比较，当前图仍以根级图件和索引为准。

## data：数据政策与输入入口

`real/`、`RG-MTM-public-scalar/` 按协议保存真实与派生输入。`code/data/real`、`code/data/public_scalar` 是相对链接，不代表第二份数据。

本地原始体与完整地图规模较大。GitHub提供经选择的小型输入、坐标、协议、清单和可核验结果。库存条目说明来源或本地存在，不意味着每个大文件都可从Git下载。见 [数据说明](../data/README.md) 和各实验协议。

## docs与references

`docs/` 的本导读解释目录；[修改流程](EDITING_AND_REPRODUCING.md)解释操作；贡献文档解释当前方法。旧整理、选图、审稿建议保留决策过程，阅读时同时检查日期。

`references/` 提供阅读与来源索引，正文引用以 `paper/manuscript/latex/refs.bib` 为准。GitHub通过原来源链接提供第三方文献，不把第三方整篇PDF作为本项目成果发布。

## 不能混用的数量与概念

| 数量或参数 | 含义 |
|---|---|
| 614帧 | Storms118、Wildfires30、OLR60、PM2.5全年366、Ring40，五组二维时序 |
| 744小时 | 独立Storms逐小时可视化，首图选取其中局部 |
| 325个布局 | 四组原缺失输入的新增ST-MTM对照，不直接与614帧相加解释共同模型规模 |
| 64帧 | 独立镜像/垂直平分线控制 |
| 201/102体 | Tangaroa/Cylinder三维时序；最终时间地图仍为二维图 |
| 1/21切片 | Nucleon静态切片、Benzene静态平行截面，不是物理时间 |
| κ | 既有P/R构造的层次放松资格，不是实际输出误差上界 |
| ε、B | 共同模型中分别约束拓扑误差与参考位移的预算 |

A/B/C等字母只在相应案例内部表示计算特征。轨迹中断、重新编号或一维坐标跳变，不直接证明物理气旋消失、换身份或发生同样的真实位移。

## 推荐阅读路线

- 理解研究：根README → 正文图1与引言 → 贡献说明 → 共同模型代码和实验。
- 继续改稿：当前PDF → main/supplement.tex → 章节模块 → 图件索引 → 修改流程。
- 核验数字：当前CSV与报告 → 实验协议 → 保存数组和元数据 → 独立检查器。
- 从头重跑：数据协议 → 准备输入 → 实验设置 → 运行 → 验证 → 导出 → 编译。阅读或编辑论文不必先重跑实验。
