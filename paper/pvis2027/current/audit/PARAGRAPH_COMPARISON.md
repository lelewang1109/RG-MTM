# 主要段落改写前后对照

基准仅为指定《AnchorMTM_投稿排版修订版.pdf》对应源文件。下列保留LaTeX引用与数学记号，便于逐段检查；数值结果段落与数学环境未改动。

## 1. Abstract

**改写前**

```latex
\abstract{Temporal merge tree maps summarize evolving scalar hierarchies, but their display axis does not identify a fixed spatial location. Giving that axis a spatial reference creates a conflict: an exact profile keeps each subtree contiguous, while projected features can interleave. We derive three layout-independent lower bounds that quantify the displacement forced by exact topology, finite feature widths and a bounded merge-level error. AnchorMTM approaches these bounds through topology-budgeted leaf ordering, capped anchor placement and scalar-profile reconstruction. Controlled four-leaf experiments recover the bounds by exhaustive ordering and independent linear programs. Comparisons on five planar and two volumetric sequences show how anchoring improves reference alignment and how a declared merge allowance reduces displacement. Recomputed feature-position and per-frame distribution plots locate these changes across complete sequences: a small budget resolves most Cylinder conflicts, whereas Tangaroa requires larger allowances.}
```

**改写后**

```latex
\abstract{Temporal merge tree maps summarize the hierarchy of a time-varying scalar field, but their display coordinate does not provide a fixed spatial reference. Anchoring this coordinate reveals a structural conflict: exact topology requires contiguous subtree blocks, whereas projected feature positions can interleave. We quantify the resulting positional cost through three layout-independent bounds for exact point orders, finite-width interval layouts and bounded merge-level error. AnchorMTM uses these bounds to guide leaf-order selection and capped anchor placement, then reconstructs scalar profiles under a controlled merge budget. Controlled four-leaf experiments compare the bounds with exhaustive ordering and independent linear programs. Existing results on five planar and two volumetric sequences then connect unavoidable displacement, absolute positioning and the effect of relaxation. The per-frame evidence shows that a budget resolves a difficult tail of Storms frames and shifts most frames in the default volume configurations. The resulting maps make feature positions readable against one shared spatial direction while exposing the hierarchical cost of that coordinate.}
```

## 2. introduction

**改写前**

```latex
An analyst following storms, pollution peaks or vortices needs to see which features exist, where they are and how they move. Animation retains the spatial field at each instant; a static temporal overview places distant times side by side~\cite{Tversky:2002:Animation,Robertson:2008:Animation,Bach:2017:STC}. When time occupies one display axis, the coordinate assigned to the other determines which spatial relationships remain readable. Figure~\ref{fig:storms_overview} connects source-field supports to the trajectories of a merge tree map.
```

**改写后**

```latex
Time-varying scalar fields describe phenomena whose structure and location evolve together: storms move, pollution peaks develop, and vortices form and shed. Analysis therefore requires three kinds of information---feature identity and hierarchy, spatial location, and temporal change. Animation retains the field at each instant; static overviews support comparison across distant times~\cite{Tversky:2002:Animation,Robertson:2008:Animation,Bach:2017:STC}. When one display axis represents time, the meaning of the remaining coordinate determines which spatial questions the overview can answer. Figure~\ref{fig:storms_overview} connects these questions through source supports, profiles and feature trajectories.
```

## 3. introduction

**改写前**

```latex
Temporal Merge Tree Maps (TMTM) compress each scalar field into a one-dimensional profile: extrema become minima and intervening barriers encode merge levels~\cite{Koepp:2023:TMTM}. Stacking the profiles preserves the evolving hierarchy. Spatiotemporal Merge Tree Maps (ST-MTM) further fit spatial distances and temporal position constraints~\cite{STMTM:2026}. Their coordinate expresses a tree traversal or relative geometry. Reading an anchor as longitude, or its displacement as eastward motion, requires an additional fixed spatial reference.
```

**改写后**

