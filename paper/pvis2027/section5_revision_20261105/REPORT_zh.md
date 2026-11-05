# 第5节与表格修订交付

唯一数值来源：experiments_ratio_p_20261104/REPORT_zh.md及CSV。数据集为Gaussian、Ring、Wildfires、Storms。没有复用七数据集寻优或ST-MTM弱参数试算来替换正式结果。

- 表1：TMTM、ST-MTM Temporal、AnchorMTM (our method)。AnchorMTM分Exact/Balanced两行；SNS/TW/NPE；无Dims/T/features/p列、无灰底、无竖线。最佳/第二按数据集和显示精度自动生成，保留并列。
- 表2：仅Balanced，单栏，epsilon、栅格长度、宽度比例参数、优化时间、总时间；不含NMLE列。
- 第5节完成设置、数值比较、预算有效性、参考解释与预算敏感性/性能，未虚构组件消融。Discussion/Conclusion由已有证据补齐，引用保留在正文最后。
- ST-MTM的TW优势与AnchorMTM的NPE优势按目标差异分析，没有将较低TW解释成基线技术普遍失效。跨来源比较与TW有效帧很少均明确披露。
- 原始论文PDF/LaTeX保存在before目录；本轮未重新运行实验或修改任何测量CSV。

复现：项目根目录运行source/update.py生成两表及第5节，再运行paper/pvis2027/build_main.py。update.py保留第6/7节已有内容。输入CSV和生成表的逐项核对见ranking_audit.csv。

第五节只报告四个二维数据集；附带发布的三维质心选轴是独立代码路径，不作为本文四数据集实验的证据。

表格排版更新：主表采用方法分组、居中数据列和紧凑行距；Balanced 参数表转置为数据集作列、参数/时间作行，保持单栏、无灰底、无竖线。数值不变。

新增默认方向 Hilbert/Morton 至论文表1，重新核验72个指标单元的逐数据集排名；表2改为自然宽度。第五节补充曲线方法协议及Ring例外结果；未修改既有实验值。
