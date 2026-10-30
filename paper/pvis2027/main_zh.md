> 2026-10-30 最新二维/三维 PPT 图已接入：首图为 744 小时 Storms，正文图 11 为 Vortex；旧半日 Storms 图与 OLR/Ring 图位于附录。下方新增段落已更新，历史段落中的旧图号以 main.tex 自动引用为准。

# 正文逐句中英对照

> 对应 `main.tex`（2026-10-27 三维补充版，正文 9 页以内、参考文献 2 页以内）。
>
> - 按论文顺序逐句对照：每句英文（EN）后接中文（中）。
> - 公式保留 LaTeX 写法；引文编号省略，用"[引]"标出。
> - 图表标题放在它们在正文中出现的位置。
> - 术语统一译法：merge tree 合并树；merge level 合并层级；barrier 屏障；reference 参考坐标；displacement 位移；order error 排序误差；budget 预算；certified 有保证的；bound 下界。

---

## 标题

- EN: Position-Faithful Merge Tree Maps: Certified Bounds and Optimal Layouts
- 中：位置忠实的合并树地图：有保证的下界与最优布局

## 摘要

- EN: Merge tree maps summarize a time-varying scalar field in one image: every time step becomes a one-dimensional profile whose basins are the features of the field, stacked along time.
- 中：合并树地图用一张图概括一个随时间变化的标量场：每个时间步变成一条一维剖面，剖面中的"盆地"就是场中的特征，这些剖面沿时间依次排开。
- EN: Existing maps keep the merge hierarchy and temporal coherence, but the axis then carries little spatial meaning, so a storm in the west may be drawn east of one in the east.
- 中：已有的地图保住了合并层次和时间连贯性，但纵轴因此几乎没有空间含义，于是西边的风暴可能被画在东边那场风暴的东边。
- EN: We ask how close such a map can stay to a fixed spatial reference, such as longitude, without misrepresenting the hierarchy.
- 中：我们要问：在不歪曲层次的前提下，这样的地图能多贴近一个固定的空间参考（例如经度）？
- EN: We prove a closed-form lower bound on the order error of every map that preserves the merge tree, which holds for every method including TMTM and ST-MTM, a width-aware bound on the worst displacement for maps that place features as intervals, as ST-MTM and our method do, and chain-aware bounds for maps whose merge levels may err by a declared budget $\varepsilon$.
- 中：我们证明了三类下界：一是任何保持合并树的地图的排序误差都有一个闭式下界，它对包括 TMTM 和 ST-MTM 在内的所有方法成立；二是对于以区间形式摆放特征的地图（ST-MTM 和我们的方法都是如此），最坏位移有一个宽度感知的下界；三是对于合并层级允许有声明预算 $\varepsilon$ 以内误差的地图，有链式下界。
- EN: We give layouts that attain them: a midpoint ordering, a width-aware search, and a budgeted ordering whose exact merge-level error is checked, combined with optimal barriers and a capped quadratic placement.
- 中：我们给出能达到这些下界的布局：中点排序、宽度感知搜索，以及精确检查合并层级误差的预算内排序，再结合最优屏障和带上限的二次规划摆位。
- EN: The bounds do not depend on the dimension of the domain.
- 中：这些下界与数据所在区域的维度无关。
- EN: A cross-method comparison on 917 frames from five planar and two volumetric sequences shows that most of the order error of existing maps is avoidable, that sorting by reference alone changes merge levels by up to 59\% of the scalar range, and that our exact maps lower the motion error of both previous methods on every sequence, while ST-MTM keeps the better distance preservation.
- 中：在 5 组平面序列和 2 组三维序列共 917 帧上的横向比较表明：已有地图的排序误差大部分是可以避免的；只按参考坐标排序会使合并层级的改变最高达到数值范围的 59%；我们的拓扑精确地图在每一组序列上都降低了两种已有方法的运动误差，而 ST-MTM 在距离保持上仍然更好。
- EN: Each of our maps reports two certified numbers, how far it moves features and how far it changes the hierarchy, and marks every changed merge on the map.
- 中：我们的每张地图都报告两个有保证的数——特征被移动了多远、层次被改变了多少——并在图上标出每一处被改动的合并。

**关键词**
- EN: Merge trees, temporal scalar fields, topology-based visualization, one-dimensional layout, lower bounds.
- 中：合并树，时变标量场，基于拓扑的可视化，一维布局，下界。

## 图 1（首图，2026-10-30 最终二维 PPT）

- EN: Hourly Storms: 744 sea-level-pressure anomaly fields from December 1999. (a) Full map at $\varepsilon=5\%$; the box selects $t=212$--239. (b) Five spatial snapshots with the fixed reference axis $q$ and exact-layout positions. (c) The same tracked minima A (green) and B (magenta) at budgets $0,1,2,3,5\%$; diamonds mark references at the selected step. Labels $A_{ij},B_{ij}$ index parameter column $i$ and sampled time $j$. (d) Complete displayed trees at $t=236$: structural depths $4,4,3,3,2$. Roots are top-aligned; vertical distance counts levels below the root, not pressure. This hourly diagnostic is separate from the half-day Storms benchmark.
- 中：逐小时 Storms：1999 年 12 月的 744 个海平面气压异常场。(a) ε=5% 的完整地图，框出 t=212–239 的局部时间窗。(b) 五个空间快照及固定参考轴 q，与拓扑精确布局中的位置对应。(c) ε 为 0%、1%、2%、3%、5% 时同一组绿色 A、紫红色 B 轨迹；菱形为选定帧的参考位置。编号第一位表示参数列，第二位表示采样时间。(d) t=236 的完整显示树，结构深度依次为 4、4、3、3、2。树根顶部对齐，纵轴表示根下方层数，不表示气压。此逐小时诊断序列独立于半日 Storms 横评序列。

## 1 引言

- EN: Static summaries of time-varying scalar fields show a whole sequence at once, without relying on memory across animation frames [引].
- 中：时变标量场的静态总结能一次展示整个序列，不需要读者在动画帧之间靠记忆比较 [引]。
- EN: Merge tree maps build such summaries from topology [引].
- 中：合并树地图从拓扑出发构建这种总结 [引]。
- EN: At each time step the merge tree of the field is linearized into a one-dimensional profile whose basins are the extrema and whose barriers are their merge levels; the profiles are stacked along time, so every feature becomes a band and the nesting of bands shows how features connect.
- 中：在每个时间步，场的合并树被线性化为一条一维剖面，剖面的盆地是极值，屏障是它们的合并层级；剖面沿时间堆叠，于是每个特征成为一条带，带的嵌套显示特征之间如何相连。

- EN: The cost of this compression is the meaning of the axis.
- 中：这种压缩的代价是纵轴的含义。
- EN: Temporal Merge Tree Maps (TMTM) order features by a tree traversal aligned across time [引]; Spatiotemporal Merge Tree Maps (ST-MTM) add pairwise distances [引].
- 中：时序合并树地图（TMTM）按跨时间对齐的树遍历来排列特征 [引]；时空合并树地图（ST-MTM）又加入了特征两两之间的距离 [引]。
- EN: Neither ties a feature to a coordinate the analyst already knows, and in Fig. 1b five pressure systems spread over the whole North Atlantic are drawn within a fifth of the axis.
- 中：两者都没有把特征绑定到分析者已经熟悉的坐标上；在图 1b 中，分布在整个北大西洋的五个气压系统被画在了不到轴长五分之一的范围内。
- EN: Hovmöller diagrams make the opposite choice [引]: the axis is longitude, which is immediately readable, but the hierarchy is lost.
- 中：Hovmöller 图做了相反的选择 [引]：纵轴就是经度，一看就懂，但层次信息丢失了。
- EN: This paper asks how close a merge tree map can come to both.
- 中：本文要问的是：合并树地图能在多大程度上兼顾两者。

- EN: The question has a precise answer.
- 中：这个问题有精确的答案。
- EN: If the merge tree is kept intact, every subtree occupies one contiguous block of the axis; two sibling subtrees whose reference ranges overlap cannot both stay at their references.
- 中：如果合并树保持完整，每棵子树都占据轴上一段连续的区块；参考坐标范围相互重叠的两棵兄弟子树，不可能都待在各自的参考位置上。
- EN: We show that this conflict determines the unavoidable displacement in closed form, that it is attainable, and that most of the displacement of existing maps lies above it (Fig. 1c).
- 中：我们证明，这种冲突以闭式形式决定了不可避免的位移，这个位移是可以达到的，而且已有地图的位移大部分都高于它（图 1c）。
- EN: When the analyst accepts a bounded change of merge levels, the same reasoning bounds how much position can be recovered, and the change is shown on the map.
- 中：如果分析者接受合并层级有上限内的改变，同样的推理可以给出能挽回多少位置的界，并且改动会显示在图上。

- EN: Our contributions are:
- 中：我们的贡献如下：
- EN: **Certified lower bounds** on the displacement of any merge tree map that keeps the hierarchy: a closed-form bound on the order error, valid for every method including TMTM and ST-MTM; a width-aware bound on the worst displacement for interval layouts such as ST-MTM and ours; and chain-aware bounds for maps with a merge-level budget $\varepsilon$ (Sect. 5). In 3-D, the order bound ranks candidate reference directions before any map is drawn.
- 中：**有保证的下界**，针对任何保持层次的合并树地图的位移：排序误差的闭式下界，对包括 TMTM 和 ST-MTM 在内的所有方法成立；最坏位移的宽度感知下界，适用于 ST-MTM 和本文这类区间布局；以及带合并层级预算 $\varepsilon$ 的地图的链式下界（第 5 节）。在三维数据上，排序下界可以在画任何地图之前，对候选的参考方向进行排序比较。
- EN: **Layouts that attain them**: midpoint ordering, a width-aware search and a budgeted ordering with exact merge-cost checks, combined with optimal barriers and a capped quadratic placement; every map reports its position and merge-level errors and marks changed merges (Sect. 6).
- 中：**达到下界的布局**：中点排序、宽度感知搜索，以及精确检查合并代价的预算内排序，结合最优屏障和带上限的二次规划摆位；每张地图都报告自己的位置误差和合并层级误差，并标出被改动的合并（第 6 节）。
- EN: **One formulation** with explicit position and topology budgets, in which TMTM and ST-MTM are exact-topology instances; given their own leaf orders, their layouts are reproduced exactly (Sect. 3).
- 中：**一个统一表述**，显式包含位置预算和拓扑预算，TMTM 和 ST-MTM 是其中拓扑精确的实例；给定它们自己的叶序，它们的布局可以被精确复现（第 3 节）。
- EN: **A cross-method comparison** of five methods on 917 frames from seven sequences, including two volumetric ones, a study of the reference direction in 3-D, and a case study with error disclosure (Sect. 7).
- 中：**横向比较**：5 种方法在 7 组序列（含 2 组三维序列）共 917 帧上的比较，一项三维参考方向的研究，以及一个带误差披露的案例研究（第 7 节）。
- EN: We study faithfulness, not readability; a perceptual study is future work.
- 中：我们研究的是忠实度，而不是可读性；感知研究留待后续工作。

## 2 相关工作

