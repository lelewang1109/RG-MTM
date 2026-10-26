# 保存结果：当前入口与历史身份

本目录保存科学数组、指标、图源与核验记录。原始结果不会因为论文改版而改写为新的实验。当前活跃入口如下：

| 目录 | 含义 |
|---|---|
| `stmtm_completion20261026/` | 当前九输入四方法总表，含四组325个新增ST-MTM布局；先读REPORT_zh.md和unified_metrics.csv |
| `unified20261025/` | 614帧×5共同模型设置，3,070个主布局；496帧穷举、118帧候选池 |
| `framework20261025/` | 独立连续前沿与反向查询，603帧穷举、11帧候选上界 |
| `slp_thresholds20261026/` | 独立压力预算及缺失列诊断，不替换共同模型运行 |
| `paper1_suite/` | Nucleon、重建Benzene、三维Cylinder正式输入结果 |
| `volume3d/` | Tangaroa201体、输入审计和三维扩展 |
| `real_case_studies/` | Storms/Wildfires/Tangaroa源场与特征对应证据 |
| `baseline_audit_20261019/` | 原生设置和实现核对 |
| `public_metrics_20261016/` | 保留的标准几何指标与参考任务核验 |
| `submission20261023/` | 历史投稿表格与冻结指标身份；不用于覆盖当前补全表 |
| `publication2027/`、`legacy_publication/` | 旧运行、图源和必要溯源；342帧等计数按其原协议解释 |

当前五个二维时序共614帧，另有Tangaroa201体、Cylinder102体、Nucleon1静态切片与Benzene21静态截面。744小时Storms首图和64帧独立控制另列，不合并总体。κ资格阈值、真正的拓扑预算和位置预算也分别解释。

论文图号由 [FIGURE_INDEX.json](../../paper/FIGURE_INDEX.json) 决定；当前论文与附录的冻结编译证据在 `../../paper/manuscript/latex/evidence/`，它不是另一套原始实验。

核验与重跑入口见 [目录导读](../../docs/DIRECTORY_GUIDE.md) 和 [修改/复现流程](../../docs/EDITING_AND_REPRODUCING.md)。全部主指标应从对应完整数组和协议重建，不依据图像像素或过时汇总文件推断。
