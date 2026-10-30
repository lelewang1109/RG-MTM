> 2026-10-30 工作更新：见 [最新论文、PPT、总览图与实验索引](docs/WORK_UPDATE_20261030.md)。

> 2026-10-30 最新图更新：二维逐小时 Storms 为首图，三维 Vortex 为图 11；正文 9+2 页、附录 10 页。见 [当前正文](paper/pvis2027/main.pdf)。

> 2026-10-30：当前 PacificVis 稿已补 N4 可控冲突实验（正文 §7.3 / 图 9，附录 §S3 / 图 S1）；正文 11 页、附录 7 页。见 [实验协议](code/experiments/controlled_conflict/README.md) 与 [正文](paper/pvis2027/main.pdf)。

# RG-MTM：统一位置—拓扑框架

> **2026-10-29 已还原：** 按用户提供的 PDF 恢复为 2026-10-27 的 *Position-Faithful Merge Tree Maps: Certified Bounds and Optimal Layouts*。见 [原版正文](paper/pvis2027/main.pdf)、[配套附录](paper/pvis2027/supplement.pdf)、[编辑入口](paper/pvis2027/README.md) 和 [还原记录](paper/pvis2027/RESTORE_20261029.md)。正文 PDF 与用户附件字节一致；原版投稿编号为 0。近期框架改写已备份。

Reference-Guided Merge Tree Maps — A Unified Position–Topology Framework