**图 2**
- EN: Existing merge tree map pipelines on a shared augmented merge tree.
- 中：已有合并树地图的处理流程，作用于同一棵增广合并树。
- EN: (a) TMTM linearizes each tree and aligns adjacent steps by subtree overlap.
- 中：(a) TMTM 将每棵树线性化，并按子树重叠对齐相邻时间步。
- EN: (b) ST-MTM orders leaves by spatial proximity, places a one-dimensional skeleton and fills it hierarchically.
- 中：(b) ST-MTM 按空间邻近对叶子排序，放置一维骨架，再按层次填充。
- EN: Neither uses an absolute spatial reference.
- 中：两者都不使用绝对的空间参考。

**空间与时间的线性化**
- EN: Space–time cubes and their flattenings organize temporal visualization [引].
- 中：时空立方体及其展平形式组织了时序可视化 [引]。
- EN: Hovmöller diagrams keep one spatial coordinate [引]; space-filling curves, geographic orderings and data-driven projections linearize the whole domain [引], and MotionRugs and related summaries order moving entities [引].
- 中：Hovmöller 图保留一个空间坐标 [引]；空间填充曲线、地理排序和数据驱动的投影把整个区域线性化 [引]；MotionRugs 及相关的总结方法则对移动实体排序 [引]。
- EN: None of them represents the merge hierarchy.
- 中：它们都不表示合并层次。
- EN: Storyline layouts solve a related time×1D problem, minimizing crossings and wiggles, partly by quadratic programming [引]; their entities have neither a fixed coordinate nor nesting.
- 中：故事线布局解决的是相关的"时间 × 一维"问题，最小化交叉和弯折，部分借助二次规划 [引]；但其中的实体既没有固定坐标，也没有嵌套。

**合并树与等值线树的绘制**
- EN: Topology-based visualization is surveyed by Heine et al. [引].
- 中：Heine 等人综述了基于拓扑的可视化 [引]。
- EN: Contour trees have been drawn in the plane [引], as terrains [引], with geometry-preserving terrain layouts [引], and as one-dimensional landscape profiles [引], which Herick et al. make temporally coherent [引].
- 中：等值线树已有多种画法：在平面上绘制 [引]、画成地形 [引]、使用保几何的地形布局 [引]，以及画成一维地形剖面 [引]；Herick 等人使后者在时间上保持连贯 [引]。
- EN: Mergemaps argue that nesting is hard to read in profiles and use treemaps [引].
- 中：Mergemaps 认为剖面中的嵌套难以阅读，因而改用树图（treemap）[引]。
- EN: TMTM introduced the time×1D merge tree map [引] and ST-MTM made it geometry-aware [引] (Fig. 2).
- 中：TMTM 提出了"时间 × 一维"的合并树地图 [引]，ST-MTM 使其感知几何 [引]（图 2）。
- EN: Tracking graphs show feature evolution without a spatial axis [引].
- 中：追踪图展示特征的演化，但没有空间轴 [引]。
- EN: We keep the TMTM/ST-MTM map and its renderer and change what the layout optimizes; our bounds apply to all such profile layouts.
- 中：我们保留 TMTM/ST-MTM 的地图形式和渲染器，只改变布局所优化的目标；我们的下界适用于所有这类剖面布局。

**树的叶子排序**
- EN: Optimal leaf ordering selects one of the $2^{n-1}$ tree-consistent orders to minimize adjacent dissimilarity [引].
- 中：最优叶序从 $2^{n-1}$ 种与树一致的叶序中选出一种，使相邻叶子的不相似度最小 [引]。
- EN: Closest to our question are reordering a tree towards a given leaf order [引] and one-sided tanglegrams [引]; geophylogenies combine tree constraints with map positions [引].
- 中：与我们的问题最接近的是：按给定叶序重排一棵树 [引]，以及单侧 tanglegram [引]；地理系统发育图把树约束与地图位置结合起来 [引]。
- EN: These works count inversions, crossings or summed displacement; minimizing the number of inversions against a target order is NP-complete for trees of unbounded degree [引].
- 中：这些工作统计的是逆序数、交叉数或位移之和；对于度数不受限的树，相对目标顺序最小化逆序个数是 NP 完全问题 [引]。
- EN: We measure the *maximum* displacement in reference units, which has a closed form, and extend it to interval widths, anchor slack and controlled violations of the tree.
- 中：我们度量的是以参考坐标为单位的**最大**位移，它有闭式解；我们还把它推广到区间宽度、锚点松弛以及受控地违反树结构的情形。

**有序合并树与距离**
- EN: A merge tree with a leaf order is equivalent to a one-dimensional curve; Beurskens et al. define a monotone interleaving distance for such ordered merge trees [引], visualized by ParkView [引].
- 中：带叶序的合并树等价于一条一维曲线；Beurskens 等人为这种有序合并树定义了单调 interleaving 距离 [引]，ParkView 对其进行了可视化 [引]。
- EN: For labelled merge trees, the $\ell_\infty$ distance between cophenetic matrices is an interleaving distance [引], used as the labelled interleaving distance [引]; it bounds the unlabelled interleaving distance [引], which bounds the bottleneck distance of persistence diagrams [引].
- 中：对于带标签的合并树，cophenetic 矩阵之间的 $\ell_\infty$ 距离是一种 interleaving 距离 [引]，并被用作带标签的 interleaving 距离 [引]；它是不带标签的 interleaving 距离的上界 [引]，而后者又是持续图 bottleneck 距离的上界 [引]。
- EN: Geometry-aware and Wasserstein comparisons extend these distances [引].
- 中：几何感知的比较和 Wasserstein 比较扩展了这些距离 [引]。
- EN: Fitting an ultrametric under $\ell_\infty$ error has a closed form [引]; our optimal barriers are such a fit under a fixed leaf order.
- 中：在 $\ell_\infty$ 误差下拟合超度量有闭式解 [引]；我们的最优屏障就是固定叶序下的这种拟合。

## 3 背景与问题

**图 3**
- EN: Our pipeline on one Storms step (17 Dec 1999, 12 UTC).
- 中：我们的流程在 Storms 某一时间步（1999 年 12 月 17 日 12 时 UTC）上的演示。
- EN: (a) Extrema and references.
- 中：(a) 极值与参考坐标。
- EN: (b) Merge tree; the root's children $\{C\}$ and $\{A,B,D,E\}$ have overlapping reference hulls (bars below), which certifies $\nu^*=20.6\%$ for every exact map.
- 中：(b) 合并树；根节点的两个子树 $\{C\}$ 和 $\{A,B,D,E\}$ 的参考范围相互重叠（下方的条），这保证了任何拓扑精确的地图都有 $\nu^*=20.6\%$。
- EN: (c) Leaf orders at $\varepsilon=0$ and $10\%$ with their exact merge cost $\delta^*$.
- 中：(c) $\varepsilon=0$ 和 $10\%$ 时的叶序，以及各自的精确合并代价 $\delta^*$。
- EN: (d) Profile with optimal barriers (ticks; orange where the merge level was changed), intervals (bars), anchors (dots) and references (triangles).
- 中：(d) 剖面，含最优屏障（短线；合并层级被改动处为橙色）、区间（条）、锚点（圆点）和参考坐标（三角形）。
- EN: (e) Map around this step with marked barriers and the per-step merge error.
- 中：(e) 该时间步附近的地图，标出被改动的屏障，并附逐步的合并误差。

**合并树地图**
- EN: A sequence of scalar fields $f_t$ on a two- or three-dimensional domain gives, per time step, a merge tree $T_t$ of its sublevel (or superlevel) sets.
- 中：定义在二维或三维区域上的一列标量场 $f_t$，在每个时间步给出其下水平集（或上水平集）的合并树 $T_t$。
- EN: Its leaves are the $n_t$ retained extrema; $V_{ij}$ is the level at which leaves $i$ and $j$ merge, the value of $\mathrm{lca}(i,j)$, and $\Delta_F$ is the scalar range.
- 中：它的叶子是保留下来的 $n_t$ 个极值；$V_{ij}$ 是叶子 $i$ 和 $j$ 合并的层级，即 $\mathrm{lca}(i,j)$ 处的值；$\Delta_F$ 是数值范围。
- EN: Features are matched across time by support overlap.
- 中：特征在时间上的对应由支撑区域的重叠确定。
- EN: Figure 2 shows the two existing pipelines.
- 中：图 2 展示了两种已有流程。
- EN: TMTM linearizes the augmented merge tree by a depth-first traversal and flips subtrees greedily to maximize the overlap of subtree intervals between adjacent steps [引].
- 中：TMTM 用深度优先遍历把增广合并树线性化，并贪心地翻转子树，使相邻时间步之间子树区间的重叠最大 [引]。
- EN: ST-MTM orders leaves by spatial proximity, places a one-dimensional skeleton by a quadratic program on pairwise distances, and fills it hierarchically [引].
- 中：ST-MTM 按空间邻近对叶子排序，用基于两两距离的二次规划放置一维骨架，再按层次填充 [引]。
- EN: A map frame is $M_t=(\pi_t,x_t,\psi_t)$: a leaf order, anchor positions and a profile $\psi_t:[0,L]\to\mathbb{R}$.
- 中：一帧地图是 $M_t=(\pi_t,x_t,\psi_t)$：一个叶序、各锚点位置，以及一条剖面 $\psi_t:[0,L]\to\mathbb{R}$。
- EN: As in ST-MTM, leaf $i$ occupies an interval of width $W_i=s\,m_i$ proportional to its support measure $m_i$, intervals are separated by a gap $g$, and the anchor (the basin extremum) lies within $H_i=\rho W_i/2$ of the interval centre.
- 中：与 ST-MTM 一样，叶子 $i$ 占据一段宽度为 $W_i=s\,m_i$ 的区间，宽度与其支撑区域大小 $m_i$ 成正比；区间之间隔开间距 $g$；锚点（盆地的极值点）位于区间中心 $H_i=\rho W_i/2$ 的范围内。

**参考坐标**
- EN: Each leaf has a reference coordinate $q_i\in[0,L]$, the projection of its location onto a fixed world direction, constant over time; $L$ is the canvas length in world units.
- 中：每个叶子有一个参考坐标 $q_i\in[0,L]$，即它的位置在一个固定的世界方向上的投影，这个方向不随时间变化；$L$ 是以世界单位计的画布长度。
- EN: On Storms the direction is west–east (Fig. 1a); on Tangaroa it is the principal direction of matched feature motion, and on Cylinder the streamwise axis.
- 中：在 Storms 上，这个方向是西—东方向（图 1a）；在 Tangaroa 上，是对应特征运动的主方向；在 Cylinder 上，是流向坐标轴。
- EN: Any fixed one-dimensional quantity, such as distance to a site, can serve.
- 中：任何固定的一维量都可以充当参考，例如到某个地点的距离。
- EN: Nothing below depends on the dimension of the domain: the bounds use only the tree, the references and the widths.
- 中：下文的一切都不依赖于区域的维度：各个下界只用到树、参考坐标和宽度。

