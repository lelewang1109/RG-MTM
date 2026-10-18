# 三维空间时序扩展实验

独立补充实验，参考 Köpp 与 Weinkauf 的 TMTM（VIS 2022，DOI 10.1109/TVCG.2022.3209387）。
不修改六序列／342 帧主表及其原始结果。输入必须是 `T×Z×Y×X`；沿静态体数据
切片构造二维序列不能作为三维空间时序支持的证据。

先阅读[实验设计与证据总览](EXPERIMENTS.md)：按验证目的区分合成机制实验、官方原网格正式实验与历史粗网格试跑。
所有指标含义、方法范围、实测结果和未完成项目在该文集中说明。

## 原网格 Tangaroa：完整 201 帧实验入口

**完整 201 帧已完成并通过独立核验。** [完整报告](../../results/volume3d/tangaroa-paper-p10-full201/REPORT.md)及
[论文风格组合图](../../results/volume3d/tangaroa-paper-p10-full201/paper_style/README.md) 已保存。
本组实验独立保存于 `results/volume3d/tangaroa-paper-p10-full201/`。运行状态见该目录
`status.json`；只有 `complete_verified` 才表示全部 201 帧已经计算、独立核验并生成报告。
此入口使用全部原始 `300×180×120` 体，**不进行空间降采样、高斯平滑或叶数筛选**。
按作者公开主工作空间采用近零替换、[0,2] 截断、绝对持久性阈值 0.2（10%）和 join tree。
主对照采用作者第 100 帧焦点、双向传播的 TMTM，不加入第二篇未验证的三维基线。

```sh
python -m pip install -e '.[volume3d]'
# 安装已固定的官方 ZIP 成员目录；只复制元数据，不下载速度体。
PYTHONPATH=src:. python -m experiments.volume3d.setup_inputs
PYTHONPATH=src:. python -m experiments.volume3d.build_native_ttk
PYTHONPATH=src:. python -m experiments.volume3d.prepare_tangaroa_paper --workers 6
PYTHONPATH=src:. python -m experiments.volume3d.paper_trees --threads 6
PYTHONPATH=src:. python -m experiments.volume3d.run_paper
PYTHONPATH=src:. python -m experiments.volume3d.verify_paper
PYTHONPATH=src:. python -m experiments.volume3d.export_input_evidence
PYTHONPATH=src:. python -m experiments.volume3d.report_paper
PYTHONPATH=src:. python -m experiments.volume3d.paper_style
```

构建需要 Python 3.10.12+、CMake、Ninja、C++ 和 OpenMP；macOS 构建从现有 Homebrew libomp 查找路径。
Linux 可使用发行版的 CMake、Ninja 与支持 OpenMP 的 C++ 编译器。
全序列原始速度体约 15.6 GB，另需保存 TTK 输出与完整地图，运行前应预留充足磁盘空间。
`setup_inputs` 在全新克隆中创建普通 `data/real/` 目录，本地已有共享数据链接时继续使用该链接；不同版本的现存清单不会被覆盖。
下载遵循普通 `HTTPS_PROXY`／`HTTP_PROXY` 环境变量，需要代理时使用用户已经配置的代理地址；
脚本不修改系统网络设置。TTK 固定为 0.9.9 源码包并验证 SHA256，不安装到系统目录。
原始包按独立 Amira 成员的 8 MiB 范围续传，每个成员先验证长度和 ZIP CRC32，再计算标量缓存。
所有大数组保存在 Git 排除的 `data/real/Tangaroa-FAU/paper_full_201/`。

这是同一官方源数据和公开输入语义上的完整方法实验，不能保证与作者未公开的最终标量导出或
原编译环境逐字节相同。实际 TTK 字段被所有方法共享。派生节点范围 36–186 与论文的 50–186 尚有差异，不能称为作者最终树的精确复现。
论文风格绘图模块仅改变显示，四个 RG 面板统一使用持久性 10%，不冒充原图四档持久性比较。
相机元数据随代码提供，绘图不依赖本地作者仓库或临时 XML。中文字体自动查找 Songti／Noto CJK／SimSun；
没有中文字体时自动输出英文，也可用 `--language en`，或设置 `RGMTM_CJK_FONT` 后使用 `--language zh`。
实现对大树有以下明确约定：

