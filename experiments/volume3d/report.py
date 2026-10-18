"""Render scientific figures and a concise Chinese report from saved evidence."""
from pathlib import Path
import csv
import json
import hashlib
from itertools import combinations
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load(path):return json.loads(Path(path).read_text())
def pct(value):return '—' if value is None else f'{100*value:.3f}%'


def main_motion(row,truth):
    return next(v for v in row['motion'] if v['lag']==2 and v['epsilon']==.02 and v['truth']==truth)


def build(directory):
    directory=Path(directory)
    notice_path=directory/'interpretation_notice.json'
    notice=load(notice_path) if notice_path.exists() else None
    metrics=load(directory/'metrics.json');meta=load(directory/'input_protocol.json')
    manifest=load(directory/'manifest.json');audit=load(directory/'preprocessing_audit.json')
    features=load(directory/'features.json');pruned=load(directory/'persistence_diagnostic.json')
    axes=load(directory/'reference_axes.json')
    boundary_count=sum(sum(b) for b in features['boundary']);instances=sum(map(len,features['ids']))
    pair_count=interior_pairs=0;interior_flags=[];distance_changes=[]
    for t in range(len(features['tracks'])-2):
        ia={v:i for i,v in enumerate(features['tracks'][t])};ib={v:i for i,v in enumerate(features['tracks'][t+2])}
        for a,b in combinations(ia.keys()&ib.keys(),2):
            pair_count+=1
            interior=not any([features['boundary'][t][ia[a]],features['boundary'][t][ia[b]],
                features['boundary'][t+2][ib[a]],features['boundary'][t+2][ib[b]]])
            interior_pairs+=interior;interior_flags.append(interior)
            old=np.asarray(features['extrema'][t]);new=np.asarray(features['extrema'][t+2])
            distance_changes.append(float(np.linalg.norm(new[ib[a]]-new[ib[b]])-np.linalg.norm(old[ia[a]]-old[ia[b]])))
    with np.load(directory/'processed_fields.npz') as source:
        fields,coords=source['fields'],source['coords']
    clear=np.abs(distance_changes)>.02*np.linalg.norm(np.ptp(coords,axis=0))
    interior_clear=int(np.sum(clear & np.asarray(interior_flags,bool)))
    assert int(np.sum(clear))==main_motion(metrics[0],'3d')['clear']
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.savefig(directory/(name+'.png'),dpi=180,bbox_inches='tight')
        fig.savefig(directory/(name+'.svg'),bbox_inches='tight');plt.close(fig)
    fig=plt.figure(figsize=(13.5,5.1),layout='constrained');volume_axes=[]
    selected=[0,len(fields)//2,len(fields)-1]
    for j,t in enumerate(selected):
        ax=fig.add_subplot(1,3,j+1,projection='3d')
        volume_axes.append(ax)
        values=fields[t].ravel();keep=values>=np.quantile(values,.95)
        cloud=ax.scatter(*coords[keep].T,c=values[keep],s=8,alpha=.14,cmap='magma',vmin=float(fields.min()),vmax=float(fields.max()),rasterized=True)
        peaks=np.array(features['extrema'][t]);ax.scatter(*peaks.T,c='#0072b2',s=35,edgecolor='white',linewidth=.7)
        for i,p in enumerate(peaks):ax.text(*p,str(features['tracks'][t][i]),fontsize=8)
        source_label=f"t={meta['times'][t]:.2f}" if 'times' in meta else f"Source index {meta['indices'][t]}"
        ax.set(xlabel='x',ylabel='y',zlabel='z',title=f'{source_label} | {len(peaks)} extrema')
        lo,hi=coords.min(0),coords.max(0);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo)
        span=hi-lo
        ax.set_xticks(np.linspace(lo[0]+.15*span[0],hi[0]-.15*span[0],3));ax.set_yticks(np.linspace(lo[1]+.15*span[1],hi[1]-.15*span[1],3));ax.set_zticks(np.linspace(lo[2],hi[2],3))
        ax.tick_params(labelsize=7,pad=0)
        ax.view_init(elev=23,azim=-60)
    fig.suptitle(('Historical coarse split-tree pilot; not the paper input\n' if notice else '')+
        'Processed 3-D scalar field: upper 5% samples (transparent); leaf extrema and shared track IDs (blue)')
    fig.colorbar(cloud,ax=volume_axes,orientation='horizontal',shrink=.55,pad=.05,aspect=40,label='Processed scalar value')
    save(fig,'input_3d')
    available={r['method'] for r in metrics}
    names=[n for n in ['TMTM','ST-MTM','Hilbert','Morton','RG-MTM-P','RG-MTM-R 0.2'] if n in available]
    fig,axs=plt.subplots(len(names),1,figsize=(12,10),layout='constrained',sharex=True)
    low,high=float(fields.min()),float(fields.max())
    # Display cap is disclosed; all numerical checks use full arrays.
    for ax,name in zip(axs,names):
        with np.load(directory/(name.replace(' ','_')+'_map.npz')) as source:
            matrix=source['map'];anchors=np.split(source['anchors'],np.cumsum(source['anchor_counts'])[:-1])
        step=max(1,int(np.ceil(len(matrix)/4096)))
        picture=ax.imshow(matrix[::step],origin='lower',aspect='auto',cmap='magma',vmin=low,vmax=high,
                  extent=(-.5,len(fields)-.5,0,1),interpolation='nearest')
        for track in sorted(set(k for ids in features['tracks'] for k in ids)):
            tt=[t for t,ids in enumerate(features['tracks']) if track in ids]
            yy=[anchors[t][features['tracks'][t].index(track)]/(len(matrix)-1) for t in tt]
            cuts=[0]+[i for i in range(1,len(tt)) if tt[i]!=tt[i-1]+1 or tt[i] in meta.get('break_before',[])]+[len(tt)]
            for start,end in zip(cuts[:-1],cuts[1:]):ax.plot(tt[start:end],yy[start:end],color='white',lw=.65,alpha=.8)
        ax.set(ylabel=name,yticks=[])
        for boundary in meta.get('break_before',[]):ax.axvline(boundary-.5,color='white',ls='--',lw=1.)
    ticks=sorted(set([0,len(fields)-1]+[b-1 for b in meta.get('break_before',[])]+meta.get('break_before',[])))
    labels=[f"{meta['times'][t]:.2f}" if 'times' in meta else str(meta['indices'][t]) for t in ticks]
    axs[-1].set_xticks(ticks,labels);axs[-1].set_xlabel('Source simulation time' if 'times' in meta else 'Original source-frame index (disconnected windows separated by dashed lines)')
    fig.suptitle(('Historical coarse split-tree pilot; not the paper input\n' if notice else '')+
        'Same processed scalar input and color scale; native curves retain all samples without refilling')
    fig.colorbar(picture,ax=axs,shrink=.65,pad=.01,label='Processed scalar value')
    save(fig,'comparison_maps')
    rows=[r for r in metrics if r['method'].startswith('RG-')]
    caps=[0 if r['method']=='RG-MTM-P' else float(r['method'].split()[-1]) for r in rows]
    fig,axs=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
    axs[0].plot(caps,[100*r['NROE_mean'] for r in rows],'o',label='NROE mean')
    axs[0].plot(caps,[100*r['anchor_MAE'] for r in rows],'s',label='Anchor MAE');axs[0].set_ylabel('% reference extent');axs[0].legend()
    axs[1].plot(caps,[100*r['NMLE_mean'] for r in rows],'o',label='NMLE mean')
    axs[1].plot(caps,[100*r['NMLE_max'] for r in rows],'s',label='NMLE max');axs[1].set_ylabel('% processed scalar range');axs[1].legend()
    for truth,color in [('3d','#d55e00'),('projected','#0072b2')]:
        points=[main_motion(r,truth) for r in rows]
        axs[2].plot(caps,[np.nan if p['error'] is None else p['error'] for p in points],'o',color=color,label=truth)
    axs[2].set_ylabel('Motion error fraction (k=2, eps=2%)');axs[2].legend()
    for ax in axs:ax.set_xlabel('Tested relaxation eligibility / scalar range');ax.grid(alpha=.2)
    save(fig,'relaxation_sensitivity')
    fig,axs=plt.subplots(1,2,figsize=(9,3.4),layout='constrained')
    xx=[p['persistence_fraction'] for p in pruned]
    axs[0].plot(xx,[p['mean_leaves'] for p in pruned],'o-');axs[0].set_ylabel('Retained leaves / frame')
    axs[1].plot(xx,[100*p['width_free_bound_mean'] for p in pruned],'o-');axs[1].set_ylabel('Width-free obstruction (% reference)')
    for ax in axs:ax.set_xlabel('Persistence deletion threshold / scalar range');ax.grid(alpha=.2)
    fig.suptitle('Hierarchy-only deletion diagnostic: no simplified scalar field or rendered claim')
    save(fig,'persistence_diagnostic')
    columns=['method','NROE_mean','NROE_max','NMLE_mean','NMLE_max','anchor_MAE','anchor_max','topology_exact_frames','seconds',
             'ME_3D','clear_3D','ME_projected','clear_projected']
    with (directory/'comparison.csv').open('w',newline='') as output:
        writer=csv.DictWriter(output,fieldnames=columns);writer.writeheader()
        for r in metrics:
            m3,mp=main_motion(r,'3d'),main_motion(r,'projected')
            writer.writerow({**{k:r.get(k) for k in columns[:-4]},'ME_3D':m3['error'],'clear_3D':m3['clear'],
                             'ME_projected':mp['error'],'clear_projected':mp['clear']})
    lines=['# 三维补充实验：'+meta['dataset'],'']
    if notice:
        lines+=['## 输入核对更正（'+notice['date']+'）','',notice['message'],'',
            '[原分辨率输入复核报告]('+notice['audit_report']+')。以下数组和数值保留为历史试跑记录；数值通过旧协议核验，不代表协议与论文一致。','']
    lines+=[
        '本结果单独保存，未并入现有六序列／342 帧主实验。以下指标均由本次真实计算生成。','',
        f"- 输入：{manifest['shape_tzyx']}（T×Z×Y×X），共 {manifest['frames']} 帧。",
        f"- 每帧保留叶数：{min(manifest['leaves'])}–{max(manifest['leaves'])}；冲突帧：{manifest['conflict_frames']}。",
        f"- 边界支持特征：{boundary_count}/{instances} 个实例；lag=2 配对窗口共 {pair_count} 个，其中纯内部配对 {interior_pairs} 个，满足默认三维清晰阈值的纯内部事件 {interior_clear} 个（支持触边不等于极值点位于边界）。",
        f"- 固定三维参考方向：{manifest['reference']['candidates']['direction']['a']}。",
        f"- 匹配运动捕获比例：{pct(manifest['reference']['candidates']['direction']['capture'])}。",
        f"- 采用的平滑 sigma：{audit[-1]['sigma_voxels']} 个网格样本；相对原重采样标量场 RMSE：{audit[-1]['rmse']:.6g}。",
        '- 特征宽度以体积计算；体积与画布的换算在整段序列中固定。','',
        '## 方法比较','',
        '| 方法 | NROE 均值 | NMLE 均值／最大值 | 三维 ME | 投影 ME | 拓扑完全相同帧数 |',
        '|---|---:|---:|---:|---:|---:|']
    for row in metrics:
        m3,mp=main_motion(row,'3d'),main_motion(row,'projected')
        rate=lambda v:'—（无清晰事件）' if v['error'] is None else f"{v['error']:.3f}（n={v['clear']}）"
        lines.append(f"| {row['method']} | {pct(row['NROE_mean'])} | {pct(row['NMLE_mean'])}／{pct(row['NMLE_max'])} | {rate(m3)} | {rate(mp)} | {row['topology_exact_frames'] if row['topology_exact_frames'] is not None else '—'} |")
    lines+=['','NROE 是每帧最优单调校准后的顺序误差，再取时间均值；不是实际锚点偏移。NMLE 是完整填充图中测得的合并层级误差，以处理后全序列标量范围归一化。ME 是清晰接近／远离事件中的反向＋漏判比例，默认间隔 2 帧、阈值 2%。所有方法共享轨迹身份和真值事件；无清晰事件时记为未定义。','',
        '## 三维参考方向诊断','','这里仅改变投影方向以诊断运动捕获比例和宽度无关的层次障碍，没有为每个方向重新运行布局。','',
        '| 方向 | 匹配运动捕获比例 | 层次障碍均值／最大值 |','|---|---:|---:|']
    for row in axes:lines.append(f"| {row['axis']} | {pct(row['capture'])} | {pct(row['width_free_bound_mean'])}／{pct(row['width_free_bound_max'])} |")
    lines+=['',
        '## 适用条件和限制','',
        '- 只证明这里保存的三维处理后输入能运行完整流程，不能据此宣称在任意三维体数据上保持空间距离或运动。',
        '- 参考轴正交方向的运动不受位置误差保证；完整三维真值与投影真值分别报告。',
        '- 持久性阈值只做树上删除诊断，没有执行 TTK 标量场简化，也没有把删叶结果当作完整渲染结果。',
        '- 平滑按所有帧的叶数和二叉性选择，未按方法胜负或运动误差选择；所有未通过候选保存在 preprocessing_audit.json。',
        '- 当前完整布局仍枚举合法叶序，容量上限为 6 叶；该实验不支持大规模完整布局的结论。',
        '- 跟踪是计算得到的一对一重叠匹配，不是物理特征身份真值，也不是用户实验。',
        '- 空间曲线保留每个处理后样本且不接受重新填充；TMTM 保留样本，RG 使用声明的填充。',
        '- 主比较使用第一篇论文 TMTM；ST-MTM 若出现，仅为本项目实现的三维扩展，不代表第二篇论文验证过三维输入。',
        '- 时序地图的图像导出最多采样 4096 行，白线为共享跟踪的极值锚点；数值验证使用完整分辨率。']
    if meta.get('dataset','').lower().startswith('cylinder'):
        lines+=['',f"- 数据来自[作者下载页面]({meta['source_page']})；公开版本为 102 帧速度场，本次先在源网格计算 Q，再进行空间重采样。",
            '- 与原论文 508 帧 Q 输入不同；这里是公开版本扩展实验，不能称为原案例精确复现。',
            '- early／middle／late 是预先固定的时间覆盖窗口，不是已验证的物理阶段分界。窗口间不建立匹配或运动事件，也不进行跨窗时间优化。',
            '- 源数据 z 方向具有周期边界；这里采用非周期网格和单边边界导数，边界特征单独标记，结论受此处理限制。']
    elif 'source_url' in meta:
        lines+=['',f"- 数据来源：[公开提供者]({meta['source_page']})。",f"- 版本说明：{meta.get('version_note','见 input_protocol.json')}。"]
    if meta['dataset']=='Tangaroa-ECNR-VTM':
        lines+=['',
            '- 原始体数据 XYZ=300×180×120，公开包共 150 帧；本次使用文件编号 1–12、70–81、139–150，共 36 帧。每一帧均是完整三维体，不是二维切片。',
            '- 全空间范围先高斯抗混叠再三线性重采样为 XYZ=30×18×12；没有按方法表现选择空间区域或帧。',
            '- 同第一篇论文使用 Tangaroa 模拟，但此版本是 VTM 通道；原论文使用 201 帧速度模长。提供方源值含负数，推断有归一化或偏移，具体变换未说明，因此不赋予物理标量单位。',
            '- 轴序遵循 ECNR 实际读取代码而非与其冲突的 README 文字；空间范围沿用 FAU 原数据范围，ECNR 源文件无独立空间头，故坐标范围是一项假设。所有距离与运动指标均在该坐标约定下计算。',
            '- 窗口之间不匹配特征、不计算运动事件，也不做跨窗口时间优化。早／中／晚仅指源文件索引覆盖。',
            '- 主指标包含边界支持特征，不能把此运动代理解释为内部涡旋运动的验证。']
    if meta['dataset']=='Tangaroa-FAU-speed':
        lines+=['',
            '- 官方数据共 201 个 XYZ=300×180×120 的速度体；本次实际下载并验证前 12 个连续体，t=0.00–0.11，步长 0.01。Amira 包的 ZIP64 目录、源成员长度、CRC32 与 SHA256 均已保存。',
            '- 从文件头直接读取物理坐标与轴序；先在完整源网格计算速度模长，再全域抗混叠、三线性重采样为 XYZ=30×18×12，未逐帧归一化。',
            '- 官方来源、原始尺寸和速度模长通道吻合，但本试跑没有执行作者近零替换和 [0,2] 截断，且采用 split tree；作者公开主工作空间采用 join tree。因此处理后科学输入不等同于论文输入，停止将其用于论文 Tangaroa 同输入比较。',
            '- 本次参考点为极值点，质心同时保存；三维跟踪极值的 z 位移能量为 0，不能用这段数据单独证明各方向复杂三维运动的表现。合成运动案例另包含三个坐标上的位移。',
            '- 参考轴和阈值均按协议确定；本次无 H>2% 冲突帧，所有放松资格阈值都不触发放松，因而不能证明放松收益。']
    p=next(r for r in metrics if r['method']=='RG-MTM-P');r=next(r for r in metrics if r['method']=='RG-MTM-R 0.2')
    lines+=['','## 本次观察','',
        f"RG-MTM-P → RG-MTM-R（资格阈值 20%）的 NROE：{pct(p['NROE_mean'])} → {pct(r['NROE_mean'])}；实际锚点 MAE：{pct(p['anchor_MAE'])} → {pct(r['anchor_MAE'])}。",
        f"对应 NMLE 的均值／最大值：{pct(r['NMLE_mean'])}／{pct(r['NMLE_max'])}。资格阈值不是实际 NMLE 上界。",
        '','三维运动是否获益，应直接对照上表中的三维 ME 与清晰事件数；不能从 NROE 下降推断。','',
        '## 图与复核入口','',
        '- [三维输入视图](input_3d.png)', '- [方法对照时序地图](comparison_maps.png)',
        '- [层次放松阈值](relaxation_sensitivity.png)','- [持久性删除诊断](persistence_diagnostic.png)',
        '- [未舍入比较表](comparison.csv)','- [源文件与输入哈希](manifest.json)',
        '- [逐帧指标](frame_metrics.json)','- [预处理候选及失败记录](preprocessing_audit.json)','']
    (directory/'REPORT.md').write_text('\n'.join(lines))
    exported=[directory/'REPORT.md',directory/'comparison.csv']+list(directory.glob('*.png'))+list(directory.glob('*.svg'))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (directory/'render_manifest.json').write_text(json.dumps(dict(
        source_sha256=digest(Path(__file__)),
        input_sha256={name:digest(directory/name) for name in ['metrics.json','manifest.json','features.json','processed_fields.npz','preprocessing_audit.json','persistence_diagnostic.json','input_protocol.json','reference_axes.json']+(['interpretation_notice.json'] if notice else [])},
        files={p.name:digest(p) for p in exported}),indent=2)+'\n')


if __name__=='__main__':build(Path(sys.argv[1]))
