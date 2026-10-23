# Figure 1：真实逐小时序列与两种固定方向

按2026-10-22用户要求保留两张方向比较图，并已选用数据方向版本更新正式图1及九页母版第1页。固定x方向版本继续单独保留。比较版本输出：

- `figures_ppt/Fig1_XAxis.pptx`、`figures_export/Fig1_XAxis.png/.pdf`。
- `figures_ppt/Fig1_DataDirection.pptx`、`figures_export/Fig1_DataDirection.png/.pdf`。

## 实验

原始数据：`02-RG-MTM/data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc`。时间为1999-12-01 00:00至1999-12-31 23:00，共744个真实小时，没有从118帧补造观测。前后真实数据用于192小时居中滑动平均，当前小时减去该平均得到海平面气压异常（hPa）。所有图采用同一RdBu_r色图及−35至35 hPa色标。

固定向东版本：d=(1,0)。数据方向版本：d=(0.94783175,−0.31877104)，相对投影x轴约−18.5886°。后者用既有RG-MTM方向估计逻辑计算，并以独立einsum协方差/特征向量重算核验；每幅地图中的d轴经过相应计算极值的真实投影位置。

使用RG-MTM既有49×49等积分析网格、250km高斯空间平滑、内域极值保留及优先洪泛处理、既有R20布局与最优标量屏障填充。**时间范围、小时采样与两篇论文相同，但空间网格和平滑协议仍是RG-MTM设置，不能声称完整复现两篇论文的预处理。** 空间快照直接从原0.25°小时观测减去对应192小时平均绘制，保留正确等积地理比例。

两个方向各自重新运行布局、追踪和填充，不旋转或拉伸已有118帧结果。保存744列是科学计算输出；帧间仅使用保锚点显示插值，每小时完整4096行标量列完全不变，无额外深色轨迹、无标量对比增强、无虚构低值连接。

## 事件标注

沿用TMTM图1报道的五个事件名称、时间，以及圆角白色注释框、箭头、细竖虚线和快照连线：

| 时刻 | 本次小时帧 | 论文事件 |
|---|---:|---|
| 1999-12-03 18:00 | 66 | Anatol |
| 1999-12-17 21:00 | 405 | Strong storm over Scandinavia |
| 1999-12-24 23:00 | 575 | Strong storm over the British Isles and Norway |
| 1999-12-26 10:00 | 610 | Lothar |
| 1999-12-27 21:00 | 645 | Martin |

事件名称与时间是文献标签；箭头目标是该时刻距报道事件区域最近的计算极值，身份、坐标、气压、锚点全部记录在每个实验的`event_annotations.json`。这不是用人工真值验证的新物理气旋追踪，不能把计算track ID直接宣称为独立气象身份验证。

参考来源：
- TMTM：Wiebke Köpp、Tino Weinkauf，https://www.csc.kth.se/~weinkauf/publications/abskoepp22.html 。其图1及数据说明给出12月逐小时异常场及五个时刻。
- ST-MTM：Mauro Diaz、Juanpablo Heredia、Nivan Ferreira、Jorge Poco，https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6604235 。两篇作者不同。

## 编辑与复现

PPT标题、坐标、事件注释、虚线、连接线和d轴均为原生对象；标量场与地图为独立高分辨率数据图层。PDF保留原生文字与路径。已检查PPT结构及LibreOffice渲染，未使用Microsoft PowerPoint实机验证。

复用已保存实验结果重建两图：

`.venv/bin/python paper_revision/scripts/regenerate_fig1_direction_comparison.py`

重新计算同一新实验并生成两图：

`.venv/bin/python paper_revision/scripts/regenerate_fig1_direction_comparison.py --recompute`

数值记录：`evidence/fig1/december1999_xaxis/`与`december1999_data_direction/`。`verification.json`给出最优填充后直接逐对核验的实测合并误差；`results_before_optimal_scalar_fill`仅为既有运行器返回的填充前统计。此次数据不混入原342帧主实验，不改变论文旧指标或核心算法。

## 已选版本右侧局部面板

正式图1与DataDirection版本保留完整744小时、五个事件和快照，并在右侧增加12月26日10:00（f610）的三个极值及00:00–23:00（f600–623）局部时间图。A=130、B=113、C=133。C仅存在f605–610，绘制时严格保留起止。全部曲线、圆形、文字、日期、引导线及浅灰箭头为PPT原生对象。标量背景为完整时间图像的精确裁切。`local_panel.json`保存坐标、逐小时锚点、参考、track IDs及范围核验；`prepare_fig1_local_panel.py`完成可复现布局。未重跑布局、优化或实验。

最新布局使用12月26日全天24个真实小时（00:00–23:00UTC）。主图橙色虚线框严格由右下图同一标量像素裁切范围反算，右下图使用同色边框。右上地图缩小，右下绘图区增高；缺失时段不外推。

完整一天展示修正：右下图使用1999-12-26全部24个原始小时剖面及完整4096行（归一化输出位置0–1），主图整高红色虚线框仅选择时间。普通事件标记为黑色虚线，选中时刻为红色虚线。C轨迹实际保存区间为05:00–10:00 UTC，图注与正文据此校正。
