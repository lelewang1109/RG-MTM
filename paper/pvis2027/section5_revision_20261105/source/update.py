from pathlib import Path
import csv,json
W=Path(__file__).resolve().parents[4];P=W/'paper/pvis2027';O=Path(__file__).resolve().parents[1];E=P/'experiments_ratio_p_20261104'
def rows(name):return list(csv.DictReader((E/name).open()))
def main():
 data=rows('comparison_final.csv')+list(csv.DictReader((P/'space_filling_baselines_20261105/results/metrics.csv').open()));params=rows('anchor_parameters.csv');runtime=rows('anchor_runtime.csv');DS=['Gaussian','Ring','Wildfires','Storms'];M=['SNS','TW','NPE']
 def find(ds,method):return next(x for x in data if x['Dataset']==ds and x['Method']==method)
 def cell(ds,method,k):
  x=float(find(ds,method)[k]);values=sorted({round(float(z[k]),4) for z in data if z['Dataset']==ds},reverse=k=='TW');rank=values.index(round(x,4))+1;s=f'{x:.4f}'
  return '$'+(r'\mathbf{'+s+'}' if rank==1 else r'\underline{'+s+'}' if rank==2 else s)+'$'
 baselines=['Hilbert','Morton','TMTM','ST-MTM Temporal']
 tex=[r'\begin{table*}[t]',r'\centering',r'\caption{Quantitative comparison on four datasets. Best and second-best distinct displayed values within each dataset are bold and underlined; ties share emphasis. Hilbert and Morton use their fixed default orientations.}',r'\label{tab:quantitative-final}',r'\footnotesize',r'\setlength{\tabcolsep}{1.5pt}',r'\renewcommand{\arraystretch}{0.85}',r'\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l*{12}{c}lccc@{}}',r'\toprule',r'\multirow{2}{*}{Dataset} & \multicolumn{3}{c}{Hilbert} & \multicolumn{3}{c}{Morton} & \multicolumn{3}{c}{TMTM} & \multicolumn{3}{c}{ST-MTM} & \multicolumn{4}{c}{AnchorMTM (ours)} \\',r'\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}\cmidrule(lr){11-13}\cmidrule(lr){14-17}', ' & '+' & '.join([r'SNS$\downarrow$',r'TW$\uparrow$',r'NPE$\downarrow$']*4+[r'Mode',r'SNS$\downarrow$',r'TW$\uparrow$',r'NPE$\downarrow$'])+r' \\',r'\midrule']
 audit=[]
 for ds in DS:
  for i,mode in enumerate(['Exact','Balanced']):
   leading=[r'\multirow{2}{*}{'+ds+'}']+[r'\multirow{2}{*}{'+cell(ds,method,k)+'}' for method in baselines for k in M] if i==0 else ['']*13
   tex.append(' & '.join(leading+[mode]+[cell(ds,'AnchorMTM '+mode,k) for k in M])+r' \\')
  for method in baselines+['AnchorMTM Exact','AnchorMTM Balanced']:
   for k in M:audit.append(dict(Dataset=ds,Method=method,Metric=k,value=float(find(ds,method)[k]),latex=cell(ds,method,k)))
 tex +=[r'\bottomrule',r'\end{tabular*}',r'\vspace{2pt}',r'\begin{minipage}{\textwidth}\footnotesize TMTM/ST-MTM (Temporal) SNS/TW are quoted from ST-MTM Table~1; all other values are locally measured. Author inputs and coverage are not confirmed identical. Curves linearize grid samples without topology guarantees; default orientation means no rotation, mirror or reversal search. Mode applies only to AnchorMTM. Local TW uses $k=1,3,5,3$ with coverage 64/64, 1/40, 4/32 and 11/744 for Gaussian, Ring, Wildfires and Storms, shared by both curves and AnchorMTM; author coverage is unspecified. Ineligible frames are omitted. Published TW values have only two decimal places.\end{minipage}',r'\end{table*}']
 (O/'table1_comparison.tex').write_text('\n'.join(tex)+'\n')
 tex=[r'\begin{table}[t]',r'\centering',r'\caption{Balanced-mode parameter settings and runtime (seconds).}',r'\label{tab:anchor-parameters-final}',r'\footnotesize',r'\setlength{\tabcolsep}{2pt}',r'\renewcommand{\arraystretch}{0.95}',r'\begin{tabular}{@{}lcccc@{}}',r'\toprule',r'Parameter & Gaussian & Ring & Wildfires & Storms \\',r'\midrule']
 pp={d:next(x for x in params if x['Dataset']==d) for d in DS}
 tt={d:next(x for x in runtime if x['Dataset']==d and x['Method']=='AnchorMTM Balanced') for d in DS}
 entries=[(r'$\varepsilon$',lambda d:f"{100*float(tt[d]['epsilon']):g}\\%"),(r'$L$',lambda d:pp[d]['L_pixels']),(r'$s_w$',lambda d:f"{float(pp[d]['width_scale']):.5f}"),(r'$t_{opt}$',lambda d:f"{float(tt[d]['t_opt']):.3f}"),(r'$t_{total}$',lambda d:f"{float(tt[d]['t_total']):.3f}")]
 for label,fmt in entries:tex.append(' & '.join([label]+[fmt(d) for d in DS])+r' \\')
 tex +=[r'\bottomrule',r'\end{tabular}',r'\vspace{2pt}',r'\begin{minipage}{\columnwidth}\footnotesize Weights $(4,1,0.5,0.1)$ and $\rho=0.5$ are fixed. $s_w$ is width per support measure; $L$ is raster length. Times are one run on Apple M4: optimization and full pipeline, respectively.\end{minipage}',r'\end{table}']
 (O/'table2_parameters_runtime.tex').write_text('\n'.join(tex)+'\n')
 with (O/'ranking_audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(audit[0]),lineterminator="\n");w.writeheader();w.writerows(audit)
 source=P/'drafts/method_anchor_figures_updated_en.tex';s=source.read_text();a=s.index(r'\section{Experiments}');b=s.index(r'\section{Discussion and Limitations}',a)
 section=r'''\section{Experiments}\label{sec:experiments}
\input{../section5_revision_20261105/table1_comparison.tex}
\input{../section5_revision_20261105/table2_parameters_runtime.tex}
\subsection{Experimental Setup}
We study Gaussian, Ring, Wildfires and Storms, containing 64, 40, 32 and 744 frames, respectively. The raster length is 4096 except for Ring, which retains 196. We interpret the ST-MTM Table~1 persistence numbers as scalar-range fractions: $p=(0.001,0.001,0.15,0.105)$, and simplify each frame at $p(F_{\max}^t-F_{\min}^t)$~\cite{STMTM:2026}. This explicitly tested interpretation corresponds to $0.1\%,0.1\%,15\%,10.5\%$; all 880 thresholds were checked.

The local inputs are a three-peak Gaussian reconstruction, the archived Ring generator, Wildfires FRP aggregated into 32 equal-duration spatial grids, and 744 ERA5 Storms anomaly fields with the archived moving-mean and smoothing convention. The authors' final processed arrays are unavailable for confirmation. Consequently, we distinguish published results from measurements on our reconstructed inputs rather than claiming an identical-input reproduction. All local layouts share trees, leaf identities, support-overlap tracks, extremum references, a fixed offline direction and a common projected range. We do not independently realign or rescale baselines in each frame.

We use three complementary metrics. SNS measures relative geometry as squared scale-normalized stress between support-centroid distances and displayed anchor distances, averaged over eligible frames~\cite{Smelser:2025:Scale,STMTM:2026}. TW measures neighborhood preservation~\cite{Venna:2001:NP}; we use the published $k=(1,3,5,3)$ and require $0<k<n_t/2$. Ineligible frames are omitted, not assigned zero. Absolute spatial anchoring is measured by
\begin{equation}\label{eq:experimental-npe}
\mathrm{NPE}=\frac{1}{T}\sum_t\frac{\max_i|x_i^t-q_i^t|}{L_{world}}.
\end{equation}
TMTM and ST-MTM SNS/TW are quoted from the latter's Table~1, using its Temporal mode for ST-MTM. Their NPE is measured separately with the local shared references and fixed canvas convention. The published SNS/TW and local NPE therefore have different provenance; Table~\ref{tab:quantitative-final} keeps this distinction explicit.

We additionally evaluate fixed Hilbert and Morton sample-domain linearizations, following the use of space-filling curves for spatio-temporal 1D projections~\cite{Franke:2021:1DP}. The canonical grid orientation is frozen: columns are $x$, rows are $y$, with no rotation, mirror or traversal-reversal search. A minimal power-of-two square is used for curve indexing; out-of-domain samples are discarded. Each original extremum receives its full-grid curve rank, normalized to the shared canvas and rounded at the original raster length. The same support centroids, extremum identities and physical reference targets are used for evaluation. These baselines do not enforce merge-tree topology or finite feature widths. Direction-tuned exploratory results remain separate from the default configurations reported here.

\paragraph{Mode selection.}
Exact fixes $\varepsilon=0$. Balanced retains a positive budget, selected separately for each dataset on the first chronological quarter from 1--10\% in steps of 1\%. Among legal reconstructions satisfying actual NMLE$_{\max}\le\varepsilon$, we minimize
\begin{equation}\label{eq:balanced-validation-score}
J=0.5\,\mathrm{NPE}_{norm}+0.5\,\mathrm{SNS}_{norm}.
\end{equation}
Each term is min--max normalized across legal validation candidates, with constant terms contributing zero. Within 0.01 of minimum $J$, we prefer smaller budgets and then smaller attained errors. Budgets are frozen before complete runs; no minimum-improvement requirement or zero-budget fallback is imposed. Full-sequence results include the validation segment. Earlier outputs were observed, so these are exploratory results, not a new blind test.

\subsection{Quantitative Comparison}
Table~\ref{tab:quantitative-final} groups five method families and shows both AnchorMTM modes. The comparison separates absolute anchoring from relative geometry: neither one implies the other.

\paragraph{Relative geometry.}
Against the reported ST-MTM values, Balanced has lower SNS on all four datasets: 0.0353 versus 0.0600 on Gaussian, 0.1334 versus 0.2100 on Ring, 0.0447 versus 0.2400 on Wildfires, and 0.0743 versus 0.2100 on Storms. These are favorable descriptive comparisons under the documented reconstruction conventions, not proof of dominance on the authors' exact processed fields.

\paragraph{Neighborhoods and coverage.}
ST-MTM reports higher TW than Balanced on all four datasets. Its relative-distance and temporal-placement objectives can preserve neighborhoods without assigning display coordinates to a fixed physical reference. AnchorMTM instead also respects reference targets, finite feature widths and a topology allowance, which can require a different ordering or spacing. This explains a possible trade-off, not a demonstrated failure of ST-MTM's technique. Furthermore, our Ring, Wildfires and Storms TW values use only 1, 4 and 11 eligible frames. Their coverage differs from the unreported author protocol, so these numbers cannot establish a reliable full-sequence neighborhood ranking. Wildfires Exact's 0.9136 is also too close to the published two-decimal 0.91 to establish superiority.

\paragraph{Space-filling curves.}
Balanced has lower SNS and higher TW than both default curves on Gaussian, Wildfires and Storms. Ring is an exception: Hilbert has SNS 0.1252 and TW 0.9048, compared with Balanced's 0.1334 and 0.8571. Ring TW uses only one eligible frame and cannot establish a full-sequence neighborhood advantage. Both curves have higher NPE than Balanced on all four inputs. Curve traversal coordinates do not represent the chosen physical projection axis, so this NPE difference measures reference alignment rather than general visualization quality; their lack of topology guarantees also distinguishes their task from merge-tree mapping.

\paragraph{Absolute anchoring.}
On the shared local inputs, Balanced has lower NPE than the two merge-tree baseline adapters and both default curves on every dataset. Relative to the ST-MTM adapter, the reductions are approximately 92.3\%, 84.0\%, 96.3\% and 96.9\%, respectively. Relative-distance optimization leaves the coordinate origin and reference direction unspecified; temporal regularization stabilizes display positions but does not enforce correspondence to our physical targets. AnchorMTM explicitly constrains this correspondence. These results support the intended absolute-position task, while the TW results retain the associated neighborhood limitations.

\subsection{Topology Budgets and Reconstruction Validity}
The requested budgets are listed in Table~\ref{tab:anchor-parameters-final}; reconstructed topology errors are checked independently. Exact has zero error in the complete fixed-leaf merge matrix on all four inputs. Balanced attains maximum normalized errors of 0, 0.982\%, 4.421\% and 9.985\%, all within its respective allowance. No continuous or rendered budget violation, collapsed-anchor frame or layout failure occurs in the eight complete runs. The checks cover the fixed leaf labels and diagonal extremum values, not every internal label of an augmented tree or every finite-root extension.

Ring is reconstructed at the original 196 positions. A checked joint-integer-rounding adapter is required in 26 Exact and 21 Balanced frames; it preserves the continuous order and barrier-pixel requirements without increasing the topology budget. Thus integer feasibility is checked explicitly rather than concealed by a larger raster.

\subsection{Interpreting the Spatial Reference}
The spatial-reference task is illustrated by Fig.~\ref{fig:storms_overview}: source supports identify where a matched extremum lies, while the temporal map exposes its displayed trajectory. The reference gives that display coordinate a consistent spatial meaning; it does not make overlap-based tracks verified physical storm identities. This qualitative archive uses separate preprocessing and a 5\% budget, and is not a visual rendering of the newly selected 10\% quantitative Storms configuration. The projection-conflict examples in Section~\ref{sec:method} explain why a spatial target may conflict with a hierarchy; they are explanatory examples rather than additional measured datasets.

\subsection{Budget Sensitivity and Performance}
The two modes share the algorithm and fixed QP weights; their comparison tests budget effects rather than removing components. Balanced reduces NPE relative to Exact by approximately 17.0\% on Ring, 11.0\% on Wildfires and 65.0\% on Storms. Gaussian retains identical outputs despite its positive 1\% budget, which we report without inventing a benefit. SNS improves on Ring and Storms but increases from 0.0426 to 0.0447 on Wildfires. Thus relaxing topology does not improve every metric. The complete 40 positive validation candidates and independent full-run checks remain archived.

Table~\ref{tab:anchor-parameters-final} reports one uncached Balanced pipeline execution per dataset on Apple M4; Exact timings are retained in the archive. BLAS and native TTK use one thread; extraction is sequential and HiGHS retains its default scheduler. Optimization covers ordering and continuous placement. Total time includes source preprocessing, tree extraction and I/O, feature matching/reference estimation, optimization, integer reconstruction and intrinsic checks; metric export, report generation and process imports are excluded. Baseline NPE uses disclosed CompactTMTM multiway and ST-MTM equal-level/same-equation solver adaptations rather than author binaries. OS page caches may be warm. The timings describe these runs and do not support statistical speedup or cross-hardware claims.

'''
 source.write_text(s[:a]+section+s[b:])
 print('SECTION5_UPDATED')
if __name__=='__main__':main()
