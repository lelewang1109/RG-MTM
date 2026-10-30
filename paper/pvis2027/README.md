> 当前更新：首图为支撑区域改进版 Storms，正文图 11 为五组数据集六参数总览；远端 Near-Optimal 标题、定理取值范围与 ERA5 文献修正已保留。正文 9+2 页、附录 10 页。

> 2026-10-30 当前版本：图 1 为改进版 Storms 支撑区域与参考位置图（`fig_storms_support.pdf`）；图 11 为五组数据集六档预算总览（`fig_dataset_overview_extended.pdf`）。正文 9 页 + 2 页参考文献，附录 10 页。当前可编辑首图为 `../figures_editable/20261030/Storms_feature_support_improved.pptx`，最新源码包为 [Current_20261030.zip](export/RG-MTM_PacificVis2027_Current_20261030.zip)。下文早期版本说明保留为历史记录。

> 历史更新（首次 PPT 图替换）：图 1 已替换为 `Storms_teaser_hybrid_editable.pptx` 对应的最终二维图；图 11 为 `Vortex_teaser_editable_final.pptx` 对应三维图。正文仍为 9 页正文 + 2 页参考文献，附录 10 页（含已有局部预算响应实验与移入的旧 Storms 图）。图源、参数及哈希见 `figures/data/latest_ppt_20261030/`。新源码包为 `export/RG-MTM_PacificVis2027_LatestPPT_20261030.zip`。下方旧更新记录保留历史身份。

> 历史更新（N4 初版）：已补 N4 可控层次冲突实验，正文 §7.3 / 图 9，附录 §S3 / 图 S1。正文仍为 11 页（正文在第 9 页结束，第 10–11 页仅参考文献），附录现为 7 页。原始 2026-10-27 源码包保留历史身份；新包见 `export/RG-MTM_PacificVis2027_N4_20261030.zip`。完整输入、结果与复现方式见 `../../code/experiments/controlled_conflict/README.md`。

# PacificVis 2027 重写稿（2026-10-27）

按新体系重写的会议稿（VGTC 模板，双盲审稿版）。主线是 ε=0 的精确拓扑版本，ε>0 的有界放松作为延伸。

| 文件 | 作用 |
|---|---|
| `main.tex` / `main.pdf` | 正文：共 11 页，正文在第 9 页结束（上限 9 页），第 10–11 页只有参考文献（上限 2 页） |
| `supplement.tex` / `supplement.pdf` | 附录（7 页，含 N4）：完整证明（定理 2、3，粗下界，最优屏障闭式解），排序和指标协议细节，N3 和 D6 的核对记录，运行时间，以及横评的全部数值、主表、三维数据表和补充图 |
| `OUTLINE.md` | 论文结构：主线、贡献顺序、各节篇幅、图表计划 |
| `main_zh.md` | 正文逐句中英对照（含标题、摘要、图表标题、记号表、算法） |
| `export/RG-MTM_PacificVis2027_LaTeX_20261027.zip` | 完整 LaTeX 工程（可直接上传 Overleaf；已在空目录中验证可独立编译） |
| `refs.bib` | 沿用旧稿 80 条，新增 12 条（逐条与 Crossref 核对过元数据） |
| `scripts/make_figures.py` | 所有图和表都从保存的实验结果生成 |
| `figures/`、`tables/` | 生成的 PDF 图和 LaTeX 表格片段；`figures/data/` 为缓存的派生数据。`fig_prior.pdf` 和 `fig_conflict.pdf` 沿用旧稿的图 2、图 4 |
| `vgtc.cls`、`abbrv-doi-narrow.bst` | 模板，复制自旧稿 |

**正文图表顺序：**

| 编号 | 内容 |
|---|---|
| 图 1 | Storms 首图 |
| 图 2 | 已有方法的流程（旧图） |
| 图 3 | 本文流程，用一帧真实数据走一遍 |
| 图 4 | 定理 1 示意 |
| 图 5 | 冲突与最优屏障（旧图） |
| 图 6 | 横评：5 种方法 × 5 类指标 |
| 图 7 | 位置—拓扑权衡曲线 |
| 图 8 | Storms 案例 |
| 表 1 | 方法作为统一问题的实例 |
| 表 2 | 数据集 |
| 算法 1 | 生成一帧地图 |

## 重新生成与编译

```sh
cd paper/pvis2027
PYTHONPATH=../../code/src ../../.venv/bin/python scripts/make_figures.py   # 图与表
tectonic -X compile main.tex && tectonic -X compile supplement.tex       # 或 Overleaf：pdfLaTeX + BibTeX
```

- 地图图（图 1）需要 Ring 和 OLR 的输入，仓库里已带。Storms 案例图需要 ERA5 输入，可用 `code/analysis/era5_arco_expanded.py` 从公开的 ARCO-ERA5 下载。Wildfires 的原始数据不在仓库中。
- 删除 `figures/data/` 会触发重算：Tangaroa 约 3 分钟，地图约 1 分钟。

## 正文中标为待补的内容（橙色 `\pending{}`）

| 位置 | 待补内容 | 对应路线图步骤 |
|---|---|---|

## 写作上已做的取舍

- 标题与贡献中不再写"统一 TMTM/ST-MTM"。改为"二者是同一问题中 ε=0、B=∞、λ_R=0 的实例"，并明确不声称复现了原生输出。
- 不声称更易读；可读性与感知留给后续的 TVCG 工作。
- κ 构造只作为对照基线出现，其误差没有上限。
- 引言中说明默认使用 ε=0，只在权衡图显示收益明显时才放松。

## N4 新增内容（2026-10-30）

- 正文：Controlled hierarchy conflict 小节；`figures/fig_controlled_conflict.pdf`（图 9）。
- 附录：完整协议、独立 LP 验证、H_hier 和父间隙扫描；`figures/fig_controlled_conflict_supp.pdf`（图 S1）。
- 正文插图后的现编号：图 7 地图比较、图 8 前沿、图 9 N4、图 10 Tangaroa、图 11 方向、图 12 Storms；以 LaTeX 自动交叉引用为准，上方旧图表计划保留历史身份。
- 数据：`code/results/controlled_conflict20261030/`；脚本：`code/experiments/controlled_conflict/`（相对仓库根目录）。
- 原稿快照与修改前完整备份：工作区 `output/n4_controlled_conflict_20261030/before/`。

## 最新 PPT 图的复现

最终 PNG 按原始像素复制到 figures/：二维 5280×3000，三维 2808×1296；PDF 仅封装图像，不缩放重绘科学内容。在 7 英寸通栏处分别约为 754 dpi 和 401 dpi。`scripts/make_figures.py` 中 `fig_latest_ppt_examples()` 从这些冻结 PNG 重新生成论文 PDF 图，需要 PyMuPDF 和 Pillow。旧 `fig_teaser()` 仍保留原图的历史重建能力，但当前正文引用独立的新图名，不会被其覆盖。

二维图的 t=236 合并误差和树结构以 hybrid_topology_audit.json 为准；三维图以保存的 evidence.json 为准。两者均是额外诊断序列，不改变 917 帧横评范围。树图纵轴是结构层数，原始标量误差另行核验。原 PPT 没有修改。
