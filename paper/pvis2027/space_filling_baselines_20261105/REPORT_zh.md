# Hilbert / Morton 补充实验

使用四数据集 ratio-p 冻结缓存；不重新提树、不修改算法、不调节曲线方向或根据结果选择配置。数据输入为此前明确标注的重建输入。

| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ | TW 有效帧 |
|---|---|---:|---:|---:|---:|
| Gaussian | Hilbert | 0.111728 | 0.671875 | 0.755715 | 64/64 |
| Gaussian | Morton | 0.039269 | 0.833333 | 0.735935 | 64/64 |
| Ring | Hilbert | 0.125153 | 0.904762 | 0.594128 | 1/40 |
| Ring | Morton | 0.148924 | 0.761905 | 0.603278 | 1/40 |
| Wildfires | Hilbert | 0.188268 | 0.830332 | 0.364069 | 4/32 |
| Wildfires | Morton | 0.130364 | 0.875784 | 0.156027 | 4/32 |
| Storms | Hilbert | 0.128970 | 0.740260 | 0.370452 | 11/744 |
| Storms | Morton | 0.118007 | 0.725108 | 0.346806 | 11/744 |

## 协议与核验

- 复用项目 `space_filling.py` 的标准固定 Hilbert/Morton 网格遍历；矩形网格嵌入最小二次幂正方形后删除域外位置，保留域内完整置换。
- 极值使用与 AnchorMTM 完全相同的原始网格样本 ID。沿曲线的全网格累计序号线性映射到固定画布，再按原 L 取整；没有每帧重排为等间距特征序号，也没有旋转、反射寻优或逐帧对齐。
- SNS/TW 的原空间点仍为既有特征支持域质心，NPE 的目标仍为既有固定物理投影 q；完全复用评价函数。NPE 是逐帧最大归一误差的时间平均。
- TW 使用 k=(1,3,5,3)，仅 0<k<n/2 有效；距离并列沿用项目稳定排序（原叶 ID 次序）。全部方法使用共同有效帧；缺失不填零。
- 四数据集分别先检查前8帧，再完整计算64/40/32/744帧；逐帧成功复现既有 Exact SNS、TW、NPE。SNS 另用独立向量公式交叉检查。
- 两种曲线所有帧均无极值画布坐标重合，无越界。这不等于通过拓扑保持或有限宽度布局检查：曲线是样本域线性化参照，不是完整合并树映射。
- 固定曲线坐标和固定物理投影轴含义不同，NPE 衡量的是其对同一物理参考的偏离；不能从较高 NPE 推导其一般可视化质量较差。

## 结果解读

- AnchorMTM Balanced 的 NPE 在四个数据集均低于两种曲线。
- SNS 并非始终占优：Ring 的 Hilbert SNS=0.125153，低于 Balanced 约0.1334；其 TW=0.904762 也高于 Balanced 0.857143，但 TW 只有1帧，不能推广成全序列结论。
- Gaussian、Wildfires、Storms 上，两种曲线的 SNS/TW 均不及当前 Balanced；仍需留意 Wildfires/Storms 的 TW 仅4/11帧。
- 合并 CSV 中 TMTM/ST-MTM 的 SNS/TW 保持原文引用，NPE 保持本地测量；作者输入及 TW 覆盖未确认相同，不能称为严格同输入的跨来源排名。

## 复现

在项目根目录执行：

```sh
.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/evaluate.py --pilot
.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/evaluate.py
.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/report.py
```

依赖既有本地 fields.npy、coordinates.npy、trees 和 Exact 缓存，GitHub 精简包不含这些大体积输入。此轮未修改论文主表。
