# Hilbert / Morton 方向验证寻优

默认是代码约定的固定网格遍历，并非估计的物理方向。x 为列，y 为行；从(0,0)开始。Morton 位交错以 x 作为低位；Hilbert 固定递归方向，其第一步随二次幂网格层级改变。默认不旋转、不镜像、不反转。

## 搜索及选择

每个方法/数据集枚举4个数组旋转×2个左右镜像×2个遍历方向，共16个名义候选；按实际网格置换哈希去重。矩形旋转后按新形状生成曲线，再映射回原样本ID。所有候选保存。

使用最初25%时间窗口，J=0.5 NPE_norm+0.5 SNS_norm；对同方法、同数据集全部不同候选的验证指标作min–max归一化。常量项贡献0，若SNS完全缺失则不作此选择。J在1e-12内相同时按固定枚举顺序选取。选择保存到selection.json后才读取后75%时间窗口。没有改数据、p、q、画布L和指标定义。

这些结果属于方向参数空间中的验证综合最优，不声称每个指标都达到全局最优。单指标验证最佳另存CSV，不将不同配置成绩拼接成一个方法。完整序列此前已观察，因此不能宣称全新盲测。

## 完整序列结果

| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ | 配置 |
|---|---|---:|---:|---:|---|
| Gaussian | Hilbert tuned | 0.111728 | 0.671875 | 0.258396 | rot0_mirror0_reverse1 |
| Gaussian | Morton tuned | 0.053404 | 0.875000 | 0.145384 | rot90_mirror1_reverse0 |
| Ring | Hilbert tuned | 0.195292 | 0.738095 | 0.116959 | rot90_mirror0_reverse1 |
| Ring | Morton tuned | 0.168636 | 0.666667 | 0.080654 | rot0_mirror1_reverse1 |
| Wildfires | Hilbert tuned | 0.153166 | 0.861190 | 0.192959 | rot270_mirror0_reverse1 |
| Wildfires | Morton tuned | 0.130364 | 0.875784 | 0.156027 | rot0_mirror0_reverse0 |
| Storms | Hilbert tuned | 0.100737 | 0.783550 | 0.248398 | rot270_mirror0_reverse0 |
| Storms | Morton tuned | 0.076350 | 0.854978 | 0.217438 | rot90_mirror1_reverse1 |

## 后75%时间窗口

| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ |
|---|---|---:|---:|---:|
| Gaussian | Hilbert tuned | 0.138654 | 0.583333 | 0.288202 |
| Gaussian | Morton tuned | 0.049895 | 0.916667 | 0.145384 |
| Ring | Hilbert tuned | 0.208311 | 0.738095 | 0.133537 |
| Ring | Morton tuned | 0.179878 | 0.666667 | 0.091035 |
| Wildfires | Hilbert tuned | 0.174845 | 0.864615 | 0.184943 |
| Wildfires | Morton tuned | 0.154042 | 0.878462 | 0.155805 |
| Storms | Hilbert tuned | 0.115368 | 0.753968 | 0.253563 |
| Storms | Morton tuned | 0.082142 | 0.920635 | 0.221716 |

## 解读与限制

- 多数配置的NPE较默认方向降低；Wildfires Morton选择原默认配置。
- Ring两方法和Gaussian Morton出现SNS变差，说明综合评分存在取舍；Ring验证窗口只有2帧SNS有效、没有TW有效帧，方向选择的泛化证据尤其弱。
- 四数据集TW有效帧仍为64/64、1/40、4/32、11/744，不能将少数有效帧成绩解释为全序列邻域保持。
- 全部配置沿曲线全网格序号映射到统一固定物理画布并取整；不对每帧拟合缩放、平移。无特征显示坐标重合，但不保证拓扑或有限特征宽度可行性。
- 调优后Balanced仍在四个数据集的NPE和SNS上优于这两种综合选定曲线，TW也较高；这不抹去默认Ring Hilbert在SNS/TW上的更好结果，两者应同时保留。
- 不修改论文主表。后续正式比较应预先冻结基线选择协议，再在独立数据上检验。

## 复现

```sh
.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/tune.py
.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/report_tuned.py
```
