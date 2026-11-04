"""Write conclusions from actual outputs and update only authorized paper sections."""
from pathlib import Path
import json,re,hashlib,shutil
O=Path(__file__).resolve().parents[1];P=O.parent
def read(p):return json.loads(p.read_text())
def f(x,n=4):return 'N/A' if x is None else f'{x:.{n}f}'

def main():
 a=read(O/'assembled.json');verify=read(O/'verification.json');assert verify['all_passed'];rows=a['comparison'];local=a['measured'];params=a['parameters'];rt=a['runtime'];topo=a['topology'];audit=a['input_audit']
 best_npe=[]
 for ds in ['Gaussian','Ring','Wildfires','Storms']:
  base=min(r['NPE'] for r in rows if r['Dataset']==ds and r['Method'] in ['TMTM','ST-MTM Base','ST-MTM Temporal'] and r['NPE'] is not None);anchor=min(r['NPE'] for r in local if r['Dataset']==ds and r['NPE'] is not None);best_npe.append((ds,base,anchor,100*(1-anchor/base)))
 lines=['# PacificVis 2027：四数据集正式定量实验包','',
 '**四数据集均完成合法的 AnchorMTM Exact 和正预算Balanced（8/8），主表保留TMTM及ST-MTM Temporal两基线（8组NPE），Base结果从当前比较中移除并保留历史缓存。** Balanced由固定验证综合评分J选择：Gaussian1%、Ring1%、Wildfires4%、Storms10%。不再回退0；Gaussian所选正预算实际未被使用，完整输出与Exact相同，无额外收益。原始算法源码哈希未改变，Ring保持L=196。','',
 '**这是明确标注重建输入的可复现实验，不是已确认原作者最终处理数组的严格复现。** 原文SNS/TW/TD只转录，不重跑、不虚构；NPE在本地共享输入上补算。主表直接列出已实测的完整画布归一化TD，不再用N/A替代数值。原文TD单位仍未确认，所以标明本地归一化单位、TD分别在引用原文组和本地归一组内自动加粗最优、下划线次优，不跨单位排名。Exact和Balanced各有独立的t_opt、t_total两列，表3已删除。Ring的TW仅显示0.857，1/40覆盖率移至表注。','',
 '## 1. 输入与论文设置核对','',
 '| Dataset | 尺寸 / T | p（按百分数执行） | 实际叶特征数 | 原表特征数 | 说明 |','|---|---|---:|---:|---:|---|']
 ref={'Gaussian':'3','Ring':'1–7','Wildfires':'2–34','Storms':'1–8'}
 for x in audit:lines.append(f"| {x['Dataset']} | {x['nx']}×{x['ny']} / {x['T']} | {x['p_percent']:g}% | {x['features_min']}–{x['features_max']} | {ref[x['Dataset']]} | {'归档作者生成器；提树版本不同' if x['Dataset']=='Ring' else '明确标注的重建输入'} |")
 lines+=['',
 '- p统一按第一篇表注的百分数口径执行；因此第二篇数字0.105对应0.105%=0.00105，不是10.5%。第二篇自身未明确单位，不能把这项约定写成作者已确认的实现。阈值为逐帧预处理场值范围的相应比例。',
 '- Gaussian：128×128、64帧、两个固定峰和一个运动峰。中心、幅度、宽度及轨迹写入preparation/protocol.json。最初旧生成器的额外连接脊产生33特征，已归档；最终仅三峰，不按指标选择中心、宽度或轨迹。不是原作者场。',
 '- Ring：复用归档作者生成器与40帧设置。原画布196没有改变。TTK提树后的逐帧叶数与原表不要求人为逐帧一致，不人为删特征。',
 '- Wildfires：使用原始10km层级FRP，2019-11-01至2020-01-01共61天。32个等长时间窗，每窗61/32天，按日常值的区间重叠权重积分。全时段固定空间正方形边界映射到64×64并求和；无log变换、平滑、背景修正、特征数过滤或按性能选日期。作者32帧具体聚合边界未公开，本项是用户授权的明确重建。',
 '- Storms：原生281×181、1999年12月744小时；逐位置减192小时滑动均值，固定Gaussian σ=2/半径5/reflect边界。经纬度范围、原始NetCDF路径及hash均记录。第一篇的282列及最终处理数组不在本地，未编造额外列。',
 '- Gaussian生成坐标、Ring作者生成坐标、Wildfires固定等距km坐标与Storms经纬度坐标均在配置中明确。各数据集内部四方法共享同一坐标、树、匹配、极值和参考；原作者原空间坐标单位尚不能逐项确认，因此引用值与本地重建不能宣称严格同设置排名。','',
 '## 2. 最终四项指标与计算正确性','',
 '- SNS↓：平方scale-normalized stress，逐帧原空间支持域质心距离与显示锚点距离最优单一缩放，最后对有效帧等权平均。无有效距离的帧缺失，不填0。',
 '- TW↑：标准Venna–Kaski trustworthiness，k依次为1、3、5、3。要求0<k<n/2；真实无效帧缺失。下面给出实际有效覆盖率，未把原表未披露的有效帧数补造出来。',
 '- TD↓：本地为所有相邻帧共同Track ID显示绝对位移之和除以完整固定物理画布跨度L；不乘100、不除时间、不改为应力。原文TD只能原样引用，跨来源可比性N/A。',
 '- NPE↓：逐帧max_i|x_i−q_i|/L的时间平均。q来自原始极值在一次全序列固定方向上的投影。所有方法共享原点、范围和像素换算；基线最多按预声明规则作一次全局反射，绝无逐帧移动、缩放或事后最小误差对齐。',
 '- 独立验证重新计算所有Anchor指标、基线NPE、实际标签合并矩阵误差；TW与独立排序实现交叉核对。八组Anchor地图有限、所有叶标签锚点存在、不重合、连续区间约束及源参考均通过。profile_validation_per_frame.csv额外核对剖面极小值个数，防止仅固定标签正确但新增未匹配极值。',
 '- 本地TMTM在Storms的15/744帧有不同叶锚点落在相同像素的现象；NPE保留这些帧，不通过删除困难样本改善结果。其余基线未检出锚点重合。基线NPE可计算不等于已获得与作者二进制一致的合法地图复现证书。',
 '- ST-MTM本地NPE的数值适配保持原QP方程、约束及数据参数。独立KKT门限为原坐标原始可行残差<10⁻⁷、目标缩放后的驻点残差<10⁻⁷、互补残差<10⁻⁷+10⁻¹⁰×objective_scale；原始残差、缩放量及实际门限逐项保存。大坐标区间变量作等价平移，未调整Anchor目标权重，也未放宽任何Anchor拓扑验收。','',
 '## 3. 原文引用与本地NPE主表','',
 '各数据集TMTM和ST-MTM Temporal的SNS/TW/TD来源是第二篇Table1；仅NPE由本地补算。LaTeX在相应指标列标题用p上标标出引用来源。SNS、TW、NPE在每个数据集四种方法之间统一自动判断显示数值最优/次优；SNS/TW是原文与重建输入数值的描述性比较，不宣称已确认严格同输入。TD跨来源单位未核实，因此按原文组、本地归一组分别排名；不把两组标记解释为共同单位下的获胜。','',
 '| Dataset | Method | SNS | TW | TD（原文或本地归一化） | NPE | t_opt(s) | t_total(s) |','|---|---|---:|---:|---:|---:|---:|---:|']
 for x in rows:lines.append(f"| {x['Dataset']} | {x['Method']} | {f(x['SNS'])} | {f(x['TW'])} | {f(x['TD'],2)} | {f(x['NPE'])} | {f(x['t_opt'],3)} | {f(x['t_total'],3)} |")
 lines+=['', '## 4. AnchorMTM四项实测值（同一来源内可比较）','',
 '| Dataset | Mode | ε | SNS | TW | TW有效帧 | TD（完整画布归一化累计） | NPE |','|---|---|---:|---:|---:|---:|---:|---:|']
 for x in local:lines.append(f"| {x['Dataset']} | {x['Method']} | {100*x['epsilon']:g}% | {f(x['SNS'])} | {f(x['TW'])} | {x['TW_valid_frames']}/{x['frames']} | {f(x['TD'])} | {f(x['NPE'])} |")
 lines+=['',
 'TD历史核对：旧Storms Balanced=29.336508来自p=10.5%、ε=5%、1–7叶、2737个匹配步；当前p=0.105%、ε=10%、9–40叶、14095个匹配步，TD=343.427839。两组同为完整画布归一累计，但输入简化和预算不同，不能混入同一正式结果。独立求和复核见TD_history_audit.csv及TD_AUDIT_zh.md；没有为变成最小值改分母、除帧数或替换旧结果。','',
 'Ring的TW只覆盖极少数帧，不能将该均值描述为全40帧邻域性能。它数学上可计算，所以保留数值并标有效帧；不合法的其余帧并未填0。','',
 '相对Exact，下面三个下降率按(Exact−Balanced)/Exact计算；负值表示变差。TW列为Balanced−Exact的绝对差。','',
 '| Dataset | NPE下降率 | SNS下降率 | TD下降率 | TW差值 |','|---|---:|---:|---:|---:|']
 for ds in ['Gaussian','Ring','Wildfires','Storms']:
  e=next(x for x in local if x['Dataset']==ds and x['Method']=='AnchorMTM Exact');b=next(x for x in local if x['Dataset']==ds and x['Method']=='AnchorMTM Balanced');g=[100*(1-b[m]/e[m]) for m in ['NPE','SNS','TD']]
  lines.append(f"| {ds} | {g[0]:.2f}% | {g[1]:.2f}% | {g[2]:.2f}% | {b['TW']-e['TW']:+.6f} |")
 lines+=['',
 '## 5. 正预算Balanced的固定综合评分选择','',
 '- 规则v3按用户最新定义冻结：验证窗口仍为前25%时间帧，测试ε=1%至10%、步长1%。Exact固定0，不参加Balanced候选。所有正候选均须布局及整数重建合法，实际NMLEmax≤自身名义ε；不再额外沿用v2的5%筛选上限，也没有任何NPE改善门槛。内部固定ε0=10⁻⁷不用于放宽实际名义预算验收。',
 '- 在合法正候选之间，对验证NPE与SNS分别作min–max归一化：v_norm=(v−min)/(max−min)，分母范围≤10⁻¹²时该评分分量记0（只表示候选间无区分度，绝不将原始指标改成0）。J=0.5×NPE_norm+0.5×SNS_norm。归一化极值只来自验证候选，不使用测试指标。',
 '- J≤Jmin+0.01的配置视为接近，先选ε较小者，再选实际拓扑代价较低者。规则及0.01容差在本轮选择前固定，不因最终排名改变。每个数据集冻结正ε后重跑Balanced完整流水线并实际计时；Exact0端点输入、核心和权重未变，保留此前完整冷流水线测量。',
 '- 全局参考由完整无标签源序列离线拟合；验证划分只控制参数选择。主表按要求报告全序列，包含验证段，后75%的assessment_NPE另存。历史全序列结果已经观察过，用户又调整了选择定义，因此本轮不宣称是全新盲测或完全未观察过的独立测试。',
 '- 所有40个正ε验证候选、归一化分量、J、实际拓扑代价和选择原因保存于balanced_selection.csv及selection.json。先前1%门槛、回退0和20%候选版本、旧Ring失败及Gaussian连接脊试验均归档，未删除原始数据或源码。','',
 '| Dataset | 选中正ε | 实际NMLEmax | 验证J | 输出状态 |','|---|---:|---:|---:|---|']
 for x in params:lines.append(f"| {x['Dataset']} | {100*x['epsilon_Balanced']:g}% | {100*x['actual_NMLEmax']:.6f}% | {x['J_validation']:.6f} | {'与Exact完整输出相同，无额外收益' if x['same_output_as_Exact'] else '独立正预算布局'} |")
 lines+=['',
 'Gaussian保留ε=1%的Balanced行，即使实际拓扑误差为0、输出与Exact相同。没有为制造差异破坏拓扑。只对选中正ε报告全序列；未把其他候选的验证结果冒充其全序列性能。','',
 '## 6. Ring原长度修复及拓扑合法性','',
 '- 原失败原因：独立四舍五入使部分间隙或锚点距离不足以容纳至少一个屏障像素。',
 '- 仅对原渲染器失败的序列启用外部联合整数舍入适配；保留原连续顺序、x/z/w、参考、目标权重和拓扑预算。在同一196点画布上，先尽量固定最近舍入锚点，再以最小最大像素误差、次级最小总绝对误差选择合法整数骨架。目标不含NPE、SNS或排名。',
 '- 当原舍入本来合法时保留原路径；修复坐标满足边界、区间包含及空屏障像素约束，随后使用原填充和原optimal-barrier校正。实际渲染的完整固定叶标签矩阵含对角线必须过预算；另检验锚点个数/值和剖面极小值个数。',
 '- Exact严格ε=0且ε0=0；正预算的数值底额ε0=10⁻⁷明确记录，不把它偷换成Exact。Exact的声明针对固定完整叶标签的合并层级；不把该检查夸大为所有增强树有限根高的完整保留证书。','',
 '| Dataset / Mode | 实际拓扑max | 预算违规（连续/渲染） | 整数修复帧 | 最大整数舍入误差 / px |','|---|---:|---:|---:|---:|']
 for x in topo:lines.append(f"| {x['Dataset']} / {x['Method']} | {100*x['actual_topology_max']:.6f}% | {x['continuous_budget_violations']}/{x['rendered_budget_violations']} | {x['repaired_raster_frames']} | {x['max_joint_rounding_error_pixels']:.6f} |")
 lines+=['',
 '## 7. 运行时间','',
 'Apple M4；TTK单线程且按帧顺序运行，BLAS单线程；HiGHS可行性LP/整数舍入保留默认内部调度，Clarabel单线程。每配置实际完整计时1次，不报虚构重复均值/方差，不据作者不同硬件计算加速比。',
 't_opt仅顺序搜索与连续锚点优化；t_total从重新读取/生成源数据开始，包含预处理、真实TTK进程提树及I/O、特征匹配和参考、优化、整数重建、填充及接口内置检查。指标导出、报告与程序导入不计入。验证缓存可复用，但不替代任何正式计时阶段；未清空操作系统页缓存，所以这里不是存储设备冷缓存基准。','',
 '| Dataset | Mode | t_opt / s | t_total / s | 次数 |','|---|---|---:|---:|---:|']
 for x in rt:lines.append(f"| {x['Dataset']} | {x['Method']} | {f(x['t_opt'],3)} | {f(x['t_total'],3)} | {x['repeats']} |")
 lines+=['',
 '## 8. 结论与适用范围','',
 '在本地统一输入和固定坐标约定下，AnchorMTM的NPE低于本地基线复现。相对每个数据集中NPE最低的基线，最低Anchor NPE如下；这是重建输入上的内部比较，不是作者官方方法性能证明。','',
 '| Dataset | 最低基线NPE | 最低AnchorNPE | 相对下降 |','|---|---:|---:|---:|']
 for ds,b,x,g in best_npe:lines.append(f'| {ds} | {b:.6f} | {x:.6f} | {g:.2f}% |')
 lines+=['',
 'Ring、Wildfires与Storms选中正预算后的本地NPE和累计TD降低，但Wildfires的SNS增加、TW降低，是明确的相对几何代价；保留这些不利结果。Gaussian正ε输出与Exact相同，实际拓扑误差0，不宣称额外收益。TD降低仅表明显示更平稳，不能单独证明物理运动表达更准确。',
 'SNS与TW有明确公共定义；NPE是任务化绝对参考位置误差；本地TD保留完整画布归一化累计定义。用于第5节的精简指标组合就是这四项，不再使用已放弃的临时指标。',
 '本轮没有额外数据集或组件消融。ε验证扫描只支撑参数选择，不能宣称某个优化项的独立因果贡献。SNS/TW/NPE按每数据集的四方法显示数值自动排名；SNS/TW跨输入只作描述性汇总，NPE来自本地共享输入。相同显示精度视为并列，不手工指定获胜。TD数值完整呈现，但原文与本地单位未确认统一，分别在原文和本地归一两组内自动加粗/下划线排名。参数表已全部改为白底。','',
 '## 9. 交付','',
 'comparison_final.csv为主表；anchor_metrics_measured.csv含全部本地四指标；anchor_parameters.csv、anchor_runtime.csv、baseline_npe.csv、topology_validation.csv、balanced_selection.csv、input_audit.csv、ranking_audit.csv及独立验证文件分别保存参数、计时、NPE、预算、选择、输入和排名。',
 'tables/quantitative_comparison.tex及anchor_parameter_settings.tex使用booktabs和table*；运行时间已合并主表，不再生成表3。source/包含实际驱动、同方程QP、整数舍入、组表和独立核验，config/保存冻结规则、硬件与源码hash。结果、地图、所有候选与真实计时树保留在results/；archive/保留历史，不直接删除原始输入或源码。',
 '论文仅同步授权的5.1、5.2、5.5及其表格引用；首图是另一份冻结的定性Storms输入，已与定量输入明确区分。重建数据不得误称作者官方同输入。','']
 (O/'REPORT_zh.md').write_text('\n'.join(lines))
 repro='''# Reproduction

Run from `/Users/lele/Desktop/MergeTreeMaps` with `.venv/bin/python`.

1. `python paper/pvis2027/experiments_final_20261104/source/run.py`
2. Retry only failed baseline NPE after the numerical fix if needed: `python paper/pvis2027/experiments_final_20261104/source/run.py --baseline-npe-only`.
3. `python paper/pvis2027/experiments_final_20261104/source/assemble.py`
4. `python paper/pvis2027/experiments_final_20261104/source/verify.py`
5. `python paper/pvis2027/experiments_final_20261104/source/write_report_paper.py`
6. `python paper/pvis2027/build_main.py`

Use `--dataset Gaussian|Ring|Wildfires|Storms` to resume one dataset. Existing successful measured runs are retained. To explicitly remeasure a successful mode, archive that mode's output directory first; the script will then rebuild its source and trees rather than reusing intermediates. OS page caches are not cleared. Numerical warnings remain in logs; final finite-value, KKT and topology checks are mandatory.

Dependencies: NumPy, SciPy (milp/HiGHS), netCDF4, OSQP, Clarabel, threadpoolctl; pinned project TTK 0.9.9 binary at `RG-MTM/code/tmp/volume3d/native-build/rgmtm_ttk_volume` (source in `code/experiments/volume3d/native`). Existing baseline/Anchor algorithm files are imported from `RG-MTM/code`, not modified. Their exact hashes are in `config/core_sha256.json`; `source/core_snapshot` is a read-only reference copy, not an alternate implementation. Input paths and hashes are recorded in each preparation protocol. Do not reinterpret archived10.5% runs as0.105%.

Exact Python versions are in `source/requirements.txt`, `config/package_versions.json`, and the full `config/python_environment.txt`. The extraction binary used is also preserved as `source/native/rgmtm_ttk_volume_macos_arm64`, with SHA256 in `config/reference_and_binary_provenance.json`. It is platform-specific. To rebuild elsewhere, use the archived native CMakeLists/main.cpp with verified TTK0.9.9 sources, for example `cmake -S source/native -B native-build -DTTK_SOURCE_DIR=/path/to/ttk-0.9.9 -DCMAKE_BUILD_TYPE=Release`, then `cmake --build native-build --target rgmtm_ttk_volume`; the driver currently expects the project binary path above. Raw source data remain in the project and are not downloaded or replaced by the script.

SNS/TW/TD baseline cells are literal Table1 transcriptions in `source/assemble.py`; baseline computation executes NPE only. Local TD is a full-canvas-normalized sum. Published TD units are unverified: actual normalized local TD is shown in the main cells with an n header, and no cross-unit TD ranking is applied. SNS/TW/NPE best and second are computed across the four methods per dataset, with SNS/TW labelled a descriptive numeric summary of potentially different processed inputs. Each Anchor method has separate t_opt/t_total columns; there is no separate runtime table. Parameter rows have white backgrounds.

Selection rule v3: positive candidates1..10% at1% increments, first chronological25% validation, actual topology maximum<=each nominal epsilon. Minmax-normalize validation NPE/SNS over legal positive candidates (constant components0 only in the score), J=.5NPE_norm+.5SNS_norm. Within Jmin+.01 prefer smaller epsilon then smaller attained topology error. NEVER fallback0; do not manufacture a changed output. Freeze positive budgets and run final Balanced cold pipelines. Full-sequence statistics contain validation; suffix statistics are separate. Earlier outputs were already observed, so this is not claimed as a new blind test.
'''
 (O/'REPRODUCE.md').write_text(repro)
 # Only authorized experiment subsections, plus dependencies and teaser provenance.
 tex=P/'drafts/method_anchor_figures_updated_en.tex';text=tex.read_text()
 if '\\usepackage{booktabs,multirow,colortbl}' not in text:text=text.replace('\\usepackage{flafter}','\\usepackage{flafter}\n\\usepackage{booktabs,multirow,colortbl}')
 setup=r'''We use Gaussian ($128\times128$, 64 frames), Ring ($14\times14$, 40), Wildfires ($64\times64$, 32), and Storms ($281\times181$, 744), following the dimensions and raster lengths in ST-MTM~\cite{STMTM:2026}. Shared rasters have 4096 positions except Ring, which retains 196. Our Gaussian is an explicit three-peak reconstruction; Wildfires integrates the available 10-km daily FRP into 32 equal-duration bins over November--December 2019, without adaptive smoothing or feature-count filtering. Ring uses the archived author generator. Storms uses native ERA5 anomalies with a fixed 192-hour moving mean and fixed spatial smoothing. Exact author-processed arrays are unavailable; these are labelled reconstructions, not verified author inputs. The qualitative teaser uses a separately frozen Storms preprocessing and is not the quantitative input.

The printed persistence settings $(0.001,0.001,0.15,0.105)$ are interpreted as percentages of each preprocessed frame's range, adopting the explicit TMTM convention~\cite{Koepp:2023:TMTM}; ST-MTM's unit is not independently confirmed. No outcome-dependent pruning or smoothing is used. All local methods share simplified fields, leaf labels, overlap tracks, extremum references, one direction, origin and projected span $L$. Baselines receive the published dataset-specific $W,K,r,\lambda$, raster length and starting frame; these are not transferred to AnchorMTM. Remaining numerical assumptions and reconstruction parameters are archived.

We retain four metrics. SNS is the scale-fitted squared distance stress of support centroids~\cite{Smelser:2025:Scale,STMTM:2026}, averaged over frames with a nonzero source-distance denominator. TW is standard trustworthiness~\cite{Venna:2001:NP}, with $k=(1,3,5,3)$ and valid only when $0<k<n_t/2$; invalid frames are missing, never zero. Our task-specific absolute position error is
\begin{equation}\label{eq:experimental-npe}
 \mathrm{NPE}=\frac{1}{T}\sum_t\frac{\max_i|x_i^t-q_i^t|}{L}.
\end{equation}
Local temporal displacement is the complete-canvas-normalized sum
\begin{equation}\label{eq:experimental-td}
 \mathrm{TD}_{\rm local}=\sum_{t=1}^{T-1}\sum_{i:\mu_t(i)\ \mathrm{exists}}
 \frac{|x_i^t-x_{\mu_t(i)}^{t-1}|}{L}.
\end{equation}
It measures display stability, not physical motion accuracy. We do not multiply by 100 or average this quantity over time.

Published TMTM and ST-MTM SNS/TW/TD are transcribed directly from ST-MTM Table~1~\cite{STMTM:2026}; only their NPE is recomputed locally. Their reported TD units and low-feature-count TW handling remain insufficiently specified. Local normalized TD is nevertheless shown directly in the main table and identified by its unit; it is not cross-ranked with published TD. SNS/TW numerical rankings include the four displayed methods per dataset, but are descriptive summaries across potentially different processed inputs. NPE uses the shared local inputs and a fixed pixel-to-reference-domain conversion; one global orientation reflection is allowed by a predefined rule, with no frame-wise alignment.

AnchorMTM Exact uses $\varepsilon=0$ with no numerical topology allowance. Balanced always reserves a positive budget, selected independently per dataset over 1--10\% at 1\% increments using the first chronological quarter. Legal candidates must satisfy attained NMLEmax $\le\varepsilon$. Validation NPE and SNS are separately min--max normalized over those candidates; a constant component has no discriminating score. We fix
\begin{equation}\label{eq:balanced-validation-score}
 J(\varepsilon)=0.5\,\mathrm{NPE}_{\rm norm}(\varepsilon)+0.5\,\mathrm{SNS}_{\rm norm}(\varepsilon).
\end{equation}
Among candidates within 0.01 of the minimum $J$, we prefer a smaller budget, then lower attained topology cost. There is no minimum NPE-gain condition and no zero-budget Balanced fallback. The selected positive budget is frozen before the final Balanced run. Suffix NPE is archived separately; full-sequence statistics include validation, and historical full-sequence outputs were previously observed, so this is not presented as a new blind test. The reference remains the complete-sequence offline input. QP weights and all other AnchorMTM rules remain fixed (Table~\ref{tab:anchor-parameters-final}).'''
 comparison=r'''Table~\ref{tab:quantitative-final} distinguishes verbatim published scores from local measurements. Bold and underlined SNS, TW and NPE identify the dataset-wide best and second displayed values, automatically computed over all four methods with ties. SNS/TW rankings summarize reported numbers and do not establish a strictly matched-input comparison. Actual full-canvas-normalized TD is shown in the main cells, and TD best/second formatting is computed separately for the published and local normalized groups because a common unit is unconfirmed. Each AnchorMTM group has separate optimization and total time columns in seconds; no separate runtime table is used.

\input{../experiments_final_20261104/tables/quantitative_comparison.tex}
\input{../experiments_final_20261104/tables/anchor_parameter_settings.tex}

All eight AnchorMTM maps and the eight displayed baseline NPE runs complete; Base is omitted from the comparison. The selected Balanced budgets are 1\%, 1\%, 4\%, and 10\% for Gaussian, Ring, Wildfires, and Storms. Gaussian's positive reserved budget attains zero topology error and produces the same complete output as Exact; we retain that row without claiming additional gain. The other three reduce local NPE and cumulative TD, while Wildfires incurs higher SNS and lower TW. This is an observed position--geometry trade-off, not uniform dominance. Ring's local TW uses only one eligible frame out of 40, stated in the table note rather than appended to the numeric cell. Local NPE is lower for AnchorMTM than the baseline reproductions, but reconstructed inputs, unspecified author coordinate units and numerical adapters limit claims about original implementations.'''
 performance=r'''We vary only the topology allowance for validation; this is parameter sensitivity, not a component ablation or evidence of each QP term's independent contribution. All 40 positive-budget validation candidates, normalized score components, $J$, attained errors and legality checks are retained. No suffix metric is used to revise a selected budget. A positive reserved budget can be unused, and identical outputs are reported rather than perturbed to manufacture a difference.

Ring initially fails under independent nearest rounding at its original 196-position raster. A checked numerical adapter jointly rounds the same continuous intervals and anchors to the closest legal integer skeleton, preserving an interior barrier pixel. It first retains nearest-rounded anchors where feasible; otherwise it minimizes maximum coordinate rounding error, then total absolute rounding error. It does not optimize benchmark scores, change the continuous order/widths, increase raster length, or relax topology. The largest correction is about 1.19 pixels. Every final fixed-leaf-label merge matrix (including diagonal), extremum value, anchor count, profile minimum count and budget is checked independently. This is not a certificate for every finite augmented-root extension.

Baseline NPE uses the existing CompactTMTM multiway extension and the disclosed ST-MTM equal-level binary adapter. ST-MTM interval allocation is solved as the same convex Eq.(2), with independent KKT checks; Eq.(1) failures use the unchanged weighted convex QP as a numerical fallback. Certificates retain raw feasibility and scaled-objective stationarity residuals (each below $10^{-7}$), and an explicitly scale-aware complementarity bound. These numerical checks do not relax AnchorMTM topology. The local TMTM reproduction has coincident leaf pixels in 15/744 Storms frames; these frames remain in NPE. No published SNS/TW/TD is recomputed, and these NPE runs are not author binaries or full reproduction certificates.

The two time columns in Table~\ref{tab:quantitative-final} report one measured run per configuration on Apple M4, with single-threaded BLAS and native TTK and sequential extraction; HiGHS keeps its default internal scheduler. Optimization time includes order search and continuous placement. Total time rebuilds source/preprocessing, trees, matching/reference and the final map, including intrinsic checks and integer rounding, without cached intermediates. Balanced is rerun after the new positive-budget selection; unchanged Exact endpoint measurements are retained. Validation and OS page caches may be warm; metric export and process import are excluded. Identical final maps do not imply equal search times. We make no cross-hardware speed claim.'''
 def replace_subsection(text,title,body):
  pattern=r'(\\subsection\{'+re.escape(title)+r'\}\n).*?(?=\\subsection\{|\\section\{)'
  updated,count=re.subn(pattern,lambda m:m.group(1)+body+'\n\n',text,flags=re.S);assert count==1,(title,count);return updated
 text=replace_subsection(text,'Experimental Setup',setup);text=replace_subsection(text,'Quantitative Comparison',comparison);text=replace_subsection(text,'Ablation Study and Performance',performance)
 text=text.replace('Storms example linking spatial feature supports to a temporal map ($\\varepsilon=5\\%$).','Qualitative Storms archive linking spatial feature supports to a temporal map ($\\varepsilon=5\\%$; separate preprocessing from Table~\\ref{tab:quantitative-final}).')
 assert 'TStress' not in text and 'TSpearman' not in text;tex.write_text(text)
 readme=P/'README.md';text=readme.read_text();marker='\n## 2026-11-04 正式定量实验\n';entry=marker+'\n四数据集8组AnchorMTM与12组基线NPE已完成。正式目录：[experiments_final_20261104](experiments_final_20261104/REPORT_zh.md)。Gaussian/Wildfires为明确标注重建输入；Ring保持196点并通过联合整数舍入。Balanced按固定验证J选择正预算：Gaussian1%、Ring1%、Wildfires4%、Storms10%；Gaussian实际误差0、输出与Exact相同，不制造收益。SNS/TW/NPE按数据集四方法统一自动标最优/次优（SNS/TW跨输入为描述性汇总），归一化TD已直接放回主表并标单位、暂不跨单位排名；两组Anchor各有独立t_opt/t_total列，删除表3、Base行和TW覆盖率上标，参数表白底；完整指标、独立参数表（含实际NMLEmax）、冷流水线时间、全部候选、LaTeX和复现脚本均在该目录。5.1、5.2、5.5已同步；其余未完成章节不因本次定量更新被视为完成。\n'
 if marker in text:text=text.split(marker)[0]
 readme.write_text(text+entry)
 print(O/'REPORT_zh.md');print(tex)

if __name__=='__main__':main()
