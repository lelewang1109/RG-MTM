"""Publish only measured ratio-p outputs; all selected budgets and conclusions are data-driven."""
from pathlib import Path
import json,re,shutil
O=Path(__file__).resolve().parents[1];P=O.parent
DS=['Gaussian','Ring','Wildfires','Storms']
def read(p):return json.loads(p.read_text())
def f(x,n=4):return 'N/A' if x is None else f'{x:.{n}f}'
def main():
 a=read(O/'assembled.json');assert read(O/'verification.json')['all_passed'];rr=a['comparison'];mm=a['measured'];pp=a['parameters'];tt=a['topology'];rt=a['runtime'];audit=a['input_audit']
 selection='、'.join(x['Dataset']+f" {100*x['epsilon_Balanced']:g}%" for x in pp)
 lines=['# 四数据集：持久性参数按标量范围比例解释的重算','',f'四数据集均完成Exact与正预算Balanced，共8组。Balanced重新验证选择：{selection}。主表包含TMTM、ST-MTM Temporal、AnchorMTM Exact和Balanced，共16行；Base不展示。','',
 '此次严格执行用户指定的比例解释：p=(0.001,0.001,0.15,0.105)，对应0.1%、0.1%、15%、10.5%。实际阈值为p×每帧预处理标量范围。旧结果在../experiments_final_20261104保留，本轮独立目录未复用旧简化树、布局、指标或时间；仅复用完全相同的简化前场及坐标用于验证缓存。','',
 '这是对ST-MTM Table1参数单位的一种明确测试，不把未公开的作者最终预处理数组、TD单位或TW小样本规则当成已经确认。Gaussian/Wildfires与Storms保留明确标注的重建约定。','',
 '## 输入与p阈值核对','',
 '| Dataset | 尺寸/T | p比例 | 百分比 | 实际叶特征数 | 原表特征数 |','|---|---|---:|---:|---:|---:|']
 ref={'Gaussian':'3','Ring':'1–7','Wildfires':'2–34','Storms':'1–8'}
 for x in audit:lines.append(f"| {x['Dataset']} | {x['nx']}×{x['ny']}/{x['T']} | {x['p_fraction']:g} | {x['p_percent']:g}% | {x['features_min']}–{x['features_max']} | {ref[x['Dataset']]} |")
 lines+=['','p_threshold_validation.csv保存全部880帧的Fmin、Fmax、p比例、预期和实际绝对简化阈值，独立核对全部通过。源场和原QP权重不变，Ring仍使用196点画布。','',
 'Gaussian仍是明确三峰重建；Ring复用归档作者生成器；Wildfires保留61天FRP积分为32个等长时间窗、64×64求和、无额外平滑的重建；Storms仍为281×181、744帧ERA5，192小时均值异常与固定空间σ=2、半径5、reflect。各方法共享源场、简化树、原极值、匹配、参考方向、画布与坐标规则。','',
 '## 四方法主比较','',
 'TMTM/ST-MTM Temporal的SNS/TW/TD直接引用第二篇Table1；它们的NPE在此次新输入上补算。Anchor两模式四指标和时间全部重新实测。','',
 '| Dataset | Method | SNS↓ | TW↑ | TD↓ | NPE↓ | t_opt(s) | t_total(s) |','|---|---|---:|---:|---:|---:|---:|---:|']
 for x in rr:lines.append(f"| {x['Dataset']} | {x['Method']} | {f(x['SNS'])} | {f(x['TW'])} | {f(x['TD'])} | {f(x['NPE'])} | {f(x['t_opt'],3)} | {f(x['t_total'],3)} |")
 lines+=['',
 'LaTeX按每数据集、每指标在四个显示方法中自动加粗最小值（TW为最大值）并下划线第二个不同显示数值；相同显示精度保留并列。没有人为指定Anchor获胜。TD也按显示数值排名，但作者TD与本地完整画布归一化TD的单位可比性仍未确认，因此此项强调仅是数字排序，不能单独证明严格同单位优势。SNS/TW的跨来源比较同样不能替代作者相同数组复现。','',
 '## 指标与有效帧','',
 'SNS采用平方scale-normalized stress，逐帧原空间支持域质心距离与显示锚点距离拟合尺度并平均。NPE为逐帧最大|x−q|/L再时间平均。TD为相邻帧共同Track ID显示绝对位移之和除固定完整画布跨度；不除帧数、不除匹配数、不乘100。TW采用标准trustworthiness，k分别为1、3、5、3；采用已冻结实现适用域0<k<n/2，不满足者缺失，不填0。','',
 '| Dataset | Mode | TW有效帧 | SNS有效帧 | 匹配步数 |','|---|---|---:|---:|---:|']
 for x in mm:
  s=read(O/'results'/x['Dataset']/x['Method'].replace('AnchorMTM ','')/'summary.json')
  lines.append(f"| {x['Dataset']} | {x['Method']} | {x['TW_valid_frames']}/{x['frames']} | {x['SNS_valid_frames']}/{x['frames']} | {s['matched_steps']} |")
 lines+=['','TW覆盖率只写表注/独立统计，不再将1/40等内容附到数值上。低覆盖的TW不被描述为完整序列的稳定邻域性能。','',
 '## Balanced选择与实际拓扑','',
 '保持既定选择规则：前25%时间帧验证，正ε=1%–10%每1%采样；合法且实际NMLEmax≤各自ε才入选。在合法正候选间分别min–max归一化NPE、SNS，常数分量记0仅用于评分。J=.5NPE_norm+.5SNS_norm，J≤Jmin+.01视为接近，先选较小ε再选较低实际拓扑误差。Exact不参加正预算候选，没有最低NPE收益门槛，不回退0。冻结后两模式各重新跑一次完整流水线。','',
 '| Dataset | 选中ε | 验证J | 实际NMLEmax | 与Exact完全相同 |','|---|---:|---:|---:|---|']
 for x in pp:lines.append(f"| {x['Dataset']} | {100*x['epsilon_Balanced']:g}% | {x['J_validation']:.6f} | {100*x['actual_NMLEmax']:.6f}% | {x['same_output_as_Exact']} |")
 lines+=['','所有候选在balanced_selection.csv及results/*/selection保存。主表为全序列，包含验证段，后75%的NPE另存。历史结果已观察过，本轮不宣称全新盲测。','',
 '| Dataset/Mode | 实际NMLEmax | 连续违规/渲染违规 | 整数修复帧 |','|---|---:|---:|---:|']
 for x in tt:lines.append(f"| {x['Dataset']}/{x['Method']} | {100*x['actual_topology_max']:.6f}% | {x['continuous_budget_violations']}/{x['rendered_budget_violations']} | {x['repaired_raster_frames']} |")
 lines+=['','八组均通过固定完整叶标签合并矩阵（含对角线）、极值值/个数、锚点唯一性、画布及区间约束、整数重建与剖面极小值个数检查。Exact实际标签误差0；该证书不扩大为所有增强有限根高扩展的完整保留证明。','',
 '## 与旧百分数解释的区别及结论','',
 '旧目录使用p=(0.001%,0.001%,0.15%,0.105%)；本轮p阈值为旧值100倍。预算由新验证重新选择，因此新旧差异不是单独p的受控消融，也不混用历史布局/基线NPE。旧Storms TD≈29.3365来自10.5%比例、ε=5%的历史配置；本轮独立结果以新选定ε为准，不直接复制旧值。','',
 '| Dataset | Exact→Balanced NPE | SNS | TD | TW |','|---|---:|---:|---:|---:|']
 for ds in DS:
  e=next(x for x in mm if x['Dataset']==ds and x['Method']=='AnchorMTM Exact');b=next(x for x in mm if x['Dataset']==ds and x['Method']=='AnchorMTM Balanced')
  lines.append(f"| {ds} | {f(e['NPE'])} → {f(b['NPE'])} | {f(e['SNS'])} → {f(b['SNS'])} | {f(e['TD'])} → {f(b['TD'])} | {f(e['TW'])} → {f(b['TW'])} |")
 lines+=['','这里如实保留所有不利变化；更小的累计TD仅表示显示位移更少，不能单独证明物理运动更准确。Gaussian或其他数据集若正预算未使用、输出相同，仍保留正ε行而不制造差异。','',
 '## 运行与复现','',
 '硬件Apple M4；BLAS、TTK单线程，逐帧提树，HiGHS保留默认调度。每模式完整实测1次。t_opt含顺序搜索及连续锚点优化；t_total重新生成/读取源场、预处理、TTK提树I/O、匹配参考、优化、整数重建及内置检查；不使用验证树替代正式计时阶段。OS页缓存可能已热，程序导入、指标导出及报告不计入；不据单次测量声称显著加速。','',
 '正式文件：comparison_final.csv、anchor_metrics_measured.csv、anchor_parameters.csv、anchor_runtime.csv、baseline_npe.csv、topology_validation.csv、p_threshold_validation.csv、ranking_audit.csv、balanced_selection.csv、input_audit.csv。源代码和冻结配置见source/与config/，完整原始输出见results/。两个LaTeX表：quantitative_comparison.tex和anchor_parameter_settings.tex；没有表3。']
 (O/'REPORT_zh.md').write_text('\n'.join(lines)+'\n')
 (O/'REPRODUCE.md').write_text('''# Reproduce ratio-p experiment

From the MergeTreeMaps workspace root, use `.venv/bin/python` with the package versions in `source/requirements.txt`. The same scripts also resolve the published repository's `code/` layout. Source data are external; paths and hashes are recorded per preparation protocol. TTK0.9.9 native source/binary and core snapshots are preserved in source/. The native binary is macOS arm64-specific.

Run in order:

1. `python paper/pvis2027/experiments_ratio_p_20261104/source/run.py`
2. `python paper/pvis2027/experiments_ratio_p_20261104/source/assemble.py`
3. `python paper/pvis2027/experiments_ratio_p_20261104/source/verify.py`
4. `python paper/pvis2027/experiments_ratio_p_20261104/source/write_report_paper.py`
5. `python paper/pvis2027/build_main.py`

`--dataset Gaussian|Ring|Wildfires|Storms` resumes one dataset. Successful measured configurations are retained. Archive a final mode directory to explicitly remeasure; it will rebuild preprocessing and trees. All p numbers are FRACTIONS: .001,.001,.15,.105, never divided by100 before threshold multiplication. Cache metadata and every tree's actual threshold are checked. Raw source fields/coordinates may be reused only when unchanged; no old simplified trees/layouts/scores are reused. The old percentage-interpretation directory remains untouched.

Positive Balanced selection remains first-quarter validation, epsilon1..10% in1% steps, normalized J=.5NPE+.5SNS, near-optimal tolerance.01 and smaller-epsilon tie rule. No test-metric retuning, no zero fallback. Baseline SNS/TW/TD are verbatim published scores; only NPE is recomputed on the new shared input. Main numerical rankings are per dataset across the four displayed methods; published TD units remain unverified against local normalized units. No Base row, no separate Table3; both Anchor modes have t_opt/t_total columns. TW coverage appears in notes only.
''')
 # Archive prior paper before the first ratio-p update.
 arc=O/'archive/prior_percentage_p_paper';arc.mkdir(parents=True,exist_ok=True)
 tex=P/'drafts/method_anchor_figures_updated_en.tex';pdf=P/'最新论文与三张PPT/AnchorMTM_最新论文.pdf'
 for p in [tex,pdf]:
  if not(arc/p.name).exists():shutil.copy2(p,arc/p.name)
 text=tex.read_text()
 setup=r'''We evaluate Gaussian ($128\times128$, 64 frames), Ring ($14\times14$, 40), Wildfires ($64\times64$, 32), and Storms ($281\times181$, 744). Raster lengths are 4096 except Ring, which retains 196. This experiment explicitly tests the ST-MTM Table~1 persistence numbers $(0.001,0.001,0.15,0.105)$ as fractions of each preprocessed frame's scalar range~\cite{STMTM:2026}: equivalently, $0.1\%,0.1\%,15\%,10.5\%$. The absolute threshold is $p(F_{\max}^t-F_{\min}^t)$, with no division of the printed $p$ by 100. All 880 actual thresholds are independently checked. This is a tested interpretation, not an assertion that the author's undocumented preprocessing is fully recovered.

Gaussian remains an explicit three-peak reconstruction; Ring uses the archived author generator. Wildfires integrates 61 days of available 10-km FRP into 32 equal-duration windows on a fixed $64\times64$ grid, without additional smoothing. Storms retains the ERA5 192-hour moving-mean anomaly and fixed spatial smoothing. Exact author-processed arrays are unconfirmed. All local methods share source fields, simplified trees, leaf labels, overlap tracks, extrema, one fixed reference direction and projected canvas span $L$. Published $W,K,r,\lambda$ and starting frames apply to the baseline adapters only. AnchorMTM core code and QP weights remain fixed. No frame-wise baseline translation or rescaling is permitted.

We report four metrics. SNS is squared scale-normalized stress of support-centroid distances~\cite{Smelser:2025:Scale,STMTM:2026}, averaged over valid frames. TW is standard trustworthiness~\cite{Venna:2001:NP}, with $k=(1,3,5,3)$ and the frozen implementation domain $0<k<n_t/2$; other frames are missing, never zero. Coverage is reported in the table note. Task-specific absolute position error and local normalized temporal displacement are
\begin{equation}\label{eq:experimental-npe}
\mathrm{NPE}=\frac1T\sum_t\frac{\max_i|x_i^t-q_i^t|}{L},
\end{equation}
\begin{equation}\label{eq:experimental-td}
\mathrm{TD}_{\rm local}=\sum_{t=1}^{T-1}\sum_{i:\mu_t(i)\ \mathrm{exists}}\frac{|x_i^t-x_{\mu_t(i)}^{t-1}|}{L}.
\end{equation}
TD is a cumulative display displacement, not physical motion accuracy; we do not divide by frame or match count. Published TMTM/ST-MTM Temporal SNS/TW/TD are quoted verbatim; their NPE is recomputed on our shared input. Published TD units remain unconfirmed, so numerical highlighting does not certify matched-unit superiority.

Exact fixes $\varepsilon=0$. Balanced is reselected on the first chronological quarter over positive budgets 1--10\% at 1\% increments. Only legal candidates with attained NMLEmax $\le\varepsilon$ are eligible. Validation NPE and SNS are separately min--max normalized among those candidates, with constant components contributing zero to the score:
\begin{equation}\label{eq:balanced-validation-score}
J=0.5\,\mathrm{NPE}_{\rm norm}+0.5\,\mathrm{SNS}_{\rm norm}.
\end{equation}
Within 0.01 of minimum $J$, smaller budgets then lower attained errors are preferred. There is no minimum-gain condition or zero-budget fallback. Each budget is frozen before a fresh full pipeline run. Full-sequence scores include validation; suffix NPE is archived separately. Earlier outputs were observed, so this is not presented as a new blind test. The reference is an offline complete-input estimate.'''
 comparison=r'''Table~\ref{tab:quantitative-final} contains four methods, with separate $t_{\rm opt}$ and $t_{\rm total}$ columns for each AnchorMTM mode. Bold and underlined entries are automatically selected per dataset and metric from the four displayed numerical values, including ties. All original-source versus reconstructed-input limitations remain explicit; in particular, TD emphasis compares reported numbers without establishing a common author/local coordinate unit.

\input{../experiments_ratio_p_20261104/tables/quantitative_comparison.tex}
\input{../experiments_ratio_p_20261104/tables/anchor_parameter_settings.tex}

'''+ 'The reselected Balanced budgets are '+', '.join(f"{100*x['epsilon_Balanced']:g}\\%" for x in pp)+r''' for Gaussian, Ring, Wildfires and Storms, respectively. Positive budgets with identical Exact output remain reported without manufactured gain. TW on few eligible frames is a limited-coverage statistic, not an all-frame performance claim. The full measured values, candidate scores, coverage and attained topology costs are archived.'''
 performance=r'''This experiment changes persistence interpretation and reselects topology budgets; it is not a component ablation. No core algorithm or QP weight is retuned. All 40 positive validation candidates and their actual errors are retained. Exact and Balanced are rerun from source processing with the original raster lengths. Independent checks verify source references, finite maps, unique leaf anchors, extremum values/counts, continuous constraints and rendered fixed-leaf merge matrices including the diagonal. These checks are not a certificate for every augmented finite-root extension.

Ring keeps its checked joint-integer-rounding adapter at 196 positions when independent rounding cannot hold a barrier pixel. The adapter preserves continuous order, widths and objectives, minimizes numerical rounding error, and never optimizes benchmark scores or relaxes topology. Baseline NPE retains the disclosed CompactTMTM multiway and ST-MTM equal-level adaptations and same-equation convex-QP numerical fallbacks, with independent KKT certificates; these runs are not author binaries.

The time columns in Table~\ref{tab:quantitative-final} report one actual run per configuration on Apple M4. BLAS and native TTK use one thread and extraction is sequential; HiGHS retains its default scheduler. Optimization time covers order search and continuous placement. Total time includes fresh source/preprocessing, extraction I/O, matching/reference, optimization, integer reconstruction and intrinsic checks; metric/report export and process import are excluded. Validation caches never replace a timed field or tree stage. OS page caches may be warm. We make no significance or cross-hardware acceleration claim.'''
 for title,body in [('Experimental Setup',setup),('Quantitative Comparison',comparison),('Ablation Study and Performance',performance)]:
  pat=r'(\\subsection\{'+re.escape(title)+r'\}\n).*?(?=\\subsection\{|\\section\{)';text,n=re.subn(pat,lambda m:m.group(1)+body+'\n\n',text,flags=re.S);assert n==1
 tex.write_text(text)
 r=P/'README.md';s=r.read_text();marker='\n## 2026-11-04 按比例解释p的重算\n';s=s.split(marker)[0];s+=marker+f'\n当前正式实验为[experiments_ratio_p_20261104](experiments_ratio_p_20261104/REPORT_zh.md)。p比例为0.001、0.001、0.15、0.105，即0.1%、0.1%、15%、10.5%。四数据集8组Exact/Balanced重新计算；选中预算：{selection}。旧百分数解释结果完整保存在experiments_final_20261104。四方法、四指标逐数据集自动数字排名，TD单位与输入限制明示；时间拆两列，删除表3，TW覆盖率只放表注，参数表白底。\n';r.write_text(s)
 print(O/'REPORT_zh.md')
if __name__=='__main__':main()
