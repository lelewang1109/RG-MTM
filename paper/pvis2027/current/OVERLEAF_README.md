# Overleaf 上传与编译说明

## 上传步骤

1. 在 Overleaf 选择 **New Project → Upload Project**。
2. 上传 `AnchorMTM_Overleaf.zip`；压缩包根目录直接包含 `main.tex`。
3. 将主文件设为 **main.tex**，编译器选择 **XeLaTeX**。
4. 点击 Recompile；参考文献由 Overleaf 自动调用 BibTeX 处理。
5. 若切换主文件后出现缓存引用，选择 Recompile from scratch。

## 主文件与文献

- 正文入口：`main.tex`，七个章节位于 `sections/`。
- 文献库：`references.bib`，内容与基准工程的 `refs.bib` 完全相同。
- 文献样式：原 `abbrv-doi-narrow.bst`，采用 BibTeX。
- 模板：原 `vgtc.cls`；保留基准的 review、匿名作者与投稿编号设置，没有替换模板或加入作者信息。
- 补充方法入口：根目录 `supplementary.tex`；内容位于 `supplementary/content.tex`。编译后切回正文入口。

## 独立性与注意事项

所有正文图表、章节、参考文献和样式均在包内，TeX 编译不读取本机绝对路径，不调用Python或实验程序，不需要shell escape。audit目录的JSON记录中出现原文件路径仅用于溯源，不是编译依赖。`audit/baseline_main.tex` 仅供比对，不应选为主文件。

已使用本地Tectonic/XeTeX及其BibTeX流程验证正文与补充材料，并对ZIP解压后的独立目录重新编译。该验证不等同于实际登录Overleaf网站编译；推荐XeLaTeX以匹配本地引擎。编译时可能提示原有部分图PDF版本高于输出版本、PDF标签被忽略，以及算法宏包注释的编码警告；这些为基准依赖产生的非致命提示，不是缺失文件或未定义引用。

本轮未运行实验，也未重绘图片。12图的二进制文件、5表完整环境、15个显示公式、3个定理、1个命题与基准一致；流程图按后续明确指令替换为指定PPTX的PDF导出。可用 `python3 audit/check_invariants.py` 重查；该脚本是可选的只读审计，不参与论文编译。

## 后续流程图替换

用户明确指定 `AnchorMTM_流程图_论文配色_布局优化.pptx` 后，本工程将其单页直接导出为论文Figure 5使用的PDF，替换 `figures/anchor_framework.pdf`，保留其余12图不变。新图的layout面板合并展示选序与锚点放置，文字和图注据此对应，算法定义、公式和实验结果未改。源PPTX保存在 `figure_sources/framework_requested.pptx`。


## 2026-11-09 图源同步

本次全部配图PPT重新导出，正文图号1–6、10–13的对应源文件位于figure_sources；图7–9保持代码生成结果。流程图为最新细节订正版；Cylinder为独立原图与可编辑标注版；PM2.5仅保留论文133小时单栏版一页。PM2.5镜像协议已补入正文实验设置。旧的“12图二进制不变”记录仅描述历史基准，不适用于本次更新。
