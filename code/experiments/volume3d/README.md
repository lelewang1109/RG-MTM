# 三维空间时序实验（当前入口）

正式三维结果是 Tangaroa 原网格201帧与 [Cylinder 三维方柱102帧](../paper1_suite/README.md)。二者均已完成并独立核验。Nucleon与Benzene为二维静态输入，不计入三维总体；所有三维研究均与六序列342帧统计分开。

[结果与边界](../../results/volume3d/README.md) · [输入核对](../../results/volume3d/tangaroa-input-audit-20261018/REPORT.md) · [全项目证据说明](../../../docs/研究证据边界与补充研究.md)。

命令在本代码目录执行，工作区使用 `../../.venv/bin/python` 代替 `python`。已有的固定TTK二进制与源码存于 `tmp/volume3d/`；旧CMake缓存含迁移前绝对路径，已归档，需要重建时重新运行构建入口。

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

## 两组三维合成补充

```sh
PYTHONPATH=src python experiments/volume3d/run.py --dataset synthetic --include-stmtm
PYTHONPATH=src python experiments/volume3d/run.py --dataset synthetic-conflict --include-stmtm
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/synthetic
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/synthetic-conflict
```

每组24帧，用于三维运动/投影区别和层次冲突机制，可补充附录。这里的ST-MTM是项目的三维扩展诊断，不代表原工作已经验证三维案例。

## 旧试跑与协议更正

旧官方12帧、ECNR36帧和粗网格Cylinder的结果及输入均已归档，不作为当前正文或三维收益证据。早期 `prepare_tangaroa_official.py`、`prepare_tangaroa.py`、`prepare.py` 仍可能被旧机制模块导入，保留代码依赖；正式真实数据入口仅使用上面的完整Tangaroa管线和 `paper1_suite/prepare_3d.py`。

历史运行指令见工作区“其他/归档/整理前说明/RG-MTM/code/experiments/volume3d/README.md”。不要按旧入口重新生成结果覆盖正式运行。
