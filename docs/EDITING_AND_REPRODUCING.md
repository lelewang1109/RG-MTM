# 在最终稿上修改、检查与复现

以下以包含code/paper/data的仓库根目录为起点。已有环境可替换 `.venv/bin/python`；不要把历史记录中的个人绝对路径当成新机器的运行命令。

## 1. 修改当前论文

入口是 `paper/manuscript/latex/main.tex` 与 `supplement.tex`。相对latex目录的模块：

| 内容 | 源文件 |
|---|---|
| 标题、摘要、首图与图注 | `frontmatter.tex` |
| 引言与贡献 | `introduction.tex` |
| 共同模型和约束 | `framework_model.tex`、`method.tex`、`unified_solver.tex` |
| 评价协议与当前总表 | `evaluation.tex` 及其引用的tables文件 |
| Storms/Wildfires解释 | `applications.tex` |
| 共同模型结果图 | `unified_results.tex` |
| 讨论与结论 | `discussion.tex`、`conclusion.tex` |
| Storms首图协议与误差 | `revision_evidence_supplement.tex`，S8.1 |
| 引用 | `refs.bib` |

正文与附录的关联事实需一起更新。日期、阈值、特征编号只在所属实验内解释。当前总表已包含325个新增ST-MTM布局，历史表生成器不是当前表的编辑入口。

## 2. 修改配图

先查 `paper/FIGURE_INDEX.json`，再修改相应母版。图1采用代码/SVG，重绘命令为：

```sh
.venv/bin/python paper/previews/storms_anatol_20261026/build_preview.py
```

该绘图入口读取 `paper/evidence/fig1/` 的保存输入和原ERA5小时文件。阅读现有图件或编译论文不需要原数据。代码显式加载macOS Arial；其他系统需安装Arial并调整字体加载路径。标量数值、实际坐标、轨迹身份与缺失区间按保存结果保留。

确认版式后，将 `Anatol_event_threshold_preview.pdf/.png/.svg` 同步到 `paper/figures_export/Fig1.*` 和 `paper/manuscript/latex/figures/Fig1.*`，同步图注、正文与索引哈希。只给已展示的时刻/特征添加标记。旧PPT图1页是历史版，不用它覆盖当前SVG/PDF。资产Fig15—17也使用代码/SVG；其余PPT图件见 `paper/STYLE_GUIDE.md`。

## 3. 编译与交付

用LaTeX编辑器打开main/supplement.tex，或在安装Tectonic后执行：

```sh
cd paper/manuscript/latex
tectonic --keep-logs main.tex
tectonic --keep-logs supplement.tex
```

也可使用pdfLaTeX + BibTeX / Overleaf。模板与图件随源码提供，LaTeX包和字体支持由编译环境提供；大原始数据不是编译依赖。

渲染检查改动页面、图注、表格与引用后，将检查过的main.pdf、supplement.pdf更新为 `paper/manuscript/Revised_RG-MTM.pdf`、`Revised_Supplement.pdf`。返回仓库根目录打包：

```sh
.venv/bin/python paper/scripts/package_delivery.py
```

该脚本刷新本地源码ZIP和文件清单，不替代编译与视觉核验。大ZIP通过Release分发，不加入普通Git文件。

## 4. 只核验保存结果

```sh
PYTHONPATH=code/src .venv/bin/python -m unittest discover -s code/tests -v
.venv/bin/python paper/scripts/verify_unified_revision.py --numerical-only
```

GitHub发布检出的清单核验为 `python tools/verify_release.py`。四组新增ST-MTM的完整数组核验还需对应源清单及坐标：

```sh
.venv/bin/python -m pip install -r code/experiments/stmtm_completion/requirements.txt
PYTHONPATH=code/src:code .venv/bin/python code/experiments/stmtm_completion/verify.py
```

检查器独立重建合并屏障、几何/运动指标和QP残差。缺输入时按协议准备；不要忽略来源哈希错误。历史生成器 `code/tools/build_submission20261023.py --check` 还会对比旧版论文表，因此在当前补全稿上会按预期失败，不应重新导出它来覆盖当前表。GitHub使用 `python tools/verify_historical_snapshot.py` 仅读取并重建冻结结果，当前活动表由 `experiments/stmtm_completion/` 核验。

## 5. 从原始输入重新计算

| 目标 | 阅读入口 |
|---|---|
| 五组二维时序/共同模型 | `code/experiments/unified/README.md` |
| 连续预算前沿与反向查询 | `code/experiments/framework/README.md` |
| 四组新增ST-MTM | `code/experiments/stmtm_completion/README.md` |
| Tangaroa全201体 | `code/experiments/volume3d/README.md` |
| Nucleon、Benzene、Cylinder | `code/experiments/paper1_suite/README.md` |
| 公共场获取 | `code/experiments/publication2027/REPRODUCING.md`、`data/README.md` |

重跑可能需要外部下载、大内存、TTK或体数据工具。保存结果检查通过，不等于从头重跑全部实验；分别记录实现测试、数组核验、重新优化和文档编译。

## 6. 发布

确认PDF、TeX与图件一致，当前结果表未被旧导出覆盖，README链接有效。环境、密钥、原始大档案、外部绝对符号链接和.build缓存不进入提交。更新GitHub发布说明和SHA清单；通过发布检出提交，源码ZIP/PDF资产同步到Release，再检查远端提交和CI。