- 不再枚举全部合法叶序。连续 Pareto DP 给出主位置证书；高元节点采用工作量下界或限时 MILP，
  保存上下界，不把未收敛结果当作精确最优。
- 次级凸目标在最多 4 个声明的合法候选顺序上求解，保存一阶差距；不声称跨全部叶序的次级全局最优。
- RG-MTM-R 关闭可选的放松后剪枝，保留满足资格阈值的所有放松。资格阈值不代表最终 NMLE 上界。
- 多重鞍点需要一维图中的同值分隔副本；TMTM 输出明确记录这些副本，并保存每个样本 ID。
  它不改动原三维标量输入；独立核验检查每个源样本出现一次及全部额外副本。
- 表格指标由完整保存数组计算，4096 行预览仅用于显示。三维与投影运动分别评价，匹配是计算代理。

### 只核验 GitHub 中保存的证据

```sh
PYTHONPATH=src:. python -m experiments.volume3d.verify_saved
```

它检查源码／数值记录／核验报告／生成图片的绑定关系，**不重新下载数据，也不重新证明原始输入或完整数组的正确性**。
完整数据与地图在本机齐备时，继续使用上文 `verify_paper` 进行独立逐值和布局核验。
`export_input_evidence` 只把已核验运行的准备协议、构建身份及逐帧树清单复制到结果目录，
使 GitHub 用户可以核对原始来源及源码绑定；它不会复制原始体、完整地图或本地可执行文件。

## 2026-10-18：按作者工作空间纠正 Tangaroa 输入

复核论文图 15 和作者固定提交 `2c75a10ed2cd55177a25ff751e0c0a8261200717` 后确认：
官方原始速度数据来源吻合，但下文旧 12 帧试跑的处理协议不等同于论文输入，不能作为论文同输入比较。
作者 Tangaroa 主处理链为：速度模长 → abs(v)<1e-6 的值改为 1 → 截断至 [0,2] →
TTK 持久性标量场简化 → **join tree**。该链没有旧试跑的高斯平滑和空间降采样。
公开主工作空间保存的绝对简化阈值为 0.2；图 15 的 0.15%、0.5%、2%、10% 是持久性阈值，
与 RG 层次放松参数不同。具体依据和未完成范围见[核对报告](../../results/volume3d/tangaroa-input-audit-20261018/REPORT.md)。

图中编号 0、100、200 分别对应原文件 `tangaroa-0.00.am`、`tangaroa-1.00.am`、`tangaroa-2.00.am`。
原分辨率核对命令（需要官方原始三个成员和作者 Git 仓库）：

```sh
# 本节为可选的原始审计重跑；正式原网格入口不需要克隆作者仓库。
git clone --no-checkout https://github.com/Wiebke/TemporalMergeTreeMaps.git tmp/volume3d/TMTM-reference
PYTHONPATH=src:. python -m experiments.volume3d.fetch_tangaroa_snapshots
PYTHONPATH=src:. python -m experiments.volume3d.audit_tangaroa
PYTHONPATH=src:. python -m experiments.volume3d.verify_tangaroa_audit
```

默认作者仓库位于 `tmp/volume3d/TMTM-reference`，可用 `--author-repo` 指定。
该入口核对源成员长度、CRC32、SHA256、坐标、轴序，输出未平滑、未降采样的预处理标量缓存与
参考体渲染；**没有执行 TTK，也没有生成完整 201 帧 RG-MTM 地图**。作者最终 Magnitude 导出文件
和校验和未公开，不声称逐字节相同。CPU 渲染沿用作者相机与传递函数，省略未取得的船体 STL 和
原 Blinn–Phong 光照。下文 `run.py` 仍保留旧 split-tree 试跑协议，以确保旧结果可追溯。

