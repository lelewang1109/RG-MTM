# 正式实验交付索引

最新规则：Exact固定ε=0；Balanced按前25%验证窗口的固定J=.5 NPE_norm+.5 SNS_norm，在1%–10%的合法正预算中选择并冻结。40个正候选均合法。四数据集各两组正式Anchor结果，当前展示TMTM与ST-MTM Temporal共8组NPE；Base历史结果保留但不展示。

| 文件 | 用途 |
|---|---|
| [REPORT_zh.md](REPORT_zh.md) | 中文结论、完整主表、本地四指标、输入及可比性限制 |
| [comparison_final.csv](comparison_final.csv) | 四数据集×四方法：主比较表及逐列来源 |
| [anchor_metrics_measured.csv](anchor_metrics_measured.csv) | 八组Anchor实测SNS/TW/TD/NPE，含TW有效帧与后75%NPE |
| [anchor_parameters.csv](anchor_parameters.csv) | 每数据集独立正ε、实际NMLEmax、验证J及固定QP参数 |
| [balanced_selection.csv](balanced_selection.csv) | 40个正ε验证候选和4个Exact诊断端点的完整选择记录 |
| [anchor_runtime.csv](anchor_runtime.csv) | Exact/Balanced优化及完整流水线时间、硬件、线程、缓存、实际重复数 |
| [baseline_npe.csv](baseline_npe.csv) | 三基线共享输入NPE、全局反射及重合锚点统计 |
| [topology_validation.csv](topology_validation.csv) | 实际连续/渲染预算、重建及锚点合法性 |
| [input_audit.csv](input_audit.csv) | 尺寸、p口径、实际特征数及输入重建标记 |
| [ranking_audit.csv](ranking_audit.csv) | SNS/TW/NPE按数据集四方法统一自动排名及来源标记 |
| [verification.json](verification.json) | 独立指标、参考、预算及源码哈希验证总结果 |
| [profile_validation_per_frame.csv](profile_validation_per_frame.csv) | 剖面极值数量、实际误差及Ring整数修复逐帧证据 |
| [REPRODUCE.md](REPRODUCE.md) | 重跑、依赖、原始输入和TTK二进制说明 |
| [LaTeX主表](tables/quantitative_comparison.tex) | booktabs、跨双栏、自动最佳/次佳 |
| [LaTeX独立参数表](tables/anchor_parameter_settings.tex) | 所选正ε与实际NMLEmax |
| [TD历史核验](TD_AUDIT_zh.md) | 29.336508与当前TD的不同输入及独立求和证据 |
| [source/](source/) / [config/](config/) | 实际脚本、同方程数值适配、核心参考快照、冻结规则及环境 |
| [results/](results/) | 全部候选、地图、布局、共享参考和真实计时提树 |
| [archive/](archive/) | 历史定义、失败试验及原论文备份；不作为当前结果 |
| [qa/](qa/) | 编译论文相关页的最终渲染与文本检查 |

Gaussian/Wildfires和Storms明确标注为处理输入重建；不能宣称已获得作者最终数组。Ring原196点画布保持不变。主表已直接列出本地归一化TD，原文TD单位未确认，仅按原文组/本地归一组分别标最优、次优，不跨单位排名。两组Anchor各补充一列Time(s)，t_opt与t_total拆为两列，删除表3；独立参数表为白底。SNS/TW/NPE统一按各数据集四方法显示数值自动判断最优/次优，SNS/TW跨输入仅为描述性汇总。Ring的本地TW仅1/40帧有效。所有时间各实测一次，未宣称统计显著加速。

已同步[正文源码](../drafts/method_anchor_figures_updated_en.tex)的5.1、5.2、5.5，编译后的[最新论文PDF](../最新论文与三张PPT/AnchorMTM_最新论文.pdf)和三图压缩包已更新。5.3、5.4、Discussion和Conclusion仍有待完成，未把定量实验交付等同于整篇论文完稿。
