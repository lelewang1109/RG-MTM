# 当前投稿的结果与证据

最终论文图使用 [paper/FIGURE_INDEX.json](../../paper/FIGURE_INDEX.json) 所列母版。这里保存原始结果和实验可复现记录。

| 入口 | 角色 |
|---|---|
| [submission20261023](submission20261023/README.md) | 当前投稿：九输入统一比较；五个小树时序278帧精确前沿，七个时序581帧，22静态切片 |
| [publication2027](publication2027/README.md) | 历史六序列342帧冻结证据；64帧镜像控制仍在当前投稿使用。原始manifest保持历史成员与哈希 |
| `final_performance.json`、`eval_projection.json`、`native_merge_errors.json`、`replicate_*.json`、`attainable_*.json` | 原始逐帧结果与表格来源；当前主套件成员以 `analysis/dataset_suite.py` 和打包清单为准 |
| `real_case_studies/` | Storms/Wildfires/Tangaroa源场及特征对应证据 |
| [paper1_suite](paper1_suite/README.md) | 当前Nucleon、二维重建Benzene、三维Cylinder |
| [volume3d](volume3d/README.md) | Tangaroa完整201帧、原分辨率输入核对与两组三维合成补充 |
| `public_metrics_20261016/` | 标准指标与参考任务复核；保留和原指标的口径区别 |
| `baseline_audit_20261019/` | TMTM/ST-MTM设置及原生实现核对 |
| `figures/`、`visualizations/` | 由证据生成的研究图与诊断图；与最终论文PPT不是两个可互换的当前稿 |
| `manuscript_tables/`、`revised_suite/` | 数值聚合表、分阶段完成记录和季节控制 |
| `archive/pm25_janfeb/`、`legacy_publication/` | **必要溯源例外**：旧选择审计和旧图源，冻结manifest及哈希检查仍依赖；不得作为当前稿或新增结论 |

旧 `paper_stats.json`、`quality.json` 等历史数值仅因原始溯源链需要而保留，禁止覆盖当前数值口径。已排除的Benzene电子密度、二维圆柱、旧Tangaroa试跑与缓存已移至“其他”。

本次整理不重算科学实验。当前各总体（278帧小树穷举、64帧控制、201/102体帧、静态切片）保持独立；342帧仅表示历史冻结套件，详见 [研究证据边界](../../docs/研究证据边界与补充研究.md)。