**误差**
- EN: *Position*: the displacement $|x_i-q_i|/L$, pooled over leaves and frames ($E_{\mathrm{pool}}$) and its maximum ($E_\infty$).
- 中：*位置*：位移 $|x_i-q_i|/L$，对所有叶子和帧汇总后的平均值（$E_{\mathrm{pool}}$）及其最大值（$E_\infty$）。
- EN: *Order*: the reference-order error of a leaf order, [公式 (1)]
- 中：*排序*：一个叶序相对参考坐标的排序误差，[公式 (1)]
  $$\mathrm{NROE}(\pi)=\frac{1}{2L}\max_{k}\Big(\max_{j\le k} q_{\pi(j)}-q_{\pi(k)}\Big),$$
- EN: the smallest worst displacement of any monotone placement in that order with zero widths; it is scale-free and therefore also compares maps without a world canvas.
- 中：它等于在该叶序下、宽度为零时，任何单调摆放所能达到的最小最坏位移；它与尺度无关，因此也可以用来比较没有世界画布的地图。
- EN: *Topology*: in the profile, leaves $i,j$ merge at the highest value of $\psi_t$ between their anchors, $V^\psi_{ij}$, and [公式 (2)]
- 中：*拓扑*：在剖面中，叶子 $i,j$ 在两锚点之间 $\psi_t$ 的最高值处合并，记为 $V^\psi_{ij}$；并且 [公式 (2)]
  $$d_{\mathrm{top}}(\psi_t,T_t)=\max_{i,j}\big|V^{\psi}_{ij}-V_{ij}\big|,\qquad \mathrm{NMLE}=d_{\mathrm{top}}/\Delta_F .$$
- EN: Labelling every extremum and its anchor by its feature, $V$ and $V^\psi$ are the cophenetic matrices of two labelled merge trees (diagonal $V_{ii}=f(i)$, which the profile keeps), so $d_{\mathrm{top}}$ is their labelled interleaving distance [引].
- 中：用所属特征给每个极值及其锚点打上标签，$V$ 和 $V^\psi$ 就是两棵带标签合并树的 cophenetic 矩阵（对角元 $V_{ii}=f(i)$，剖面保持不变），因此 $d_{\mathrm{top}}$ 就是它们的带标签 interleaving 距离 [引]。
- EN: It requires the labels to cover all leaves, i.e., no unlabelled extremum in the profile; every rendered column we checked satisfies this.
- 中：这要求标签覆盖所有叶子，即剖面中不能有不带标签的极值；我们检查过的每一列渲染结果都满足这一点。
- EN: Hence $d_B\le d_I\le d_{\mathrm{top}}$ [引]: a map with $d_{\mathrm{top}}\le\varepsilon\Delta_F$ displays a tree, and a persistence diagram, within $\varepsilon\Delta_F$ of the source.
- 中：因此 $d_B\le d_I\le d_{\mathrm{top}}$ [引]：满足 $d_{\mathrm{top}}\le\varepsilon\Delta_F$ 的地图所显示的树及其持续图，与源数据相差都不超过 $\varepsilon\Delta_F$。
- EN: For superlevel sets all statements apply to $-f$.
- 中：对于上水平集，以上所有陈述对 $-f$ 成立。

**统一问题**
- EN: All maps we consider solve, per sequence, [公式 (3)]
- 中：我们考虑的所有地图，都在每个序列上求解如下问题 [公式 (3)]：
  $$\min_{\{M_t\}}\ \textstyle\sum_t \lambda_O E_O+\lambda_G E_G+\lambda_M E_M+\lambda_R E_R+\lambda_W E_W \quad \text{s.t. } M_t\in\mathcal{L}(\pi_t),\ \|x_t-q_t\|_\infty\le B_t,\ d_{\mathrm{top}}(\psi_t,T_t)\le(\varepsilon_0+\varepsilon)\Delta_F$$
- EN: with the TMTM overlap term $E_O$, the stress $E_G$ of anchor distances against source distances, a temporal term $E_M$ on matched anchors, the reference error $E_R$, the width deviation $E_W$ and layout model $\mathcal{L}$ (notation in Table 1).
- 中：其中 $E_O$ 是 TMTM 的重叠项，$E_G$ 是锚点距离相对源距离的应力，$E_M$ 是对应锚点上的时间项，$E_R$ 是参考误差，$E_W$ 是宽度偏差，$\mathcal{L}$ 是布局模型（记号见表 1）。
- EN: The data resolution $\varepsilon_0$ treats merge levels closer than $\varepsilon_0\Delta_F$ as ties (float32 round-off); $\varepsilon$ is the budget the analyst spends and $B_t$ a position cap.
- 中：数据分辨率 $\varepsilon_0$ 把相差小于 $\varepsilon_0\Delta_F$ 的合并层级视为相等（float32 舍入误差）；$\varepsilon$ 是分析者愿意花的预算，$B_t$ 是位置上限。
- EN: Table 2 lists the methods we compare as instances.
- 中：表 2 把我们比较的各方法列为该问题的实例。
- EN: Given their native leaf orders, both previous layouts are reproduced exactly on all five planar sequences: the TMTM linearization equals the official implementation in all 3127 arc intervals and anchors, and the ST-MTM anchors satisfy the optimality conditions of its quadratic programs (relative KKT residuals below $10^{-6}$, below $10^{-10}$ on the volumetric sequences).
- 中：给定它们原来的叶序，两种已有布局在全部 5 组平面序列上都能被精确复现：TMTM 的线性化与官方实现在全部 3127 个弧区间和锚点上完全一致；ST-MTM 的锚点满足其二次规划的最优性条件（相对 KKT 残差低于 $10^{-6}$，三维序列上低于 $10^{-10}$）。
- EN: Both methods are heuristic in the order: ST-MTM's leaf ordering exceeds the exhaustive optimum of its own objective on 10 frames, and TMTM's greedy choice is optimal at 434 of 463 enumerated steps but up to 85.5\% above the per-step optimum elsewhere.
- 中：两种方法在"排序"这一步都是启发式的：ST-MTM 的叶序在 10 帧上高于其自身目标的穷举最优；TMTM 的贪心选择在 463 个穷举过的步骤中有 434 步是最优的，但其余步骤最多比逐步最优高出 85.5%。
- EN: The bounds below depend only on the shared constraints.
- 中：下文的下界只依赖于这些共同的约束。

**表 1：记号**

| 记号 | 含义 |
|---|---|
| $T_t$, $V_{ij}$, $\Delta_F$ | 第 $t$ 步的合并树；叶子 $i,j$ 的合并层级；数值范围 |
| $q_i$, $L$ | 叶子 $i$ 的参考坐标；画布长度 |
| $W_i$, $g$, $H_i$ | 区间宽度；区间间距；锚点松弛 $\rho W_i/2$ |
| $\pi_t$, $x_i$, $\psi_t$ | 第 $t$ 步的叶序、锚点位置、剖面 |
| NROE, $\tau$ | 参考排序误差（式 1）；达到的最坏位移 |
| $d_{\mathrm{top}}$, NMLE | 带标签的合并误差（式 2）；$d_{\mathrm{top}}/\Delta_F$ |
| $\nu^*$ | 拓扑精确地图 NROE 的下界（定理 1） |
| $\varepsilon$, $\varepsilon_0$, $B_t$ | 合并层级预算；数据分辨率；位置上限 |
| $\delta^*(\pi)$ | 叶序 $\pi$ 的最小合并误差（最优屏障） |

**表 2：作为问题 (3) 实例的各比较方法**

| 方法 | $\varepsilon$ | $B$ | 目标 | 求解器 |
|---|---|---|---|---|
| TMTM | 0 | $\infty$ | $E_O$ | 贪心翻转子树 |
| ST-MTM | 0 | $\infty$ | $E_G+\lambda E_M$；$E_W$ | 先定叶序，再解二次规划 |
| $\kappa$ R20（旧方法） | 无上限 | – | $E_R+E_G+E_M$ | 候选池 + 二次规划 |
| 投影 | $\infty$ | $\tau_t+\beta$ | – | 按 $q$ 排序 + 二次规划 |
| 本文 | 0 或 $\varepsilon$ | $\tau_t+\beta$ | $E_R+E_G+E_M$ | 算法 1 |

## 4 方法总览

- EN: Figure 3 follows one Storms time step through our pipeline.
- 中：图 3 跟随 Storms 的一个时间步走完我们的流程。
- EN: (a) The extrema of the field are projected onto the reference axis.
- 中：(a) 场的极值被投影到参考轴上。
- EN: (b) Their merge tree is fixed by the data.
- 中：(b) 它们的合并树由数据决定。
- EN: Minimum C joins the other four only at the root, so any exact map keeps A, B, D, E in one block and places C at one of its ends; since C's reference lies inside the range of that block, the order error is at least $\nu^*=20.6\%$ (Theorem 1).
- 中：极小值 C 只在根节点处才与其余四个合并，因此任何拓扑精确的地图都把 A、B、D、E 放在同一个区块里，并把 C 放在区块的一端；由于 C 的参考坐标落在该区块的范围之内，排序误差至少为 $\nu^*=20.6\%$（定理 1）。
- EN: (c) With a budget $\varepsilon=10\%$, the budgeted ordering moves C next to D, near its reference, at an exact merge cost $\delta^*=4.7\%$.
- 中：(c) 在预算 $\varepsilon=10\%$ 下，预算内排序把 C 移到 D 旁边，靠近它的参考位置，精确合并代价为 $\delta^*=4.7\%$。
- EN: (d) Optimal barriers realize this order with the smallest possible merge error, and a capped quadratic program places the anchors.
- 中：(d) 最优屏障以尽可能小的合并误差实现这一叶序，带上限的二次规划摆放锚点。
- EN: (e) The stacked map marks every barrier whose displayed merge level was changed, and a strip reports the merge error spent per step.
- 中：(e) 堆叠后的地图标出每一个显示的合并层级被改动的屏障，并用一条条带报告每一步花掉的合并误差。

## 5 有保证的下界

- EN: All bounds follow from one lemma about where a leaf may sit.
- 中：所有下界都来自一个关于"叶子可以放在哪里"的引理。

**图 4**
- EN: Theorem 1 on sibling subtrees $X$ (blue) and $Y$ (orange).
- 中：定理 1 在兄弟子树 $X$（蓝）和 $Y$（橙）上的示意。
- EN: With exact topology one block must precede the other; the cheaper orientation costs $\min(M_X-m_Y,M_Y-m_X)/2$ and is chosen by sorting hull midpoints.
- 中：拓扑精确时，一个区块必须整体排在另一个之前；代价较小的方向为 $\min(M_X-m_Y,M_Y-m_X)/2$，按参考范围的中点排序即可选中它。

**引理 1（分离）**
- EN: Let $u$ be a node of $T_t$ with level $f(u)$, and let leaf $k$ lie strictly between two leaves $i,j$ of $u$ in a map with $d_{\mathrm{top}}\le\varepsilon$.
- 中：设 $u$ 是 $T_t$ 中层级为 $f(u)$ 的节点，在一张满足 $d_{\mathrm{top}}\le\varepsilon$ 的地图中，叶子 $k$ 严格位于 $u$ 的两个叶子 $i,j$ 之间。
- EN: Then $V_{ik}\le f(u)+2\varepsilon$.
- 中：则 $V_{ik}\le f(u)+2\varepsilon$。
- EN: *Proof.* The displayed merge of $i,j$ is the highest profile value between them, which is at least the displayed merge of $i,k$.
- 中：*证明.* $i,j$ 的显示合并是两者之间剖面的最高值，它不小于 $i,k$ 的显示合并。
- EN: Hence $V_{ik}-\varepsilon\le V^\psi_{ik}\le V^\psi_{ij}\le V_{ij}+\varepsilon\le f(u)+\varepsilon$.
- 中：因此 $V_{ik}-\varepsilon\le V^\psi_{ik}\le V^\psi_{ij}\le V_{ij}+\varepsilon\le f(u)+\varepsilon$。

