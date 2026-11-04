# 比例p实验交付索引

当前比例p为Gaussian=.001、Ring=.001、Wildfires=.15、Storms=.105，对应0.1%、0.1%、15%、10.5%。Exact/重新选择的Balanced共8组完成；TMTM与ST-MTM Temporal的NPE随共享输入重算。原文SNS/TW/TD保留引用，Base不展示。

- [中文报告](REPORT_zh.md)：完整16行方法对比、8组Anchor原始指标、覆盖率、预算和时间。
- [主表CSV](comparison_final.csv)、[参数表](anchor_parameters.csv)、[时间](anchor_runtime.csv)、[本地四指标](anchor_metrics_measured.csv)。
- [阈值核对](p_threshold_validation.csv)：880帧p×标量范围全部核对。
- [验证选参](balanced_selection.csv)：40个正预算候选；Gaussian1%、Ring1%、Wildfires5%、Storms10%。
- [拓扑检查](topology_validation.csv)、[独立复核](verification.json)、[自动排名](ranking_audit.csv)。
- [复现说明](REPRODUCE.md)、source/、config/、results/：完整代码、冻结规则和实际地图、树与计时输出。
- [LaTeX主表](tables/quantitative_comparison.tex)、[参数表](tables/anchor_parameter_settings.tex)：时间拆两列，只有两张表，参数表白底。

旧百分数解释实验完整保留于../experiments_final_20261104；旧论文另在archive/prior_percentage_p_paper保存。当前论文5.1/5.2/5.5已同步，其他待补章节不因此成为完成稿。表格按四方法显示数值逐数据集/指标自动排名；作者TD单位和最终处理数组未确认，数值强调不构成严格同单位/同输入性能证明。
