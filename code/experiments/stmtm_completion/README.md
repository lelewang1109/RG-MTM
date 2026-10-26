# ST-MTM 与评价指标补全（2026-10-26）

针对旧表中四个 `n/r` 补跑 Nucleon 1、Benzene 21、Tangaroa 201、Cylinder 102，共 325 个原生 ST-MTM 布局。完整剖面保存在独立结果目录，不改写历史输入、布局和 submission20261023 快照。

从仓库根目录执行（已有环境可替换解释器路径）：

```sh
.venv/bin/python -m pip install -r code/experiments/stmtm_completion/requirements.txt
PYTHONPATH=code/src:code .venv/bin/python code/experiments/stmtm_completion/run.py
PYTHONPATH=code/src:code .venv/bin/python code/experiments/stmtm_completion/export.py
PYTHONPATH=code/src:code .venv/bin/python code/experiments/stmtm_completion/verify.py
```

`run.py` 也接受数据键以单独运行。输出为 `results/stmtm_completion20261026/`。`export.py` 更新活动论文的六张结果表及九数据总账，并保留旧稿备份。它保留原有五时序的 SNS/TW/TD，独立计算四个新增输入上四种方法的几何指标。`verify.py` 从完整数组逐对复核标量屏障，从保存坐标独立重建几何与运动指标，并核对输入/代码哈希、投影 KKT 和区间零目标证书。

二维七组数据在前，三维两组在后。Nucleon 和 Benzene 的 TD/时间 ME 不适用；Benzene 的相邻截面位移单列。三维使用三维质心距离；多叉树的固定等标量二叉细化限制可选顺序，属于声明的扩展。固定通用设置不调参择优，不能视作原作者参数复现。Tangaroa 的宽度度量为物理体积，其他组为样本数。

历史 `build_submission20261023.py --check` 只核验原快照，不用于生成本轮活动表；重新导出旧表会覆盖本轮活动表。本轮应使用此目录的导出和核验入口。
