# AnchorMTM 正文叙事修订与工程整理报告

## 1. 内容基准与源文件定位

唯一事实基准为 `output/paper_narrative_reproduced_9pages_20261108/AnchorMTM_投稿排版修订版.pdf`；其对应同目录同名 `.tex` 与实际编译源一致。修改前重新编译该源文件，确认10页文字与逐页渲染图像均与指定PDF完全一致。基准PDF SHA-256为 `562279819310d56afdad65c948b15e6bc660bc1c438e1c770c41ed38c758c035`。

本地仓库remote仍为 `https://github.com/lelewang1109/RA-MTM.git`，任务写明的仓库为 `RG-MTM`。本轮以已验证对应的本地工程工作，没有修改remote，也没有从另一版本、远端稿件或老师版本取数据替换本稿。独立修改目录为 `output/AnchorMTM_Overleaf/`，基准工程未覆盖。

## 2. 原叙事的问题

原稿已具备理论—算法—实验骨架，但部分段落仍按实现或图表加入顺序展开：固定坐标的需求与层次冲突之间的因果桥接较短；有限宽度为什么使点排序不足，需要读者自行从公式推断；方法先概括“两阶段”，随后又以四个操作组织，输入输出关系不够显式；Table 2中的下界诊断分散在定位比较里；案例顺序与验证/运行时间说明交错。Balanced、Budgeted和Exact的层级也需要统一陈述。

## 3. 核心主线

**Keeping merge-tree topology has an unavoidable positional cost. We quantify this cost and develop AnchorMTM to approach the resulting bounds under a controlled topology budget.**

全文由空间坐标的需求进入连续子树与投影顺序的冲突，再依次讨论点排序、有限宽度与有界合并误差；方法把这些限制转化为选序、定位和重建约束；实验先验证限制，再评价固定空间定位，随后解释预算的作用，最后阅读真实地图。

## 4. 分章节修改

- **Abstract**：按坐标缺口、结构冲突、三个界、AnchorMTM与已有证据组织，明确只在相应模型下讨论界；未添加实验结论。
- **Introduction**：从二维/三维时序场的三类分析需求展开，准确承认TMTM和ST-MTM解决的层次、几何和时间问题，再提出固定物理坐标及其代价。贡献保持理论、算法、实验三部分。
- **Related Work**：显式区分domain-based、feature-based、topology-based保留的信息，随后连接到时序拓扑图、叶排序、受约束布局和树比较。保留Figure 2及全部原引用条目，不采用“后者全面优于前者”的叙述。
- **Problem Formulation**：分为树/剖面/身份、固定参考、统一模型、空间—拓扑冲突四节。Figure 3/4与原数学定义保留。将A,C,D,B冲突单列，并显式提出RQ1--RQ3。
- **Position Bounds**：重写定理前后的动机与解释，依次回答“树本身强迫什么”“真实间隔多增加什么”“预算释放哪些块约束”。所有15个显示公式、3个定理、1个命题的完整环境逐字保留；不把有限宽度下界宣称为普遍可达最优值。
- **AnchorMTM**：用Figure 5的Extract and Reference → Search Leaf Orders → Place Anchors → Reconstruct and Assemble说明每阶段的输入、约束和输出。保留原搜索、最优屏障、QP和重建规则以及Figure 6。明确Exact/Budgeted是同框架预算取值，Balanced只是实验选定的正预算配置，预算不是位置误差的直接上限。
- **Experiments**：设为6.1设置、6.2下界验证、6.3绝对定位、6.4位置—拓扑权衡、6.5案例、6.6实现与运行时间。将原基线顺序误差段与Table 2移入下界验证，保留所有数值。案例按Storms、Cylinder、Ring、PM2.5顺序阅读；复核与计时段从案例之间移至6.6。保留Gaussian不改善、Wildfires SNS变化、PM2.5 TW变化、Storms困难帧改善等结果。
- **Discussion and Conclusion**：回到强制代价与具体布局选择，分别讨论单投影、邻域关系、启发式排序、证书间隙、匹配/方向估计和不同案例配置的含义，最后收束到固定参考坐标与受控合并预算。

