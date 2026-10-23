# 第一篇论文的数据集补充入口

目标是补齐对应数据集，并明确数据维度和版本，不要求逐项复现第一篇表格的网格和帧数。
用户要求 Benzene 使用电势并已更正为二维切片序列，接受明确标注的电势重建版；Cylinder 使用三维方柱模拟。

- Ring：已有 40 帧实验。
- Storms：已有 ERA5 海平面气压异常实验，对应同类风暴案例，无需为表中尺寸重做一套。
- Tangaroa：已有原网格 201 帧三维时序实验。
- Nucleon：本目录新增作者 64×64 单帧输入实验。
- Cylinder：本目录新增原作者公开三维方柱 DNS，全部 102 帧，源速度为 192×64×48；先算三维 Q，再按作者子域保留 135×64×48。
- Benzene：新增 OPLS-AA 12-site 部分电荷电势重建，61×61、21 张二维 z 切片。作者原始文件仍缺失，重建不能冒充原始数据；z 不代表物理时间。

原来的 `volume3d/prepare.py` 是平滑和粗网格历史协议；这里的 `prepare_3d.py` 使用不同的原网格协议，单独保存结果，不覆盖旧实验。

从 RG-MTM 仓库根目录运行：

```sh
PYTHONPATH=src:. python -m experiments.paper1_suite.prepare nucleon
PYTHONPATH=src:. python -m experiments.paper1_suite.run nucleon
PYTHONPATH=src:. python -m experiments.paper1_suite.verify nucleon
PYTHONPATH=src:. python -m experiments.paper1_suite.report nucleon

# 如需代理，使用已经配置的 HTTPS_PROXY；下载器不修改系统网络设置。
PYTHONPATH=src:. python -m experiments.paper1_suite.acquire_cylinder
PYTHONPATH=src:. python -m experiments.paper1_suite.prepare_3d
PYTHONPATH=src:. python -m experiments.paper1_suite.run square-cylinder3d
PYTHONPATH=src:. python -m experiments.paper1_suite.verify square-cylinder3d
PYTHONPATH=src:. python -m experiments.paper1_suite.report square-cylinder3d

# 使用保存的公开 cube 原子头和 Yale BOSS 参数；不是密度转电势。
PYTHONPATH=src:. python -m experiments.paper1_suite.benzene_reconstructed prepare
PYTHONPATH=src:. python -m experiments.paper1_suite.benzene_reconstructed run
PYTHONPATH=src:. python -m experiments.paper1_suite.verify_benzene_reconstructed
PYTHONPATH=src:. python -m experiments.paper1_suite.report_benzene_reconstructed
```

大型输入、原始速度、完整树与地图保存在 Git 排除的 `data/real/`。
下载器可从旧不完整包复用前缀，但先验证镜像身份，严格检查 HTTP Range，最后校验完整 7z 并解压核对 CRC。
所有 102 帧均保持三维，未作空间降采样、平滑或按叶数删帧。Q 在完整源速度网格上用物理步长计算，随后裁剪；不先裁剪再求导。

`run.py` 复用已有的原网格树布局实现，比较 TMTM、RG-MTM-P、R 三档资格参数，固定 x 方向；次级凸目标仅在最多四个合法候选顺序上优化。
`verify.py` 逐值检查完整数组，并用独立 Amira 解析和旋转/应变张量范数公式重算全部三维 Q。
只有 `complete_verified` 才表示计算及独立核验完成。

Benzene 单独使用正号电势 join tree，不调用旧 `save_input` 的取负变换；`verify_benzene_reconstructed.py` 保留全数组地图检查并增加独立逐点 Coulomb 重算。模型参数、公开来源、输入和生成器哈希保存于 `model.json`，Yale 参数 PDF 和公开 cube 保存在该数据目录。当前目录已保留 `benzene-geometry-source.cube.xz`（仅作几何来源）和 `boss49.pdf` 两个冻结副本。全新准备时将这两个来源文件直接放入 `data/real/paper1_suite/benzene-potential-reconstructed2d/`，避免依赖已归档的电子密度试跑或临时目录。来源链接见结果中的 `model.json`。

`benzene-density` 与 `cylinder2d` 是旧试跑，**已排除**，不计入当前电势/三维方柱证据。
结果总入口：[数据覆盖与实验状态](../../results/paper1_suite/README.md)。
