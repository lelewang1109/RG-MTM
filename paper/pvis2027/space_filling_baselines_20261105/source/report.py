from pathlib import Path
import csv,json
O=Path(__file__).resolve().parents[1];P=O.parent
read=lambda p:list(csv.DictReader(p.open()))
new=read(O/'results/metrics.csv');old=read(P/'experiments_ratio_p_20261104/comparison_final.csv');dslist=['Gaussian','Ring','Wildfires','Storms'];combined=[]
for ds in dslist:
 for r in old+new:
  if r['Dataset']!=ds:continue
  combined.append({k:r.get(k,'') for k in ['Dataset','Method','SNS','TW','NPE','TW_k','TW_valid_frames']}|dict(SNS_TW_source=r.get('metrics_source','local canonical sample-domain curve'),NPE_source='local shared frozen reference'))
with (O/'comparison_with_space_filling.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(combined[0]));w.writeheader();w.writerows(combined)
text=['# Hilbert / Morton 补充实验','', '使用四数据集 ratio-p 冻结缓存；不重新提树、不修改算法、不调节曲线方向或根据结果选择配置。数据输入为此前明确标注的重建输入。','', '| Dataset | Method | SNS ↓ | TW ↑ | NPE ↓ | TW 有效帧 |','|---|---|---:|---:|---:|---:|']
for r in new:
 text.append('| '+' | '.join([r['Dataset'],r['Method']]+[f"{float(r[k]):.6f}" if r[k] else 'N/A' for k in ['SNS','TW','NPE']]+[r['TW_valid_frames']+'/'+r['frames']])+' |')
text+=['','## 协议与核验','','- 复用项目 `space_filling.py` 的标准固定 Hilbert/Morton 网格遍历；矩形网格嵌入最小二次幂正方形后删除域外位置，保留域内完整置换。','- 极值使用与 AnchorMTM 完全相同的原始网格样本 ID。沿曲线的全网格累计序号线性映射到固定画布，再按原 L 取整；没有每帧重排为等间距特征序号，也没有旋转、反射寻优或逐帧对齐。','- SNS/TW 的原空间点仍为既有特征支持域质心，NPE 的目标仍为既有固定物理投影 q；完全复用评价函数。NPE 是逐帧最大归一误差的时间平均。','- TW 使用 k=(1,3,5,3)，仅 0<k<n/2 有效；距离并列沿用项目稳定排序（原叶 ID 次序）。全部方法使用共同有效帧；缺失不填零。','- 四数据集分别先检查前8帧，再完整计算64/40/32/744帧；逐帧成功复现既有 Exact SNS、TW、NPE。SNS 另用独立向量公式交叉检查。','- 两种曲线所有帧均无极值画布坐标重合，无越界。这不等于通过拓扑保持或有限宽度布局检查：曲线是样本域线性化参照，不是完整合并树映射。','- 固定曲线坐标和固定物理投影轴含义不同，NPE 衡量的是其对同一物理参考的偏离；不能从较高 NPE 推导其一般可视化质量较差。','','## 结果解读','','- AnchorMTM Balanced 的 NPE 在四个数据集均低于两种曲线。','- SNS 并非始终占优：Ring 的 Hilbert SNS=0.125153，低于 Balanced 约0.1334；其 TW=0.904762 也高于 Balanced 0.857143，但 TW 只有1帧，不能推广成全序列结论。','- Gaussian、Wildfires、Storms 上，两种曲线的 SNS/TW 均不及当前 Balanced；仍需留意 Wildfires/Storms 的 TW 仅4/11帧。','- 合并 CSV 中 TMTM/ST-MTM 的 SNS/TW 保持原文引用，NPE 保持本地测量；作者输入及 TW 覆盖未确认相同，不能称为严格同输入的跨来源排名。','','## 复现','','在项目根目录执行：','','```sh','.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/evaluate.py --pilot','.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/evaluate.py','.venv/bin/python paper/pvis2027/space_filling_baselines_20261105/source/report.py','```','','依赖既有本地 fields.npy、coordinates.npy、trees 和 Exact 缓存，GitHub 精简包不含这些大体积输入。此轮未修改论文主表。']
(O/'REPORT_zh.md').write_text('\n'.join(text)+'\n')
tex=[r'\begin{table}[t]',r'\centering',r'\caption{Canonical sample-domain curve baselines on the local frozen inputs.}',r'\label{tab:space-filling-supplement}',r'\footnotesize',r'\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{llrrr}',r'\toprule',r'Dataset & Method & SNS$\downarrow$ & TW$\uparrow$ & NPE$\downarrow$ \\',r'\midrule']
for r in new:tex.append(' & '.join([r['Dataset'],r['Method']]+[f"{float(r[k]):.4f}" if r[k] else 'N/A' for k in ['SNS','TW','NPE']])+r' \\')
tex +=[r'\bottomrule',r'\end{tabular}',r'\end{table}'];(O/'space_filling_metrics.tex').write_text('\n'.join(tex)+'\n')
(O/'verification.json').write_text(json.dumps(dict(full_frames=880,curve_evaluations=1760,Exact_shared_metric_reproduction=True,independent_SNS_check=True,TW_coverage=[64,1,4,11],coincident_anchor_frames=0,paper_modified=False),indent=2)+'\n')
print('Saved combined CSV, supplemental LaTeX and report')
