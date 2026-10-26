# GitHub当前研究材料发布

目标仓库：[lelewang1109/RG-MTM](https://github.com/lelewang1109/RG-MTM)。本次发布标记：[research-2026-10-26-final](https://github.com/lelewang1109/RG-MTM/releases/tag/research-2026-10-26-final)。默认下载使用 [轻量ZIP](https://github.com/lelewang1109/RG-MTM/archive/refs/heads/main.zip)。

## 本次更新

- 正文26页、附录52页，首图更新为全时序定位、五张地理快照及P/R1/R2/R5对照；图注、引言、Results和S8同步。
- 当前九数据评价表包含四组325个新增ST-MTM布局，完整保存剖面和核验入口随仓库提供。
- 总README、目录导读、修改/复现流程与代码/结果README说明当前入口、历史材料和外部输入。
- 同步当前图3时序显示与其他当前稿修改，稳定资产编号与正文编号通过FIGURE_INDEX关联。

## 分发范围

Git仓库保存代码、可核验的数值证据、当前PDF、模块化LaTeX、SVG/PDF/PNG图件、既有PPT和数据协议。图1当前母版是SVG/Python；旧PPT的对应页仅保留历史版。

默认ZIP只携带代码、当前PDF、可编译LaTeX、小型输入及文档。`.gitattributes` 的 `export-ignore` 排除大实验结果、PPT、重复导出和绘图证据；这些按需材料仍在完整Git检出中。旧稿备份目录已从主分支移除。具体范围和获取方式见 [下载说明](../DOWNLOADS.md)。

`RG-MTM_LaTeX.zip` 大于100MB，作为Release资产上传。原始大体数据、下载档案、环境和.build缓存不进入Git；读取保存结果或编译论文无需下载全部原始体。

## 阅读和复现

从 [目录导读](../DIRECTORY_GUIDE.md) 和 [修改/复现流程](../EDITING_AND_REPRODUCING.md) 开始。数据库存见 [DATA_INVENTORY.csv](DATA_INVENTORY.csv)，included=True才表示当前仓库实际携带，False仅记录来源/库存。

本次分别核验57项实现测试、325个新增ST-MTM布局、共同模型保存见证、当前PDF/图件身份、ZIP和内部链接；没有从头重跑全部科学实验。最新检查见 [VALIDATION.json](VALIDATION.json)，历史2026-10-23检查另存。完整文件SHA清单见 [PUBLISHED_FILES.sha256](PUBLISHED_FILES.sha256)。

历史记录中的个人绝对路径是冻结溯源信息，不是新机器的运行命令。公共检出保留已有路径迁移与历史源码身份ledger，不把这些兼容层覆盖回本机版本。