## 合成验证与历史小树入口

从 RG-MTM 仓库根目录执行。工作区可用 `../.venv/bin/python` 替换 `python`。

```sh
python -m pip install -e '.[volume3d]'
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python experiments/volume3d/run.py --dataset synthetic --include-stmtm
PYTHONPATH=src python experiments/volume3d/run.py --dataset synthetic-conflict --include-stmtm
PYTHONPATH=src python -m experiments.volume3d.prepare_tangaroa_official
PYTHONPATH=src python experiments/volume3d/run.py --dataset tangaroa --input data/real/Tangaroa-FAU/prepared_speed_12.npz --out results/volume3d/tangaroa-official
PYTHONPATH=src python -m experiments.volume3d.prepare_tangaroa
PYTHONPATH=src python experiments/volume3d/run.py --dataset tangaroa --input data/real/Tangaroa-ECNR/prepared_vtm_36.npz
PYTHONPATH=src python experiments/volume3d/prepare.py
PYTHONPATH=src python experiments/volume3d/run.py --dataset cylinder
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/synthetic
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/synthetic-conflict
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/cylinder
PYTHONPATH=src python -m experiments.volume3d.verify_tangaroa_input results/volume3d/tangaroa-official
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/tangaroa-official
```

`prepare.py` 下载并解压约 519 MB 的 7z 文件；原始数据、缓存 Q 输入及源协议存放于
被 Git 排除的 `data/real/SquareCylinder/`（本地链接到共享 `00-data/real/`）。
所有步骤都不会执行下载内容。`run.py` 无网络操作；缺少真实数据时明确失败。
下载完成前检查 7z 长度与头部 CRC；服务器忽略 Range 时另写重试文件，保留既有
不完整包。Cylinder 下载未完成，见 `results/volume3d/cylinder/status.json`。
Tangaroa 的 ECNR 公开 VTM 备份已完成 36 帧端到端计算和独立验证；它是同源数据扩展，
并非 TMTM 原始标量输入的精确复现。

## 数据版本与预处理

作者数据页：<https://www.csc.kth.se/~weinkauf/notes/squarecylinder.html>。
该公开版本是 `192×64×48×102` 的三分量速度场，空间范围
`[-12,20]×[-4,4]×[0,6]`。它与论文使用的 `135×64×48×508` Q 标量序列不同。
本实验是公开版本扩展，不能称为论文 Cylinder 案例的精确复现。

先在源网格的物理坐标中计算 `Q=-0.5 trace(J²)`，再对 Q 做三线性重采样；不能先
把速度转为模长，或在任意归一化坐标中直接求导。本次固定下游范围
`[-2,20]×[-4,4]×[0,6]`，重采样为 `28×14×10`。源导数使用中心差分和二阶单边边界
差分，未连接源 z 方向的周期边界，因此边界特征及其解释受到限制。

在计算布局前固定三组索引窗口 `[0,12)`、`[45,57)`、`[90,102)`，共 36 帧。这只是
early/middle/late 时间覆盖，不预先宣称它们正好对应启动／形成／充分发展的物理阶段。
跨窗不匹配特征、不产生运动事件，TMTM/ST-MTM 的时间优化也独立重置。

为完成当前枚举叶序的完整流程，平滑只按“全部帧的叶数不超过 6 且均为二叉树”选择
预先列出的首个 sigma。任何候选失败均保留完整帧计数；不会跳过不利帧。固定的
`1e-10×原标量范围` C-order ramp 只用来打破平值，所有方法共享处理后输入。
该处理不同于原论文的 TTK 持久性简化。平滑后的数据不能代表未经处理的全分辨率场。

所有阈值与规则见 `run.py` 的 `PROTOCOL`；每次运行开始先保存协议副本。
`synthetic` 的运动在三个空间坐标上均变化；`synthetic-conflict` 用一条连接两个固定峰的
三维脊与一个横穿其 x 投影区间的独立峰，检验参考顺序冲突及其放松代价。
旧 `run.py` 的持久性阈值诊断只做树上删叶，不生成经过 TTK 简化的标量场；
新增原网格入口已另行执行真正的 TTK 标量场简化，固定持久性为 10%。

