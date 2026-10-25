> 当前主线（2026-10-26）：[统一体系说明](../docs/统一体系贡献说明_20261025.md)。同模型实验为code/experiments/unified/，结果为unified20261025；旧framework20261025是独立连续前沿实验。原生方法不再作为“切换构造模式”的统一贡献。

# RG-MTM 代码与可复现证据

2026-10-25 的独立连续前沿实验入口：[预算化体系实验](experiments/framework/README.md)，实现为 `src/rgmtm/framework.py`，新结果为 `results/framework20261025/`。原 P/R、九数据与 3D 结果保留为单独构造模式的证据，不作为新 LP witness 的时序/运动测试。

本目录保留独立 Git 仓库。当前论文编辑入口在 [../paper](../paper/README.md)，`paper` 兼容链接指向同一当前 LaTeX 源码。旧 `publications/` 无图 PDF 已移出本次投稿目录。

| 目录 | 作用 |
|---|---|
| `src/rgmtm/` | RG-MTM-P/R、参考点、误差预算与 TMTM/ST-MTM/空间填充曲线基线 |
| `analysis/` | 理论证书、数据处理、指标及作图共用模块；存在互相导入，作为完整依赖集合保留 |
| `experiments/publication2027/` | 历史五个二维时序278帧运行入口（当前年度替换另见tools/run_pm25_annual.py）、64帧独立控制；原六序列342帧冻结证据标明为legacy，见 [复现说明](experiments/publication2027/REPRODUCING.md) |
| [results/submission20261023](results/submission20261023/README.md) | 当前投稿九数据统一指标、四张主表与细化配置；917时序帧和22静态切片分开计数 |
| `experiments/volume3d/` | 原网格 Tangaroa 201帧及三维合成补充研究 |
| `experiments/paper1_suite/` | Nucleon、二维重建 Benzene、三维方柱 Cylinder 的正式输入/实验/验证 |
| `experiments/baseline_audit/` | 基线设置及原始实现核对 |
| [results](results/README.md) | 正文/附录源结果、冻结快照和必要复现凭据 |
| [data](data/README.md) | 指向同一 `../data` 实体的本地链接与小型地理资产 |
| `tests/` | 已有数值、渲染、输入协议和三维测试 |
| `tmp/volume3d/` | 必要保留的固定版本 TTK 源码、编译环境与二进制；其余临时文件已归档 |
| `provenance/` | 可逆源代码变更及原始数值哈希的溯源记录 |

在本目录运行轻量复核：

```sh
PYTHONPATH=src ../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../.venv/bin/python experiments/publication2027/validate.py
PYTHONPATH=src ../../.venv/bin/python tools/verify_rgmtm_migration.py
```

这些检查验证已存证据与实现，不会重跑整套科学实验。当前主结果、冻结数值和必要旧图源各有不同角色；阅读 [研究证据边界](../docs/研究证据边界与补充研究.md)，避免把不同实验总体或旧试跑混为同一比较。