```latex
Temporal Merge Tree Maps (TMTM) address hierarchy and temporal comparison by converting each frame into a one-dimensional scalar profile, with extrema at minima and merges at intervening barriers, and assembling these profiles along time~\cite{Koepp:2023:TMTM}. Spatiotemporal Merge Tree Maps (ST-MTM) extend this foundation with relative spatial geometry and temporal position constraints~\cite{STMTM:2026}. These objectives organize the features coherently, but they do not assign the display axis a fixed physical direction and origin. Consequently, a position cannot directly be read as longitude or distance along a flow, and a trajectory does not by itself express motion along that coordinate.
```

## 4. introduction

**改写前**

```latex
We quantify this distinction before constructing a map. Three bounds measure the minimum displacement forced by an exact point order, by finite-width intervals and by the restrictions surviving a merge-error allowance. The point bound is attained by recursive midpoint ordering; the interval bounds provide certificates against which a chosen order can be assessed. They depend on the tree, reference and widths, so the same analysis applies across layout objectives.
```

**改写后**

```latex
The central question is therefore the positional cost of keeping the tree: how much displacement is unavoidable, and how much is introduced by a particular order or placement? We answer progressively for exact point orders, finite-width interval layouts and bounded merge-level error. Recursive midpoint ordering attains the point bound; the interval bounds certify unavoidable cost without asserting that every such certificate is attainable. Because the bounds depend on the tree, reference and widths, they separate structural restrictions from the objectives used to draw a map.
```

## 5. introduction

**改写前**

```latex
AnchorMTM uses these quantities to give the temporal map a shared spatial axis. It fixes a direction from matched feature motion or an analyst's choice, selects a leaf order within a merge budget, places anchors under a displacement cap and reconstructs the scalar profiles. Experiments follow the same argument: test the bounds, measure reference positioning, then inspect what additional merge error buys in complete sequences.
```

**改写后**

```latex
AnchorMTM turns this analysis into a temporal map with one fixed spatial reference. It prepares the trees and feature correspondences, searches orders within a merge budget, optimizes anchors under a displacement cap, and reconstructs the scalar profiles. The evidence follows the same chain: establish the bounds on controlled trees and existing sequences, evaluate absolute positioning, then examine which conflicts a budget releases and how those changes appear in the maps.
```

## 6. related_work

**改写前**

```latex
\subsection{Spatial Coordinates in Temporal Overviews}
```

**改写后**

```latex
\subsection{Domain-, Feature-, and Topology-Based Summaries}
```

## 7. related_work

**改写前**

```latex
One-dimensional projections and MotionRugs summarize moving entities~\cite{Franke:2021:1DP,Buchmueller:2019:MR}. More generally, embeddings trade original-domain relationships against display organization~\cite{Nonato:2019:MP}. Figure~\ref{fig:related-work-mapping} contrasts sample traversal, selected features and hierarchy-preserving profiles. AnchorMTM assigns projected spatial targets to extrema while retaining the profile's scalar and hierarchical representation.
```

**改写后**

```latex
Feature-based approaches organize selected entities and their motion, as in one-dimensional projections and MotionRugs~\cite{Franke:2021:1DP,Buchmueller:2019:MR}. Their emphasis differs from traversing every domain sample. Embeddings more generally balance original-domain relationships against display organization~\cite{Nonato:2019:MP}. Figure~\ref{fig:related-work-mapping} makes the distinction explicit: domain-based traversal retains samples, feature-based summaries select structures of interest, and topology-based profiles retain hierarchical relations. AnchorMTM builds on the last representation and assigns its extrema targets in a fixed physical projection.
```

## 8. related_work

**改写前**

```latex
Topology organizes scalar structures by connectivity~\cite{Heine:2016:Survey}. Landscapes and one-dimensional profiles express these hierarchies geometrically~\cite{Weber:2007:TL,Oesterling:2013:TLP}, including geometry-aware and temporally coherent extensions~\cite{Beketayev:2012:GPTL,Herick:2020:TCTL}. TMTM aligns profiles across time~\cite{Koepp:2023:TMTM}; ST-MTM adds spatial-distance fitting and temporal constraints~\cite{STMTM:2026}. AnchorMTM reuses this profile foundation and gives its axis a fixed origin, direction and scale.
```

