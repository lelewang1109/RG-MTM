# 四数据集：持久性参数按标量范围比例解释的重算

四数据集均完成Exact与正预算Balanced，共8组。Balanced重新验证选择：Gaussian 1%、Ring 1%、Wildfires 5%、Storms 10%。主表包含TMTM、ST-MTM Temporal、AnchorMTM Exact和Balanced，共16行；Base不展示。

此次严格执行用户指定的比例解释：p=(0.001,0.001,0.15,0.105)，对应0.1%、0.1%、15%、10.5%。实际阈值为p×每帧预处理标量范围。旧结果在../experiments_final_20261104保留，本轮独立目录未复用旧简化树、布局、指标或时间；仅复用完全相同的简化前场及坐标用于验证缓存。

这是对ST-MTM Table1参数单位的一种明确测试，不把未公开的作者最终预处理数组、TD单位或TW小样本规则当成已经确认。Gaussian/Wildfires与Storms保留明确标注的重建约定。

## 输入与p阈值核对

| Dataset | 尺寸/T | p比例 | 百分比 | 实际叶特征数 | 原表特征数 |
|---|---|---:|---:|---:|---:|
| Gaussian | 128×128/64 | 0.001 | 0.1% | 3–3 | 3 |
| Ring | 14×14/40 | 0.001 | 0.1% | 1–7 | 1–7 |
| Wildfires | 64×64/32 | 0.15 | 15% | 1–13 | 2–34 |
| Storms | 281×181/744 | 0.105 | 10.5% | 1–7 | 1–8 |

p_threshold_validation.csv保存全部880帧的Fmin、Fmax、p比例、预期和实际绝对简化阈值，独立核对全部通过。源场和原QP权重不变，Ring仍使用196点画布。

Gaussian仍是明确三峰重建；Ring复用归档作者生成器；Wildfires保留61天FRP积分为32个等长时间窗、64×64求和、无额外平滑的重建；Storms仍为281×181、744帧ERA5，192小时均值异常与固定空间σ=2、半径5、reflect。各方法共享源场、简化树、原极值、匹配、参考方向、画布与坐标规则。

## 四方法主比较

TMTM/ST-MTM Temporal的SNS/TW/TD直接引用第二篇Table1；它们的NPE在此次新输入上补算。Anchor两模式四指标和时间全部重新实测。

| Dataset | Method | SNS↓ | TW↑ | TD↓ | NPE↓ | t_opt(s) | t_total(s) |
|---|---|---:|---:|---:|---:|---:|---:|
| Gaussian | TMTM | 0.2500 | 0.7700 | 55.5600 | 0.1118 | N/A | N/A |
| Gaussian | ST-MTM Temporal | 0.0600 | 1.0000 | 31.8700 | 0.1154 | N/A | N/A |
| Gaussian | AnchorMTM Exact | 0.0353 | 0.9323 | 0.3834 | 0.0089 | 0.156 | 1.499 |
| Gaussian | AnchorMTM Balanced | 0.0353 | 0.9323 | 0.3834 | 0.0089 | 0.156 | 1.340 |
| Ring | TMTM | 0.2800 | 0.6800 | 12.2300 | 0.1756 | N/A | N/A |
| Ring | ST-MTM Temporal | 0.2100 | 0.8800 | 27.9200 | 0.2463 | N/A | N/A |
| Ring | AnchorMTM Exact | 0.1485 | 0.8571 | 3.9641 | 0.0471 | 0.133 | 0.475 |
| Ring | AnchorMTM Balanced | 0.1334 | 0.8571 | 3.9231 | 0.0395 | 0.150 | 0.486 |
| Wildfires | TMTM | 0.4400 | 0.8800 | 7487.6700 | 0.2280 | N/A | N/A |
| Wildfires | ST-MTM Temporal | 0.2400 | 0.9100 | 3895.3300 | 0.3180 | N/A | N/A |
| Wildfires | AnchorMTM Exact | 0.0426 | 0.9136 | 2.9429 | 0.0131 | 3.084 | 4.279 |
| Wildfires | AnchorMTM Balanced | 0.0447 | 0.8989 | 2.8816 | 0.0116 | 3.324 | 4.424 |
| Storms | TMTM | 0.3400 | 0.7100 | 164.1400 | 0.5753 | N/A | N/A |
| Storms | ST-MTM Temporal | 0.2100 | 0.9400 | 36.2400 | 0.4579 | N/A | N/A |
| Storms | AnchorMTM Exact | 0.0790 | 0.8463 | 42.3775 | 0.0399 | 2.179 | 55.514 |
| Storms | AnchorMTM Balanced | 0.0743 | 0.8766 | 27.2889 | 0.0140 | 2.600 | 63.447 |

LaTeX按每数据集、每指标在四个显示方法中自动加粗最小值（TW为最大值）并下划线第二个不同显示数值；相同显示精度保留并列。没有人为指定Anchor获胜。TD也按显示数值排名，但作者TD与本地完整画布归一化TD的单位可比性仍未确认，因此此项强调仅是数字排序，不能单独证明严格同单位优势。SNS/TW的跨来源比较同样不能替代作者相同数组复现。

## 指标与有效帧

SNS采用平方scale-normalized stress，逐帧原空间支持域质心距离与显示锚点距离拟合尺度并平均。NPE为逐帧最大|x−q|/L再时间平均。TD为相邻帧共同Track ID显示绝对位移之和除固定完整画布跨度；不除帧数、不除匹配数、不乘100。TW采用标准trustworthiness，k分别为1、3、5、3；采用已冻结实现适用域0<k<n/2，不满足者缺失，不填0。

