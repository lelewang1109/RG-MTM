# 下载研究材料

[研究材料ZIP](https://github.com/lelewang1109/RG-MTM/archive/refs/heads/main.zip)完整保留以下四类已发布材料：

| 内容 | 目录 |
|---|---|
| 数据及获取协议 | `data/`、`code/data/` |
| 当前论文、LaTeX、图件与科学证据 | `paper/manuscript/`、`paper/figures_export/`、`paper/evidence/`、`paper/previews/` |
| 实验代码、方法实现、分析与测试 | `code/experiments/`、`code/src/`、`code/analysis/`、`code/tests/` |
| 全部已保存实验结果 | `code/results/` |

默认ZIP仅省略两个重复PPT合集、`main.pdf`/`supplement.pdf`别名、旧图1编辑版本、附录备选稿及历史整理记录。单图PPT、当前正文与附录PDF、完整LaTeX、当前PNG/SVG/PDF图件、科学数组和核验记录均保留。旧稿备份目录已移除。

ZIP仍包含较多科学数组。只需要阅读时，可直接下载 [正文PDF](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/Revised_RG-MTM.pdf) 和 [附录PDF](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/Revised_Supplement.pdf)；只需独立论文项目时，可下载 [当前LaTeX包](https://github.com/lelewang1109/RG-MTM/releases/download/research-2026-10-26-final/RG-MTM_LaTeX.zip)。

也可使用浅克隆，仅下载当前提交，避免下载全部Git历史：

```sh
git clone --depth 1 https://github.com/lelewang1109/RG-MTM.git
cd RG-MTM
python3 tools/verify_release.py
```

研究材料ZIP解压后同样可运行 `python3 tools/verify_release.py`。数值核验与重跑命令见 [修改与复现流程](EDITING_AND_REPRODUCING.md)；文件校验通过不代表已从头重跑全部实验。

此前未随Git发布的原始大体数据和完整下载档案仍按 [数据说明](../data/README.md) 准备；此次整理没有减少已发布数据。两个PPT合集仍可通过GitHub网页或Git检出获取，各单图PPT已包含在ZIP中。