- EN: With $\varepsilon=0$, a leaf outside $u$ merges with $u$ strictly above $f(u)$, so *every subtree is contiguous*: the children of a node occupy disjoint blocks.
- 中：当 $\varepsilon=0$ 时，$u$ 之外的叶子与 $u$ 的合并严格高于 $f(u)$，所以*每棵子树都是连续的*：一个节点的各个子树占据互不相交的区块。
- EN: Let $[m_X,M_X]$ be the reference hull of a subtree $X$.
- 中：记 $[m_X,M_X]$ 为子树 $X$ 的参考范围。

**定理 1（排序下界）**
- EN: Every map with $d_{\mathrm{top}}=0$ satisfies [公式 (4)]
- 中：每张满足 $d_{\mathrm{top}}=0$ 的地图都满足 [公式 (4)]
  $$\mathrm{NROE}(\pi_t)\ \ge\ \nu^*(T_t)=\frac{1}{2L}\max_{v}\ \max_{X\ne Y\in\mathrm{ch}(v)}\big[\min(M_X-m_Y,\ M_Y-m_X)\big]^+ ,$$
- EN: and sorting the children of every node by hull midpoint attains the bound in $O(n\log n)$.
- 中：并且把每个节点的子树按参考范围的中点排序，就能在 $O(n\log n)$ 时间内达到这个下界。
- EN: *Proof.* If $X$ precedes $Y$, the leaf of $X$ at $M_X$ precedes the leaf of $Y$ at $m_Y$, which by (1) costs at least $(M_X-m_Y)/2L$; the other orientation costs $(M_Y-m_X)/2L$.
- 中：*证明.* 若 $X$ 排在 $Y$ 之前，则 $X$ 中位于 $M_X$ 的叶子排在 $Y$ 中位于 $m_Y$ 的叶子之前，由式 (1) 其代价至少为 $(M_X-m_Y)/2L$；另一个方向的代价为 $(M_Y-m_X)/2L$。
- EN: In a midpoint order every inverted pair lies in sibling blocks $X\prec Y$ of its lowest common ancestor, and $m_X+M_X\le m_Y+M_Y$ is exactly $M_X-m_Y\le M_Y-m_X$.
- 中：在中点排序中，每一对逆序的叶子都位于其最近公共祖先的兄弟区块 $X\prec Y$ 中，而 $m_X+M_X\le m_Y+M_Y$ 恰好等价于 $M_X-m_Y\le M_Y-m_X$。

- EN: The bound is geometric (Fig. 4): siblings pay in proportion to how deeply their reference hulls overlap.
- 中：这个下界有直观的几何含义（图 4）：兄弟子树的代价与它们参考范围重叠的深度成正比。
- EN: It holds for any width rule, layout model or solver, hence for TMTM and ST-MTM.
- 中：它对任何宽度规则、布局模型或求解器都成立，因此也适用于 TMTM 和 ST-MTM。
- EN: The width-aware bound below needs the interval model, which ST-MTM and our layouts share.
- 中：下面的宽度感知下界需要区间布局模型，ST-MTM 和本文的布局都采用这一模型。

**宽度**
- EN: A wide feature pushes its neighbours away.
- 中：宽的特征会把相邻特征推开。
- EN: The attained interval cost $\tau(\pi)=\min_{x\in\mathcal{L}(\pi)}\max_i|x_i-q_i|$ has a closed form over the packed intervals.
- 中：可达到的区间代价 $\tau(\pi)=\min_{x\in\mathcal{L}(\pi)}\max_i|x_i-q_i|$ 在紧排的区间上有闭式表达。
- EN: With $\ell_k=q_k-W_k/2-H_k$, $h_k=q_k+W_k/2+H_k$, $s_k=W_k+g$ and, for a leaf set $S$, [公式 (5)]
- 中：令 $\ell_k=q_k-W_k/2-H_k$，$h_k=q_k+W_k/2+H_k$，$s_k=W_k+g$，并对叶子集合 $S$ 定义 [公式 (5)]
  $$A(S)=\max_{\alpha}\Big[\alpha+\sum_{k\in S,\ \ell_k\ge\alpha} s_k\Big],\quad B(S)=\max_{\beta}\Big[\sum_{k\in S,\ h_k\le\beta} s_k-\beta\Big],$$

**定理 2（宽度感知下界）**
- EN: In the interval layout model, if block $X$ precedes block $Y$, then $\tau\ge (A(X)+B(Y)-g)/2$.
- 中：在区间布局模型中，若区块 $X$ 排在区块 $Y$ 之前，则 $\tau\ge (A(X)+B(Y)-g)/2$。
- EN: Hence every exact interval layout has $\tau(\pi_t)\ge\max_v\max_{X\ne Y\in\mathrm{ch}(v)}\frac12[\min(A(X)+B(Y),A(Y)+B(X))-g]$, and every map has $\tau\ge B(\text{all})-g$ and $\tau\ge A(\text{all})-g-L$ at the canvas ends.
- 中：因此每个拓扑精确的区间布局都满足 $\tau(\pi_t)\ge\max_v\max_{X\ne Y\in\mathrm{ch}(v)}\frac12[\min(A(X)+B(Y),A(Y)+B(X))-g]$；并且在画布两端，每张地图都满足 $\tau\ge B(\text{all})-g$ 与 $\tau\ge A(\text{all})-g-L$。
- EN: *Proof sketch.* For $S_X\subseteq X$, $S_Y\subseteq Y$, the first interval of $S_X$ and the last of $S_Y$ enclose all of $S_X\cup S_Y$; their anchors are thus at least $\sum_{S_X\cup S_Y}s_k-g-W_a/2-W_b/2-H_a-H_b$ apart, and $\tau$ is at least half the shortfall against $q_a-q_b$.
- 中：*证明要点.* 对 $S_X\subseteq X$、$S_Y\subseteq Y$，$S_X$ 的第一个区间与 $S_Y$ 的最后一个区间之间夹着 $S_X\cup S_Y$ 的全部区间；因此两者的锚点至少相距 $\sum_{S_X\cup S_Y}s_k-g-W_a/2-W_b/2-H_a-H_b$，而 $\tau$ 至少是这一距离相对 $q_a-q_b$ 的差额的一半。
- EN: Upper sets of $\ell$ and lower sets of $h$ separate the maximization into $A$ and $B$, computed by sorting and prefix sums.
- 中：取 $\ell$ 的上集和 $h$ 的下集，可以把最大化拆成 $A$ 和 $B$ 两部分，用排序和前缀和即可算出。
- EN: The full proof is in the supplement.
- 中：完整证明见附录。
- EN: With zero widths and gap, Theorem 2 reduces to $L\,\nu^*$.
- 中：当宽度和间距都为零时，定理 2 退化为 $L\,\nu^*$。

**合并层级预算**
- EN: With $d_{\mathrm{top}}\le\varepsilon$, Lemma 1 still forbids a leaf between two leaves of $u$ unless it merges with $u$ within $2\varepsilon$ of $f(u)$.
- 中：当 $d_{\mathrm{top}}\le\varepsilon$ 时，引理 1 仍然禁止一个叶子出现在 $u$ 的两个叶子之间，除非它与 $u$ 的合并层级距 $f(u)$ 在 $2\varepsilon$ 以内。
- EN: Let $A_\varepsilon(u)$ be the highest ancestor of $u$ with level at most $f(u)+2\varepsilon$.
- 中：记 $A_\varepsilon(u)$ 为 $u$ 的层级不超过 $f(u)+2\varepsilon$ 的最高祖先。

**定理 3（链式下界）**
- EN: In a map with $d_{\mathrm{top}}\le\varepsilon$, every leaf outside $A_\varepsilon(u)$, and every node $w$ with $w\notin A_\varepsilon(u)$ and $u\notin A_\varepsilon(w)$, lies entirely on one side of $u$.
- 中：在满足 $d_{\mathrm{top}}\le\varepsilon$ 的地图中，$A_\varepsilon(u)$ 之外的每个叶子，以及每个满足 $w\notin A_\varepsilon(u)$ 且 $u\notin A_\varepsilon(w)$ 的节点 $w$，都整体位于 $u$ 的同一侧。
- EN: Applying the argument of Theorem 1 (resp. 2) to these separated pairs bounds NROE (resp. $\tau$) from below.
- 中：对这些相互分离的组对应用定理 1（相应地，定理 2）的论证，即可得到 NROE（相应地，$\tau$）的下界。

- EN: A coarser bound flattens every node within $2\varepsilon$ of its parent and applies Theorems 1 and 2; the chain bound charges a chain of small gaps by their sum and is never weaker.
- 中：一个较粗的下界是把所有与父节点相差 $2\varepsilon$ 以内的节点展平，再应用定理 1 和 2；链式下界则按一串小间隙的总和来计价，因此从不弱于粗下界。
- EN: All bounds use $\varepsilon_0+\varepsilon$ when a data resolution is declared.
- 中：声明了数据分辨率时，所有下界都用 $\varepsilon_0+\varepsilon$ 代替 $\varepsilon$。
- EN: Full proofs are in the supplement; every bound was checked against exhaustive enumeration on random trees.
- 中：完整证明见附录；每个下界都在随机树上与穷举结果做过核对。

**图 5**
- EN: (a) Reference order A–C–B splits the subtree A–B.
- 中：(a) 参考顺序 A–C–B 拆开了子树 A–B。
- EN: (b) Filling barriers with the original lowest-common-ancestor levels errs by the full gap $\gamma$.
- 中：(b) 用原始的最近公共祖先层级填充屏障，误差为整个间隙 $\gamma$。
- EN: (c) Optimal barriers balance the error at $\gamma/2$, the minimum for this order.
- 中：(c) 最优屏障把误差平衡在 $\gamma/2$，这是该顺序下的最小值。

## 6 达到下界的布局

**图 6**
- EN: Cross-method comparison on seven sequences (left of the grey line: planar; right: volumetric).
- 中：7 组序列上的横向比较（灰线左侧为平面数据，右侧为三维数据）。
- EN: Order error with the certified lower bound $\nu^*$ (black ticks; no exact map can go below), worst merge error, motion error, and the two distance measures of ST-MTM.
- 中：依次为排序误差及其有保证的下界 $\nu^*$（黑色短线；任何拓扑精确的地图都不可能低于它）、最坏合并误差、运动误差，以及 ST-MTM 的两项距离指标。
- EN: Exact-topology methods (TMTM, ST-MTM, ours at $\varepsilon=0$) have zero merge error; the projection has zero order error but up to 59\% merge error.
- 中：拓扑精确的方法（TMTM、ST-MTM、本文 $\varepsilon=0$）合并误差为零；投影的排序误差为零，但合并误差最高达 59%。
- EN: Values are in the supplement.
- 中：具体数值见附录。