## 5. 理论与算法衔接

点界说明应先处理叶顺序；宽度界说明应按真实区间成本评价候选；有界拓扑界说明预算只释放特定连续性限制。因此方法用固定顺序的精确packing代价排名，用最小合并误差决定准入，再在选定顺序的位移上限内协调空间、几何和时间项，最后重建并检查。重写的是解释，不是算法定义。

## 6. 实验与研究问题的对应

6.2用原受控四叶实验、真实1624帧下界与基线误差表回答RQ1--RQ3的理论机制；6.3用原五组平面表、两组体数据表及位置对比图评价最终锚点；6.4用原预算分布图解释限制的释放及不同指标的变化；6.5连接统计与原始场的现象；6.6保留参数、计时和现有核验流程。

七个序列Gaussian、Ring、Wildfires、Storms、PM2.5、Cylinder、Tangaroa全部保留。公开SNS/TW与本地测量来源仍区分；体数据图的默认配置与主表选定配置仍区分；Cylinder guidance变体和Ring联合变化仍明确说明。

## 7. 不变量检查

- 原Figure 1--13中12个图文件逐字节一致；唯一例外是用户后续明确指定的新流程图。新图由所给PPTX第1页原版导出PDF，无重绘，PPTX及PDF的SHA-256和源文件均随工程保留。
- 原Table 1--5全部迁移，5个完整表环境逐字一致，未改数值、强调、单位、脚注或排名。
- 15个显示公式、3个定理、1个命题的完整环境逐字一致；基准中的全部不同内联数学表达式仍存在。
- 正文数值token清单及出现次数与基准一致；引用清单及使用次数一致，完整原文献库逐字迁移为references.bib。
- 保留原模板、匿名设置、题目和作者元数据。未重跑实验、改参数、换指标或导入其他版本的结论。

`audit/check_invariants.py` 可复查上述项目；完整源清单在 `audit/source_manifest.json`，逐段对照在 `PARAGRAPH_COMPARISON.md`。

## 8. 工程与编译

拆为main.tex和七个sections文件；13图、5表、完整文献库及原样式均随包迁移。保留既有补充方法，根入口为supplementary.tex，正文入口为main.tex。原refs.bib仅改文件名，补充材料的文献文件引用相应改为references。

本地完成正文和补充编译；再将ZIP解压到独立临时目录，在清除TEXINPUTS/BIBINPUTS外部搜索路径的环境中重新编译。编译日志、页数、图表与引用检查见独立编译核验记录。推荐Overleaf选择XeLaTeX，由latexmk自动处理BibTeX。图的允许宽度调整仅用于消除浮动页溢出，未改图内容、色彩或坐标。

## 9. 审稿视角复查与范围

研究问题、理论递进、算法输入输出和证据顺序已经显式连接。Exact/Budgeted/Balanced、点界可达性与宽度证书、位置误差与SNS/TW的区别在各自出现处解释。没有通过删掉不理想结果来增强结论。

没有发现本轮引入的研究事实变更、缺失文件、未定义引用或严重排版错误。既有补充材料中一个指向主文表格的跨文档引用原来显示为??，本轮改为明确的文字指向，未改表格或数值。保留了基准的数学成立条件与不同配置的解释，没有借重写重新裁定原研究结论。已验证本地独立解压编译；未实际登录Overleaf云端编译。原图PDF版本/标签和算法宏包注释编码会产生非致命依赖提示，需与缺失文件或引用错误区别对待。

## 后续流程图替换

用户明确指定 `AnchorMTM_流程图_论文配色_布局优化.pptx` 后，本工程将其单页直接导出为论文Figure 5使用的PDF，替换 `figures/anchor_framework.pdf`，保留其余12图不变。新图的layout面板合并展示选序与锚点放置，文字和图注据此对应，算法定义、公式和实验结果未改。源PPTX保存在 `figure_sources/framework_requested.pptx`。
