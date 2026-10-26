# 下载与按需材料

日常阅读、修改论文或查看实现，下载 [轻量ZIP](https://github.com/lelewang1109/RG-MTM/archive/refs/heads/main.zip)。包含当前正文和附录PDF、模块化LaTeX、编译所需图件、代码、实验协议、小型输入与文档。

大实验结果、PPT、重复图件导出和绘图证据不进入默认ZIP。当前PDF和LaTeX的内容保持不变。解压后可运行 `python3 tools/verify_release.py` 核验所含文件；输出会明确列出按分发规则省略的文件数。

| 需求 | 获取方式 |
|---|---|
| 阅读、修改、编译当前论文 | [轻量ZIP](https://github.com/lelewang1109/RG-MTM/archive/refs/heads/main.zip) |
| 只读正文或附录 | [正文PDF](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/Revised_RG-MTM.pdf) · [附录PDF](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/Revised_Supplement.pdf) |
| 独立论文包，包含论文证据 | [当前LaTeX完整包](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/RG-MTM_LaTeX.zip) |
| 查看评价汇总，不下载完整数组 | [当前指标CSV](https://github.com/lelewang1109/RG-MTM/blob/main/code/results/stmtm_completion20261026/unified_metrics.csv) · [补全报告](https://github.com/lelewang1109/RG-MTM/blob/main/code/results/stmtm_completion20261026/REPORT_zh.md) |
| 编辑SVG/PPT或重绘首图 | 在线打开 [图件](https://github.com/lelewang1109/RG-MTM/tree/main/paper/figures_export)、[PPT](https://github.com/lelewang1109/RG-MTM/tree/main/paper/figures_ppt) 或 [绘图源码](https://github.com/lelewang1109/RG-MTM/tree/main/paper/previews)，下载所需单个文件；完整依赖用下方Git命令获取 |
| 核验保存数组、运行科学测试或重跑实验 | 获取下方完整Git检出，再按实验协议准备外部原始数据 |

完整检出只拉取当前提交，避免下载整个Git历史：

```sh
git clone --depth 1 https://github.com/lelewang1109/RG-MTM.git
cd RG-MTM
python3 tools/verify_release.py
```

完整检出仍较大，适用于需要全部保存结果的研究者。轻量ZIP中的相对结果/PPT/证据链接可能指向按需材料，可通过上述GitHub网页访问。完整实验命令和结果核验命令需要完整检出；ZIP的文件校验不代表已运行这些实验检查。

原始大体数据和完整下载档案另按 [数据说明](../data/README.md) 准备。独立LaTeX包属于当前Release附件，不受主分支的轻量ZIP规则影响。