**图 7**
- EN: Maps of daily outgoing longwave radiation (OLR, 60 days) and the synthetic Ring sequence (40 steps) that differ only in the layout objective.
- 中：逐日向外长波辐射（OLR，60 天）和合成的 Ring 序列（40 步）的地图，各图只有布局目标不同。
- EN: Each column is one time step; black dots mark the reference of each feature.
- 中：每一列是一个时间步；黑点标出每个特征的参考坐标。
- EN: Layouts that optimize hierarchy and time (TMTM-type) or pairwise distance (ST-MTM-type) place features far from their references; ours follows them.
- 中：优化层次和时间（TMTM 型）或两两距离（ST-MTM 型）的布局把特征放在远离参考坐标的位置；我们的布局则跟随参考坐标。

- EN: Algorithm 1 computes one map frame; frames are processed in time order so that the temporal term refers to the previous frame.
- 中：算法 1 计算一帧地图；各帧按时间顺序处理，使时间项参照前一帧。

**算法 1：有保证的第 $t$ 帧地图**
- EN: Require: tree $T_t$, references $q$, widths $W$, budget $\varepsilon$, resolution $\varepsilon_0$, slack $\beta$, previous anchors $x_{t-1}$
- 中：输入：树 $T_t$、参考坐标 $q$、宽度 $W$、预算 $\varepsilon$、分辨率 $\varepsilon_0$、松弛量 $\beta$、前一帧锚点 $x_{t-1}$
- EN: 1: $\mathcal{S}\gets\{T_t\}\cup\{T_t^{(s)}: s\le 2(\varepsilon_0+\varepsilon)\}\cup\{\text{conflict-driven flattening}\}$ ▷ candidate trees
- 中：1：$\mathcal{S}\gets\{T_t\}\cup\{T_t^{(s)}: s\le 2(\varepsilon_0+\varepsilon)\}\cup\{\text{冲突驱动的展平}\}$ ▷ 候选树
- EN: 2: for $S\in\mathcal{S}$ do
- 中：2：对每个 $S\in\mathcal{S}$：
- EN: 3: $\pi\gets$ midpoint order of $S$; skip if $\delta^*(\pi)>(\varepsilon_0+\varepsilon)\Delta_F$
- 中：3：$\pi\gets S$ 的中点排序；若 $\delta^*(\pi)>(\varepsilon_0+\varepsilon)\Delta_F$ 则跳过
- EN: 4–6: repeat — move one child block of a node of $S$ if it lowers $(\tau,\sum\text{positive terms}^2)$ and $\delta^*\le(\varepsilon_0+\varepsilon)\Delta_F$ — until no move improves ▷ width-aware local search
- 中：4–6：重复——若移动 $S$ 中某个节点的一个子区块能降低 $(\tau,\ \text{正项平方和})$ 且满足 $\delta^*\le(\varepsilon_0+\varepsilon)\Delta_F$，就执行该移动——直到没有移动能带来改进 ▷ 宽度感知局部搜索
- EN: 7: $\pi_t\gets$ best order by $(\tau,\mathrm{NROE})$ ▷ includes the point-model order
- 中：7：$\pi_t\gets$ 按 $(\tau,\mathrm{NROE})$ 选出的最优叶序 ▷ 包括点模型的叶序
- EN: 8: barriers $\gets$ optimal barriers of $\pi_t$, attaining $\delta^*(\pi_t)$
- 中：8：屏障 $\gets$ $\pi_t$ 的最优屏障，达到 $\delta^*(\pi_t)$
- EN: 9: $x_t\gets\arg\min E_R+E_G+E_M$ s.t. $\mathcal{L}(\pi_t)$, $\|x-q\|_\infty\le\tau(\pi_t)+\beta$
- 中：9：$x_t\gets\arg\min E_R+E_G+E_M$，约束为 $\mathcal{L}(\pi_t)$ 和 $\|x-q\|_\infty\le\tau(\pi_t)+\beta$
- EN: 10: report lower bound, $\tau(\pi_t)$, $\delta^*(\pi_t)$; mark barriers changed by more than $10^{-3}\Delta_F$
- 中：10：报告下界、$\tau(\pi_t)$ 和 $\delta^*(\pi_t)$；标出改动超过 $10^{-3}\Delta_F$ 的屏障

**排序**
- EN: For $\varepsilon=0$, midpoint ordering attains $\nu^*$.
- 中：当 $\varepsilon=0$ 时，中点排序达到 $\nu^*$。
- EN: With widths, a local search over the child permutations of each node minimizes $\tau$; the sum of squared positive pair terms breaks plateaus of the minimax objective.
- 中：考虑宽度时，对每个节点子树排列的局部搜索最小化 $\tau$；正的成对项的平方和用来打破极小极大目标的平台。
- EN: Every child permutation of the exact tree keeps $d_{\mathrm{top}}=0$.
- 中：精确树的任意子树排列都保持 $d_{\mathrm{top}}=0$。
- EN: For $\varepsilon>0$, candidate trees flatten nodes either by threshold or by repeatedly releasing the sibling pair that sets the order cost when Theorem 3's chain condition allows; every candidate and every search move is checked with the exact merge cost $\delta^*$ and rejected if it exceeds the budget.
- 中：当 $\varepsilon>0$ 时，候选树或按阈值展平节点，或在定理 3 的链条件允许时反复释放决定排序代价的那对兄弟子树；每个候选和每一步搜索都用精确合并代价 $\delta^*$ 检查，超出预算即拒绝。
- EN: The best previous order is always kept, so refinement never increases $\tau$.
- 中：之前最好的叶序始终保留，因此细化永远不会使 $\tau$ 变大。

**搜索细节**
- EN: Threshold candidates use one tree per distinct parent gap up to $2(\varepsilon_0+\varepsilon)$.
- 中：阈值候选对每个不超过 $2(\varepsilon_0+\varepsilon)$ 的不同父间隙各取一棵树。
- EN: The conflict-driven candidate starts from the exact tree, finds the sibling pair with the largest order cost and flattens one or both of its nodes when the chain condition holds and the exact $\delta^*$ of the new midpoint order stays within the budget; it repeats while the order error does not increase.
- 中：冲突驱动的候选从精确树出发，找出排序代价最大的那对兄弟子树；当链条件成立且新的中点排序的精确 $\delta^*$ 仍在预算内时，展平其中一个或两个节点；只要排序误差不增大就继续重复。
- EN: The four candidates with the lowest initial $\tau$, together with the exact tree, are refined.
- 中：初始 $\tau$ 最低的 4 个候选与精确树一起进入细化。
- EN: A move reinserts one child block at another position among its siblings, over all positions for nodes with up to eight children and within distance three otherwise, for at most eight passes.
- 中：一次移动是把一个子区块重新插入到兄弟之间的另一个位置：子节点不超过 8 个时尝试所有位置，否则只尝试距离 3 以内的位置；最多进行 8 轮。
- EN: On 300 random trees with random widths and budgets, this search reached the exhaustive optimum of $\tau$ on 296; the point-model order alone on 250.
- 中：在 300 棵宽度和预算随机的随机树上，这一搜索在 296 棵上达到了 $\tau$ 的穷举最优；只用点模型叶序时为 250 棵。

**最优屏障**
- EN: For a fixed order, the barrier between consecutive basins determines every displayed merge.
- 中：对固定的叶序，相邻盆地之间的屏障决定了所有显示的合并。
- EN: The smallest achievable error $\delta^*(\pi)$ has a closed form: each pair is limited by the lowest true merge level among the pairs it separates, an $\ell_\infty$ ultrametric fit under a fixed leaf order [引].
- 中：可达到的最小误差 $\delta^*(\pi)$ 有闭式解：每个屏障受它所分隔的各组对中最低真实合并层级的限制，这是固定叶序下的 $\ell_\infty$ 超度量拟合 [引]。
- EN: Figure 5 shows the effect: keeping original merge levels doubles the error that a balanced barrier needs.
- 中：图 5 展示了效果：保留原始合并层级时，误差是平衡屏障所需误差的两倍。
- EN: The profile is filled from the source arc samples with the renderer of ST-MTM [引].
- 中：剖面用 ST-MTM 的渲染器，从源数据的弧样本填充 [引]。

**带上限的摆位**
- EN: The anchors solve the convex quadratic program of (3) with widths, gaps, canvas and anchor slack.
- 中：锚点位置通过求解式 (3) 的凸二次规划得到，约束包括宽度、间距、画布和锚点松弛。
- EN: The cap $B_t=\tau(\pi_t)+\beta$ is feasible because $\tau$ is attained by the order, and it bounds $E_\infty$; without it the geometry term can pull single anchors far from their references.
- 中：上限 $B_t=\tau(\pi_t)+\beta$ 一定可行，因为 $\tau$ 是该叶序能达到的；它限制了 $E_\infty$。没有这个上限，几何项可能把个别锚点拉到远离其参考坐标的地方。

**代价**
- EN: Bounds cost $O(n\log n)$ to $O(n^2\log n)$, $\delta^*$ $O(n^3)$ per order.
- 中：各下界的计算代价为 $O(n\log n)$ 到 $O(n^2\log n)$，每个叶序的 $\delta^*$ 为 $O(n^3)$。
- EN: On an Apple M2 Pro (single Python process; NumPy 2.0, SciPy 1.13), all bounds take at most 0.6 ms per planar frame (1–11 leaves) and 5.5 ms per volumetric frame (up to 93 leaves), the ordering at most 3.7 ms and 103 ms, and the capped QP (SciPy SLSQP) 2.3–9.0 ms and 0.25–0.50 s.
- 中：在 Apple M2 Pro 上（单个 Python 进程；NumPy 2.0，SciPy 1.13），全部下界在每个平面帧（1–11 个叶子）上最多耗时 0.6 毫秒，在每个三维帧（最多 93 个叶子）上最多 5.5 毫秒；排序分别最多 3.7 毫秒和 103 毫秒；带上限的二次规划（SciPy SLSQP）分别为 2.3–9.0 毫秒和 0.25–0.50 秒。
- EN: All 917 frames take 94 s at $\varepsilon=0$ and at most 137 s with a budget.
- 中：全部 917 帧在 $\varepsilon=0$ 时耗时 94 秒，带预算时最多 137 秒。

## 7 评价

**图 8**
- EN: Position–topology frontier per sequence.
- 中：各序列的位置—拓扑权衡曲线。
- EN: Each point is one layout of all frames at budget $\varepsilon$ (labels, in percent), placed by its measured worst merge error and its worst (dark) and mean (light) displacement.
- 中：每个点代表预算 $\varepsilon$ 下全部帧的一种布局（标注为百分比），横坐标是实测的最坏合并误差，纵坐标是最坏位移（深色）和平均位移（浅色）。
- EN: Stars: projection ($\varepsilon=\infty$).
- 中：五角星：投影（$\varepsilon=\infty$）。
- EN: Grey crosses: earlier candidate-pool QP, planar only.
- 中：灰色叉号：旧的候选池二次规划，仅限平面数据。

### 7.1 实验设置

