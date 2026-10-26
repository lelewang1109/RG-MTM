# 当前LaTeX项目

2026-10-26：当前最终稿已将 Storms 五快照与 P/R1/R2/R5 对照合入图1，图注位于 `frontmatter.tex`，动机说明位于 `introduction.tex`，具体案例位于 `applications.tex`，方法与误差证据位于 `revision_evidence_supplement.tex` 的 S8.1。图1的 PDF/SVG 位于 `figures/`，冻结数组与绘图代码副本位于 `evidence/storms_teaser20261026/`。正文保持26页，附录更新为52页。九数据评价表及325个新增ST-MTM结果保留。

编辑main.tex和supplement.tex。当前副标题：A Unified Position–Topology Framework。

framework_model.tex定义共同四项目标、时间参数η、真实拓扑ε和位置B预算以及四个工作区域。unified_solver.tex给出共享候选过滤/QP/零空间次级规则/填充流程。framework_evaluation.tex给出同模型实验与独立前沿证据。unified_results.tex展示图16—17；framework_supplement.tex给出解释与保证边界。

图1—14资产保持原编号身份；图1已更新为用户选定的时序定位、地理快照和阈值对照版。图15为前沿实验；图16—17为新共同QP实验。新图的SVG和代码保存在对应figures_export与code/experiments目录。

证据目录evidence/unified20261025记录3,070个主布局、双预算查询、候选覆盖和原生相似性。所有数值来自保存的完整坐标/屏障；原生相似性采用单个全序列仿射变换，不逐帧拟合。

数值、图件、PDF和ZIP一致性检查使用paper/scripts/verify_unified_revision.py。旧检查器保留其历史版本范围。
