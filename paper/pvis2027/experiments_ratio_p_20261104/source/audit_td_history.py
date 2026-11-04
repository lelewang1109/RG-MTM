"""Compare saved historical and formal Storms TD without changing inputs or scores."""
from pathlib import Path
import csv,json,numpy as np
O=Path(__file__).resolve().parents[1];W=O.parents[2]
H=W/'output/anchormtm_storms_paper_settings_20261103'
def read(p):return json.loads(p.read_text())
def csvrows(p):return list(csv.DictReader(p.open()))
def main():
 rows=[]
 for mode in ['Exact','Balanced']:
  old=H/'full'/mode;s=read(old/'summary.json');steps=csvrows(old/'matched_displacements.csv')
  # Column is explicit: sum canvas-normalized displacements, no rescaling.
  keys=list(steps[0]);key=next(k for k in keys if 'canvas' in k.lower());value=sum(float(x[key]) for x in steps)
  expected=next(float(x['TD_canvas_normalized']) for x in csvrows(H/'AnchorMTM_metrics.csv') if x['Method']=='AnchorMTM '+mode)
  np.testing.assert_allclose(value,expected,atol=1e-10)
  rows.append(dict(experiment='historical',mode=mode,p_percent=10.5,epsilon=0 if mode=='Exact' else .05,feature_range='1-7',matched_steps=len(steps),TD_recomputed=value,TD_reported=expected,absolute_difference=abs(value-expected)))
  new=O/'results/Storms'/mode;s=read(new/'summary.json');per=csvrows(new/'per_frame.csv');value=sum(float(x['TD_unit_canvas_increment']) for x in per);np.testing.assert_allclose(value,s['TD'],atol=1e-10)
  rows.append(dict(experiment='formal',mode=mode,p_percent=.105,epsilon=s['epsilon'],feature_range='9-40',matched_steps=sum(int(x['matched_steps']) for x in per),TD_recomputed=value,TD_reported=s['TD'],absolute_difference=abs(value-s['TD'])))
 with (O/'TD_history_audit.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
 (O/'TD_AUDIT_zh.md').write_text('''# Storms TD历史核对

旧Balanced 29.336508与当前343.427839均为Σ相邻匹配锚点绝对位移/固定完整画布跨度。脚本对旧逐匹配位移及新逐帧增量独立求和，均与各自缓存记录一致，没有发现多除/漏除画布长度的错误。

旧实验把p=0.105作为比例，即10.5%；ε=5%，叶数1–7，2737匹配步。正式实验按此前确认的百分数口径执行p=0.105%，ε依据验证J选择10%，叶数9–40，14095匹配步。预算、提树、匹配与最终布局都不同，不能用旧29替换当前结果，也不能据更小的累计值推断它更准确。这里不声称仅p一个因素造成所有差异。

TD是累计量，会随有效匹配数和单步显示位移共同变化。没有除以匹配数或帧数来压低当前数字。作者TD的坐标单位仍不清楚，主表分别对原文组和本地归一组标最优/次优，禁止把组内加粗解释为跨单位公平排名。Storms当前本地Balanced低于Exact，但不能说低于作者Temporal的36.24。

`source/audit_td_history.py`、`TD_history_audit.csv`保存核验代码及原数值；历史原始结果仍保留，未重新运行或调整算法。
''')
 print(rows)
if __name__=='__main__':main()
