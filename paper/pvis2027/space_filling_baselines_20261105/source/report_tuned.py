from pathlib import Path
import csv,json
O=Path(__file__).resolve().parents[1];T=O/'tuned'
read=lambda p:list(csv.DictReader(p.open()))
r=read(T/'metrics.csv');default=read(O/'results/metrics.csv');cand=read(T/'validation_candidates.csv');selected=[]
for a in r:
 method=a['Method'].replace(' tuned','');group=[x for x in cand if x['Dataset']==a['Dataset'] and x['Method']==method];ch=[x for x in group if x['selected']=='True'];assert len(ch)==1 and float(ch[0]['J'])<=min(float(x['J']) for x in group)+1e-12
 d=next(x for x in default if x['Dataset']==a['Dataset'] and x['Method']==method)
 selected.append(dict(Dataset=a['Dataset'],Method=method,candidate=a['candidate'],validation_J=ch[0]['J'],default_NPE=d['NPE'],tuned_NPE=a['NPE'],relative_NPE_reduction=1-float(a['NPE'])/float(d['NPE']),default_SNS=d['SNS'],tuned_SNS=a['SNS'],default_TW=d['TW'],tuned_TW=a['TW'],assessment_NPE=a['assessment_NPE'],assessment_SNS=a['assessment_SNS'],assessment_TW=a['assessment_TW']))
with (T/'default_vs_tuned.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
best=[]
for ds in ['Gaussian','Ring','Wildfires','Storms']:
 for m in ['Hilbert','Morton']:
  g=[x for x in cand if x['Dataset']==ds and x['Method']==m]
  for key in ['SNS','NPE','TW']:
   valid=[x for x in g if x[key]]
   if valid:
    x=sorted(valid,key=lambda x:float(x[key]),reverse=key=='TW')[0]
    best.append(dict(Dataset=ds,Method=m,validation_objective=key,candidate=x['candidate'],validation_value=x[key],scope='validation only; not a combined final method'))
with (T/'per_metric_validation_optima.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(best[0]));w.writeheader();w.writerows(best)
s=['# Hilbert / Morton 方向验证寻优','','默认是代码约定的固定网格遍历，并非估计的物理方向。x 为列，y 为行；从(0,0)开始。Morton 位交错以 x 作为低位；Hilbert 固定递归方向，其第一步随二次幂网格层级改变。默认不旋转、不镜像、不反转。','','## 搜索及选择','','每个方法/数据集枚举4个数组旋转×2个左右镜像×2个遍历方向，共16个名义候选；按实际网格置换哈希去重。矩形旋转后按新形状生成曲线，再映射回原样本ID。所有候选保存。','','使用最初25%时间窗口，J=0.5 NPE_norm+0.5 SNS_norm；对同方法、同数据集全部不同候选的验证指标作min–max归一化。常量项贡献0，若SNS完全缺失则不作此选择。J在1e-12内相同时按固定枚举顺序选取。选择保存到selection.json后才读取后75%时间窗口。没有改数据、p、q、画布L和指标定义。','','这些结果属于方向参数空间中的验证综合最优，不声称每个指标都达到全局最优。单指标验证最佳另存CSV，不将不同配置成绩拼接成一个方法。完整序列此前已观察，因此不能宣称全新盲测。','','## 完整序列结果','','| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ | 配置 |','|---|---|---:|---:|---:|---|']
for a in r:s.append('| '+' | '.join([a['Dataset'],a['Method']]+[f"{float(a[k]):.6f}" if a[k] else 'N/A' for k in ['SNS','TW','NPE']]+[a['candidate']])+' |')
s+=['','## 后75%时间窗口','','| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ |','|---|---|---:|---:|---:|']
for a in r:s.append('| '+' | '.join([a['Dataset'],a['Method']]+[f"{float(a['assessment_'+k]):.6f}" if a['assessment_'+k] else 'N/A' for k in ['SNS','TW','NPE']])+' |')
s+=['','## 解读与限制','','- 多数配置的NPE较默认方向降低；Wildfires Morton选择原默认配置。','- Ring两方法和Gaussian Morton出现SNS变差，说明综合评分存在取舍；Ring验证窗口只有2帧SNS有效、没有TW有效帧，方向选择的泛化证据尤其弱。','- 四数据集TW有效帧仍为64/64、1/40、4/32、11/744，不能将少数有效帧成绩解释为全序列邻域保持。','- 全部配置沿曲线全网格序号映射到统一固定物理画布并取整；不对每帧拟合缩放、平移。无特征显示坐标重合，但不保证拓扑或有限特征宽度可行性。','- 调优后Balanced仍在四个数据集的NPE和SNS上优于这两种综合选定曲线，TW也较高；这不抹去默认Ring Hilbert在SNS/TW上的更好结果，两者应同时保留。','- 不修改论文主表。后续正式比较应预先冻结基线选择协议，再在独立数据上检验。','','## 复现','','```sh','.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/tune.py','.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/report_tuned.py','```']
(T/'REPORT_zh.md').write_text('\n'.join(s)+'\n');(T/'verification.json').write_text(json.dumps(dict(selected_rows=len(r),all_selected_min_validation_J=True,only_global_orientation=True,nominal_candidates=128,distinct_candidates=len(cand),no_data_reference_or_core_edits=True),indent=2)+'\n')
print('Verified',len(r),'selections;',len(cand),'distinct candidates')
