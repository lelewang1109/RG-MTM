# 论文与相关项目索引

此索引从当前正文实际使用的 BibTeX 提取，共 80 条；完整作者、期刊、卷页和引用键以 [refs.bib](../paper/manuscript/latex/refs.bib) 为准。这里整理本项目已有参考文献，不声称覆盖领域全部研究。第三方阅读 PDF 保留在本地，使用 DOI 或作者来源访问原文。

## 核心方法与实现

| 项目/方法 | 入口 | 与本项目关系 |
|---|---|---|
| Temporal Merge Tree Maps | [论文](https://doi.org/10.1109/TVCG.2022.3209387) · [作者代码](https://github.com/Wiebke/TemporalMergeTreeMaps) | 拓扑时序地图基线，原始实现核对见 code/experiments/volume3d/audit_tangaroa.py |
| Spatiotemporal Merge Tree Maps | [论文预印本](https://doi.org/10.2139/ssrn.6604235) | 几何感知基线；本项目实现/参数核对见 code/experiments/baseline_audit |
| Topology ToolKit | [固定 0.9.9 源码](https://github.com/topology-tool-kit/ttk/tree/0.9.9) | 合并树提取依赖，构建脚本见 code/experiments/volume3d/build_native_ttk.py |
| RG-MTM | [方法实现](../code/src/rgmtm) · [实验目录](../code/experiments) | 本仓库参考引导方法与可复现证据 |

## 当前稿参考文献

| 引用键 | 年份 | 论文/来源 |
|---|---|---|
| Koepp:2023:TMTM | 2023 | [Temporal Merge Tree Maps: A Topology-Based Static Visualization for Temporal Scalar Data](https://doi.org/10.1109/tvcg.2022.3209387) |
| STMTM:2026 | 2026 | [Spatiotemporal Merge Tree Maps: A Topology and Geometry Aware Visualization for Temporal Scalar Data](https://doi.org/10.2139/ssrn.6604235) |
| Franke:2021:1DP | 2021 | [Visual Analysis of Spatio-temporal Phenomena with 1D Projections](https://doi.org/10.1111/cgf.14311) |
| Zhou:2021:DSF | 2021 | [Data-Driven Space-Filling Curves](https://doi.org/10.1109/tvcg.2020.3030473) |
| Hovmoller:1949 | 1949 | [The Trough-and-Ridge Diagram](https://doi.org/10.1111/j.2153-3490.1949.tb01260.x) |
| Keim:2000:PIX | 2000 | [Designing Pixel-Oriented Visualization Techniques: Theory and Applications](https://doi.org/10.1109/2945.841121) |
| Buchmueller:2019:MR | 2019 | [MotionRugs: Visualizing Collective Trends in Space and Time](https://doi.org/10.1109/tvcg.2018.2865049) |
| Wulms:2021:SVS | 2021 | [Stable Visual Summaries for Trajectory Collections](https://doi.org/10.1109/pacificvis52677.2021.00016) |
| Valdrighi:2024:MRV | 2024 | [MoReVis: A Visual Summary for Spatiotemporal Moving Regions](https://doi.org/10.1109/tvcg.2023.3250166) |
| Stolk:2025:GR | 2025 | [GroupRugs: Visual Summaries for Groups in Collective Movement Data](https://doi.org/10.1109/pacificvis64226.2025.00019) |
| Beurskens:2025:ParkView | 2025 | [ParkView: Visualizing Monotone Interleavings](https://doi.org/10.1109/pacificvis64226.2025.00018) |
| Weber:2007:TL | 2007 | [Topological Landscapes: A Terrain Metaphor for Scientific Data](https://doi.org/10.1109/tvcg.2007.70601) |
| Beketayev:2012:GPTL | 2012 | [Geometry-Preserving Topological Landscapes](https://doi.org/10.1145/2425296.2425324) |
| BarJoseph:2001:OLO | 2001 | [Fast Optimal Leaf Ordering for Hierarchical Clustering](https://doi.org/10.1093/bioinformatics/17.suppl_1.s22) |
| Eisen:1998:CA | 1998 | [Cluster Analysis and Display of Genome-Wide Expression Patterns](https://doi.org/10.1073/pnas.95.25.14863) |
| Klawitter:2025:GP | 2025 | [Visualizing Geophylogenies -- Internal and External Labeling with Phylogenetic Tree Constraints](https://doi.org/10.7155/jgaa.v29i1.2975) |
| Bulteau:2022:RT | 2022 | [Reordering a Tree According to an Order on Its Leaves](https://doi.org/10.4230/LIPIcs.CPM.2022.24) |
| Huson:2026:DOT | 2026 | [Displacement-Optimized Tanglegrams for Trees and Networks](https://doi.org/10.1093/molbev/msag066) |
| McNutt:2020:SVM | 2020 | [Surfacing Visualization Mirages](https://doi.org/10.1145/3313831.3376420) |
| Wattenberg:2016:TSNE | 2016 | [How to Use t-SNE Effectively](https://doi.org/10.23915/distill.00002) |
| Venna:2001:NP | 2001 | [Neighborhood Preservation in Nonlinear Projection Methods: An Experimental Study](https://doi.org/10.1007/3-540-44668-0_68) |
| Aupetit:2007:VD | 2007 | [Visualizing Distortions and Recovering Topology in Continuous Projection Techniques](https://doi.org/10.1016/j.neucom.2006.11.018) |
| Rauscher:2026:VB | 2026 | [Visual Boosting Techniques for Spatiotemporal Dense Pixel Visualizations](https://doi.org/10.2312/eurova.20261004) |
| Rauscher:2025:1DO | 2025 | [Visually Assessing 1-D Orderings of Contiguous Spatial Polygons](https://doi.org/10.1111/cgf.70100) |
| Nusrat:2016:CART | 2016 | [The State of the Art in Cartograms](https://doi.org/10.1111/cgf.12932) |
| vanBeusekom:2023:DSL | 2023 | [Data-Spatial Layouts for Grid Maps](https://doi.org/10.4230/LIPIcs.GIScience.2023.10) |
| Wood:2008:SOT | 2008 | [Spatially Ordered Treemaps](https://doi.org/10.1109/tvcg.2008.165) |
| Meulemans:2026:AP | 2026 | [An Algorithmic Perspective on Information Visualization](https://doi.org/10.48550/arXiv.2607.29360) |
| Kindlmann:2014:AVD | 2014 | [An Algebraic Process for Visualization Design](https://doi.org/10.1109/tvcg.2014.2346325) |
| Li:2019:SOI | 2019 | [Separating Overlapped Intervals on a Line](https://doi.org/10.20382/jocg.v10i1a11) |
| Dwyer:2006:IPSEP | 2006 | [IPSep-CoLa: An Incremental Procedure for Separation Constraint Layout of Graphs](https://doi.org/10.1109/tvcg.2006.156) |
| Morozov:2013:IDMT | 2013 | [Interleaving Distance between Merge Trees](https://mrzv.org/publications/interleaving-distance-merge-trees/) |
| Munch:2019:LINF | 2019 | [The $\ell^\infty$-Cophenetic Metric for Phylogenetic Trees as an Interleaving Distance](https://doi.org/10.1007/978-3-030-11566-1_5) |
| Smelser:2025:Scale | 2025 | [How Scale Breaks ``Normalized Stress'' and KL Divergence: Rethinking Quality Metrics](https://doi.org/10.48550/arXiv.2510.08660) |
| Gasparovic:2024:IID | 2025 | [Intrinsic Interleaving Distance for Merge Trees](https://doi.org/10.1007/s44007-024-00143-9) |
| Yan:2022:GAMT | 2023 | [Geometry-Aware Merge Tree Comparisons for Time-Varying Data with Interleaving Distances](https://doi.org/10.1109/tvcg.2022.3163349) |
| Yan:2024:TROPHY | 2024 | [TROPHY: A Topologically Robust Physics-Informed Tracking Framework for Tropical Cyclones](https://doi.org/10.1109/tvcg.2023.3326905) |
| Lan:2024:AR | 2024 | [Topological Characterization and Uncertainty Visualization of Atmospheric Rivers](https://doi.org/10.1111/cgf.15084) |
| Pont:2022:WMT | 2022 | [Wasserstein Distances, Geodesics and Barycenters of Merge Trees](https://doi.org/10.1109/tvcg.2021.3114839) |
| Koepp:2019:TT | 2019 | [Temporal Treemaps: Static Visualization of Evolving Trees](https://doi.org/10.1109/tvcg.2018.2865265) |
| Lukasczyk:2017:NTG | 2017 | [Nested Tracking Graphs](https://doi.org/10.1111/cgf.13164) |
| Hersbach:2020:ERA5 | 2020 | [The ERA5 Global Reanalysis](https://doi.org/10.1002/qj.3803) |
| Edelsbrunner:2002:TPS | 2002 | [Topological Persistence and Simplification](https://doi.org/10.1007/s00454-002-2885-2) |
| Carr:2004:SFI | 2004 | [Simplifying Flexible Isosurfaces Using Local Geometric Measures](https://doi.org/10.1109/visual.2004.96) |
| Tierny:2012:GTS | 2012 | [Generalized Topological Simplification of Scalar Fields on Surfaces](https://doi.org/10.1109/tvcg.2012.228) |
| Farach:1995:RM | 1995 | [A Robust Model for Finding Optimal Evolutionary Trees](https://doi.org/10.1007/bf01188585) |
| Chepoi:2000:LIA | 2000 | [$\ell_\infty$-Approximation via Subdominants](https://doi.org/10.1006/jmps.1999.1270) |
| Eldridge:2015:MD | 2015 | [Beyond Hartigan Consistency: Merge Distortion Metric for Hierarchical Clustering](https://proceedings.mlr.press/v40/Eldridge15.html) |
| Liu:2013:SF | 2013 | [StoryFlow: Tracking the Evolution of Stories](https://doi.org/10.1109/tvcg.2013.196) |
| Nguyen:2013:FGV | 2013 | [On the Faithfulness of Graph Visualizations](https://doi.org/10.1109/pacificvis.2013.6596147) |
| Nonato:2019:MP | 2019 | [Multidimensional Projection for Visual Analytics: Linking Techniques with Distortions, Tasks, and Layout Enrichment](https://doi.org/10.1109/tvcg.2018.2846735) |
| Rieck:2015:PH | 2015 | [Persistent Homology for the Evaluation of Dimensionality Reduction Schemes](https://doi.org/10.1111/cgf.12655) |
| Doraiswamy:2021:TM | 2021 | [TopoMap: A 0-dimensional Homology Preserving Projection of High-Dimensional Data](https://doi.org/10.1109/tvcg.2020.3030441) |
| NOAA:OLR | 2011 | [NOAA Climate Data Record of Daily Outgoing Longwave Radiation, Version 1.2](https://doi.org/10.7289/V5SJ1HH2) |
| Dong:2026:PM25 | 2026 | [An Integrated Dataset of PM2.5, Elevation, and Meteorological Variables over China at a 10-km Resolution (2000--2023)](https://doi.org/10.57760/sciencedb.35623) |
| Popinet:2004:Tangaroa | 2004 | [Experimental and Numerical Study of the Turbulence Characteristics of Airflow around a Research Vessel](https://doi.org/10.1175/1520-0426(2004)021<1575:EANSOT>2.0.CO;2) |
| Lukasczyk:2020:DNTG | 2020 | [Dynamic Nested Tracking Graphs](https://doi.org/10.1109/TVCG.2019.2934368) |
| Saikia:2017:GFT | 2017 | [Global Feature Tracking and Similarity Estimation in Time-Dependent Scalar Fields](https://doi.org/10.1111/cgf.13163) |
| Tversky:2002:Animation | 2002 | [Animation: Can It Facilitate?](https://doi.org/10.1006/ijhc.2002.1017) |
| Tierny:2018:TTK | 2018 | [The Topology ToolKit](https://doi.org/10.1109/TVCG.2017.2743938) |
| Widanagamaachchi:2012:DTG | 2012 | [Interactive exploration of large-scale time-varying data using dynamic tracking graphs](https://doi.org/10.1109/ldav.2012.6378962) |
| Weissenboeck:2019:DVL | 2019 | [Dynamic Volume Lines: Visual Comparison of 3D Volumes through Space-filling Curves](https://doi.org/10.1109/tvcg.2018.2864510) |
| Samtaney:1994:Tracking | 1994 | [Visualizing Features and Tracking Their Evolution](https://doi.org/10.1109/2.299407) |
| Silver:1997:Tracking | 1997 | [Tracking and Visualizing Turbulent 3D Features](https://doi.org/10.1109/2945.597796) |
| Bach:2017:STC | 2017 | [A Descriptive Framework for Temporal Data Visualizations Based on Generalized Space-Time Cubes](https://doi.org/10.1111/cgf.12804) |
| Robertson:2008:Animation | 2008 | [Effectiveness of Animation in Trend Visualization](https://doi.org/10.1109/tvcg.2008.125) |
| Oesterling:2017:TVMT | 2017 | [Computing and Visualizing Time-Varying Merge Trees for High-Dimensional Data](https://doi.org/10.1007/978-3-319-44684-4_5) |
| Dafner:2000:CSFC | 2000 | [Context-based Space Filling Curves](https://doi.org/10.1111/1467-8659.00413) |
| Guo:2006:SpatialOrder | 2006 | [Spatial ordering and encoding for geographic data mining and visualization](https://doi.org/10.1007/s10844-006-9952-8) |
| Lohfink:2020:FCT | 2020 | [Fuzzy Contour Trees: Alignment and Joint Layout of Multiple Contour Trees](https://doi.org/10.1111/cgf.13985) |
| Wetzels:2022:BDI | 2022 | [Branch Decomposition-Independent Edit Distances for Merge Trees](https://doi.org/10.1111/cgf.14547) |
| Bremer:2010:Burning | 2010 | [Analyzing and Tracking Burning Structures in Lean Premixed Hydrogen Flames](https://doi.org/10.1109/tvcg.2009.69) |
| Yan:2021:Survey | 2021 | [Scalar Field Comparison with Topological Descriptors: Properties and Applications for Scientific Visualization](https://doi.org/10.1111/cgf.14331) |
| Camarri:2005:Cylinder | 2005 | Simulation of the Three-Dimensional Flow around a Square Cylinder between Parallel Walls at Moderate Reynolds Numbers |
| Weinkauf:SquareCylinder |  | [3D Flow around a Confined Square Cylinder](https://tinoweinkauf.net/notes/squarecylinder.html) |
| Funck:2008:Smoke | 2008 | [Smoke Surfaces: An Interactive Flow Visualization Technique Inspired by Real-World Flow Experiments](https://doi.org/10.1109/TVCG.2008.163) |
| Jorgensen:2013:BOSS | 2013 | [BOSS, Version 4.9: User's Manual](https://zarbi.chem.yale.edu/doc/boss49.pdf) |
| Inviwo:BenzeneGeometry |  | [Benzene Molecular Cube: Atomic Coordinate Header](https://github.com/inviwo/modules/blob/6152a00ab100ec10c1eb36f078fb42dc949010ab/molvis/gaussian/data/volumes/benzene-dens.cube.xz) |
| NaturalEarth:Admin1 |  | [Admin 1 -- States and Provinces, 1:50m](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-1-states-provinces/) |
| NaturalEarth:WildfireAdmin1 |  | [Admin 1 -- States and Provinces, 1:10m](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/) |
