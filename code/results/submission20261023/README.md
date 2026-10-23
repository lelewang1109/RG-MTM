# 当前投稿实验摘要（2026-10-23）

本目录是当前投稿的选取与统一指标快照。PM2.5在独立目录重新执行全年实验并验证；其他数值从受哈希保护的原结果读取，Tangaroa、Cylinder及静态输入的共同连续位移指标从已保存布局重新汇总。

- 当前统一比较：9个数据输入；7个时序共917帧，另有Nucleon 1静态切片与Benzene 21静态截面。
- 小树穷举前沿：Storms、Wildfires、OLR、PM2.5、Ring，5序列614帧；R20位于精确前沿611/614帧；层级冲突123/614帧。
- Tangaroa 201帧与Cylinder 102帧是原始三维体场；指标与其他输入统一列示，输入维度、预处理、参考和事件分母仍分别注明。
- 本次退出的是64×64、64帧Gaussian；历史342帧冻结结果及manifest原样保留。独立241×241、64帧镜像控制不受影响。

`unified_metrics.json`和`unified_metrics.csv`保留完整精度；`tables/`保存论文当前三主表及补充表（运动列并入共同指标主表）的对应快照。`selected_evidence/`只保留当前五小树成员的核心原记录；原始混合六数据源文件和完整历史manifest仍在原路径。`manifest.json`逐一记录输入来源与输出哈希。

```sh
PYTHONPATH=src ../../.venv/bin/python tools/build_submission20261023.py --check
PYTHONPATH=src ../../.venv/bin/python experiments/publication2027/validate.py --require-complete-run
PYTHONPATH=src ../../.venv/bin/python tools/verify_rgmtm_migration.py
```

以上命令在code目录运行。第二条同时验证历史六数据冻结证据与当前九数据摘要，并检查历史30项数值阶段的完成记录。代码中`analysis/dataset_suite.py`的当前默认成员已改为五小树；历史build/validate实现明确命名为`*_legacy.py`。

共同NROE/NMLE和连续Epool/Einf均为百分比。运动给出errors/Nclear，按输入维度使用空间欧氏距离；投影真值另用自己的事件分母。ST-MTM未跑的四个输入为n/r，静态运动为n/a；不存在补零或跨数据合并运动准确率。体场R参数未启用可选剪枝，不能将相同kappa误写为相同误差上限。

所有编辑前代码备份位于`../../../其他/归档/实验重构前_20261023/code_edits/`；新增`provenance/submission_selection_20261023.json`要求反向编辑重建历史源码的精确字节，不跳过原验证。

PM2.5当前使用results/pm25_2000完整2000年366场，同区域/网格/100km平滑；primary运动P42/95、R20 47/95。旧January文件保留在历史路径。显示插值不计入科学样本。