**数据**
- EN: Table 3 lists seven sequences, 917 frames in total [引].
- 中：表 3 列出 7 组序列，共 917 帧 [引]。
- EN: All methods share the processed fields, extrema, supports, matches and references; preprocessing follows prior work.
- 中：所有方法共用同样处理后的场、极值、支撑区域、对应关系和参考坐标；预处理沿用以往工作。

**表 3：数据序列**（叶子：每帧保留的极值个数）

| 序列 | 标量场 | 帧数 | 叶子数 | 树类型 |
|---|---|---|---|---|
| Storms | ERA5 平均海平面气压，二维 | 118 | 1–8 | join |
| Wildfires | $\log(1+\mathrm{FRP})$，二维 | 30 | 6–11 | split |
| OLR | 向外长波辐射，二维 | 60 | 2–8 | join |
| PM$_{2.5}$ | PM$_{2.5}$ 浓度，二维 | 366 | 1–7 | split |
| Ring | 合成的环形强度，二维 | 40 | 1–7 | split |
| Tangaroa | 速度模长，三维 | 201 | 18–93 | join |
| Cylinder | Q 判据，三维 | 102 | 4–75 | split |

**方法与指标**
- EN: We compare native TMTM and ST-MTM outputs, the earlier uncapped $\kappa$ construction (R20), the projection baseline, which sorts every frame by reference and uses the same optimal barriers and capped QP, and our layouts at $\varepsilon=0$ and $10\%$ (Table 2), with $\varepsilon_0=10^{-7}$.
- 中：我们比较以下方法：原生 TMTM 和 ST-MTM 的输出；旧的、没有误差上限的 $\kappa$ 构造（R20）；投影基线（每帧按参考坐标排序，并使用同样的最优屏障和带上限的二次规划）；以及本文在 $\varepsilon=0$ 和 $10\%$ 时的布局（表 2）。取 $\varepsilon_0=10^{-7}$。
- EN: Metrics are the order error NROE, the worst merge error, and, with the protocol of ST-MTM [引], scale-normalized stress (SNS) and trustworthiness (TW, $k=1$) of anchor distances against support-centroid distances, and the motion error (ME): the fraction of clear approach or separation events between two features over two steps that the map shows in the wrong direction or not at all.
- 中：指标包括排序误差 NROE、最坏合并误差，以及按 ST-MTM 的协议 [引] 计算的三项：锚点距离相对支撑区域质心距离的尺度归一化应力（SNS）和可信度（TW，$k=1$），以及运动误差（ME），即两个特征在两步内明显靠近或远离的事件中，被地图显示为方向相反或没有显示出来的比例。
- EN: Recomputing the stored baseline values from their saved anchors reproduces SNS and TD to a relative $10^{-5}$ and TW and ME to the third decimal or one event.
- 中：用保存的锚点重新计算已存的基线数值，SNS 和 TD 的相对误差在 $10^{-5}$ 以内，TW 和 ME 的差别在小数点后第三位或一个事件以内。

### 7.2 横向比较

- EN: *Exact-topology maps can be far more position-faithful than existing ones; the remaining error is certified, and distance preservation is a different trade-off.*
- 中：*拓扑精确的地图可以比已有地图在位置上忠实得多；剩下的误差有保证，而距离保持是另一种取舍。*
- EN: Figure 6 compares all methods on all sequences.
- 中：图 6 在所有序列上比较了所有方法。
- EN: *Order*: no method falls below $\nu^*$ on any of the 917 frames.
- 中：*排序*：在全部 917 帧中，没有任何方法低于 $\nu^*$。
- EN: Most of the order error of TMTM and ST-MTM is avoidable: on Storms, TMTM's 19.2\% contains 3.8\% that the hierarchy forces and ST-MTM's 16.3\% contains 12.5\% that it does not.
- 中：TMTM 和 ST-MTM 的排序误差大部分是可以避免的：在 Storms 上，TMTM 的 19.2% 中只有 3.8% 是层次迫使的；ST-MTM 的 16.3% 中有 12.5% 不是层次迫使的。
- EN: Our exact layouts lie within 0.03 percentage points of $\nu^*$ on every planar sequence; on Tangaroa and Cylinder the width-aware order trades a little NROE (9.67\% against 9.24\% on Tangaroa) for a lower worst displacement.
- 中：我们的拓扑精确布局在每一组平面序列上都与 $\nu^*$ 相差不超过 0.03 个百分点；在 Tangaroa 和 Cylinder 上，宽度感知排序用少量 NROE 换取更低的最坏位移（Tangaroa 上为 9.67% 对 9.24%）。
- EN: On all 637 frames with at most eight leaves, the budgeted order matches exhaustive enumeration at nine budgets from 0 to 100\%.
- 中：在全部 637 个叶子数不超过 8 的帧上，预算内排序在从 0 到 100% 的 9 档预算下都与穷举结果一致。
- EN: *Topology*: the projection has zero order error but changes merge levels by up to 58.66\% of the scalar range on Storms, 52.58\% on Wildfires, 33.56\% on OLR and 31.02\% on Tangaroa, where no frame keeps its tree; the uncapped $\kappa$ construction reached the same worst values on OLR and Tangaroa.
- 中：*拓扑*：投影的排序误差为零，但对合并层级的改变最高达到数值范围的 58.66%（Storms）、52.58%（Wildfires）、33.56%（OLR）和 31.02%（Tangaroa，其中没有一帧保持原来的树）；没有上限的 $\kappa$ 构造在 OLR 和 Tangaroa 上达到了同样的最坏值。
- EN: Our budgeted maps never exceed their budget.
- 中：我们带预算的地图从不超出预算。
- EN: *Motion*: our exact maps make fewer motion errors than both TMTM and ST-MTM on all seven sequences, e.g., 5.4\% against 21.4\% on OLR and 52.2\% against 70.0\% on Tangaroa, because a feature that moves along the reference moves on the map; the projection, which follows the references exactly, is lowest on most sequences.
- 中：*运动*：我们的拓扑精确地图在全部 7 组序列上的运动误差都低于 TMTM 和 ST-MTM，例如 OLR 上为 5.4% 对 21.4%，Tangaroa 上为 52.2% 对 70.0%，原因是沿参考方向移动的特征在图上也会移动；完全跟随参考坐标的投影在多数序列上最低。
- EN: *Distance*: ST-MTM, which optimizes pairwise distances, has the best TW on all seven sequences and the best SNS on five; on Cylinder our budgeted map (0.041) and the $\kappa$ construction (0.040) are far below ST-MTM's 0.135.
- 中：*距离*：以两两距离为优化目标的 ST-MTM 在全部 7 组上 TW 最好，在 5 组上 SNS 最好；在 Cylinder 上，我们带预算的地图（0.041）和 $\kappa$ 构造（0.040）都远低于 ST-MTM 的 0.135。

- EN: Figure 7 shows the planar sequences OLR and Ring with the same renderer and widths.
- 中：图 7 用相同的渲染器和宽度展示平面序列 OLR 和 Ring。
- EN: On Ring, the TMTM-type objective keeps all features near the centre of the axis and the ST-MTM-type objective spreads them by pairwise distance; both place them far from their references, whereas our exact layout follows them and a 10\% budget changes the map only locally.
- 中：在 Ring 上，TMTM 型目标把所有特征都放在轴的中部附近，ST-MTM 型目标按两两距离把它们散开；两者都把特征放在远离参考坐标的地方，而我们的拓扑精确布局跟随参考坐标，10% 的预算只在局部改变地图。
- EN: On OLR, our exact map already places the low-radiation basins near their references, which makes it comparable to a time–longitude plot while keeping each basin's nesting.
- 中：在 OLR 上，我们的拓扑精确地图已经把低辐射盆地放在参考坐标附近，使它可以与"时间—经度"图相对照，同时保留每个盆地的嵌套关系。

### 7.3 可控层次冲突（N4，2026-10-30 新增）

- EN: To isolate spatial conflict, we fix two sibling pairs $X=\{A,B\}$ and $Y=\{C,D\}$, merging at $0.4$ below a root at $1$, with leaf values $0$.
- 中：为单独考察空间冲突，我们固定两个兄弟子树 $X=\{A,B\}$ 和 $Y=\{C,D\}$，各组在层级 0.4 合并，根层级为 1，叶值为 0。
- EN: On a unit canvas their references are $(0.2,0.5,0.5-d,0.8-d)$; signed overlap $d$ varies from $-0.12$ to $0.30$.
- 中：单位画布上的参考坐标为 $(0.2,0.5,0.5-d,0.8-d)$；带符号的重叠量 $d$ 从 −0.12 变化到 0.30，负值表示两组参考范围分离。
- EN: Across 43 overlaps and four widths, we enumerate all 24 leaf orders and solve independent minimax placement LPs.
- 中：在 43 档重叠量和 4 档宽度下，枚举全部 24 种叶序，并独立构造线性规划求最小最大位移。
- EN: The point optimum is exactly $\nu^*=\max(0,d)/2$.
- 中：点模型的最优值恰为 $\nu^*=\max(0,d)/2$。
- EN: With equal widths $W=0.06$, gap $0.01$ and $\rho=0.5$, both the width bound and our search attain the exhaustive optimum $\tau=\max(0,(d+0.04)/2)$ (Fig. 9a).
- 中：在等宽 $W=0.06$、间隔 0.01、$\rho=0.5$ 时，宽度下界和本文搜索均达到穷举最优值 $\tau=\max(0,(d+0.04)/2)$（图 9a）。
- EN: At $d=0.24$, these costs are $12\%$ and $14\%$.
- 中：当 $d=0.24$ 时，点模型与区间模型的代价分别为 12% 和 14%。
- EN: Sweeping the budget and four parent gaps confirms that interleaving becomes feasible at $2\varepsilon=h$; the $h=0.6$ case reaches zero displacement at $\varepsilon=0.3$ (Fig. 9b).
- 中：扫描预算和四档父间隙，确认交错叶序从 $2\varepsilon=h$ 时开始可行；父间隙 $h=0.6$ 时，在预算 $\varepsilon=0.3$ 达到零位移（图 9b）。
- EN: These are controlled instances, not a general tightness claim for the width bound; full settings and packing costs are in the supplement.
- 中：这些结果针对该受控实例族，不表示宽度下界在任意树上都紧；完整设置和装箱代价见附录。

**新增图 9：** 可控四叶树。(a) 兄弟参考范围的重叠增加，迫使位置位移增大；圆圈表示被穷举区间最优解达到的宽度下界。(b) 当重叠为 24% 时，只有合并预算达到父间隙 60% 的一半，14% 的区间位移才消失。百分比分别按单位画布或单位标量范围归一化。

### 7.4 位置—拓扑权衡曲线

