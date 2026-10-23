# 新增数据集正式结果

| 输入 | 当前论文角色 | 边界 |
|---|---|---|
| [Nucleon](nucleon/REPORT.md) | 正文图8、二维结果表与S9/S10 | 单帧二维切片，无运动结论 |
| [Benzene二维电势重建](benzene-potential-reconstructed2d/REPORT.md) | 正文图9、二维结果表与S9/S10 | 21个静态z截面；OPLS-AA重建，非原作者文件，z不是物理时间 |
| [三维方柱Cylinder](square-cylinder3d/REPORT.md) | 正文图11、三维表与S9/S10 | 102帧原公开三分量速度导出的Q，135×64×48；不宣称原论文508帧输入的精确复现 |

实验代码与参数见 [experiments/paper1_suite](../../experiments/paper1_suite/README.md)。Storms、Ring和Tangaroa已有独立结果；各总体不合并为新的342帧统计。

旧 `benzene-density/`、`cylinder2d/` 以及 `benzene-potential3d/` 搜寻记录已移至 `../../../../其他/归档/历史或排除结果/paper1_suite/`，不得作为当前电势或三维方柱证据。