## 方法和评价

- 主比较使用 TMTM：第一篇论文有三维时变体数据案例，当前项目复现与 RG 使用相同处理后标量场与树。
- ST-MTM 默认不加入三维主比较。第二篇论文未提供三维案例并不等于其树布局算法不能接收三维提取的树；
  但本项目对它的三维运行属于额外扩展验证，不能当作原文已验证的基线。若需要此诊断，显式传入
  `--include-stmtm`。既有两组合成实验保留此选项及原来的指标。
- RG-MTM-P、RG-MTM-R：以体积确定绝对区间宽度，以三维物理坐标确定固定参考轴。
  放松资格阈值为标量范围的 2%、20%、100%；不是实际合并层级误差的硬上界。
- Hilbert、Morton：三维固定 xyz 朝向；每个处理后样本出现一次，不接受最优重新填充。
  三维 Hilbert 使用 `hilbertcurve==2.0.5` 的 Skilling 实现；现有二维朝向保持原实现。
- Exact projection：只用作运动和顺序控制，没有标量图，NMLE 不定义。

报告 NROE（时间均值）、实际 RG 锚点偏移、测量得到的 NMLE（均值和最坏帧）、
填充闭式代价核对、完整树签名核对、清晰运动事件数与误差。完整三维距离真值和
一维投影真值分别计算，lag=1/2/4，判定阈值为域对角线／参考轴长度的 1%/2%/5%。
默认比较为 lag=2、2%；没有清晰事件时记录 null，不填 0。所有方法共享计算跟踪，
因此不把运动代理称为物理身份真值或读者实验。

这里的位置保证是 **directional positional fidelity（方向位置保真）**。本次与二维主实验保持
相同特征约定：参考点为叶特征的三维极值点 e_i，q_i=dot(e_i,d)，不是质心投影；三维质心同时
保存供检查。固定方向 d 是整段已匹配极值位移散布矩阵的最大特征向量，报告其捕获能量比例及
特征值间隙；它是离线参考，不是逐帧重新拟合或在线预测。原有一维宽度、合法叶序、位置证书
和拓扑代价计算不因输入维度改变而重写。小位置证书／NROE 不代表完整三维距离保持，甚至精确
q 投影也可能把三维接近误读为远离；必须单独报告完整三维运动代理。

## Tangaroa 公开备份

优先使用第一篇论文中的真实三维时变模拟。`prepare_tangaroa.py` 从 ECNR 作者的公开数据链接
读取 ZIP 中预先指定的源体数据；只下载所需成员，不下载其他数据集。每个成员验证 ZIP CRC32、
大小和 SHA256。源体数据为 little-endian float32、300×180×120、150 帧；冻结窗口是
文件编号 `[1,13)`、`[70,82)`、`[139,151)`，共 36 帧。跨窗口重置跟踪、运动事件和布局时间优化。
早／中／晚只是索引覆盖，不是物理阶段标注。

这是 **ECNR 的 VTM 通道**；第一篇 TMTM 使用 201 帧速度模长，两者并非相同标量输入。
公开文件出现负值，推断提供方作过归一化或偏移，但具体变换未文档化。因此不赋予标量物理单位，
也不称为第一篇案例的精确复现。这里只使用模拟源标量，没有使用 ECNR 模型的重建输出。
提供方元数据、读取代码及其固定提交和哈希均保存在原始数据目录。

轴序采用作者 `dataio.py` 的实际读取代码：先 reshape(Z,Y,X)，再转为其内部 XYZ；
本项目直接保留 ZYX。该代码与 README 的文字说明存在冲突，结果明确以代码约定为准。
坐标范围沿用 FAU 的 Tangaroa 规则网格范围 `[-.35,.65]×[-.3,.3]×[-.5,-.3]`；
ECNR 文件没有独立空间头，因此相同范围是一项已披露的假设，运动指标是此约定下的几何代理。