- EN: *Small budgets can recover most of the position, but not on every sequence; the frontier shows where.*
- 中：*小预算往往能挽回大部分位置，但并非每组序列都如此；权衡曲线告诉你在哪里有效。*
- EN: Figure 8 places every layout by its measured worst merge error and its displacement, from $\varepsilon=0$ to the projection.
- 中：图 8 按实测的最坏合并误差和位移排列每一种布局，从 $\varepsilon=0$ 一直到投影。
- EN: On Cylinder a 1\% budget reaches the lowest worst displacement of the whole curve (27.00\% to 5.27\%), below the projection's 5.73\%, because sorting by reference ignores widths.
- 中：在 Cylinder 上，1% 的预算就达到了整条曲线上最低的最坏位移（从 27.00% 降到 5.27%），甚至低于投影的 5.73%，因为按参考坐标排序会忽略宽度。
- EN: On Wildfires 1\% reduces $E_\infty$ from 20.48\% to 8.71\%, and on PM$_{2.5}$ 5\% reaches the projection result.
- 中：在 Wildfires 上，1% 的预算把 $E_\infty$ 从 20.48% 降到 8.71%；在 PM$_{2.5}$ 上，5% 的预算即达到投影的结果。
- EN: Storms needs much more: its worst displacement stays above 18\% up to $\varepsilon=20\%$, and OLR keeps $E_\infty=17.14\%$ up to 10\% because one frame needs a larger change.
- 中：Storms 需要多得多的预算：直到 $\varepsilon=20\%$，其最坏位移仍在 18% 以上；OLR 在 10% 以内一直保持 $E_\infty=17.14\%$，因为有一帧需要更大的改动。
- EN: Mean merge errors are far below the maxima (Storms at 10\%: 0.90\% mean, 8.51\% maximum), so the budget is spent on few frames.
- 中：合并误差的均值远低于最大值（Storms 在 10% 时均值 0.90%、最大值 8.51%），说明预算只花在少数帧上。
- EN: Compared with the uncapped $\kappa$ construction at similar positions, the worst merge error is now bounded (Storms: 26.07\% to 8.51\%; Wildfires: 19.56\% to 8.35\%).
- 中：在位置水平相近时与没有上限的 $\kappa$ 构造相比，最坏合并误差现在有了上限（Storms：从 26.07% 降到 8.51%；Wildfires：从 19.56% 降到 8.35%）。

### 7.5 大特征

**图 9**
- EN: Tangaroa, 201 time steps: interval cost $\tau_t/L$ of the point-model order (orange), the width-aware order (blue) and the $\kappa$ construction (dashed, mostly hidden under the blue line), with the certified lower bound (grey area, the larger of Theorems 2 and 3).
- 中：Tangaroa，201 个时间步：点模型叶序（橙）、宽度感知叶序（蓝）和 $\kappa$ 构造（虚线，大部分被蓝线遮住）的区间代价 $\tau_t/L$，以及有保证的下界（灰色区域，取定理 2 和定理 3 中较大者）。

- EN: *Ordering for the point model is not enough when features are large; the width-aware bound and search close the gap.*
- 中：*特征较大时，只按点模型排序是不够的；宽度感知的下界和搜索弥补了这一差距。*
- EN: On Tangaroa, ordering by NROE alone gave a worst displacement of 20.69\%, above the $\kappa$ construction's 16.86\%.
- 中：在 Tangaroa 上，只按 NROE 排序得到的最坏位移为 20.69%，高于 $\kappa$ 构造的 16.86%。
- EN: Ordering by $\tau$ lowers it to 15.10\% at $\varepsilon=0$ and to 14.55\% at $\varepsilon=2\%$, where the worst frame meets the lower bound; on Cylinder $\varepsilon\ge2\%$ lowers $E_\infty$ from 5.73\% to 5.27\%, again at the bound.
- 中：按 $\tau$ 排序后，$\varepsilon=0$ 时降到 15.10%，$\varepsilon=2\%$ 时降到 14.55%，此时最坏帧达到下界；在 Cylinder 上，$\varepsilon\ge2\%$ 时 $E_\infty$ 从 5.73% 降到 5.27%，同样达到下界。
- EN: The chain bound makes these certificates informative for large trees: at $\varepsilon=5\%$ the coarse bound averages 0.38\% on Tangaroa, the chain width bound 7.40\% against an attained 8.10\%.
- 中：链式下界使这些保证在大树上也有信息量：$\varepsilon=5\%$ 时，Tangaroa 上粗下界的平均值只有 0.38%，链式宽度下界为 7.40%，实际达到 8.10%。
- EN: The remaining gap of about one percentage point also appears at $\varepsilon=0$, which suggests that the bound, not the ordering, is loose.
- 中：剩余约 1 个百分点的差距在 $\varepsilon=0$ 时同样存在，这提示松的是下界，而不是排序。
- EN: Figure 9 shows where the gain comes from: the point-model order lies far above the bound in the first 30 steps, and the width-aware order removes most of this excess.
- 中：图 9 显示了收益来自哪里：点模型叶序在前 30 步远高于下界，宽度感知叶序消除了其中的大部分超出量。
- EN: Table 4 lists both volumetric sequences.
- 中：表 4 列出两组三维序列。
- EN: The $\kappa$ construction keeps lower mean jumps on Tangaroa (2.59\% against 2.82\%) and a lower pooled displacement than our 2\% map (4.16\% against 4.55\%); its merge error, however, has no cap.
- 中：$\kappa$ 构造在 Tangaroa 上的平均跳动更低（2.59% 对 2.82%），平均位移也低于我们 2% 预算的地图（4.16% 对 4.55%）；但它的合并误差没有上限。

**表 4：三维序列（单位：%）**
- EN: $\kappa$ P (exact) and R2 (relaxed, no merge-error cap) are the earlier construction; N1 orders by NROE only. Jump: mean $|\Delta x-\Delta q|/L$ of matched features.
- 中：$\kappa$ P（拓扑精确）和 R2（放松，合并误差无上限）是旧的构造；N1 只按 NROE 排序。跳动：对应特征的 $|\Delta x-\Delta q|/L$ 的平均值。

| 数据 | 布局 | $E_{\mathrm{pool}}$ | $E_\infty$ | NROE | 跳动 | NMLE 最大值 |
|---|---|---|---|---|---|---|
| Tangaroa | $\kappa$ P | 5.01 | 16.86 | 9.61 | 2.59 | 0 |
| Tangaroa | N1，$\varepsilon=0$ | 4.92 | 20.69 | 9.24 | 2.73 | 0.00 |
| Tangaroa | 本文，$\varepsilon=0$ | 5.01 | 15.10 | 9.67 | 2.82 | 0.00 |
| Tangaroa | $\kappa$ R2 | 4.16 | 14.65 | 8.56 | 2.49 | 无上限 |
| Tangaroa | N1，$\varepsilon=2\%$ | 4.49 | 20.69 | 8.23 | 2.60 | 2.00 |
| Tangaroa | 本文，$\varepsilon=2\%$ | 4.55 | 14.55 | 8.60 | 2.76 | 2.00 |
| Cylinder | $\kappa$ P | 5.40 | 32.08 | 12.26 | 5.87 | 0 |
| Cylinder | N1，$\varepsilon=0$ | 3.76 | 27.00 | 8.01 | 3.83 | 0.00 |
| Cylinder | 本文，$\varepsilon=0$ | 3.76 | 27.00 | 8.01 | 3.89 | 0.00 |
| Cylinder | $\kappa$ R2 | 0.62 | 5.27 | 0.25 | 0.47 | 无上限 |
| Cylinder | N1，$\varepsilon=2\%$ | 0.64 | 5.73 | 0.17 | 0.46 | 1.84 |
| Cylinder | 本文，$\varepsilon=2\%$ | 0.64 | 5.27 | 0.19 | 0.47 | 1.67 |

### 7.6 三维中的参考方向

**图 10**
- EN: Reference direction in 3-D.
- 中：三维中的参考方向。
- EN: Disks: mean order bound $\nu^*$ over 400 directions of the hemisphere (equal-area projection; centre $=z$, rim $=xy$ plane); markers: coordinate axes, stored direction (star) and smallest bound (cross).
- 中：圆盘：半球上 400 个方向各自的平均排序下界 $\nu^*$（等面积投影；圆心对应 $z$ 轴，边缘对应 $xy$ 平面）；标记：各坐标轴、原先选用的方向（五角星）和下界最小的方向（十字）。
- EN: Bars: $\nu^*$ and mean order error of our exact layout, ST-MTM and TMTM for the key directions (native orientations chosen in their favour).
- 中：柱状图：在这些关键方向上的 $\nu^*$，以及本文拓扑精确布局、ST-MTM 和 TMTM 的平均排序误差（原生方法的整体朝向取对它们最有利的一种）。

- EN: *In 3-D the choice of reference matters, and the bound measures its cost before any layout is computed.*
- 中：*在三维中，参考方向的选择很重要，而下界能在计算任何布局之前就衡量出它的代价。*
- EN: Projecting a volume onto one direction discards two coordinates, so the unavoidable order error depends on the direction.
- 中：把一个体数据投影到一个方向上会丢掉两个坐标，因此不可避免的排序误差取决于方向。
- EN: Because the bounds use only the tree and the extremum positions, we recomputed them for 400 directions over the hemisphere on both volumetric sequences, with references built exactly like the stored ones (Fig. 10).
- 中：由于下界只用到树和极值的位置，我们在两组三维序列上，对半球上的 400 个方向重新计算了下界，参考坐标的构造方式与原先完全相同（图 10）。
- EN: No native TMTM or ST-MTM frame falls below $\nu^*$ in any direction, even with the global orientation chosen in their favour.
- 中：在任何方向上，原生 TMTM 和 ST-MTM 都没有一帧低于 $\nu^*$，即使它们的整体朝向取对它们最有利的一种。
- EN: The mean bound ranges from 4.70\% to 10.14\% on Tangaroa and from 5.26\% to 28.15\% on Cylinder.
- 中：平均下界在 Tangaroa 上介于 4.70% 到 10.14% 之间，在 Cylinder 上介于 5.26% 到 28.15% 之间。
- EN: On Tangaroa, the stored direction, chosen to follow the main motion of the features, is among the most costly: only 3 of the 400 directions have a higher bound, and the $x$ axis would lower $\nu^*$ from 9.24\% to 6.09\%.
- 中：在 Tangaroa 上，原先选用的方向（为了跟随特征的主要运动）属于代价最高的一类：400 个方向中只有 3 个的下界更高；改用 $x$ 轴可以把 $\nu^*$ 从 9.24% 降到 6.09%。
- EN: On Cylinder, the streamwise axis lies near the median (7.72\%).
- 中：在 Cylinder 上，流向坐标轴处于中位附近（7.72%）。
- EN: In every key direction the previous methods stay far above the bound, while our exact order stays within 0.6 percentage points of it, except on the Tangaroa $z$ axis (2.6 points), where large widths dominate.
- 中：在每个关键方向上，已有方法都远高于下界；而我们的拓扑精确排序与下界相差不超过 0.6 个百分点，唯一的例外是 Tangaroa 的 $z$ 轴（2.6 个百分点），那里大宽度的影响占主导。
- EN: Since $\nu^*$ costs milliseconds per frame, an analyst can rank candidate references before computing any map, and weigh following the motion against hierarchical conflict.
- 中：由于每帧计算 $\nu^*$ 只需几毫秒，分析者可以在计算任何地图之前就对候选参考方向进行排序比较，在"跟随运动"和"层次冲突"之间做权衡。

### 7.7 三维案例：Vortex（2026-10-30 新增）

