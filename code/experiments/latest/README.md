# 当前实验文件索引

`manifest.json` 由 `../../tools/build_latest_experiment_index.py` 从现存文件重新生成，记录代码、结果与图源的字节哈希，包含主实验、三维正式结果、Nucleon、Benzene二维重建、Cylinder及基线/案例证据。

当前投稿比较包含九个数据输入；五个二维时序278帧、Tangaroa201帧、Cylinder102帧合计七时序581帧，22静态切片单列。64帧镜像控制仍独立；六序列342帧属于历史冻结证据。新摘要见 `../../results/submission20261023/`。最终论文图号与母版见 `../../../paper/FIGURE_INDEX.json`。

在代码目录运行 `../../.venv/bin/python tools/build_latest_experiment_index.py --check` 验证索引。此操作不重跑实验。
