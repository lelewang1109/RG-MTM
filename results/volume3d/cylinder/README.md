# Cylinder：输入数据尚未完整取得

**真实数据实验未运行，没有生成方法指标或案例图。**

作者的公开输入为 102 帧速度体数据。本次从作者页面下载的 7z 在
324,782,331 字节处断开，而其 7z 头声明完整大小应为 542,415,447 字节。
完整性检查明确拒绝该文件。服务器对非零字节区间请求返回 HTTP 200 和文件开头，
没有执行续传；重试未取得超出既有文件前缀的新数据。浏览器下载及其他公开入口
也未得到可验证的完整输入。详见 [状态与尝试记录](status.json)。

不把 24 帧合成运动或 24 帧合成冲突案例当作 Cylinder 真实结果，也不将它们并入
原有六序列／342 帧主表。

## 准备好的流程

- 在源网格物理坐标计算 Q，再进行三维重采样。
- 固定 `[0,12)`、`[45,57)`、`[90,102)` 三组窗口，共 36 帧；窗口间重置跟踪和时间优化。
- 仅按全部帧的特征数量和二叉性选择预先规定的平滑尺度。
- 默认对照为 TMTM、三维 Hilbert/Morton、RG-MTM-P／R 和精确投影控制；ST-MTM 仅为显式可选的项目扩展诊断。
- 保存完整渲染、逐帧误差、放松阈值、三维与投影运动真值、方向诊断和独立核验。

取得完整的作者原始 `SquareCylinder.7z` 后，放入 `data/real/SquareCylinder/`，
从 RG-MTM 仓库根目录执行：

```sh
PYTHONPATH=src python experiments/volume3d/prepare.py
PYTHONPATH=src python experiments/volume3d/run.py --dataset cylinder
PYTHONPATH=src python experiments/volume3d/verify.py results/volume3d/cylinder
```

`prepare.py` 会先验证 7z 文件长度和头部 CRC，再解压；每个源速度帧及准备后的输入
另存 SHA-256。该入口目前通过合成 Amira 格式和解析导数检查，尚未获得真实完整包的
端到端验证。不得将“代码入口已实现”写成“真实案例已复现”。

作者数据页：<https://www.csc.kth.se/~weinkauf/notes/squarecylinder.html>。
公开输入与原论文 508 帧 Q 标量序列不同，取得后仍应标为公开版本补充实验。