- EN: Figure 11 links spatial references, profiles and displayed trees on the separate 90-frame Vortex diagnostic. The reference q=X/127 is the normalized voxel coordinate, with physical units unavailable.
- 中：图 11 在独立的 90 帧 Vortex 诊断序列上对应三维参考位置、剖面与显示树。q=X/127 是归一化体素坐标，没有可用的物理单位。
- EN: At t=8 every budget retains all 142 leaves; structural depths are 74, 53, 48, 48, 18, 18 and normalized merge errors are 0%, 1.58%, 2.98%, 2.98%, 19.06%, 27.14%.
- 中：t=8 的所有预算均保留 142 片叶子；结构深度为 74、53、48、48、18、18，归一化合并误差为 0%、1.58%、2.98%、2.98%、19.06%、27.14%，均未超过对应预算。深度相同不意味着合并层级或映射位置相同。此序列和 744 小时首图均不计入原 917 帧横评。

### 7.8 案例研究：带误差披露的 Storms

**图 11**
- EN: Storms, 118 half-day steps.
- 中：Storms，118 个半天时间步。
- EN: Top: maps that differ only in the layout objective; dots mark references.
- 中：上排：只有布局目标不同的地图；圆点标出参考坐标。
- EN: On the $\varepsilon=10\%$ map, yellow ticks mark barriers whose displayed merge level differs from the source by more than 0.1\% of the scalar range.
- 中：在 $\varepsilon=10\%$ 的地图上，黄色短线标出显示的合并层级与源数据相差超过数值范围 0.1% 的屏障。
- EN: Bottom left: worst displacement per step.
- 中：左下：每一步的最坏位移。
- EN: Bottom right: merge error spent per step at $\varepsilon=10\%$, always below the cap.
- 中：右下：$\varepsilon=10\%$ 时每一步花掉的合并误差，始终低于上限。

- EN: *A budgeted map shows where, and by how much, the hierarchy was changed.*
- 中：*带预算的地图会显示层次在哪里被改动、改动了多少。*
- EN: Figure 11 compares maps on Storms, where minima of sea-level pressure are low-pressure systems crossing the North Atlantic.
- 中：图 11 比较 Storms 上的各种地图，这里海平面气压的极小值是穿越北大西洋的低压系统。
- EN: Within the same layout model, the TMTM-type and ST-MTM-type objectives place features on average 37.3\% and 50.7\% of the canvas from their references in the worst case of each step; our exact map has a median of 0.8\% and a mean of 5.1\%, with peaks of up to 26.2\% in a few steps.
- 中：在同一布局模型内，TMTM 型和 ST-MTM 型目标在每一步的最坏情形下，平均把特征放在离参考坐标画布长度 37.3% 和 50.7% 的地方；我们的拓扑精确地图中位数为 0.8%，平均为 5.1%，少数几步的峰值最高达 26.2%。
- EN: A 10\% budget lowers the mean to 2.7\%.
- 中：10% 的预算把平均值降到 2.7%。
- EN: It is spent in 31 of 118 steps, at most 8.51\% and 0.90\% on average, and the 89 barriers whose merge level changed by more than 0.1\% of the scalar range are marked.
- 中：预算只花在 118 步中的 31 步，最多 8.51%，平均 0.90%；合并层级改动超过数值范围 0.1% 的 89 个屏障都被标出。
- EN: At $\varepsilon=0$ no mark appears.
- 中：当 $\varepsilon=0$ 时，图上没有任何标记。

**读图**
- EN: Reading the hourly map: Figure 1 follows two tracked minima through five spatial snapshots, separated by six hours, and the corresponding budget columns. At t=236, the trees retain all five leaves; their normalized merge errors are 0, 0, 1.07%, 1.07%, 3.08%, within the displayed budgets.
- 中：逐小时图的读法：图 1 将相隔六小时的五个空间快照，与不同预算列中的两个跟踪极小值对应起来。t=236 的树始终保留五片叶子；归一化合并误差分别为 0、0、1.07%、1.07%、3.08%，均在对应预算内。结构层数变少不表示气压减少相同数值。原半日 Storms 对照图移入附录。

## 8 讨论与局限

**预算改变了什么**
- EN: A budget never removes a feature, changes an extremum value or moves the data; it changes displayed merge levels by at most $\varepsilon\Delta_F$, and the displayed tree and its persistence diagram stay within that distance of the source.
- 中：预算从不删除特征、不改变极值的数值、也不移动数据；它只把显示的合并层级改变至多 $\varepsilon\Delta_F$，显示出的树及其持续图与源数据的距离都不超过这个量。
- EN: Where a subtree is split, its band is no longer contiguous and the reading "one band, one component" fails locally, which is why we mark such barriers.
- 中：在子树被拆开的地方，它的带不再连续，"一条带对应一个连通分量"的读法在局部失效，这正是我们标出这些屏障的原因。
- EN: Persistence simplification spends a comparable budget differently, removing features below $2\varepsilon$ [引].
- 中：持续性简化以不同的方式花同等量级的预算：它删除持续性低于 $2\varepsilon$ 的特征 [引]。
- EN: Open refinements are a one-sided error that never shows an earlier connection and a constraint that keeps barriers inside the data range.
- 中：尚待完善的有两点：一是只允许单侧误差，使地图永远不会显示比真实更早的连接；二是加一个约束，使屏障不超出数据范围。
- EN: We recommend $\varepsilon=0$ as the default and a budget only where the frontier shows a clear gain.
- 中：我们建议默认使用 $\varepsilon=0$，只在权衡曲线显示收益明显时才使用预算。

**如何选择预算**
- EN: The data resolution $\varepsilon_0$ should match the precision of the data; with float32 fields we used $10^{-7}$ of the range.
- 中：数据分辨率 $\varepsilon_0$ 应与数据的精度相匹配；对 float32 的场，我们取数值范围的 $10^{-7}$。
- EN: On Cylinder, whose saddles are nearly degenerate, the bound $\nu^*$ is 12.24\% when only exactly equal levels are merged and 6.15\% at $\varepsilon_0=10^{-6}$, which shows that part of its hierarchy lies below data precision.
- 中：在鞍点近乎退化的 Cylinder 上，只合并完全相等的层级时下界 $\nu^*$ 为 12.24%，取 $\varepsilon_0=10^{-6}$ 时为 6.15%，这说明它的部分层次结构低于数据精度。
- EN: The budget $\varepsilon$ is a choice of the analyst: the frontier of Fig. 8 shows its effect on position before any map is read, and the disclosure strip shows where it was spent.
- 中：预算 $\varepsilon$ 由分析者选择：图 8 的权衡曲线在读任何地图之前就显示了它对位置的影响，披露条带则显示预算花在了哪里。

**一维的局限**
- EN: Projecting onto one direction loses the other coordinates; features at the same longitude compete for the same position, and $\nu^*$ quantifies exactly this conflict for the chosen direction, which in 3-D varies by a factor of two to five between directions.
- 中：投影到一个方向会丢失其他坐标；处于同一经度的特征会争夺同一个位置，而 $\nu^*$ 恰好量化了所选方向上的这种冲突；在三维中，不同方向之间的这一冲突相差 2 到 5 倍。
- EN: Our metrics of position are defined against the reference the layout optimizes; the comparison therefore also reports the scale-free order error of native outputs and the distance and motion measures of ST-MTM, on which ST-MTM keeps the better distance preservation.
- 中：我们的位置指标是相对布局所优化的那个参考坐标来定义的；因此比较中也报告了原生输出的与尺度无关的排序误差，以及 ST-MTM 的距离和运动指标，在这些指标上 ST-MTM 的距离保持仍然更好。
- EN: Readability was not tested: whether analysts read position and nesting together, and whether disclosure marks prevent misreading [引], requires a user study.
- 中：我们没有测试可读性：分析者能否同时读出位置和嵌套，误差披露标记能否防止误读 [引]，都需要用户研究来回答。

**可复现性**
- EN: All results are computed from saved experiment records by scripts that we will release with the paper; every figure and table of this paper and the supplement is regenerated by one script, and 68 unit tests, among them checks of the bounds and orders against exhaustive enumeration, cover the implementation.
- 中：所有结果都由脚本从保存的实验记录计算得到，这些脚本将随论文一起发布；本文和附录的每一张图表都由同一个脚本重新生成；68 项单元测试覆盖了整个实现，其中包括用穷举核对下界和叶序的测试。

**下界**
- EN: The order bound is attained exactly.
- 中：排序下界可以精确达到。
- EN: The width bound is attained on most planar frames and on the worst Tangaroa and Cylinder frames but not uniformly on large trees; Wildfires at $\varepsilon>0$ and one OLR frame at $\varepsilon=10\%$ keep a worst-frame gap.
- 中：宽度下界在大多数平面帧以及 Tangaroa 和 Cylinder 的最坏帧上可以达到，但在大树上并非处处达到；Wildfires 在 $\varepsilon>0$ 时，以及 OLR 在 $\varepsilon=10\%$ 时的一帧，最坏帧仍有差距。

## 9 结论

- EN: Merge tree maps can stay close to a spatial reference without giving up their hierarchy, and how close is computable.
- 中：合并树地图可以在不放弃层次的前提下贴近空间参考，而且能贴近到什么程度是可以计算的。
- EN: The order bound and its width and chain versions give the unavoidable displacement of every exact map; most of the displacement of existing maps lies above it, and our layouts remove it.
- 中：排序下界及其宽度版本和链式版本给出了每张拓扑精确地图不可避免的位移；已有地图的位移大部分高于这个下界，而我们的布局消除了这一部分。
- EN: A merge-level budget recovers more position where the data allow, with the error certified, reported and marked on the map.
- 中：在数据允许的地方，合并层级预算能挽回更多位置，同时误差有保证、被报告，并标在图上。
- EN: Each map therefore carries two numbers: how far it moves features and how far it changes the hierarchy.
- 中：因此每张地图都带着两个数：它把特征移动了多远，以及它把层次改变了多少。


## 2026-10-30：预算增大时的局部位置响应

EN: Aggregate gains do not imply pointwise improvement. In a four-leaf control, enumerating all 24 orders lowers the optimal worst displacement from 22% to 1% at epsilon=30%, yet one feature's error rises from 0.087% to 1%.

中：整体指标改善不意味着每个点都改善。四叶受控实验枚举全部 24 种叶序，预算增至 30% 后，全局最优的最坏位移从 22% 降至 1%，但某个点从 0.087% 增至 1%。这个反例不依赖启发式搜索或时间历史。

EN: On an additional 90-frame Vortex diagnostic, increasing epsilon from 20% to 30% lowers pooled error from 8.79% to 4.27%, while 30.91% of 12,446 feature-frame observations worsen; 24.72% worsen by at least 0.5 percentage points of L.

中：额外的 Vortex 诊断中，预算从 20% 增至 30% 时，全部特征—帧的平均误差从 8.79% 降至 4.27%，但 12,446 个观测中 30.91% 变差，其中 24.72% 至少增加 0.5 个百分点。这些诊断与原稿 917 帧主横评分开报告。

正文前沿小节后新增 Local budget response；Choosing the budget 改为同时检查关注特征的局部误差变化。原数值精度的 Cylinder 例子完整移至附录 S4。附录 S4 包含诊断总体、阈值、全部转档统计、24 叶序穷举反例、案例选择规则和两幅图。
