from pathlib import Path
import csv,json
W=Path(__file__).resolve().parents[4];P=W/'paper/pvis2027';O=Path(__file__).resolve().parents[1];E=P/'experiments_ratio_p_20261104'
def rows(name):return list(csv.DictReader((E/name).open()))
def main():
 data=rows('comparison_final.csv');params=rows('anchor_parameters.csv');runtime=rows('anchor_runtime.csv');DS=['Gaussian','Ring','Wildfires','Storms'];M=['SNS','TW','NPE']
 def find(ds,method):return next(x for x in data if x['Dataset']==ds and x['Method']==method)
 def cell(ds,method,k):
  x=float(find(ds,method)[k]);values=sorted({round(float(z[k]),4) for z in data if z['Dataset']==ds},reverse=k=='TW');rank=values.index(round(x,4))+1;s=f'{x:.4f}'
  return '$'+(r'\mathbf{'+s+'}' if rank==1 else r'\underline{'+s+'}' if rank==2 else s)+'$'
 tex=[r'\begin{table*}[t]',r'\centering',r'\caption{Four-dataset quantitative comparison. TMTM and ST-MTM (Temporal mode) SNS/TW are reported values from ST-MTM Table~1; AnchorMTM values and all NPE values are locally measured. Bold/underline mark the best/second distinct displayed value within each dataset, including ties. This numerical comparison does not establish identical author inputs or evaluation coverage.}',r'\label{tab:quantitative-final}',r'\footnotesize',r'\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{lrrrrrrlrrr}',r'\toprule',r'\multirow{2}{*}{Dataset} & \multicolumn{3}{c}{TMTM} & \multicolumn{3}{c}{ST-MTM} & \multicolumn{4}{c}{AnchorMTM (our method)} \\',r'\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-11}',r' & SNS$\downarrow$ & TW$\uparrow$ & NPE$\downarrow$ & SNS$\downarrow$ & TW$\uparrow$ & NPE$\downarrow$ & Mode & SNS$\downarrow$ & TW$\uparrow$ & NPE$\downarrow$ \\',r'\midrule']
 audit=[]
 for ds in DS:
  for i,mode in enumerate(['Exact','Balanced']):
   leading=[r'\multirow{2}{*}{'+ds+'}']+[r'\multirow{2}{*}{'+cell(ds,method,k)+'}' for method in ['TMTM','ST-MTM Temporal'] for k in M] if i==0 else ['']*7
   tex.append(' & '.join(leading+[mode]+[cell(ds,'AnchorMTM '+mode,k) for k in M])+r' \\')
  tex.append(r'\addlinespace[1pt]')
  for method in ['TMTM','ST-MTM Temporal','AnchorMTM Exact','AnchorMTM Balanced']:
   for k in M:audit.append(dict(Dataset=ds,Method=method,Metric=k,value=float(find(ds,method)[k]),latex=cell(ds,method,k)))
 tex +=[r'\bottomrule',r'\end{tabular}',r'\vspace{2pt}',r'\begin{minipage}{\textwidth}\footnotesize Mode applies to AnchorMTM; baseline entries are shared by both rows. TW uses $k=1,3,5,3$ for Gaussian, Ring, Wildfires and Storms. AnchorMTM TW coverage is respectively 64/64, 1/40, 4/32 and 11/744 in both modes; author coverage is unspecified. Ineligible frames are omitted. Published TW values have only two decimal places, so apparent small differences are not evidence of superiority.\end{minipage}',r'\end{table*}']
 (O/'table1_comparison.tex').write_text('\n'.join(tex)+'\n')
 tex=[r'\begin{table}[t]',r'\centering',r'\caption{Balanced-mode parameters and runtime (seconds) on Apple M4; one measured run per dataset.}',r'\label{tab:anchor-parameters-final}',r'\footnotesize',r'\setlength{\tabcolsep}{2.5pt}',r'\begin{tabular}{lrrrrr}',r'\toprule',r'Dataset & $\varepsilon$ & $L$ & $s_w$ & $t_{opt}$ & $t_{total}$ \\',r'\midrule']
 topology=rows('topology_validation.csv')
 for ds in DS:
  p=next(x for x in params if x['Dataset']==ds)
  for mode in ['Balanced']:
   t=next(x for x in runtime if x['Dataset']==ds and x['Method']=='AnchorMTM '+mode);v=next(x for x in topology if x['Dataset']==ds and x['Method']=='AnchorMTM '+mode)
   tex.append(f"{ds} & {100*float(t['epsilon']):g}\\% & {p['L_pixels']} & {float(p['width_scale']):.5f} & {float(t['t_opt']):.3f} & {float(t['t_total']):.3f}"+r' \\')
  tex.append(r'\addlinespace[1pt]')
 tex +=[r'\bottomrule',r'\end{tabular}',r'\vspace{2pt}',r'\begin{minipage}{\columnwidth}\footnotesize Weights $(4,1,0.5,0.1)$ and $\rho=0.5$ are fixed. $s_w$ is width per support measure; $L$ is raster length. Optimization covers ordering/placement; total includes the full pipeline.\end{minipage}',r'\end{table}']
 (O/'table2_parameters_runtime.tex').write_text('\n'.join(tex)+'\n')
 with (O/'ranking_audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
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

\paragraph{Mode selection.}
Exact fixes $\varepsilon=0$. Balanced retains a positive budget, selected separately for each dataset on the first chronological quarter from 1--10\% in steps of 1\%. Among legal reconstructions satisfying actual NMLE$_{\max}\le\varepsilon$, we minimize
\begin{equation}\label{eq:balanced-validation-score}
J=0.5\,\mathrm{NPE}_{norm}+0.5\,\mathrm{SNS}_{norm}.
\end{equation}
Each term is min--max normalized across legal validation candidates, with constant terms contributing zero. Within 0.01 of minimum $J$, we prefer smaller budgets and then smaller attained errors. Budgets are frozen before complete runs; no minimum-improvement requirement or zero-budget fallback is imposed. Full-sequence results include the validation segment. Earlier outputs were observed, so these are exploratory results, not a new blind test.

\subsection{Quantitative Comparison}
Table~\ref{tab:quantitative-final} groups the three method families and shows both AnchorMTM modes. The comparison separates absolute anchoring from relative geometry: neither one implies the other.

\paragraph{Relative geometry.}
Against the reported ST-MTM values, Balanced has lower SNS on all four datasets: 0.0353 versus 0.0600 on Gaussian, 0.1334 versus 0.2100 on Ring, 0.0447 versus 0.2400 on Wildfires, and 0.0743 versus 0.2100 on Storms. These are favorable descriptive comparisons under the documented reconstruction conventions, not proof of dominance on the authors' exact processed fields.

\paragraph{Neighborhoods and coverage.}
ST-MTM reports higher TW than Balanced on all four datasets. Its relative-distance and temporal-placement objectives can preserve neighborhoods without assigning display coordinates to a fixed physical reference. AnchorMTM instead also respects reference targets, finite feature widths and a topology allowance, which can require a different ordering or spacing. This explains a possible trade-off, not a demonstrated failure of ST-MTM's technique. Furthermore, our Ring, Wildfires and Storms TW values use only 1, 4 and 11 eligible frames. Their coverage differs from the unreported author protocol, so these numbers cannot establish a reliable full-sequence neighborhood ranking. Wildfires Exact's 0.9136 is also too close to the published two-decimal 0.91 to establish superiority.

\paragraph{Absolute anchoring.}
On the shared local inputs, Balanced has lower NPE than both baseline adapters on every dataset. Relative to the ST-MTM adapter, the reductions are approximately 92.3\%, 84.0\%, 96.3\% and 96.9\%, respectively. Relative-distance optimization leaves the coordinate origin and reference direction unspecified; temporal regularization stabilizes display positions but does not enforce correspondence to our physical targets. AnchorMTM explicitly constrains this correspondence. These results support the intended absolute-position task, while the TW results retain the associated neighborhood limitations.

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
