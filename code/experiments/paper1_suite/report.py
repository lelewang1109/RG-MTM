"""Render supplementary evidence only after independent map verification."""
from itertools import combinations
import argparse, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from experiments.paper1_suite.prepare import DATA, RESULTS
from experiments.volume3d.run_paper import dump


def read(p):return json.loads(Path(p).read_text())


def motion(out):
    protocol=read(out/'protocol.json');p=read(out/'parameters.json')
    f=read(out/'features.json');rows=read(out/'frame_metrics.json');tracks=f['tracks'];frames=f['frames']
    coords=np.load(DATA/protocol['name']/'coordinates.npz')
    diagonal=float(np.linalg.norm([np.ptp(coords[k]) for k in coords.files]))
    lag=2;epsilon=.02;results=[]
    qs=[np.asarray(r['extrema'])[:,0] for r in frames]
    positions={m:[r['positions'] for r in rows if r['method']==m] for m in protocol['methods']}
    positions['Exact x projection']=qs
    for method,positions_m in positions.items():
        for truth in ['spatial','projected']:
            clear=reversal=miss=0
            for t in range(len(frames)-lag):
                A={v:i for i,v in enumerate(tracks[t])};B={v:i for i,v in enumerate(tracks[t+lag])}
                P=np.asarray(frames[t]['extrema']);Q=np.asarray(frames[t+lag]['extrema'])
                for a,b in combinations(sorted(set(A)&set(B)),2):
                    i,j,k,l=A[a],A[b],B[a],B[b]
                    real=(np.linalg.norm(Q[k]-Q[l])-np.linalg.norm(P[i]-P[j]) if truth=='spatial' else
                          abs(qs[t+lag][k]-qs[t+lag][l])-abs(qs[t][i]-qs[t][j]))
                    if abs(real)<=epsilon*(diagonal if truth=='spatial' else p['canvas']):continue
                    clear+=1
                    mapped=abs(positions_m[t+lag][k]-positions_m[t+lag][l])-abs(positions_m[t][i]-positions_m[t][j])
                    if abs(mapped)<=epsilon*p['canvas']:miss+=1
                    elif np.sign(mapped)!=np.sign(real):reversal+=1
            results.append(dict(method=method,truth=truth,lag=lag,epsilon=epsilon,clear_events=clear,
                reversal=reversal,miss=miss,error=(reversal+miss)/clear if clear else None))
    dump(out/'motion.json',results)
    return results