**下载：** [研究材料ZIP（数据、论文、实验代码和结果）](https://github.com/lelewang1109/RG-MTM/archive/refs/heads/main.zip)。上述四类材料完整保留在默认下载中；仅省略重复PPT合集、PDF别名和历史编辑材料。分发范围及获取方式见 [下载说明](docs/DOWNLOADS.md)。

RG-MTM 将时变标量场压缩成“时间 × 一维位置”的地图，在同一组区间变量、四项布局目标、QP求解和标量绘制中，研究层次连接、相对几何、时间连续性与固定空间参考之间的折中。原生TMTM/ST-MTM是独立比较方法；本模型中的inspired区域表达其设计原则，不宣称算法等价。

## 历史长稿与研究材料入口

| 你的目的 | 直接入口 |
|---|---|
| 阅读 2026-10-26 长稿 | [正文PDF](paper/manuscript/Revised_RG-MTM.pdf) · [附录PDF](paper/manuscript/Revised_Supplement.pdf) |
| 理解整个文件夹 | [目录导读与阅读路线](docs/DIRECTORY_GUIDE.md) |
| 修改历史长稿文字或图片 | [修改流程](docs/EDITING_AND_REPRODUCING.md) · [LaTeX入口](paper/manuscript/latex/main.tex) |
| 理解方法、贡献与边界 | [统一体系说明](docs/统一体系贡献说明_20261025.md) · [方法代码](code/src/rgmtm/) |
| 查看当前九数据评价表 | [指标CSV](code/results/stmtm_completion20261026/unified_metrics.csv) · [补全报告](code/results/stmtm_completion20261026/REPORT_zh.md) |
| 查看统一模型实验 | [实验协议](code/experiments/unified/README.md) · [保存结果](code/results/unified20261025/) |
| 准备数据或重跑 | [数据说明](data/README.md) · [分级复现流程](docs/EDITING_AND_REPRODUCING.md) |
| 下载独立LaTeX整包 | [2026-10-26 Release](https://github.com/lelewang1109/RG-MTM/releases/tag/research-2026-10-26-final) |

## 历史长稿版本：2026-10-26

- 正文 **26页**、附录 **52页**，正文保留17张图。当前PDF与 `paper/manuscript/latex/` 是继续修改的基线。
- **图1已更新**：完整744小时Storms定位图 → 选中窗口的五张地理快照 → P/R1/R2/R5局部对照。只标注已展示时刻；字母表示计算极值轨迹。编辑源为 [SVG](paper/figures_export/Fig1.svg) 和 [Python](paper/previews/storms_anatol_20261026/render_teaser.py)，既有PPT图1页是历史版。
- **表3已补全**：Nucleon、Benzene、Tangaroa、Cylinder新增325个ST-MTM布局；九输入、四方法完整指标汇总在同一张表中，二维在前、三维在后。
- **统一模型实验**：614帧×5设置，共3,070个主布局、15,141个固定顺序QP和360个Ring双预算查询。496帧覆盖全部顺序，其余118帧使用记录的候选池。
- **独立前沿实验**：`framework20261025` 的603/11穷举/候选覆盖属于另一项实验，不能替代上述共同模型实验的覆盖结论。

## 文件夹结构

```text
RG-MTM/
├── README.md                  # 总入口、当前版本、阅读路线
├── code/
│   ├── src/rgmtm/             # 方法实现、求解器、基线
│   ├── experiments/           # 实验协议、运行与导出入口
│   ├── analysis/              # 证书、指标、处理和作图共用模块
│   ├── results/               # 数值结果、完整剖面、验证记录
│   ├── tests/                 # 数值和输入协议测试
│   └── provenance/            # 冻结哈希与历史源码身份
├── paper/
│   ├── manuscript/            # 当前正文、附录和模块化LaTeX
│   ├── figures_export/        # 当前PDF/PNG/SVG图件
│   ├── previews/              # Storms首图源代码与比较候选
│   ├── evidence/             # 图件证据与显示核验
│   ├── figures_ppt/           # 既有PPT；新版图源另见索引
│   └── FIGURE_INDEX.json      # 正文图号、稳定文件名与图源对应
├── data/                      # 数据协议、小型输入与外部大文件入口
├── docs/                      # 目录导读、修改流程、贡献和证据边界
└── references/                # 参考文献索引；引用以refs.bib为准
```

`code/` 是实现与科学证据，`paper/` 是论文交付物；旧运行记录不会因为论文更新而改写为新实验。正文图号与 `FigN` 文件名不总相同，请查询 [图件索引](paper/FIGURE_INDEX.json)。

## 安装与轻量核验

以下命令从本仓库根目录运行，适用于类Unix shell；已有环境可替换解释器路径。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e './code[volume3d]' pymupdf==1.28.2
.venv/bin/python -m pip install -r code/experiments/stmtm_completion/requirements.txt
PYTHONPATH=code/src .venv/bin/python -m unittest discover -s code/tests -v
.venv/bin/python paper/scripts/verify_unified_revision.py --numerical-only
```

提供 `python tools/verify_release.py` 检查Git检出或研究材料ZIP中的文件哈希和符号链接。两种方式都包含已发布数据和完整保存结果，可按上述命令进行实验检查；外部原始大数据仍需依协议准备。四组补全实验的完整数组核验入口见 [ST-MTM补全协议](code/experiments/stmtm_completion/README.md)。

论文编译入口是 `paper/manuscript/latex/main.tex` 和 `supplement.tex`。已有PDF和所有编译图件随仓库提供，阅读不需要安装LaTeX。修改与重新编译见 [修改流程](docs/EDITING_AND_REPRODUCING.md)。

## 数据、分发与解释边界

原始体数据、下载档案和本地编译缓存不随Git全量发布。获取方法、已有库存与缺失文件见 [数据说明](data/README.md) 和各实验协议；读取结果、重新作图、从原始数据重跑是不同层级。

独立LaTeX ZIP通过 [当前Release](https://github.com/lelewang1109/RG-MTM/releases/tag/research-2026-10-26-final) 分发；上方研究材料ZIP同时保留数据、论文、实验代码和结果，其中的LaTeX文件夹可直接编辑和编译。

五个二维时序的614帧、744小时Storms首图、64帧独立控制、三维体和静态截面是不同总体。首图资格参数κ不是真实合并误差硬上限；共同模型中的拓扑预算ε、位置预算B有各自定义。详见 [目录导读](docs/DIRECTORY_GUIDE.md) 和 [研究证据边界](docs/研究证据边界与补充研究.md)。
