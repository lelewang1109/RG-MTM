"""Scientific figures and Chinese report for the verified original-grid run."""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.cm import ScalarMappable

from experiments.volume3d.run_paper import ROOT,OUT,DATA,TREES
from experiments.volume3d.prepare import sha256
from experiments.volume3d.audit_tangaroa import reference_dvr


def read(p):return json.loads(Path(p).read_text())
def pct(v):return f'{100*v:.3f}%'
def primary_motion(row,truth='3d'):return next(m for m in row['motion'] if m['lag']==2 and m['epsilon']==.02 and m['truth']==truth)


def build(directory=OUT,volume=True):
    out=Path(directory);verification=read(out/'verification.json');manifest=read(out/'manifest.json')
    assert verification['status']=='passed' and verification['manifest_sha256']==sha256(out/'manifest.json')
    assert verification['verification_source_sha256']==sha256(Path(__file__).with_name('verify_paper.py'))
    metrics=read(out/'metrics.json');rows=read(out/'frame_metrics.json');features=read(out/'features.json')
    ref=read(out/'reference.json');params=read(out/'parameters.json');certificates=read(out/'certificates.json');protocol=read(out/'protocol.json')
    indices=manifest['indices'];T=len(indices);is_full=indices==list(range(201));names=[r['method'] for r in metrics if r['method']!='Exact projection']
    settings_path=ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json';settings=read(settings_path)
    tf=np.array(settings['transfer_function_points']);cmap=LinearSegmentedColormap.from_list('Tangaroa author',[(v[0],tuple(v[1:4])) for v in tf],N=1024)
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    generated=[]
    def save(fig,name):
        for extension in ['png','svg']:
            p=out/(name+'.'+extension);fig.savefig(p,dpi=180,bbox_inches='tight');generated.append(p)
        plt.close(fig)
    maps=np.load(out/'display_maps.npz')
    fig,axes=plt.subplots(len(names),1,figsize=(12,10.5),layout='constrained',sharex=True)
    for ax,name in zip(axes,names):
        ax.imshow(maps[name],origin='lower',aspect='auto',extent=(indices[0]-.5,indices[-1]+.5,0,1),vmin=0,vmax=2,cmap=cmap,interpolation='nearest')
        # Subpixel-width intervals can disappear in a uniform display preview.
        # Overlay the actual retained extrema, identically for every method;
        # this is an explicit landmark layer, not edited scalar-map samples.
        for t,index in enumerate(indices):
            row=next(r for r in rows if r['index']==index and r['method']==name)
            values=[features['frames'][t]['source_node_values'][str(v)] for v in features['frames'][t]['leaf_ids']]
            ax.scatter(np.full(len(values),index),np.asarray(row['anchors'])/(row['raster']-1),c=values,cmap=cmap,vmin=0,vmax=2,s=.7,linewidths=0)
        ax.set_ylabel(name.replace('RG-MTM-R ','R kappa='));ax.set_yticks([0,.5,1])
    axes[-1].set_xlabel('Original source-frame index (dt=0.01)')
    fig.suptitle(f'Tangaroa: {T} original 300 x 180 x 120 volumes | TTK persistence 10%\n4096-row scalar previews with actual extrema overlaid; all metrics use full arrays\nVertical axis: normalized TMTM linearization / fixed-reference domain fraction for RG')
    fig.colorbar(ScalarMappable(norm=Normalize(0,2),cmap=cmap),ax=axes,pad=.01,shrink=.7,label='Velocity magnitude after author preprocessing and TTK')
    save(fig,'comparison_maps')
    own=[next(r for r in metrics if r['method']==name) for name in names if name.startswith('RG-')]
    xx=[0,.02,.2,1.];fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    axes[0].plot(xx,[100*r['NROE_mean'] for r in own],'o-');axes[0].set_ylabel('Mean NROE (%)')
    axes[1].plot(xx,[100*r['NMLE_mean'] for r in own],'o-',label='mean');axes[1].plot(xx,[100*r['NMLE_max'] for r in own],'s--',label='maximum');axes[1].legend();axes[1].set_ylabel('Measured merge-level error (% of [0,2])')
    for truth,marker in [('3d','o-'),('projected','s--')]:
        axes[2].plot(xx,[primary_motion(r,truth)['error'] if primary_motion(r,truth)['error'] is not None else np.nan for r in own],marker,label=truth)
    axes[2].legend();axes[2].set_ylabel('Motion error (lag=2, eps=2%)')
    for ax in axes:ax.set_xlabel('Relaxation eligibility fraction');ax.grid(alpha=.2)
    fig.suptitle('Eligibility is not an NMLE cap; optional flattening pruning disabled')
    save(fig,'relaxation_tradeoff')
    fig,axes=plt.subplots(2,1,figsize=(12,5),layout='constrained',sharex=True)
    for key,label in [('hierarchy','hierarchy'),('free','free')]:
        lo=np.array([r[key]['lower'] for r in certificates])/ref['extent'];hi=np.array([r[key]['upper'] for r in certificates])/ref['extent']
        axes[0].plot(indices,100*hi,label=label+' upper');axes[0].fill_between(indices,100*lo,100*hi,alpha=.2)
    axes[0].legend();axes[0].set_ylabel('Position certificate (% axis)')
    axes[1].fill_between(indices,100*np.array([r['H_lower'] for r in certificates])/ref['extent'],100*np.array([r['H_upper'] for r in certificates])/ref['extent'],alpha=.4,label='hierarchy obstruction interval')
    # Tight verified brackets have subpixel thickness: draw their midpoint too.
    axes[1].plot(indices,50*np.array([r['H_lower']+r['H_upper'] for r in certificates])/ref['extent'],lw=1.2,label='H bracket midpoint')
    axes[1].axhline(2,c='black',ls='--',lw=1,label='2% gate');axes[1].legend();axes[1].set_ylabel('H (% axis)');axes[1].set_xlabel('Original source-frame index')
    save(fig,'certificate_bounds')
    if volume:
        selected=[indices[0],indices[len(indices)//2],indices[-1]]
        fig,axes=plt.subplots(3,1,figsize=(10,10),layout='constrained')
        for ax,index in zip(axes,selected):
            field=np.memmap(str(TREES/f'frame_{index:03d}')+'.values.f32',dtype='<f4',mode='r').reshape(120,180,300)
            img,corners,projected=reference_dvr(field,np.array([-.35,.65,-.3,.3,-.5,-.3]),settings,width=640)
            ax.imshow(img,origin='lower',extent=(-1,1,-1,1),aspect=1/settings['camera']['aspect'])
            for a in range(len(corners)):
                for b in range(a+1,len(corners)):
                    if np.count_nonzero(corners[a]!=corners[b])==1:ax.plot(projected[[a,b],0],projected[[a,b],1],c='.5',lw=.5)
            # One fixed camera viewport for all frames; no spatial data crop.
            ax.set_xlim(projected[:,0].min()-.03,projected[:,0].max()+.03);ax.set_ylim(projected[:,1].min()-.03,projected[:,1].max()+.03)
            ax.axis('off');ax.set_title(f'Actual TTK-simplified layout input: frame {index}',loc='left')
        fig.suptitle('Original grid, persistence 10% | author camera and transfer function\nCPU reference DVR; vessel mesh and original lighting omitted')
        fig.colorbar(ScalarMappable(norm=Normalize(0,2),cmap=cmap),ax=axes,shrink=.6,pad=.01,label='Velocity magnitude')
        save(fig,'actual_3d_inputs')
    columns=['method','frames','NROE_mean','NROE_max','NMLE_mean','NMLE_max','anchor_MAE','exact_topology_frames','relaxed_frames','ME_3D','clear_3D','ME_projected','clear_projected']
    with (out/'comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for row in metrics:
            a,b=primary_motion(row),primary_motion(row,'projected')
            writer.writerow({**{k:row.get(k) for k in columns[:-4]},'ME_3D':a['error'],'clear_3D':a['clear'],'ME_projected':b['error'],'clear_projected':b['clear']})
    counts=[len(r['leaf_ids']) for r in features['frames']];nodes=[len(r['children']) for r in features['frames']]
    gate={s:sum(r['gate']==s for r in certificates) for s in ['active','inactive','undetermined']}
    max_p_gap=max(r['hierarchy']['upper']-r['hierarchy']['lower'] for r in certificates)/ref['extent']
    max_r_gap=max([r['primary_certificate']['upper']-r['primary_certificate']['lower'] for r in rows if 'primary_certificate' in r]+[0])/ref['extent']
    virtual=sum(r.get('virtual_saddle_copies',0) for r in rows)
    max_qp_gap=max(r['layout']['convex_first_order_gap'] for r in rows if 'layout' in r)
    max_raster_error=max(r['raster_errors']['anchor_error'] for r in rows if 'raster_errors' in r)/ref['extent']
    max_width_error=max(r['raster_errors']['interval_extent_error'] for r in rows if 'raster_errors' in r)/ref['extent']
    boundary=sum(sum(r['boundary']) for r in features['frames']);instances=sum(counts)
    scalar_meta=[read(DATA/f'scalar_{i:03d}.json') for i in indices]
    maximum_frame_range=max(r['processed_range'][1]-r['processed_range'][0] for r in scalar_meta)
    first_max=next(r['raw_range'][1] for r in scalar_meta if r['index']==indices[0])
    lines=['# Tangaroa 原网格 RG-MTM 三维实验','',
        ('**完整 201 帧已计算并通过独立复核。**' if is_full else f'**运行检查：仅 {T} 帧，不能作为完整序列实验。**'),' ',
        f'输入为官方 Tangaroa 速度场编号 {indices[0]}–{indices[-1]}，每帧 XYZ=300×180×120，时间步长 0.01。'
        '在原网格计算速度模长，将 abs(v)<1e-6 替换为 1，再截断到 [0,2]，'
        '使用 TTK 0.9.9 的传统标量简化算法、绝对持久性阈值 0.2（声明范围的 10%），提取 join tree。'
        '**没有空间降采样、高斯平滑、逐帧归一化或按叶数删帧。**','',
        '本实验落实作者公开工作空间的输入语义；作者最终 Magnitude 导出文件、校验和及原二进制环境未取得，'
        '不声称与未公开文件逐字节一致，或图 15 像素级复现。此前粗网格 split-tree 试跑不与本组结果合并。','',
        f'派生拓扑的复现差异：本组实际节点数范围为 {min(nodes)}–{max(nodes)}，'
        '论文表 1 的 10% 行报告为 50–186。'
        +('范围一致，但没有作者逐帧输出可用于逐树校验。' if (min(nodes),max(nodes))==(50,186) else
          '两者不完全一致；差异原因尚未逐帧定位，当前不能把本组派生树称为作者最终树的精确复现。'
          '固定库版本、CPU 标量计算与未公开最终导出／运行设置均属于需要进一步核对的环节，不能据此断言某一环节就是原因。')+
        '本次方法对照共享已保存、已校验的同一输入和实际树；这项差异不通过改阈值或挑帧来消除。','',
        f'输入一致性补充：源第 {indices[0]} 帧原始速度模长最大值为 {first_max}；'
        f'所用帧的最大单帧标量范围为 {maximum_frame_range:.12g}（float32 为 {float(np.float32(maximum_frame_range))}）。'
        '完整序列对应作者工作空间记录的原始最大值 3.0590057373046875 和最大持久性约 1.9994903；'
        '这是额外的数值指纹，不代替未公开导出文件的校验和。','',
        '## 方法实现与可证明范围','',
        f'- 实际树规模：每帧 {min(nodes)}–{max(nodes)} 个节点，{min(counts)}–{max(counts)} 个叶特征；没有 6 叶容量限制。',
        f'- TMTM 以作者工作空间的第 {protocol["tmtm_focus_source_index"]} 帧为焦点，向两个时间方向进行重叠优化。',
        f'- 真正多重鞍点采用明确的一维输出补充：m 个子树之间放置 m−1 个同值分隔样本；全序列额外 {virtual} 个同值鞍点副本。'
        '原始输入与 TTK 标量场不变，原样本 ID 全量核对，每个原网格样本以共享的 TTK 简化标量值出现一次。该非二叉处理是对论文二叉算法的显式实现扩展。',
        '- RG-MTM 仍使用原连续宽度、间距、位置预算和三维几何／运动残差目标；宽度按叶弧支持体积换算，比例在全序列固定。',
        '- 大树主问题使用连续 Pareto DP，较高元数时使用工作量下界或限时 MILP，并保留主／对偶界。'
        '**次级凸目标仅在最多 4 个声明的合法候选顺序上求解，不声称遍历所有顺序或次级全局最优。**',
        '- 本组 RG-MTM-R 关闭可选的放松后剪枝，保留全部满足资格的放松节点；这与旧小树默认开启剪枝的试跑设置不同，需按本协议复现。',
        f'- P 主位置证书最大区间宽度为 {max_p_gap:.6g} L；所有 R 证书最大区间宽度为 {max_r_gap:.6g} L（L 为固定参考轴长度）。'
        f'候选固定顺序凸 QP 的最大一阶差距为 {max_qp_gap:.6g}（目标按参考长度平方归一化）。',
        f'- 连续预算在未取整布局上检查；实际渲染锚点额外取整误差最大为 {max_raster_error:.6g} L，'
        f'区间宽度的栅格误差最大为 {max_width_error:.6g} L。渲染位置保证相应包含保存的取整误差。',
        f'- H>2% 门控：确定触发 {gate["active"]} 帧，确定未触发 {gate["inactive"]} 帧，未判定 {gate["undetermined"]} 帧；未判定帧保守地保持层次，不冒充精确分类。',
        f'- 固定三维参考方向 d={ref["direction"]}，捕获 {pct(ref["capture"])} 的匹配极值位移能量；参考值是三维极值坐标投影，不是完整三维位置。',
        f'- {boundary}/{instances} 个叶支持实例触边。匹配为计算得到的叶弧体素重叠，不是物理涡旋身份或用户感知真值。','',
        '## 实测结果','',
        '| 方法 | NROE 均值 | 实测 NMLE 均值／最大值 | 三维运动错误 | 投影运动错误 | 层次无误差帧数 |',
        '|---|---:|---:|---:|---:|---:|']
    for r in metrics:
        a,b=primary_motion(r),primary_motion(r,'projected')
        rate=lambda m:'未定义（无清晰事件）' if m['error'] is None else f"{m['error']:.4f}（n={m['clear']}）"
        lines.append(f"| {r['method']} | {pct(r['NROE_mean'])} | "+('—' if 'NMLE_mean' not in r else pct(r['NMLE_mean'])+'／'+pct(r['NMLE_max']))+
            f" | {rate(a)} | {rate(b)} | {r.get('exact_topology_frames','—')} |")
    lookup={r['method']:r for r in metrics};baseline=lookup['TMTM'];preserve=lookup['RG-MTM-P'];relaxed=lookup['RG-MTM-R 0.2']
    lines+=['','## 本次观察','',
        f"TMTM → RG-MTM-P 的平均 NROE 为 {pct(baseline['NROE_mean'])} → {pct(preserve['NROE_mean'])}。"
        +('本组数据中，P 改善了固定方向上的顺序保持。' if preserve['NROE_mean']<baseline['NROE_mean'] else '本组数据中，P 没有降低 TMTM 的平均顺序误差，不能宣称顺序方面优于该对照。'),
        f"P → R（20% 资格、未剪枝）的平均 NROE 为 {pct(preserve['NROE_mean'])} → {pct(relaxed['NROE_mean'])}，"
        f"R 的实测 NMLE 均值／最大值为 {pct(relaxed['NMLE_mean'])}／{pct(relaxed['NMLE_max'])}。"
        '应将位置变化与这项实际拓扑代价一起解释，不能只展示位置收益。']
    bmotion,pmotion=primary_motion(baseline),primary_motion(preserve)
    if bmotion['clear']:
        lines+=['',f"默认三维几何运动代理的错误率：TMTM {bmotion['error']:.4f}，P {pmotion['error']:.4f}，"
            f"共享 {bmotion['clear']} 个清晰事件；其中纯内部事件 {bmotion['interior_clear']} 个。"
            '这项结果直接评价三维接近／远离代理，不由 NROE 大小推出，也不能当作物理流场跟踪或读者准确率。']
    projection=primary_motion(lookup['Exact projection'])
    if projection['clear'] and projection['error']:
        lines+=['',f"精确参考投影的 NROE 为 0，但三维代理错误率仍为 {projection['error']:.4f}。"
            '这表明该参考投影对这些事件丢失了三维距离信息；它不是所有一维布局的通用误差下界。']
    anchor_notes='；'.join(r['method']+'：'+pct(r['anchor_MAE']) for r in metrics if r['method'].startswith('RG-'))
    lines+=['',
        'NROE 是按每帧叶顺序作最优单调校准后的误差，再取时间均值；不能当作实际锚点偏移。'
        'NMLE 从完整保存的一维图中实际测量每对叶的最大间隔值，与同一输入树的 LCA 标量比较，再除以声明标量范围 2。'
        '表中层次无误差帧数指原叶间合并层级误差不超过 1e-6 的帧数。','',
        'RG 实际渲染锚点的 MAE（按参考轴长度归一化，逐帧均值后再平均）：'+anchor_notes+'。'
        'TMTM 纵轴表示归一化线性化位置，RG 纵轴对应固定物理参考轴的域比例；不把 TMTM 纵轴直接当作真实物理位置。','',
        '运动比较默认 lag=2、阈值 2%；三维真值使用原物理坐标欧氏距离变化，投影真值使用同一固定参考方向。'
        '表中 n 是共享计算轨迹中的清晰事件数；完整结果另含 lag=1/2/4 和 1%/2%/5% 阈值。'
        '这些是几何判断代理，不能直接表述为读者实验或物理涡旋识别准确率。','',
        '**持久性 10% 与 RG 的 2%／20%／100% 放松资格参数不同。资格参数也不是输出 NMLE 的硬上界。**'
        '放松的实际拓扑代价以上表实测 NMLE 为准；不能仅用参考顺序改善推断完整三维运动必然改善。','',
        '## 独立核验与图','',
        f'- 独立重新解析 {T} 个原始速度体并逐值重算近零替换／截断后的全部标量样本；最大差 {verification["input_max_difference"]}。',
        '- 检查原始 ZIP 成员 CRC32／SHA256、坐标头、全部增广弧样本所有权、直接父链 LCA、全部保存地图的实际障碍、固定宽度与位置预算。',
        '- TMTM 保存输出样本 ID，独立证明每个源样本出现一次，额外样本严格等于声明的同值鞍点副本。',
        '- 独立按向下取整像素模型在均匀验证帧复核连续位置证书下界；详细数值见 verification.json。',
        '- 图像仅采样到 4096 行显示；数值复核读取完整 TMTM 原样本地图和 131072 行 RG 地图，未从 PNG 计算误差。',
        '- 时序图另用同一规则叠加各方法实际保留极值的坐标及标量颜色，避免小于一个显示像素的特征被预览采样漏掉；此标记层不改动任何标量数组。',
        '- [方法时序地图](comparison_maps.png)','- [放松参数与实测代价](relaxation_tradeoff.png)','- [位置证书及门控区间](certificate_bounds.png)']
    if volume:lines.append('- [实际 TTK 简化后三维输入体渲染](actual_3d_inputs.png)（作者相机／传递函数；省略未取得的船体 STL 和原光照）')
    lines.append('- [简化前的原分辨率三帧体渲染核对](../tangaroa-input-audit-20261018/original_resolution_volume_audit.png)（与用于布局的 TTK 简化后输入分别展示）')
    lines.append('- [论文风格组合图及显示协议](paper_style/README.md)：2×2 RG-P/R 时间图、三帧体渲染，以及 TMTM 全域／作者中间 20% 视窗对照；持久性统一为 10%。')
    lines+=['- [未舍入比较表](comparison.csv)','- [逐帧数值、完整数组路径及哈希](frame_metrics.json)',
        '- [输入、源码与证据清单](manifest.json)','- [独立核验记录](verification.json)','- [完整协议](protocol.json)','',
        '完整原始体、TTK 输出和大体积地图存放于本地 data/real/Tangaroa-FAU/paper_full_201/，不并入 Git；'
        '报告保留其哈希与复现脚本。现有六序列／342 帧主表没有重算或改写。','',
        '## 来源','',
        '- [FAU 官方数据页](https://www.vc.tf.fau.de/publications/datasets/)',
        '- 原始模拟致谢：Stéphane Popinet、Murray Smith、Craig Stevens，'
        '[Experimental and Numerical Study of the Turbulence Characteristics of Airflow around a Research Vessel](https://journals.ametsoc.org/abstract/journals/atot/21/10/1520-0426_2004_021_1575_eansot_2_0_co_2.xml)，'
        '*Journal of Atmospheric and Oceanic Technology* 21(10):1575–1589，2004。规则网格公开版本由数据提供方重采样并发布。',
        '- [TMTM 作者仓库](https://github.com/Wiebke/TemporalMergeTreeMaps)，工作空间固定提交 2c75a10ed2cd55177a25ff751e0c0a8261200717。',
        '- [TTK 0.9.9 源码](https://github.com/topology-tool-kit/ttk/tree/0.9.9)；本地记录压缩包、适配源码与可执行文件 SHA256。','']
    (out/'REPORT.md').write_text('\n'.join(lines));generated +=[out/'REPORT.md',out/'comparison.csv']
    render_manifest=dict(source_sha256=sha256(__file__),input_sha256={name:sha256(out/name) for name in
        ['manifest.json','verification.json','metrics.json','frame_metrics.json','certificates.json','features.json','reference.json','parameters.json','protocol.json','display_maps.npz']},
        author_rendering_settings_sha256=sha256(settings_path),files={p.name:sha256(p) for p in generated})
    (out/'render_manifest.json').write_text(json.dumps(render_manifest,indent=2)+'\n')
    (out/'status.json').write_text(json.dumps(dict(status='complete_verified' if is_full else 'complete_verified_smoke_test',frames=T),indent=2)+'\n')
    print('Built verified report',out/'REPORT.md')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path,nargs='?',default=OUT)
    parser.add_argument('--skip-volume',action='store_true');args=parser.parse_args();build(args.directory,not args.skip_volume)