**改写后**

```latex
Topology-based representations organize scalar structures through connectivity~\cite{Heine:2016:Survey}. Landscapes and profiles turn the hierarchy into geometry~\cite{Weber:2007:TL,Oesterling:2013:TLP}, with extensions for spatial geometry and temporal coherence~\cite{Beketayev:2012:GPTL,Herick:2020:TCTL}. TMTM aligns these profiles through time~\cite{Koepp:2023:TMTM}; ST-MTM incorporates spatial-distance fitting and temporal constraints~\cite{STMTM:2026}. AnchorMTM retains that scalar-profile foundation. Its additional requirement is that one display coordinate refer to the same physical direction, origin and scale throughout the sequence.
```

## 9. problem_formulation

**改写前**

```latex
\section{Spatially Anchored Merge Tree Maps}
```

**改写后**

```latex
\section{Problem Formulation}
```

## 10. problem_formulation

**改写前**

```latex
\subsection{Trees, Profiles and Feature Identity}
```

**改写后**

```latex
\subsection{Merge Trees, Profiles, and Feature Identity}
```

## 11. problem_formulation

**改写前**

```latex
\subsection{One Reference for the Whole Sequence}
```

**改写后**

```latex
\subsection{Fixed Spatial Reference}
```

## 12. problem_formulation

**改写前**

```latex
\subsection{Layout Model and Errors}
```

**改写后**

```latex
\subsection{A Unified Layout Formulation}
```

## 13. problem_formulation

**改写前**

```latex
A projection can instead follow every $q_i$, but the order $A,C,D,B$ breaks the $A,B$ subtree block. This conflict motivates bounds that hold across objective choices.
```

**改写后**

```latex
\subsection{Conflict Between Topology and Spatial Position}
A projection can follow every $q_i$, but the order $A,C,D,B$ breaks the $A,B$ subtree block. The issue is the interaction between the spatial target order and the contiguous blocks required by a profile. Keeping those blocks may displace anchors; allowing some merge-level error may admit an order closer to the targets. This structural conflict precedes any choice of optimizer.

We address three questions: how much displacement exact topology forces (RQ1), how finite feature widths and interval constraints increase that cost (RQ2), and which conflicts can be released by bounded merge-level error (RQ3). The next section answers them in this order; the construction then uses the same quantities to select and place a map.
```

## 14. position_bounds

**改写前**

```latex
We first bound the point-order obstruction, then include widths, then identify which constraints survive a merge allowance. Suppress $t$, write $[v]^+=\max(v,0)$ and take empty maxima as zero. The supplementary material gives the complete packing derivations; here each bound identifies the particular constraint that the construction must address.
```

**改写后**

```latex
The positional cost comes from two sources: constraints imposed by the hierarchy and additional choices made by a layout. We first isolate the hierarchy in a point model, then account for interval packing, and finally allow controlled changes to merge levels. This progression answers RQ1--RQ3 using the same reference coordinate. Suppress $t$, write $[v]^+=\max(v,0)$ and take empty maxima as zero; complete packing derivations are in the supplementary material.
```

## 15. position_bounds

**改写前**

```latex
Let $[m_X,M_X]$ be the reference hull of subtree $X$ in the reduced equal-level tree.
```

**改写后**

```latex
The first question removes feature width and asks what the hierarchy alone forces. Exact topology keeps sibling subtrees in separate blocks, so their reference hulls determine the cost of choosing either block orientation. Let $[m_X,M_X]$ be the reference hull of subtree $X$ in the reduced equal-level tree.
```

## 16. position_bounds

**改写前**

```latex
The first and last anchors enclose their intervals and gaps up to the permitted anchor slack; sibling contiguity fixes a block orientation. The two canvas ends supply $E_\partial$. The bound has coordinate units, while $\nu^*$ is normalized by $L$.
```

**改写后**

