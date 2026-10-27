# PacificVis 2027 重写稿（2026-10-27）

按新体系重写的会议稿（VGTC 模板，双盲审稿版）。主线是 ε=0 的精确拓扑版本，ε>0 的有界放松作为延伸。

| 文件 | 作用 |
|---|---|
| `main.tex` / `main.pdf` | 正文（当前 9 页，含参考文献；已没有待补标记） |
| `refs.bib` | 沿用旧稿 80 条，新增 12 条（逐条与 Crossref 核对过元数据） |
| `scripts/make_figures.py` | 所有图和表都从保存的实验结果生成 |
| `figures/`、`tables/` | 生成的 PDF 图和 LaTeX 表格片段；`figures/data/` 为缓存的派生数据 |
| `vgtc.cls`、`abbrv-doi-narrow.bst` | 模板，复制自旧稿 |

## 重新生成与编译

```sh
cd paper/pvis2027
PYTHONPATH=../../code/src ../../.venv/bin/python scripts/make_figures.py   # 图与表
tectonic -X compile main.tex                                               # 或 Overleaf：pdfLaTeX + BibTeX
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
