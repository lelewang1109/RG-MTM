"""Diagnose line visibility without changing scientific arrays or final Figure 1.

The third panel is an explicitly labelled display-reconstruction experiment.
It is not an observed field, a new temporal sample, or a new layout result.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import colormaps

R=Path(__file__).resolve().parents[1]
D=R.parent/'code/results/real_case_studies/evidence'
OUT=R/'evidence/fig1/diagnostics';OUT.mkdir(exist_ok=True)
a=np.load(D/'era5.npz');m=json.loads((D/'era5.json').read_text())
G=a['mapR'];N,T=G.shape;U=np.linspace(0,1,N)
norm=Normalize(min(a['mapR'].min(),a['mapP'].min()),max(a['mapR'].max(),a['mapP'].max()))
factor=41
times=np.clip((np.arange(T*factor)+.5)/factor-.5,0,T-1)
fixed=np.empty((N,len(times)),dtype=np.float64)
aligned=np.empty_like(fixed)
pair_rules=[]
for t in range(T-1):
    common=sorted((set(a['track'][t])&set(a['track'][t+1]))-{-1})
    i0=[int(np.flatnonzero(a['track'][t]==tr)[0]) for tr in common]
    i1=[int(np.flatnonzero(a['track'][t+1]==tr)[0]) for tr in common]
    v0=a['normR'][t,i0];v1=a['normR'][t+1,i1]
    order=np.argsort(v0);v0=v0[order];v1=v1[order]
    eligible=len(common)>0 and np.all(np.diff(v1)>0) and np.all(abs(v0-v1)<=.2)
    reason='eligible' if eligible else 'crossing order' if np.any(np.diff(v1)<=0) else 'large anchor jump'
    # Use exact scalar-sample indices because original extrema are preserved
    # at these saved raster positions. Real continuous anchors remain unedited.
    knots0=np.r_[0,np.rint(v0*(N-1))/(N-1),1]
    knots1=np.r_[0,np.rint(v1*(N-1))/(N-1),1]
    eligible=eligible and np.all(np.diff(knots0)>0) and np.all(np.diff(knots1)>0)
    pair_rules.append(dict(frame_pair=[t,t+1],eligible=bool(eligible),reason=reason,common_track_ids=[int(common[k]) for k in order],knots0=knots0.tolist(),knots1=knots1.tolist()))

for k,tt in enumerate(times):
    t=int(np.floor(tt));alpha=tt-t
    if t==T-1 or alpha==0:
        fixed[:,k]=aligned[:,k]=G[:,t];continue
    fixed[:,k]=(1-alpha)*G[:,t]+alpha*G[:,t+1]
    rule=pair_rules[t]
    if not rule['eligible']:
        aligned[:,k]=fixed[:,k];continue
    k0=np.array(rule['knots0']);k1=np.array(rule['knots1']);km=(1-alpha)*k0+alpha*k1
    q0=np.interp(U,km,k0);q1=np.interp(U,km,k1)
    aligned[:,k]=(1-alpha)*np.interp(q0,U,G[:,t])+alpha*np.interp(q1,U,G[:,t+1])

assert np.array_equal(fixed[:,factor//2::factor],G)
assert np.array_equal(aligned[:,factor//2::factor],G)
assert aligned.min()>=G.min()-1e-10 and aligned.max()<=G.max()+1e-10
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})

fig,axs=plt.subplots(3,1,figsize=(13,8.2),sharex=True,sharey=True)
titles=['(a) Saved R20 columns: native frames',
        '(b) Current display: linear interpolation at fixed reference positions',
        '(c) Diagnostic only: anchor-aligned interpolation in eligible intervals']
for ax,arr,title in zip(axs,[G,fixed,aligned],titles):
    im=ax.imshow(arr,origin='lower',extent=(-.5,T-.5,0,1),aspect='auto',cmap='RdBu_r',norm=norm,interpolation='nearest')
    ax.set_title(title,loc='left',fontsize=11,pad=5)
    ax.set_ylabel('Reference position');ax.set_yticks([0,.5,1])
    ax.axvspan(18,22,fill=False,edgecolor='#D55E00',linewidth=1)
axs[-1].set_xlabel('Frame')
fig.subplots_adjust(left=.07,right=.89,top=.96,bottom=.08,hspace=.29)
cb=fig.colorbar(im,cax=fig.add_axes([.915,.16,.014,.68]));cb.set_label('Absolute MSLP (hPa); identical colour mapping')
fig.savefig(OUT/'R20_Line_Visibility_Full.png',dpi=230)
fig.savefig(OUT/'R20_Line_Visibility_Full.pdf')
plt.close(fig)

# Local diagnostic: same colour mapping and exact same original frame columns.
lo,hi=18,22;yl,yh=.15,.75
native=G[:,lo:hi+1]
sl=slice(lo*factor,(hi+1)*factor)
fig,axs=plt.subplots(1,3,figsize=(13,4.5),sharex=True,sharey=True)
for ax,arr,title in zip(axs,[native,fixed[:,sl],aligned[:,sl]],['Native frames','Fixed-position interpolation','Diagnostic: anchor-aligned']):
    im=ax.imshow(arr,origin='lower',extent=(lo-.5,hi+.5,0,1),aspect='auto',cmap='RdBu_r',norm=norm,interpolation='nearest')
    ax.set(xlim=(lo-.5,hi+.5),ylim=(yl,yh),xticks=range(lo,hi+1),xlabel='Frame')
    ax.set_title(title,fontsize=11)
axs[0].set_ylabel('Reference position')
fig.subplots_adjust(left=.065,right=.91,top=.84,bottom=.15,wspace=.14)
fig.suptitle('Track 19 near f20: original-frame values unchanged; no trajectory lines overlaid',fontsize=12)
cb=fig.colorbar(im,cax=fig.add_axes([.93,.17,.012,.64]));cb.set_label('MSLP (hPa)')
fig.savefig(OUT/'R20_Line_Visibility_Local.png',dpi=260)
fig.savefig(OUT/'R20_Line_Visibility_Local.pdf')
plt.close(fig)

examples=[]
for tr,t in [(19,18),(19,19),(19,20),(73,63),(78,79),(93,100)]:
    j0=int(np.flatnonzero(a['track'][t]==tr)[0]);j1=int(np.flatnonzero(a['track'][t+1]==tr)[0])
    u0=float(a['normR'][t,j0]);u1=float(a['normR'][t+1,j1]);um=(u0+u1)/2
    endpoint_avg=float((a['value'][t,j0]+a['value'][t+1,j1])/2)
    midpoint_fixed=float((np.interp(um,U,G[:,t])+np.interp(um,U,G[:,t+1]))/2)
    # Evaluate the aligned reconstruction at the midpoint of its grid anchors.
    rule=pair_rules[t]
    midpoint_aligned=None
    if rule['eligible']:
        k0=np.asarray(rule['knots0']);k1=np.asarray(rule['knots1']);km=(k0+k1)/2
        um_grid=(round(u0*(N-1))+round(u1*(N-1)))/(2*(N-1))
        q0=np.interp(um_grid,km,k0);q1=np.interp(um_grid,km,k1)
        midpoint_aligned=float((np.interp(q0,U,G[:,t])+np.interp(q1,U,G[:,t+1]))/2)
    examples.append(dict(track=tr,frame_pair=[t,t+1],movement_L=abs(u1-u0),endpoint_average_hPa=endpoint_avg,fixed_midpoint_hPa=midpoint_fixed,apparent_minimum_loss_hPa=midpoint_fixed-endpoint_avg,aligned_midpoint_hPa=midpoint_aligned))
report=dict(source=str(D/'era5.npz'),source_protocol=m['protocol'],
    observed_frames_unchanged_exactly=True,scalar_range_unchanged=True,
    pairs_eligible=sum(v['eligible'] for v in pair_rules),pairs_total=T-1,
    rules=pair_rules,examples=examples,
    display_only_notice='Anchor-aligned reconstruction is a diagnostic display technique. Intermediate columns are interpolated, not observed fields or original RG-MTM outputs. Ineligible crossing/large-jump pairs use current fixed-position interpolation. Do not use this diagnostic image as evidence of improved scientific/layout performance.',
    main_limitations=['118 half-day input frames rather than 744 hourly anomaly frames','Fixed-reference anchors can move substantially between sampled frames','Optimal scalar barriers constrain merge levels but do not optimize visual valley/ridge contrast','Relaxation can produce nearly flat inter-extremum regions; display interpolation cannot recover absent observations'])
(OUT/'line_visibility_diagnosis.json').write_text(json.dumps(report,indent=2))
table='\n'.join(f"| {x['track']} | f{x['frame_pair'][0]}→f{x['frame_pair'][1]} | {100*x['movement_L']:.2f} | {x['endpoint_average_hPa']:.2f} | {x['fixed_midpoint_hPa']:.2f} | {x['apparent_minimum_loss_hPa']:.2f} |" for x in examples)
md=f'''# RG-MTM 低压线可见性诊断

## 结论

上一轮叠加轨迹不是标量渲染本身的改进。当前确实存在帧间显示插值造成的特征稀释，不能只归因于色标。固定位置的逐列线性插值相当于两个位置不同的尖谷之间淡入淡出；它不保证沿移动极值的连线保留低值。因此会看到逐帧蓝色片段或宽色带，而非连续清晰的深蓝谷线。

## 数值证据

| 计算轨迹 ID | 帧对 | 锚点移动 (%L) | 两端极值平均 hPa | 当前位置插值在连线中点的值 hPa | 表观极值损失 hPa |
|---|---|---:|---:|---:|---:|
{table}

例如 f20→21，原始极值平均约975.72 hPa，当前位置插值在两锚点中点显示约1001.35 hPa，升高25.63 hPa，颜色已接近色标中部。原始两帧的极值并没有丢失，问题发生在显示重采样的帧间位置。

此外，输入是49×49分析网格、250 km既有平滑和半日采样的绝对气压；与参考论文逐小时气压异常不同。最优屏障填充优化的是合并层级误差，不是低压谷的视觉尖锐度；裁剪屏障可以产生真实的近平台区域。这些都不能通过简单模糊或加深颜色解决。

## 诊断图怎么读

`R20_Line_Visibility_Local.png/pdf` 无任何轨迹叠加，从左到右为保存的离散帧、当前固定位置线性显示插值、保锚点的显示重建。三者的原始帧列、颜色范围和标量数据相同。第三种先把前后帧的同序匹配锚点映射到插值位置，再插值其标量剖面，用于检查是否是时间显示重建导致线条变淡。

第三种只在匹配顺序一致、单帧锚点位移不超过0.2L且坐标变换严格单调时启用；当前有{report['pairs_eligible']}/{T-1}个帧对满足条件，其他帧对保留当前位置插值。第三种保留所有原始帧列，但中间列是显示重建，**不是新增观测、原算法新输出或已经验证的物理气旋路径**，不能将其清晰度当作算法性能提高。

完整时间范围见 `R20_Line_Visibility_Full.png/pdf`；原始论文 Figure 1/PPT 在此诊断步骤中不修改。对照中若第三种明显恢复细谷线，说明显示重建值得继续研究；如果要公平比较事件发现能力，应统一输入、采样、预处理和显示重建策略，再对所有方法验证。

## 论文表述的实际边界

现有结果能支持固定空间参考的冲突诊断和位置—合并代价分析，不能仅凭目前时间图声称气象事件比 TMTM/ST-MTM 更清楚或发现了新气旋。修正显示方案与改变方法填充是不同的工作，后者需要重新验证拓扑误差、极值保持和比较公平性。
'''
(OUT/'Line_Visibility_Diagnosis.md').write_text(md)
print(json.dumps(dict(eligible_pairs=report['pairs_eligible'],total_pairs=T-1,examples=examples),indent=2))