```latex
The first and last anchors must accommodate their intervals and intervening gaps up to the permitted anchor slack. Sibling contiguity chooses a block orientation, while the canvas ends supply $E_\partial$. Thus ordering alone no longer determines the positional cost: even an order attaining the point bound may require additional displacement to fit its intervals. The bound has coordinate units, while $\nu^*$ is normalized by $L$. This motivates evaluating the exact packing cost of each candidate order before optimizing its anchors.
```

## 17. position_bounds

**改写前**

```latex
\subsection{A Bounded Merge Error}
```

**改写后**

```latex
\subsection{Bounded Merge Error}
```

## 18. position_bounds

**改写前**

```latex
The accumulated ancestor gap determines when an outside leaf can enter a block. Flattening parent gaps of at most $2\eta$ gives a second certificate; we use the larger of the two valid bounds. These certificates describe an unavoidable cost. The exact fixed-order value $\tau$ then measures how closely a candidate approaches it.
```

**改写后**

```latex
The accumulated ancestor gap determines which outside leaves may enter a block, so an allowance releases only the conflicts supported by sufficiently small merge-level differences. Flattening parent gaps of at most $2\eta$ gives a second certificate; we use the larger of the two valid bounds. Together, the three results distinguish forced displacement from displacement chosen by a layout. Their algorithmic implication is to search orders using the exact fixed-order cost $\tau$, admit them only when their merge error fits the allowance, and limit additional displacement during anchor placement. A certificate is a lower bound; the construction must still produce and check a feasible map.
```

## 19. anchor_mtm

**改写前**

```latex
\section{AnchorMTM: Approaching the Bounds}
```

**改写后**

```latex
\section{AnchorMTM}
```

## 20. anchor_mtm

**改写前**

```latex
AnchorMTM follows the bounds in two stages: first select a legal order with low $\tau$, then balance spatial and temporal quality within a cap on that order's displacement.
```

**改写后**

```latex
Figure~\ref{fig:framework} summarizes the construction; its topology-budgeted layout panel contains the separate order-search and anchor-placement stages. Extract and Reference prepares the trees, identities and fixed targets defined in Section~\ref{sec:formulation}. Search Leaf Orders chooses an admissible order with low $\tau$. Place Anchors balances spatial and temporal objectives within a cap on that order's displacement. Reconstruct and Assemble builds the scalar profiles and stacks them along time. The output of each stage fixes the constraints passed to the next.
```

## 21. anchor_mtm

**改写前**

```latex
Exact Mode sets $\varepsilon=0$; the exact experiments use zero labelled error. Widths, gap, slack and weights stay fixed during a budget sweep.
```

**改写后**

```latex
Exact Mode sets $\varepsilon=0$; the exact experiments use zero labelled error. Budgeted Mode uses a positive allowance within the same construction. Balanced denotes an experimentally selected positive-budget configuration, not all budgeted maps. Widths, gap, slack and weights stay fixed during a budget sweep; the merge allowance controls hierarchical error rather than directly bounding positional error.
```

## 22. anchor_mtm

**改写前**

```latex
A finite candidate pool $\mathcal C$ starts from midpoint orders of the strict tree, threshold flattenings and selective conflict flattenings. Width-aware block moves refine promising structures. Each visited order is evaluated against the original merge matrix, and selection is lexicographic:
```

**改写后**

```latex
Order search receives the prepared tree, reference targets, widths and merge allowance. A finite candidate pool $\mathcal C$ starts from midpoint orders of the strict tree, threshold flattenings and selective conflict flattenings. Width-aware block moves refine promising structures. The point bound supplies an exact-topology initialization, while the interval analysis motivates evaluating packing displacement. Each visited order is checked against the original merge matrix, and selection is lexicographic:
```

## 23. anchor_mtm

**改写前**

```latex
Unmatched leaves have no temporal penalty. Placement solves the convex quadratic objective under the interval constraints and
```

**改写后**

```latex
The selected order is now fixed, so placement changes coordinates without revisiting the discrete search. Unmatched leaves have no temporal penalty. Placement solves the convex quadratic objective under the interval constraints and
```

