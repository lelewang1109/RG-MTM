"""Read-only event/contrast audit of existing outputs; no experimental rerun."""
from pathlib import Path
from itertools import combinations
import json,hashlib
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import to_hex

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent/'code'
DATA=ROOT/'results/real_case_studies/evidence'
a=np.load(DATA/'era5.npz');meta=json.loads((DATA/'era5.json').read_text())
rng=float(meta['field_range']);L=float(a['geometry'][1])

def measured(t):
    tree=meta['trees'][t]
    parent={int(c):int(p) for p,cs in tree['children'].items() for c in cs}
    def lca(i,j):
        ancestors={i}
        while i in parent:i=parent[i];ancestors.add(i)
        while j not in ancestors:j=parent[j]
        return j
    ids=a['leaf'][t];ids=ids[ids>=0]
    anchors=np.rint(a['normR'][t,:len(ids)]*4095).astype(int)
    errors=[]
    for i,j in combinations(range(len(ids)),2):
        lo,hi=sorted([anchors[i],anchors[j]])
        true=tree['values'][str(lca(int(ids[i]),int(ids[j])))]
        errors.append(abs(float(a['mapR'][lo:hi+1,t].max())-true))
    return max(errors,default=0.)

metrics=[]
for t in [42,48,62,86,100]:
    ep=float(np.nanmax(abs(a['normP'][t]-a['qnorm'][t])))
    er=float(np.nanmax(abs(a['normR'][t]-a['qnorm'][t])))
    cost=measured(t)
    metrics.append(dict(frame=t,date=str(a['dates'][t]),H_percent_L=100*a['H'][t]/L,
        packing_percent_L=100*a['F'][t]/L,max_position_error_P_percent_L=100*ep,
        max_position_error_R_percent_L=100*er,position_gain_percentage_points_L=100*(ep-er),
        measured_merge_error_hPa=cost,measured_NMLE_percent=100*cost/rng,
        analytic_delta_hPa=float(a['delta'][t])))

vmin=float(a['mapR'].min());vmax=float(a['mapR'].max())
contrast=[]
for t in [20,48,64,80,100]:
    j=int(np.nanargmin(a['value'][t]));v=float(a['value'][t,j])
    contrast.append(dict(frame=t,date=str(a['dates'][t]),track=int(a['track'][t,j]),
        processed_minimum_hPa=v,current_colour=to_hex(colormaps['RdBu_r']((v-vmin)/(vmax-vmin))),
        lonlat=a['lonlat'][t,j].tolist()))

result=dict(source_sha256=hashlib.sha256((DATA/'era5.npz').read_bytes()).hexdigest(),
    scope='derived inspection of frozen outputs, not a rerun of layout/optimization',
    selected_snapshot_frames=[20,48,64,80,100],contrast=contrast,candidate_geometric_events=metrics,
    primary_sources=[
      dict(title='TMTM original author PDF',url='https://www.csc.kth.se/~weinkauf/publications/documents/koepp22.pdf',sections=['Figure 1','3.3','4.1','5'],facts='744 hourly pressure-anomaly fields for December 1999; subtract 8-day mean; light Gaussian smoothing; temporal display interpolation'),
      dict(title='ST-MTM manuscript',url='https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6604235',local_text=str(HERE/'reference_review/STMTM_full_text.txt'),sections=['5.1','6'],facts='Storms uses hourly pressure anomalies; Fig.6 describes geometry and persistent low-pressure tracks'),
      dict(title='ECMWF Lothar case study',url='https://confluence.ecmwf.int/display/OIFS/Lothar+storm',facts='24–27 December 1999 Lothar case; not an identity link to our saved minima')],
    novelty_boundary='No demonstrated previously unknown cyclone or baseline missed detection. Additional evidence concerns fixed-reference hierarchy barriers and measured position/cost trade-offs, plus extended November/January coverage.')
(HERE/'evidence/fig1/event_analysis.json').write_text(json.dumps(result,indent=2))

