# RG-MTM代码与可复现证据

完整仓库的 [总README](../README.md) 和 [目录导读](../docs/DIRECTORY_GUIDE.md) 是阅读入口。本目录负责方法实现、实验与保存结果；当前论文在 [paper/](../paper/README.md)。

## 当前入口

| 目录或文件 | 职责 |
|---|---|
| `src/rgmtm/unified.py` | 共同四项QP、候选过滤、时间目标与共享布局 |
| `src/rgmtm/framework.py` | 连续合并代价、位置可行性与预算工具 |
| `src/rgmtm/error_budget.py` | 区间约束、固定序与预算布局基础 |
| `src/rgmtm/baselines/` | 独立TMTM/ST-MTM/空间填充基线 |
| [experiments/unified](experiments/unified/README.md) | 614帧×5设置的共同模型实验 |
| [experiments/framework](experiments/framework/README.md) | 独立连续前沿、反向查询与603/11覆盖 |
| [experiments/stmtm_completion](experiments/stmtm_completion/README.md) | 四组共325个新增ST-MTM布局、当前九数据总表 |
| `analysis/` | 证书、处理、指标与作图共用模块 |
| `results/` | 带实验身份的保存输出与核验记录 |
| `tests/` | 数值、渲染与输入协议测试 |
| `provenance/` | 冻结哈希、历史源码身份与迁移记录 |
| `data/` | 指向仓库data目录的相对链接和小型地理资产 |

既有P/R、三维、静态和historical运行保留为不同证据。`submission20261023` 与 `publication2027` 是旧快照身份，不代表当前共同模型或补全表重新运行。

## 安装和核验

先按根README安装 `code/pyproject.toml`。从仓库根目录执行：

```sh
PYTHONPATH=code/src .venv/bin/python -m unittest discover -s code/tests -v
.venv/bin/python paper/scripts/verify_unified_revision.py --numerical-only
```

四组新增ST-MTM另需 `experiments/stmtm_completion/requirements.txt`；其验证脚本独立读取完整剖面、输入清单及坐标。原始体数据的获取与计算可能需要TTK等额外依赖。保存结果核验不是从头重跑全部实验。

## 结果选择

当前总表：`results/stmtm_completion20261026/unified_metrics.csv`。共同模型实验：`results/unified20261025/`。独立前沿：`results/framework20261025/`。详细对应见 [results/README](results/README.md)。

历史表生成器的 `--check` 同时绑定旧版论文表，在当前稿上不直接运行。GitHub使用 `python tools/verify_historical_snapshot.py` 重建历史数值摘要并核验冻结文件；不使用旧导出覆盖当前补全表。当前论文修改和图件同步见 [操作流程](../docs/EDITING_AND_REPRODUCING.md)。