## 24. anchor_mtm

**改写前**

```latex
Leaf-arc samples fill the intervals and LCA paths fill their gaps~\cite{Koepp:2023:TMTM,STMTM:2026}.
```

**改写后**

```latex
The final stage receives the order, anchor intervals and optimal barriers. Leaf-arc samples fill the intervals and LCA paths fill their gaps~\cite{Koepp:2023:TMTM,STMTM:2026}.
```

## 25. experiments

**改写前**

```latex
Setup; Q1 controlled/width hits; Q2 baseline-bound diagnostic and positioning; Q3 budgets; Ring/Storms/PM2.5/Cylinder cases interleaved with verification/runtime.
```

**改写后**

```latex
6.1 setup; 6.2 controlled and real bound validation, baseline diagnostic and Table 2; 6.3 absolute positioning; 6.4 budget effects; 6.5 Storms/Cylinder/Ring/PM2.5; 6.6 implementation/runtime. All factual result paragraphs and table cells retained.
```

## 26. discussion_conclusion

**改写前**

```latex
A spatial axis has a quantifiable hierarchical cost. The point bound identifies order error removable without changing the tree; finite-width and budgeted bounds identify remaining constraints. AnchorMTM follows this distinction by choosing an order before optimizing its placement. The experiments connect the controlled optima to real feature trajectories: budgets act on a small difficult tail in Storms and on most frames in the two default volumes.
```

**改写后**

```latex
Keeping merge-tree topology has an unavoidable positional cost. The point bound isolates the part forced by subtree ordering; the width-aware and bounded-error results identify restrictions that remain when intervals and a merge allowance are included. AnchorMTM follows this analysis by selecting an order before optimizing its placement. The evidence connects controlled optima to temporal feature trajectories: relaxation acts on a difficult tail in Storms and on most frames in the two default volume configurations.
```

## 27. discussion_conclusion

**改写前**

```latex
Absolute position, relative geometry and hierarchical unfolding serve different readings of the same map. The curve comparisons and Cylinder guidance example make these choices visible. Tracking quality controls the estimated direction, and a single projection merges perpendicular spatial differences; source snapshots and analyst-selected directions address these ambiguities. Finite-width ordering remains heuristic, and a gap above its lower bound can originate in either the search or the certificate. These issues motivate tighter ordering methods and task-based studies of how readers use the anchored coordinate.
```

**改写后**

```latex
The fixed coordinate supports location and motion along the chosen direction, while relative geometry and hierarchical unfolding support different readings. Neighborhood preservation is therefore a separate objective, as the curve comparisons and Cylinder guidance case illustrate. A single projection merges differences perpendicular to that direction, and matching quality affects the motion samples used to estimate it. Source snapshots and analyst-selected directions provide complementary context. Finite-width ordering remains heuristic; a residual certificate gap may reflect the search or a non-tight bound. The distinct objectives of the case configurations make these choices explicit and motivate tighter ordering methods and task-based evaluation of the anchored coordinate.
```

## 28. discussion_conclusion

**改写前**

```latex
The result is a temporal merge tree map whose coordinate can be read against a fixed spatial reference, with an explicit merge allowance and measured displacement. Three bounds explain the restrictions; the reconstruction checks connect those restrictions to the displayed map.
```

**改写后**

```latex
AnchorMTM thus provides a temporal merge tree map whose positions are read against one fixed spatial reference. The bounds quantify the hierarchical restrictions, the merge budget controls which constraints may be released, and checked reconstruction carries that choice into the displayed map.
```

## 后续指令：流程图替换与图注对应

用户指定的PPTX仅作原版PDF导出。

**原图注**

AnchorMTM: extract and match features; fix spatial references; search admissible leaf orders; optimize anchors under a displacement cap; reconstruct scalar profiles and stack them along time.

**新图注**

Schematic AnchorMTM workflow: extraction and referencing, topology-budgeted layout, and topology-to-1D reconstruction produce the temporal map. The layout panel combines leaf-order search and anchor placement.
