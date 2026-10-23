# 两篇参考论文的方法核验

本次使用原有 ERA5（118 帧）和 Wildfire（30 帧）真实输入；不使用 Gaussian，不新建合成案例，不重跑主实验评价，不覆盖原有实验记录。Tangaroa 核对现有完整 201 帧实验的独立核验及来源绑定。

结论是：**TMTM 的二叉树核心与作者官方 C++ 等价；ST-MTM 的实现流程及优化方程通过独立检查，但当前主实验不是原论文逐数据集同参复现。** 不将这个结论写成“两个原论文的图和指标已精确复现”。

## TMTM

- 官方来源：[Wiebke/TemporalMergeTreeMaps](https://github.com/Wiebke/TemporalMergeTreeMaps)，固定 commit `2c75a10ed2cd55177a25ff751e0c0a8261200717`。
- 核验器编译作者原始 `LandscapeInfo / objectiveForSeveralArcs / decideGreedy / decideGreedyTree` 核心，只以测试适配器提供已有真实树及同一空间重叠计数。它不冒充执行了完整 Inviwo/TTK 环境。
- ERA5：117 对相邻帧、285 个分支决策、687 组区间与锚点，**0 差异**。
- Wildfire：29 对相邻帧、201 个分支决策、431 组区间与锚点，**0 差异**。
- 共 148 帧核对了每个样本恰好出现一次、子树区间连续性、所有叶对实际一维合并层级。最大合并层级误差为 **0**。
- 核心公式对应原文 Algorithm 1、§3.2.1–3.2.2、Eq. (1)–(4)。左右镜像与焦点时间属于可声明的布局选择，不以截图相似度判正确。

## ST-MTM

对照本地参考论文 §4.1–4.2、Eq. (1)/(2)、Fig. 4/5，并执行以下检查：

- 树层次合法性、SciPy OLO 调用、匹配叶对的 concordance、r 阈值及 OLO 镜像选择。
- Eq. (1) 距离目标和时间锚定：独立构造矩阵形式凸二次目标梯度，验证可行性及非负约束乘子的 KKT 驻点残差。最大相对残差 ERA5 `3.55e-8`、Wildfire `1.89e-8`。
- Eq. (2) 相对宽度目标、固定总宽 K、锚点包含、非重叠：最大相对 KKT 残差 ERA5 `1.25e-8`、Wildfire `9.64e-7`。
- 额外在真实首/中/末帧检查 uniform/inverse 权重与 base/temporal 模式，方程检查均通过。
- 全序列共享坐标缩放、padding、离散化后，148 帧所有叶对实际合并层级误差为 **0**，完整拓扑签名失败帧为 **0**。
- 真实数据覆盖 Fig. 5 的 sibling、direct–deep、deep–deep 和 border 四种填充路径。

**OLO 的实际范围：** 论文 §4.1.1 将 SciPy OLO 作为 heuristic。本地 SciPy 1.13.1 在 ERA5 的 1 帧和 Wildfire 的 7 帧未达到独立穷举的最小邻接代价。例如 ERA5 第 24 帧返回代价 182.717226，穷举合法叶序最小值为 152.485568。本次保留论文明确指定的 SciPy 调用，没有悄悄替换为其他排序器；也不再把此步骤描述为“穷举全局最优已验证”。这些记录不应被隐去。

**作者代码等价性：** 手头 ST-MTM 预印本 §4.3 说完整实现将在接收后公开，当前没有可核验的作者运行环境和输出。本次证明范围是公式、约束与流程的一致性，不是与作者程序逐字节等价。

## 主实验参数与论文参数必须区分

| 数据 | 当前主实验 W / K / r / λ / L / Start | 原文对应数据集 W / K / r / λ / L / Start |
|---|---|---|
| ERA5 vs Storms | uniform / 5.644221 / 0.95 / 0.5 / 4096 / 0 | inverse / 135 / 0.65 / 0.05 / 4096 / 40 |
| Wildfire | uniform / 6.269531 / 0.95 / 0.5 / 2048 / 0 | uniform / 10 / 0.85 / 0.5 / 4096 / 5 |

K 具有输入坐标单位含义；本项目的坐标归一化、帧数、标量处理和树也与原文不同。因此不能机械替换 K 后称为原论文复现。当前数值比较应标注为 **ST-MTM reimplementation under the shared-input protocol**。上述参数未因绘图或此次核验而调整；原有数值结果全部保留。

## Tangaroa 的核验范围和修正

完整 201 帧结果已经有逐样本独立核验，核对了源体数据、树归属、原始样本 ID、TMTM 实际合并层级、明确记录的非二叉鞍点副本。此次重新核对这些核验文件与结果的哈希绑定，状态通过；未重跑 201 帧数值实验。

- 通用 `tmtm.PAPER_PRESETS` 中 4 个 Tangaroa 条目错误地写成 split tree，本次修正为作者工作空间的 join tree。
- 活跃的完整 201 帧管线本来就使用 join tree，因此旧结果没有改动。
- 原始 TMTM Algorithm 1 假设二叉；完整 Tangaroa 管线对真实多重鞍点使用同标量值的额外分隔副本，属于已经披露的扩展，不冒充作者二叉算法原样覆盖非二叉输入。
- 派生节点范围 36–186 与原论文 50–186 不同；这项输入复现限制仍然有效。
- ST-MTM 真实三维实验未完成，不宣称已经核验了不存在的三维基线结果。

## 可复现入口

从 RG-MTM 仓库运行：

```sh
PYTHONPATH=src:analysis:. ../.venv/bin/python experiments/baseline_audit/audit.py
PYTHONPATH=src:analysis:. ../.venv/bin/python -m unittest discover -s tests -p 'test_provenance.py' -v
PYTHONPATH=src:analysis:. ../.venv/bin/python tools/verify_rgmtm_migration.py
```

机器可读证据为 `algorithm_audit.json`；修正前后源哈希及原因在 `preset_correction.json`。新增来源账本能逐字节恢复修正前源码，旧数值结果的 177 项保护哈希继续通过核验。这是历史源码溯源，不表示用新源码重跑过旧实验。