rows='\n'.join(f"| f{m['frame']} | {m['date'][:10]} | {m['H_percent_L']:.2f} | {m['max_position_error_P_percent_L']:.2f} | {m['max_position_error_R_percent_L']:.2f} | {m['measured_NMLE_percent']:.2f} |" for m in metrics)
colours='\n'.join(f"| f{c['frame']} | {c['track']} | {c['processed_minimum_hPa']:.3f} | `{c['current_colour']}` |" for c in contrast)
report=f'''# Figure 1 事件标注与深蓝轨迹审查

## 已实施的标注

主图保留 f20、f48、f64、f80、f100 五个真实时刻，以及对应的五幅源空间快照。新加的英文标签依次是 Norwegian Sea low、Reference-order conflict、Northern Europe low、North Atlantic low、January low；标签箭头落在保存的 R20 精确锚点上。地理文字描述保存极值的位置，不把计算 ID 当作已核实的命名气旋。

新版主图不再叠加深蓝轨迹。清晰的细谷线来自保锚点的标量显示重建：先对齐同序匹配锚点，再在单调坐标映射下插值剖面。118个原始帧列完全保留；中间列是显示重建，不是新增观测或新布局输出。93/117个帧间隔启用此方式；其余24个存在交叉或大位置跳变的间隔采用原固定位置插值。完整主图与局部窗从同一重建数组裁切。右侧A/B/C原生轨迹仍表示真实锚点。

保存的匹配 ID 不等于经气象核验的物理身份。例如 ID73 在 f62→63 的位置从约0.0368跳至0.7067L，经纬度也发生大幅变化。因此这种区间不进行锚点对齐重建，不作为连续气旋路径证据。

## 为什么参考图的事件线更深

TMTM [作者原文](https://www.csc.kth.se/~weinkauf/publications/documents/koepp22.pdf) 第4.1节说明 Storms 是1999年12月的744个逐小时气压异常场，减去8日均值并作轻度高斯平滑；Fig.1 色标是 −35 到35 hPa。ST-MTM 的[稿件](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6604235)同样描述逐小时异常场。

当前数据则是1999-11-17至2000-01-14的118个半日绝对 MSLP 场，经已有投影、重采样和平滑协议处理。色标是 {vmin:.6f} 到 {vmax:.6f} hPa。这些低压未达到色标最深端，不能用“全部改深蓝”模拟异常场的效果；同时，118帧的时间细节不会因显示插值变成744帧的观测信息。表中为真实处理后极小值与原色标颜色：

| 帧 | 最低值轨迹 ID | 处理后最小气压 hPa | 原颜色 |
|---|---:|---:|---|
{colours}

新版修正了会稀释移动尖谷的固定位置插值；没有改变气压范围，也不通过叠线或事后模糊来制造深蓝线。显示重建只影响原始帧之间的显示位置，不改变保存的科学指标。

## 是否存在“前两篇没发现而本方法能显示的新事件”

目前没有证据支持新增命名气旋或前两篇漏检气象事件的结论。Nov/Jan 时刻超出参考图的1999年12月范围，属于覆盖范围的扩展。f48 以及下表的高层次障碍帧可作为 RG-MTM 额外解释能力的例子：它量化固定参考与层次连续性发生冲突的程度，以及放松后的位置收益和实际合并代价。它们不是气象学发现。

| 帧 | 日期 | H (%L) | P 最大位置误差 (%L) | R20 最大位置误差 (%L) | 实测 NMLE (%) |
|---|---|---:|---:|---:|---:|
{rows}

其中 f62 的 P/R 位置偏差约为22.85%/1.06%L，f86 约为21.47%/0.83%L，是可核验的补充分析候选。f42 虽有最大的 H，但 R20 仍有约9.86%L残余偏差，也应保留这个反例，不能只挑收益最大的图形。上述合并代价由保存的4096行完整二维输出逐对读取，不把解析 delta 当作实测值。

## 与原文命名事件的时间对应

已有 `code/results/real_case_studies/event_correspondence_zh.md` 记录：Anatol 对应 f33.5、Scandinavia storm 对应 f61.75、British Isles/Norway 对应 f75.917、Lothar 时窗 f78.833、Martin 时窗 f81.75。这些都不是任意选取的 f20/48/64/80/100 的同义名称。尤其 f79 没有可确认为 Lothar 的独立叶特征，因此本图不添加该名字。

建议正文表述：The fixed reference additionally reveals hierarchy-forced position conflicts and quantifies the position gains and merge-level costs of relaxation. 不宜写：RG-MTM discovers storms missed by TMTM and ST-MTM。

## 复核

运行 `scripts/audit_events.py` 只读取冻结 NPZ/JSON 并计算派生检查，不重跑提取、优化、填充或原实验。原始数组 SHA256 为 `{result['source_sha256']}`。逐条数值及来源保存在 `event_analysis.json`。
'''
(HERE/'evidence/fig1/Fig1_Event_Analysis.md').write_text(report)
print(json.dumps(metrics,indent=2))
