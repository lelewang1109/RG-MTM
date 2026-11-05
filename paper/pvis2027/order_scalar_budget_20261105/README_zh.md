# 单栏预算图：只保留NROE与NMLE

用户指定删除事件ME，只保留正文已定义的两个指标，并将二维、三维结果压缩成单栏图。

- Figure 6：Storms、Wildfires、Ring，3行2列，左为NROE，右为NMLE。
- Figure 7：Tangaroa、Cylinder，2行2列，指标相同。
- 两图均在当前PDF第8页，替换旧位移五子图；Cylinder中央树展示图保留，自动编号为Figure 8、第9页。
- 全稿仍为10页（含现有中央树展示节），无正文尾句独立页或仅一个浮动图的空白页。

## 正文定义核对

NROE已有第4.1节式(6)：给定叶顺序后，最小非递减点布局所需的最坏参考位移除以画布长度；它忽略宽度，不是实际锚点位移。曲线使用逐帧NROE的时间平均。

NMLE已有第4.1节式(8)后的定义：实际固定标签合并误差d_top除以完整序列标量范围ΔF。曲线先逐帧求完整固定叶标签矩阵（含对角极值）的最大误差，再画跨帧平均与序列最坏值；不是叶对误差的算术平均。第5.1节已增加这两种统计口径并引用相应公式，图注也明确百分比和配置含义。

图使用共同的五种配置：Exact、ε=2%、5%、10%、20%，横轴为等距分类设置，连接的是五个实际运行结果，不声称连续精确前沿。数据集的输入、参考、宽度及QP权重未改动，原Balanced选择未重选。零预算Cylinder有ε0=1e-7数值 allowance，图注已说明。

## 数据与复现

metrics.csv只含dataset、epsilon、frames、NROE_mean、NMLE_mean、NMLE_max，共25个完整序列配置。科学来源为output/order_topology_motion_curves_20261105/data/metrics.csv的对应列，删列不重估或修改数值。ME及其事件数均不进入这两张图及本目录CSV。

从项目根目录运行：

```sh
.venv/bin/python paper/pvis2027/order_scalar_budget_20261105/plot.py
python3 paper/pvis2027/build_main.py
```

图件为../figures/anchor_planar_order_scalar.{pdf,png,svg}和anchor_volume_order_scalar.{pdf,png,svg}，采用论文Times New Roman、蓝/青绿/橙曲线、共用图例，边缘已裁紧。plot.py仅依赖numpy/matplotlib与本目录CSV，可独立重画。

旧含ME三指标图和旧位移权衡图保留在历史输出中，但当前正文不再引用。修改前正文和PDF保存在output/order_scalar_single_column_20261105/before/。
