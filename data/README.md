> GitHub发布范围：本目录展示完整输入结构，仓库只携带选定小型输入、协议、坐标和清单。大原始体与完整下载档案需依协议准备。实际携带状态见 [数据库存](../docs/github/DATA_INVENTORY.csv)。

# 本次投稿数据

| 目录 | 用途 |
|---|---|
| `real/ERA5_MSLP/` | 118帧主风暴、744小时可视化及历史2013/14独立控制输入 |
| `real/wildfire/` | Wildfires 输入 |
| `real/CN-Reanalysis/` | 完整2000年366场主PM2.5与历史季节控制来源 |
| `RG-MTM-public-scalar/` | OLR、PM2.5等已保存的处理输入和来源协议 |
| `real/Tangaroa-FAU/` | 官方速度体、原网格201帧派生输入、树与完整地图 |
| `real/SquareCylinder/` | 完整公开三分量速度档案及解包输入 |
| `real/paper1_suite/nucleon/` | 单个二维切片输入与输出 |
| `real/paper1_suite/benzene-potential-reconstructed2d/` | 21个静态二维重建电势截面 |
| `real/paper1_suite/square-cylinder3d/` | 102帧三维Q、树与510张方法地图 |

`../code/data/real`、`../code/data/public_scalar` 是相对链接，不复制数据。RA-MTM 的共享输入链接也指向这里。Ring/Gaussian 主实验可由代码生成，旧独立生成数据移至 `../../其他/其他研究数据/generated/`。

已退出投稿的 OISST、旧PM2.5时间窗、电子密度Benzene、二维圆柱、ECNR备份试跑和3帧smoke输出已移至“其他”。完整原始档案与派生输入分层保留，不能仅因同属一个数据集就视为重复。原始数据仅搬迁保留；本轮新增完整2000年处理输入与结果，不覆盖旧一月输入。

数据集来源、处理参数与科学适用范围见 [研究证据边界](../docs/研究证据边界与补充研究.md) 和各实验协议。大体数据与完整地图不进入 LaTeX 投稿包。
