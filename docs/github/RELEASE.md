# GitHub 完整研究材料发布说明

发布目标：现有 `lelewang1109/RG-MTM`，2026-10-23。仅更新 RG-MTM；原本地工作区和 RA-MTM 历史保留。

## 发布范围

算法、分析、实验、已有测试、可携带的数值证据与结果；当前正文/附录及模块化 LaTeX；全部当前配图的单图与合并 PPT、PDF/PNG/SVG；冻结证据、审计记录、参考文献 BibTeX 和数据来源。修改前稿与图1补充候选按原说明保留。

`RG-MTM_LaTeX.zip` 超过单文件 100 MB，置于 GitHub Release；同样内容的可编辑 TeX、图与证据在 `paper/manuscript/latex/` 可直接访问。第三方论文阅读 PDF 不作为本项目成果重新发布，使用参考文献链接。

历史两套候选整包 `RG-MTM_Evidence_Reorganized_20261023` 与 `RG-MTM_PacificVis2027_9plus2_20261023` 以及 `.build` 缓存不进入当前发布。它们本地保留，当前论文入口只有 `paper/manuscript/latex/main.tex` 与 `supplement.tex`。

## 数据获取与重跑

- 二维公共数据处理及来源：`code/tools/fetch_public_scalar.py`、`prepare_cn_pm25.py`，`code/experiments/publication2027/REPRODUCING.md`。
- PM2.5 全年：`code/tools/run_pm25_annual.py`、`export_pm25_annual.py`，保存结果在 `code/results/pm25_2000/`。
- Tangaroa：`code/experiments/volume3d/prepare_tangaroa_official.py` 和同目录 README、输入协议及 `build_native_ttk.py`。大型原始速度档案、二进制与完整地图需另行下载或重建。
- Nucleon、Benzene 重建、Cylinder：`code/experiments/paper1_suite/README.md`。Benzene 几何来源快照已保留在对应数据目录；外部参数 PDF 从 `model.json` 中的来源获取。
- 数据库存见 `DATA_INVENTORY.csv`：`included=True` 表示随 Git 分发；其余条目只记录库存，不声称可以直接从本仓库下载。清单不包含个人绝对路径。

进入 `code/` 后执行各实验说明中的原命令。代码数据相对链接指向本仓库的 `data/`，不依赖原电脑的路径。

## 验证边界

发布检查分开记录代码测试、保存结果一致性、论文/图件身份、ZIP 完整性和仓库内部链接。全部科学实验未在本轮重新运行。旧审计记录属于其标注的历史版本，最终快照检查见同目录 `VALIDATION.json`；完整文件 SHA256 见 `PUBLISHED_FILES.sha256`。

历史审计及整理报告中的原电脑绝对路径仅作为溯源数据保留，不是新机器的运行命令。部分历史保存证据核验需要本地归档；当前投稿表格核验与常规测试应从本仓库运行。
