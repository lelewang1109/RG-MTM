"""Report reconstructed Benzene without implying original-file reproduction."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from experiments.paper1_suite.prepare import DATA, RESULTS, sha256
from experiments.paper1_suite.benzene_reconstructed import NAME
from experiments.volume3d.run_paper import dump


def read(p):
    return json.loads(Path(p).read_text())


def diagnostics():
    out=RESULTS/NAME; directory=DATA/NAME
    features=read(out/'features.json'); frames=features['frames']; tracks=features['tracks']
    rows=read(out/'frame_metrics.json'); methods=read(out/'protocol.json')['methods']
    extent=read(out/'parameters.json')['canvas']
    # Distinguish extrema on the domain boundary from leaf-arc supports that
    # merely reach it: a central minimum can own samples on a domain edge.
    boundary=[np.any(np.abs(np.asarray(f['extrema']))==6.,axis=1) for f in frames]
    summary=[]
    for method in methods:
        selected=[r for r in rows if r['method']==method]
        shifts=[]; interior_scores=[]; reflected=[]
        for t,r in enumerate(selected):
            mask=~boundary[t]
            pos=np.array(r['positions'])[mask]
            q=np.array(frames[t]['extrema'])[mask,0]
            ordered=q[np.argsort(pos)]
            inversion=max((ordered[i]-ordered[j] for i in range(len(q))
                           for j in range(i+1,len(q))), default=0.)
            # A single interior leaf has no pairwise ordering question.
            if len(q)>=2:
                interior_scores.append(max(0.,float(inversion))/(2*extent))
            if t:
                a={v:i for i,v in enumerate(tracks[t-1])}; b={v:i for i,v in enumerate(tracks[t])}
                for v in sorted(set(a)&set(b)):
                    dx=r['positions'][b[v]]-selected[t-1]['positions'][a[v]]
                    dq=frames[t]['extrema'][b[v]][0]-frames[t-1]['extrema'][a[v]][0]
                    shifts.append(abs(dx-dq)/extent)
        # Full arrays, interpolated onto a declared common coordinate grid;
        # no frame-wise reflection, alignment or calibration fitted here.
        grid=np.linspace(0.,1.,32768)
        for t in range(len(selected)//2):
            pair=[]
            for r in [selected[t],selected[-1-t]]:
                col=np.load(directory/'maps'/f'{method.replace(" ","_")}_{r["index"]:03d}.npy')
                pair.append(np.interp(grid,np.linspace(0.,1.,len(col)),col))
            reflected.append(float(np.mean(abs(pair[0]-pair[1]))))
        summary.append(dict(method=method,
            interior_NROE_mean=float(np.mean(interior_scores)) if interior_scores else None,
            interior_frames_with_at_least_two_leaves=len(interior_scores),
            adjacent_matched_events=len(shifts),
            adjacent_projected_displacement_residual_mean=float(np.mean(shifts)),
            reflection_pair_count=len(reflected),
            map_z_reflection_MAE_mean=float(np.mean(reflected)),
            map_z_reflection_MAE_max=max(reflected)))
    dump(out/'slice_diagnostics.json', dict(rows=summary,
        physical_time=False, matching='same overlap-derived tracks for every method',
        displacement='abs((mapped_x[t]-mapped_x[t-1])-(source_x[t]-source_x[t-1])) / x_extent',
        reflection='mean absolute scalar discrepancy at same normalized map coordinate for z,-z; 32768-point interpolation of full saved arrays',
        scalar_normalization='one fixed source sequence range',
        boundary_definition='extremum itself lies on x or y = +/-6 bohr',
        boundary_leaf_counts=[int(b.sum()) for b in boundary],
        interior_leaf_counts=[int((~b).sum()) for b in boundary],
        support_touches_boundary_leaf_counts=[sum(f['boundary']) for f in frames],
        interpretation='slice coherence and approximate reflection diagnostics, not molecular dynamics or user-study results'))
    return summary


def figures():
    out=RESULTS/NAME; directory=DATA/NAME
    p=read(out/'protocol.json'); scale=p['scalar_scale']
    fields=np.load(directory/'source_fields.npy'); coords=np.load(directory/'coordinates.npz')
    frames=read(out/'features.json')['frames']; rows=read(out/'frame_metrics.json')
    limit=float(np.max(abs(fields))); linthresh=.02*scale
    norm=SymLogNorm(linthresh=linthresh,vmin=-limit,vmax=limit,base=10)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,5,figsize=(15,3.5),layout='constrained')
    for ax,t in zip(axes,[0,5,10,15,20]):
        im=ax.imshow(fields[t],origin='lower',extent=[-6,6,-6,6],cmap='coolwarm',norm=norm)
        xy=np.array(frames[t]['extrema'])
        ax.scatter(xy[:,0],xy[:,1],s=22,facecolors='none',edgecolors='black',linewidths=.75)
        ax.set(title=f'z = {coords["slice_z"][t]:g} bohr',xlabel='x (bohr)',ylabel='y (bohr)')
    fig.colorbar(im,ax=axes.tolist(),shrink=.7,ticks=[-1,-.1,0,.1,1],
        label='Reconstructed V (a.u.; symmetric log)')
    fig.suptitle('Benzene: OPLS-AA potential reconstruction | 2-D sections; circles = retained minima',fontsize=12)
    fig.savefig(out/'source_slices.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(5,1,figsize=(12,10),sharex=True,layout='constrained')
    grid=np.linspace(0.,1.,32768)
    for ax,method in zip(axes,p['methods']):
        full=[]
        for r in [r for r in rows if r['method']==method]:
            col=np.load(directory/'maps'/f'{method.replace(" ","_")}_{r["index"]:03d}.npy')
            full.append(np.interp(grid,np.linspace(0,1,len(col)),col)*scale)
            ax.scatter(np.full(len(r['positions']),coords['slice_z'][r['index']]),
                (np.array(r['positions'])+6)/12,s=3,c='black',linewidths=0)
        im=ax.imshow(np.array(full).T,origin='lower',aspect='auto',cmap='coolwarm',norm=norm,
            extent=[-2.1,2.1,0,1],zorder=-1)
        ax.set(title=method,ylabel='Map coordinate')
    axes[-1].set_xlabel('Section z (bohr), NOT physical time')
    fig.colorbar(im,ax=axes.tolist(),ticks=[-1,-.1,0,.1,1],
        label='Reconstructed V (a.u.; symmetric log)',shrink=.65)
    fig.suptitle('Benzene reconstruction | common color scale; dots = every retained extremum',fontsize=12)
    fig.savefig(out/'comparison_maps.png',dpi=170);plt.close(fig)
    dump(out/'display_metadata.json', dict(normalization='shared symmetric logarithmic',
        linthresh_potential_au=linthresh,vmin=-limit,vmax=limit,
        scalar_arrays_modified=False, minima_markers='all retained leaves, including boundary leaves',
        source_slice_indices=[0,5,10,15,20],
        map_sampling='full maps interpolated onto 32768 common display coordinates',physical_time=False))


def report():
    out=RESULTS/NAME; assert read(out/'verification.json')['passed']
    d=diagnostics(); figures()
    metrics=read(out/'metrics.json'); tree=read(out/'tree_summary.json')
    rows=read(out/'frame_metrics.json'); p=read(out/'parameters.json')
    numerical=[r for r in rows if r['method']!='TMTM']
    bracket=max((r['primary_certificate']['upper']-r['primary_certificate']['lower'])/p['canvas'] for r in numerical)
    qp_gap=max(r['layout']['convex_first_order_gap'] for r in numerical)
    failed=sum(not r['layout']['qp_success'] for r in numerical)
    audit=read(out/'verification.json')['reconstructed_potential_audit']
    text='''# Benzene 二维电势重建补充实验

**21 张二维切片、5 组方法、105 张完整地图已计算并独立核验。本数据为明确标注的电势重建版，不是第一篇论文作者的原始文件。**

本次遵从用户更正后的二维 Benzene 设置。每张输入为 61×61，x、y∈[−6,6] bohr，z∈[−2,2] bohr 等距取 21 张。z 是静态分子电势的切片坐标，不是物理时间；这组结果不用于证明三维时变处理能力。

模型采用 OPLS-AA 的 12 个固定部分电荷：每个 C 为 −0.115e、每个 H 为 +0.115e，净电荷为零。参数来自 [Yale BOSS 4.9 手册，第 67 页表 1](https://zarbi.chem.yale.edu/doc/boss49.pdf)。原子几何来自 [Inviwo 公开苯分子 cube](https://github.com/inviwo/modules/blob/6152a00ab100ec10c1eb36f078fb42dc949010ab/molvis/gaussian/data/volumes/benzene-dens.cube.xz) 的原子坐标头；不读取其密度值来生成电势。

计算 V(r)=Σᵢqᵢ/‖r−Rᵢ‖，距离单位 bohr，电势单位 Hartree/e，真空介电系数为 1。没有软化半径、截断、平滑或拟合电荷，采样点没有落在电荷奇点上。这是经典部分电荷近似，不能解释为量子化学电子结构的精确电势，也不是原文的分数电荷构造或作者原始体数据。网格、阈值和模型均在布局比较前固定，没有为匹配原表节点数或优化收益调参。

电子密度表示电子在空间的分布；电势表示单位正电荷在该位置的电势能，涉及全部电荷的作用，两者不是可直接更名的同一标量。旧电子密度试跑保持排除，不能当作本文电势结果。

对电势本身提取 join tree（低电势极小值），没有取负号改成极大值。所有方法共享相同的 TTK 简化标量和树，预处理持久性为每张切片范围的 0.05%；布局标量只除以一个固定全序列范围，没有逐帧归一化。固定 x 为参考方向，TMTM 使用首帧方向选择和相邻帧对齐，P 保留层次，R 的资格参数为 0.02/0.2/1；资格参数不是最终 NMLE 上界。

'''
    text+=f'实际树节点范围 {tree["nodes_range"]}、叶特征范围 {tree["leaves_range"]}，原表节点为 14–68。每张切片包含 4 个极值位于域边界的叶；其余为 1 或 6 个内部极值叶。这里按极值坐标判断内外，不按叶弧支持是否触边判断；中心叶的支持有时也会触边。边界叶全部保留、所有方法一致，故整体排序误差受边界结构显著影响；下表不能直接外推为真实电子结构数据上的改进幅度。\n\n'
    text+='| 方法 | NROE 均值 | NMLE 均值 | NMLE 最大值 | 层次无误差帧数 |\n|---|---:|---:|---:|---:|\n'
    for r in metrics:
        text+=f'| {r["method"]} | {r["NROE_mean"]:.4%} | {r["NMLE_mean"]:.4%} | {r["NMLE_max"]:.4%} | {r["exact_topology_frames"]}/21 |\n'
    text+='\nNROE 是叶序经最优单调校准后的位置误差，不等于实际锚点 MAE。TMTM 本身不优化给定 x 方向的位置参考，其位置误差不能直接解释为原论文优化目标的失败。NMLE 从完整地图的合并层级测量，按固定全序列电势范围归一化。三个 R 参数得到相同结果：本模型中可放松障碍已在 0.02 档内覆盖，不能据此声称参数越大收益越大。15 张切片触发放松，6 张未触发。\n\n'
    text+='| 方法 | 内部叶 NROE（15 张切片） | 相邻切片位移残差 | z 镜像地图 MAE |\n|---|---:|---:|---:|\n'
    for r in d:
        text+=f'| {r["method"]} | {r["interior_NROE_mean"]:.4%} | {r["adjacent_projected_displacement_residual_mean"]:.4%} | {r["map_z_reflection_MAE_mean"]:.4%} |\n'
    text+='\n内部叶指标仅作为公开的边界敏感性诊断，不替换完整叶集主指标；只有至少两个内部叶的 15 张切片参加。位移残差是地图锚点变化与源 x 投影变化之差的绝对值，除以域宽；全部方法使用相同的叶弧重叠匹配，匹配只作为几何代理。镜像 MAE 比较 10 对 ±z 切片在同一地图坐标的电势差，按全序列范围归一化，不额外翻转或拟合对齐。它们是切片连续性和近似对称性诊断，不是分子运动或读者实验。\n\n'
    text+=f'公开几何略偏离理想平面，源电势的最大 ±z 镜像差为全序列范围的 {audit["normalized_z_reflection_discrepancy"]:.4%}；没有强行把输入改成完全镜像。\n\n'
    text+=f'数值记录：连续主位置证书最大上下界宽度 {bracket:.6g} L；所选固定顺序 QP 最大一阶差距 {qp_gap:.6g}（目标按 L² 归一化）；未报告成功的所选 QP 数为 {failed}。次级优化最多比较四个合法候选顺序，不声称全局次级最优。\n\n'
    text+='独立核验用 Python 标量距离及 math.fsum 重新计算全部 78,141 个电势采样，与保存 float32 源数组逐值一致；逐帧检查正号缩放、树所有权、弧单调性、父链 LCA、完整输出屏障、TMTM 样本计数和 RG 硬约束，并重算汇总指标。TTK 的持久性简化本身没有另行独立实现。\n\n'
    text+='图像使用统一对称对数色标，仅用于显示；定量指标使用完整数组。原有 342 帧主表、正文和已有 Tangaroa 结果未改写。\n\n'
    text+='- [完整汇总表](comparison.csv) · [逐帧指标](frame_metrics.json)\n- [二维源电势切片](source_slices.png) · [五组方法对照图](comparison_maps.png)\n- [切片连续性与边界诊断](slice_diagnostics.json)\n- [独立核验](verification.json) · [模型及来源](model.json) · [输入协议](input_protocol.json)\n'
    (out/'REPORT.md').write_text(text)
    dump(out/'artifact_manifest.json', {f.name:sha256(f) for f in out.iterdir()
        if f.is_file() and f.name!='artifact_manifest.json'})
    print('Benzene reconstructed report and figures saved:',out)


if __name__=='__main__':
    report()