整个空间范围固定重采样为 XYZ=30×18×12，先按源／目标步长作高斯抗混叠，再三线性采样，
不逐帧归一化。随后使用统一平滑候选按全部帧树复杂度选择；所有方法共享最终标量场。
原始文件和缓存输入位于 Git 排除的 `data/real/Tangaroa-ECNR/`。

来源：[ECNR 作者仓库](https://github.com/TouKaienn/ECNR)，
[原始模拟说明及致谢](https://www.vc.tf.fau.de/publications/datasets/)。
原始模拟请引用 Popinet、Smith 与 Stevens，*Experimental and numerical study of the turbulence
characteristics of airflow around a research vessel*（2004）；公开备份请同时致谢 Tang 与 Wang 的 ECNR（PacificVis 2024）。

## 官方 Tangaroa 输入

第一优先入口是 FAU 的公开共享目录（上文官网中的 Tangaroa 下载链接）。`prepare_tangaroa_official.py`
通过 Synology 公共共享的正常匿名会话访问，不使用用户凭据。解析 ZIP64 目录后，只下载前 12 个
连续时间体：t=0.00、0.01、…、0.11。Amira 包共 201 个速度体，XYZ=300×180×120，
时刻 0.00–2.00，与第一篇论文所述数据维度一致。NetCDF 包只有一个大文件，因此选择同源逐帧
Amira 格式以避免完整下载十余 GB。原始变量未改变；下述旧处理与作者后处理不一致，见顶部更正。

每个源文件逐一核对 ZIP 成员长度、CRC32、SHA256。直接读取 Amira 文件头的空间范围与轴序，
在原网格计算 `speed=sqrt(u*u+v*v+w*w)`，再作与备份实验相同的全域抗混叠和三线性重采样
至 XYZ=30×18×12，之后按完整帧序列复杂度选择平滑。源文件和缓存存于
Git 排除的 `data/real/Tangaroa-FAU/`。

这只属于官方数据经旧粗网格 split-tree 协议处理后的试跑；未进行作者近零替换、截断和 join-tree
设置，不能用于论文同输入比较；不是完整 201 帧实验，也没有复现原文 TTK 简化设置。
不能把处理后小树的精确结果解释成完整 648 万体素复杂树的可扩展性证据。

`verify_tangaroa_input.py` 独立解析所有下载的官方二进制速度体，核对源 SHA256／CRC32，
重新计算速度模长，并用物理坐标 `RegularGridInterpolator` 复核预处理器的索引坐标插值。
结果保存在 `input_verification.json`；布局验证另由 `verify.py` 重建树和实际渲染障碍，不依赖布局器
自报的误差。该源输入复核需要原始 12 个体数据文件，已保存地图的数值复核只需结果目录。

结果入口为 `results/volume3d/<dataset>/REPORT.md`。所有数值使用未压缩分辨率；
地图图像最多抽样 4096 行，图像不能替代数组级拓扑验证。报告与四组图均由
`report.py` 从保存证据生成，可独立重建。

## 数据致谢

原始模拟：Simone Camarri、Maria-Vittoria Salvetti、Marcelo Buffoni、Angelo Iollo，
*Simulation of the three-dimensional flow around a square cylinder between parallel walls at
moderate Reynolds numbers*，2005。均匀重采样版本由 Tino Weinkauf 提供，曾用于 von Funck
等的 *Smoke Surfaces: An Interactive Flow Visualization Technique Inspired by Real-World Flow
Experiments*，IEEE TVCG 14(6)，1396–1403，2008。数据页允许在适当致谢下使用。

## 历史证据

三维扩展修改的共享文件通过 `provenance/volume3d_extension_20261017.json` 保存逐字节
可逆差异。旧实验验证恢复历史源文件快照后核对原哈希；这不表示使用新代码重新计算了
旧实验，也不修改旧结果或把历史哈希更新为当前哈希。新实验具有独立输入、源码、输出哈希。
