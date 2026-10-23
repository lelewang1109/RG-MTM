# 数据配色与显示规则

本轮以原数据发布材料及现有本地色表为核对对象，不把数据集参考论文的配色当作发布色表。未核实到发布色表的输入，保留现有标量配色并注明其来源状态，不宣称“精确还原官方配色”。

| 数据 | 当前处理 | 来源状态与边界 |
|---|---|---|
| Storms | 保留蓝—白—红压力距平；图1不改 | 气压距平的现有语义配色，不能说是 ERA5 原始 NetCDF 内置色表 |
| Wildfires | 保留黄—橙—棕的 log-FRP | 现有火强度配色；灰蓝单列人工负连接，不表示负观测 |
| OLR | 保留现有蓝—白—红标量色标 | 未核实本次 v1.2 原数据固定 LUT；不把 v2 发布说明当作 v1.2 色表 |
| PM2.5 | 绿—黄—橙—红—紫，全年及四方法共用浓度色标 | 用户授权沿用污染配色；连续浓度 μg/m³，不是 AQI 分类或法定等级 |
| Ring | 保留现有强度色标 | 合成发生器；未核实到独立发布 LUT |
| Tangaroa | 保留现有速度模长紫—白—橙 | 原数据为速度向量，现有工作区传递函数不冒称发布页官方 LUT |
| Cylinder | 保留以零为中心的蓝—灰—红 Q 色标及对称对数规范 | 发布输入为速度；Q 在本工程计算，不能直接把速度配色称作 Q 发布配色 |
| Nucleon | 保留现有原切片显示与相同标量范围 | 原 scalar 切片未附已核实的固定 LUT，未以参考论文代替发布材料 |
| Benzene | 保留以零为中心的势场色标 | 本工程重建的点电荷势场，没有可声称完全匹配的发布势场 LUT |

数据入口核对材料包括本地数据清单，以及 [Tangaroa 发布页](https://cgl.ethz.ch/research/visualization/data.php)、[Cylinder 发布页](https://tinoweinkauf.net/notes/squarecylinder.html)、[NOAA OLR v1.2 元数据](https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc%3AC00875/html)。PM2.5 的 V2 DOI 身份沿用用户标识，未将无法在线核实的元数据写成已独立认证。

## 减少矩形拼贴感

- PM2.5 从一月30场替换为完整2000年366场，区域仍为102–114°E、28–38°N，49×49网格、100 km平滑。方向、追踪和标量范围按全年重新计算，未按表现筛选日期。
- OLR、PM2.5、Ring 的正文图12和附录四方法图使用保守的锚点对齐分段线性显示插值。共同极值顺序改变、位移超过0.2L或边界结点不能严格排序时，退回固定位置线性插值。
- 所有原始帧列逐元素保持不变，插值不产生标量过冲。中间列只供显示，不增加观测、布局求解帧、追踪事件或评价样本。
- 指标始终从保存的完整科学数组和锚点计算。1–7个叶子的宽色带来自提取与填充，不能靠伪造细节掩盖。图12配色和尺度在每组方法之间一致。

复现入口：`scripts/complete_dataset_figures_prepare.py`、`scripts/anchor_aligned_renderer.py`；全年实验入口在 `../code/tools/run_pm25_annual.py`、`export_pm25_annual.py`、`annual_reference_tasks.py`。插值核验记录存入 `evidence/complete20261023/display/`。
