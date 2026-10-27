# PacificVis 2027 重写稿（2026-10-27）

按新体系重写的会议稿（VGTC 模板，双盲审稿版）。主线是 ε=0 的精确拓扑版本，ε>0 的有界放松作为延伸。

| 文件 | 作用 |
|---|---|
| `main.tex` / `main.pdf` | 正文：共 10 页，其中正文约 8.1 页（上限 9 页），参考文献约 1.9 页（上限 2 页） |
| `supplement.tex` / `supplement.pdf` | 附录（6 页）：完整证明（定理 2、3，粗下界，最优屏障闭式解），排序和指标协议细节，N3 和 D6 的核对记录，运行时间，以及横评的全部数值、主表、三维数据表和补充图 |
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