def figures(name):
    out=RESULTS/name;protocol=read(out/'protocol.json')
    assert read(out/'verification.json')['passed']
    fields=np.load(DATA/name/'source_fields.npy',mmap_mode='r')
    maps=np.load(out/'display_maps.npz');metrics=read(out/'metrics.json')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    if fields.ndim==4:
        coords=np.load(DATA/name/'coordinates.npz');indices=[0,len(fields)//2,len(fields)-1]
        fig,axes=plt.subplots(2,3,figsize=(13,5.3),layout='constrained')
        maximum=max(float(np.max(f)) for f in fields);minimum=min(float(np.min(f)) for f in fields)
        limit=max(abs(minimum),abs(maximum))
        norm=SymLogNorm(linthresh=.02,vmin=-limit,vmax=limit,base=10)
        dump(out/'display_metadata.json',dict(normalization='shared symmetric logarithmic',
            linear_threshold_Q=.02,vmin=-limit,vmax=limit,scalar_arrays_modified=False,
            source_figure='orthogonal source-volume planes; each displayed plane is not a timestep',
            maps='2048-row display previews plus every preserved extremum marker; metrics use full arrays'))
        for col,t in enumerate(indices):
            axes[0,col].imshow(fields[t,len(coords['z'])//2],origin='lower',aspect='auto',cmap='coolwarm',
                norm=norm,extent=[coords['x'].min(),coords['x'].max(),coords['y'].min(),coords['y'].max()])
            im=axes[1,col].imshow(fields[t,:,len(coords['y'])//2,:],origin='lower',aspect='auto',cmap='coolwarm',
                norm=norm,extent=[coords['x'].min(),coords['x'].max(),coords['z'].min(),coords['z'].max()])
            axes[0,col].set(title=f'Source frame {t}: x-y plane',xlabel='x',ylabel='y')
            axes[1,col].set(title=f'Source frame {t}: x-z plane',xlabel='x',ylabel='z')
        fig.colorbar(im,ax=axes.ravel().tolist(),label='Source Q (symmetric log; linear within +/-0.02)',shrink=.8)
        fig.suptitle('3-D square-cylinder DNS: two orthogonal planes of each full volume')
        fig.savefig(out/'source_3d.png',dpi=170);plt.close(fig)
        fig,axes=plt.subplots(5,1,figsize=(12,10),sharex=True,layout='constrained')
        for ax,m in zip(axes,protocol['methods']):
            source_units=-maps[m]*protocol['scalar_scale']
            map_im=ax.imshow(source_units,origin='lower',aspect='auto',cmap='coolwarm',norm=norm,
                      extent=[-.5,len(fields)-.5,0,1])
            # Mark every preserved extremum so display sampling does not hide it.
            rows=[r for r in read(out/'frame_metrics.json') if r['method']==m]
            for r in rows:
                ax.scatter(np.full(len(r['positions']),r['index']),
                    (np.asarray(r['positions'])-coords['x'].min())/np.ptp(coords['x']),s=.3,c='black',alpha=.6,linewidths=0)
            ax.set(title=m,ylabel='Map coordinate')
        axes[-1].set_xlabel('Consecutive source frame index (each input is 135 x 64 x 48)')
        fig.colorbar(map_im,ax=axes.tolist(),label='Source Q (symmetric log; linear within +/-0.02)',shrink=.7)
        fig.savefig(out/'comparison_maps.png',dpi=160);plt.close(fig)
    else:
        fig,axes=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
        axes[0].imshow(fields[0],origin='lower',cmap='viridis');axes[0].set(title='Nucleon: author 64 x 64 input',xlabel='x index',ylabel='y index')
        for ax,m in zip(axes[1:],['TMTM','RG-MTM-P']):
            row=next(r for r in read(out/'frame_metrics.json') if r['method']==m)
            full=np.load(DATA/name/'maps'/f'{m}_000.npy')
            ax.plot(np.linspace(0,1,len(full)),-full*protocol['scalar_scale'],lw=.7)
            ax.set(title=m,xlabel='Map coordinate',ylabel='Source scalar')
        fig.savefig(out/'comparison_maps.png',dpi=170);plt.close(fig)


def report(name):
    out=RESULTS/name;assert read(out/'verification.json')['passed']
    p=read(out/'protocol.json');summary=read(out/'metrics.json');tree=read(out/'tree_summary.json')
    figures(name)
    mot=motion(out) if p.get('shape_tzyx',[1])[0]>1 else []
    text=f'# {name} 补充实验\n\n**全部 {summary[0]["frames"]} 帧已计算并通过独立核验。**\n\n'
    text+=p['correspondence']+'。\n\n'
    if name=='square-cylinder3d':
        text+='输入来自作者公开的三维方柱 DNS 速度场，而非二维圆柱绕流。102 个时刻均保留完整三个空间维度；在 192×64×48 源速度网格计算 Q，再保留作者 x=57…191 的子域，布局输入为 102×48×64×135（T×Z×Y×X）。没有空间降采样、平滑或按叶数筛选。公开档案为 102 帧，论文表中为 508 帧，本实验不声称精确复现原作者未公开的最终 Q 导出。\n\n'
        text+='Q 使用三维物理坐标导数，预处理持久性为每帧范围的 2%，所有方法共享 TTK 简化后标量与实际树。固定 x 方向，固定全序列标量缩放与宽度比例。RG 放松资格 2%/20%/100% 与预处理持久性不同，也不代表输出 NMLE 上界。z 方向源模拟周期性在本次边界导数中未连接，边界采用二阶单边差分，触边特征另行标记。\n\n'
    else:
        text+='直接使用 TMTM 作者提供的 64×64 uint8 切片。单帧静态输入，不能用于时间稳定性或三维时变验证。本次 TTK 节点数为 26，原表为 28，保留该差异；未为匹配节点数修改输入。\n\n'
    text+=f'实际树节点范围 {tree["nodes_range"]}，叶特征范围 {tree["leaves_range"]}。\n\n'
    text+='| 方法 | NROE 均值 | NMLE 均值 | NMLE 最大值 | 层次无误差帧数 |\n|---|---:|---:|---:|---:|\n'
    for r in summary:text+=f'| {r["method"]} | {r["NROE_mean"]:.3%} | {r["NMLE_mean"]:.3%} | {r["NMLE_max"]:.3%} | {r["exact_topology_frames"]} |\n'
    text+='\nNROE 为叶序经最优单调校准后的位置误差，不等于实际锚点 MAE；NMLE 从完整输出数组测量，按固定全序列原始标量范围归一化。P 保留层次；R 的位置收益需结合实测拓扑代价解释。次级目标只优化最多四个声明的合法候选顺序，不声称全局次级最优。单次运行时间不与原论文硬件计时作速度结论。\n\n'
    numerical=[r for r in read(out/'frame_metrics.json') if r['method']!='TMTM']
    gap=max(r['layout']['convex_first_order_gap'] for r in numerical)
    nonconverged=sum(not r['layout']['qp_success'] for r in numerical)
    bracket=max((r['primary_certificate']['upper']-r['primary_certificate']['lower'])/read(out/'parameters.json')['canvas'] for r in numerical)
    text+=f'优化数值记录：连续主位置证书最大上下界宽度 {bracket:.6g} L；所选固定顺序凸 QP 最大一阶差距 {gap:.6g}（目标按 L² 归一化）；求解器未报告成功的所选 QP 数为 {nonconverged}。独立核验通过表示保存结果满足所核验的样本/拓扑/硬约束，不将未收敛证书或次级候选集合当作全局最优证明。\n\n'
    if mot:
        text+='| 方法 | 三维运动代理错误率 | 共享清晰事件数 | 投影运动代理错误率 |\n|---|---:|---:|---:|\n'
        for m in p['methods']+['Exact x projection']:
            spatial=next(r for r in mot if r['method']==m and r['truth']=='spatial')
            projected=next(r for r in mot if r['method']==m and r['truth']=='projected')
            def fmt(v):return '无清晰事件' if v is None else f'{v:.3%}'
            text+=f'| {m} | {fmt(spatial["error"])} | {spatial["clear_events"]} | {fmt(projected["error"])} |\n'
        text+='\n运动以三维叶极值坐标的接近/远离为几何代理，lag=2、阈值为域对角线的 2%；匹配由相邻帧叶弧体素重叠计算。它不是物理涡旋身份真值或读者实验。精确 x 投影单独量化降维造成的信息损失。\n\n'
    text+='核验覆盖全部保存输入变换、树样本所有权、弧单调性、父链 LCA、完整地图的合并层级、TMTM 样本计数及 RG 硬约束；不从 PNG 推算指标。原有六序列 342 帧主表和 Tangaroa 201 帧实验未改写。\n\n'
    text+='- [逐帧与方法指标](frame_metrics.json)\n- [未舍入汇总表](comparison.csv)\n- [独立核验记录](verification.json)\n- [对照图](comparison_maps.png)\n- [输入协议与来源](input_protocol.json)\n'
    if name=='square-cylinder3d':text+='- [三维源体正交截面](source_3d.png)\n\n源体图与全部方法图共享对称对数色标，Q∈[-0.02,0.02] 内为线性、范围外为对数；显示变换未修改任何标量数组，具体见 display_metadata.json。\n\n来源与致谢：Camarri、Salvetti、Buffoni、Iollo (2005) 的三维方柱绕流模拟；Tino Weinkauf 提供规则网格重采样，见 [作者数据页](https://tinoweinkauf.net/notes/squarecylinder.html) 和 von Funck 等的 Smoke Surfaces (TVCG 2008)。\n'
    (out/'REPORT.md').write_text(text)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('dataset')
    report(parser.parse_args().dataset)
