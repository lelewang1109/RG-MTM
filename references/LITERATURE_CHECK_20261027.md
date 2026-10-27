# 文献查漏：合并树的一维表示与布局优化（2026-10-27）

**问题：** 除 TMTM、ST-MTM 之外，有没有别人也做了合并树一维表示的布局优化，或者给出了类似的整套数学计算？

**结论：** 检索范围内没有发现与本文重合的工作，即"以固定参考坐标为目标，对拓扑精确的地图给出位置下界并达到它"。最接近的是下面第 1、2 组，已全部写进新稿相关工作（`paper/pvis2027/refs.bib`）。

检索方式与范围：网络检索，并用 Crossref 核对元数据，覆盖关键词组合 merge tree map、contour tree drawing、topological landscape、ordered merge tree、one-sided tanglegram、storyline optimization、mental map。检索并不穷尽，只是没有找到重合的工作。

## 1. 合并树或等值线树的一维、平面布局（直接相关）

| 引用键 | 工作 | 与本文的关系 |
|---|---|---|
| Koepp:2023:TMTM（已有） | Temporal Merge Tree Maps | 原始的"时间 × 一维"地图，用贪心的子树重叠对齐 |
| STMTM:2026（已有） | Spatiotemporal Merge Tree Maps | 用优化得到受层次约束的一维骨架（保持特征间距离），再填充 |
| Oesterling:2013:TLP（新增） | Topological landscape profiles | 由合并树得到的一维剖面，没有时间和参考坐标 |
| Herick:2020:TCTL（新增） | 时间连贯的拓扑地形 | 使时变地形在时间上连贯，没有位置目标 |
| Heine:2011:DCT（新增） | 平面上绘制等值线树 | 树的绘制美学准则，不是一维剖面 |
| Weber:2007:TL、Beketayev:2012:GPTL（已有） | 拓扑地形、保几何的地形 | 地形隐喻，后者引入了邻近关系 |
| Kamakshidasan:2021:MM（新增） | Mergemaps | 认为剖面中的嵌套不易读，改用 treemap。这正是可读性质疑的出处，讨论部分已引用 |

## 2. 带叶序的合并树与距离（数学上最接近）

| 引用键 | 工作 | 与本文的关系 |
|---|---|---|
| Beurskens:2025:OMT（新增） | 有序合并树与 Fréchet 距离（SODA 2025） | 带叶序的合并树等价于一条一维曲线，与我们每帧的剖面是同一对象；他们定义了单调 interleaving 距离，没有讨论布局或参考位置 |
| Beurskens:2025:ParkView（已有） | ParkView | 可视化单调 interleaving |
| Munch:2019:LINF、Gasparovic:2024:IID（已有） | 标记 interleaving = ℓ∞-cophenetic | 我们拓扑误差的理论依据；定理条件仍待核对（D6） |
| Farach:1995:RM（已有） | ℓ∞ 超度量拟合 | 最优屏障的理论来源 |

## 3. 树约束下的叶序（组合优化）

| 引用键 | 工作 | 与本文的关系 |
|---|---|---|
| BarJoseph:2001:OLO（已有） | 最优叶序 | 目标是相邻相似度，不是位置 |
| Bulteau:2022:RT（已有） | 按给定叶序重排树 | 最接近的组合问题，但目标是计数或和，不是最大位移，也不考虑宽度 |
| Fernau:2010:CTC、Dobler:2026:BCT（新增）；Huson:2026:DOT（已有） | 单侧 tanglegram（一侧叶序固定） | 最小化交叉、块交叉或位移之和；没有闭式的最大位移下界 |

## 4. 时间 × 一维的其他布局（背景）

| 引用键 | 工作 | 与本文的关系 |
|---|---|---|
| Tanahashi:2012:Storyline、Dobler:2025:Wiggle（新增）；Liu:2013:SF（已有） | Storyline 布局 | 部分用二次规划，但实体没有固定坐标，也没有嵌套 |
| Archambault:2011:AMM（新增） | 动态图的心理地图 | 说明静态总结与稳定性的动机 |
| Heine:2016:Survey（新增） | 拓扑可视化综述 | 背景 |
| Li:2023:SMT（新增，未在正文引用） | 合并树草图 | 压缩大量合并树，与布局无关 |

## 尚未处理

- Köpp 的博士论文（把动态层次结构表示为堆叠的一维图）。检索中提到，但没有核实出版信息，暂未加入。
- Geniesse 等人的 2024 年 arXiv 工作（损失函数地形剖面）。属于外围文献，暂未加入。
