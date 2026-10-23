# Reference-Guided Merge Tree Maps (RG-MTM)

完整研究材料更新：2026-10-23。此仓库集中保存 RG-MTM-P / RG-MTM-R 方法、论文与附录、可编辑配图和实验凭据。当前稿是研究稿，尚需按投稿会议要求调整篇幅。

## 论文与图件

- [正文 PDF](paper/manuscript/Revised_RG-MTM.pdf) · [附录 PDF](paper/manuscript/Revised_Supplement.pdf)
- [正文 LaTeX](paper/manuscript/latex/main.tex) · [附录 LaTeX](paper/manuscript/latex/supplement.tex) · [完整参考文献](paper/manuscript/latex/refs.bib)
- [正文配图 PPT](paper/figures_ppt/All_Figures.pptx) · [附录配图 PPT](paper/figures_ppt/All_Supplementary_Figures.pptx) · [单图编辑母版](paper/figures_ppt) · [PDF/PNG/SVG 图件](paper/figures_export)
- [独立 LaTeX 压缩包及下载附件](https://github.com/lelewang1109/RG-MTM/releases/tag/research-2026-10-23)

## 项目导航

| 目录 | 内容 |
|---|---|
| [code](code/README.md) | 算法实现、分析模块、实验入口、测试、原始结果与溯源记录 |
| [paper](paper/README.md) | 当前正文/附录、模块化 TeX、图件、冻结证据与维护脚本 |
| [data](data/README.md) | 小型处理输入、树与来源协议；大体量输入见数据清单 |
| [docs](docs/README.md) | 正文与附录索引、实验组织、证据边界及整理记录 |
| [references](references/README.md) | 核心论文、相关方法与项目入口 |
| [发布与验证说明](docs/github/RELEASE.md) | 发布范围、复现步骤和明确限制 |

当前主结果见 [九数据统一结果](code/results/submission20261023/README.md)。917 个时序帧与 22 个静态切片分别计数；Benzene 为二维电势重建截面，不能视为作者原始数据或物理时间序列。显示插值不增加科学样本；性能与精度结论以保存的原始数值为准。

## 安装与复核

```sh
# 从克隆后的仓库根目录执行
python3 -m venv .venv
.venv/bin/python -m pip install -e './code[volume3d]'
cd code
PYTHONPATH=src ../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../.venv/bin/python tools/build_submission20261023.py --check
```

三维实验按需安装 `pip install -e './code[volume3d]'`；固定版本 TTK 的获取和构建见 `code/experiments/volume3d/build_native_ttk.py`。大型科学实验需要先准备相应输入；已有数值检查通过不等于本轮重跑了全部实验。

论文编译入口位于 `paper/manuscript/latex`，使用支持 `vgtc.cls` 的 LaTeX 环境依次运行 `pdflatex main`、`bibtex main`、两次 `pdflatex main`；附录将 `main` 换成 `supplement`。独立源码包包含编译所需图件与证据。

## 数据与历史

[数据库存清单](docs/github/DATA_INVENTORY.csv) 列出本次本地输入的路径、字节数和是否随仓库提供。原始大体积 NetCDF、三维体、完整地图、系统缓存及第三方论文阅读副本不直接打入 Git；获取入口见 [数据与复现指南](docs/github/RELEASE.md)。代码与数值保留原始哈希，发布额外提供文件校验清单。

旧提交仍保留在 Git 历史中。2026-10-23 起代码从仓库根目录迁至 `code/`，论文材料集中在 `paper/`，运行原脚本前请先进入 `code/`。独立 RA-MTM 项目不包含在本次更新中。