| Dataset | Mode | TW有效帧 | SNS有效帧 | 匹配步数 |
|---|---|---:|---:|---:|
| Gaussian | AnchorMTM Exact | 64/64 | 64/64 | 189 |
| Gaussian | AnchorMTM Balanced | 64/64 | 64/64 | 189 |
| Ring | AnchorMTM Exact | 1/40 | 32/40 | 143 |
| Ring | AnchorMTM Balanced | 1/40 | 32/40 | 143 |
| Wildfires | AnchorMTM Exact | 4/32 | 31/32 | 112 |
| Wildfires | AnchorMTM Balanced | 4/32 | 31/32 | 112 |
| Storms | AnchorMTM Exact | 11/744 | 740/744 | 2737 |
| Storms | AnchorMTM Balanced | 11/744 | 740/744 | 2737 |

TW覆盖率只写表注/独立统计，不再将1/40等内容附到数值上。低覆盖的TW不被描述为完整序列的稳定邻域性能。

## Balanced选择与实际拓扑

保持既定选择规则：前25%时间帧验证，正ε=1%–10%每1%采样；合法且实际NMLEmax≤各自ε才入选。在合法正候选间分别min–max归一化NPE、SNS，常数分量记0仅用于评分。J=.5NPE_norm+.5SNS_norm，J≤Jmin+.01视为接近，先选较小ε再选较低实际拓扑误差。Exact不参加正预算候选，没有最低NPE收益门槛，不回退0。冻结后两模式各重新跑一次完整流水线。

| Dataset | 选中ε | 验证J | 实际NMLEmax | 与Exact完全相同 |
|---|---:|---:|---:|---|
| Gaussian | 1% | 0.000000 | 0.000000% | True |
| Ring | 1% | 0.000000 | 0.981990% | False |
| Wildfires | 5% | 0.152912 | 4.421387% | False |
| Storms | 10% | 0.029772 | 9.985078% | False |

所有候选在balanced_selection.csv及results/*/selection保存。主表为全序列，包含验证段，后75%的NPE另存。历史结果已观察过，本轮不宣称全新盲测。

| Dataset/Mode | 实际NMLEmax | 连续违规/渲染违规 | 整数修复帧 |
|---|---:|---:|---:|
| Gaussian/AnchorMTM Exact | 0.000000% | 0/0 | 0 |
| Gaussian/AnchorMTM Balanced | 0.000000% | 0/0 | 0 |
| Ring/AnchorMTM Exact | 0.000000% | 0/0 | 26 |
| Ring/AnchorMTM Balanced | 0.981990% | 0/0 | 21 |
| Wildfires/AnchorMTM Exact | 0.000000% | 0/0 | 0 |
| Wildfires/AnchorMTM Balanced | 4.421387% | 0/0 | 0 |
| Storms/AnchorMTM Exact | 0.000000% | 0/0 | 0 |
| Storms/AnchorMTM Balanced | 9.985078% | 0/0 | 0 |

八组均通过固定完整叶标签合并矩阵（含对角线）、极值值/个数、锚点唯一性、画布及区间约束、整数重建与剖面极小值个数检查。Exact实际标签误差0；该证书不扩大为所有增强有限根高扩展的完整保留证明。

## 与旧百分数解释的区别及结论

旧目录使用p=(0.001%,0.001%,0.15%,0.105%)；本轮p阈值为旧值100倍。预算由新验证重新选择，因此新旧差异不是单独p的受控消融，也不混用历史布局/基线NPE。旧Storms TD≈29.3365来自10.5%比例、ε=5%的历史配置；本轮独立结果以新选定ε为准，不直接复制旧值。

| Dataset | Exact→Balanced NPE | SNS | TD | TW |
|---|---:|---:|---:|---:|
| Gaussian | 0.0089 → 0.0089 | 0.0353 → 0.0353 | 0.3834 → 0.3834 | 0.9323 → 0.9323 |
| Ring | 0.0471 → 0.0395 | 0.1485 → 0.1334 | 3.9641 → 3.9231 | 0.8571 → 0.8571 |
| Wildfires | 0.0131 → 0.0116 | 0.0426 → 0.0447 | 2.9429 → 2.8816 | 0.9136 → 0.8989 |
| Storms | 0.0399 → 0.0140 | 0.0790 → 0.0743 | 42.3775 → 27.2889 | 0.8463 → 0.8766 |

这里如实保留所有不利变化；更小的累计TD仅表示显示位移更少，不能单独证明物理运动更准确。Gaussian或其他数据集若正预算未使用、输出相同，仍保留正ε行而不制造差异。

## 运行与复现

硬件Apple M4；BLAS、TTK单线程，逐帧提树，HiGHS保留默认调度。每模式完整实测1次。t_opt含顺序搜索及连续锚点优化；t_total重新生成/读取源场、预处理、TTK提树I/O、匹配参考、优化、整数重建及内置检查；不使用验证树替代正式计时阶段。OS页缓存可能已热，程序导入、指标导出及报告不计入；不据单次测量声称显著加速。

正式文件：comparison_final.csv、anchor_metrics_measured.csv、anchor_parameters.csv、anchor_runtime.csv、baseline_npe.csv、topology_validation.csv、p_threshold_validation.csv、ranking_audit.csv、balanced_selection.csv、input_audit.csv。源代码和冻结配置见source/与config/，完整原始输出见results/。两个LaTeX表：quantitative_comparison.tex和anchor_parameter_settings.tex；没有表3。
