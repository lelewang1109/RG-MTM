"""Standard rank and confusion-matrix metrics on saved annual PM2.5 anchors."""
from pathlib import Path
import sys,pickle,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'analysis'),str(ROOT/'src'),str(ROOT)]
import evaluate_reference_task_metrics as e
class Metrics:
 @staticmethod
 def accuracy_score(y,p):return np.mean(y==p)
 @staticmethod
 def balanced_accuracy_score(y,p):return np.mean([np.mean(p[y==k]==k)for k in np.unique(y)])
 @staticmethod
 def f1_score(y,p,labels,average,zero_division):
  scores=[]
  for k in labels:
   tp=np.sum((y==k)&(p==k));den=np.sum(y==k)+np.sum(p==k);scores.append(2*tp/den if den else 0.)
  return np.mean(scores)
p=ROOT/'results/pm25_2000';z=np.load(p/'landmarks.npz');sz=z['count'];ex=[z['extrema'][t,:n]for t,n in enumerate(sz)];tr=[z['tracks'][t,:n].tolist()for t,n in enumerate(sz)];u=[[z['u'+str(i)][t,:n]for t,n in enumerate(sz)]for i in range(4)]
a=e.direction(ex,tr);r,d=e.rank_scores([xy@a for xy in ex],u)
with (p/'dataset.pkl').open('rb')as f:ds=pickle.load(f)
m,events=e.motion_scores(ex,tr,u,float(np.linalg.norm(ds['hi']-ds['lo'])),Metrics)
old=json.loads((p/'eval_projection.json').read_text())['pm25_2000'];changes={}
for method,key in zip(e.ev.METHODS,['TMTM','ST-MTM','A','R 20%']):
 x=next(x for x in m if x['method']==method and x['scope']=='clear_events');y=next(x for x in old['proxy']if x['method']==key and x['k']==2 and x['eps']==.02)
 assert x['events']==y['clear']==95
 changes[method]=x['reversal']+x['miss']-round(y['clear']*y['error'])
(p/'reference_tasks.json').write_text(json.dumps(dict(protocol=e.PROTOCOL,metric_implementation='direct accuracy, class-recall mean and fixed-label macro-F1 formulas',ranks=r,motion=m,events=events,raster_error_changes=changes,source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [Path(__file__),p/'landmarks.npz',ROOT/'tools/evaluate_reference_task_metrics.py']}),indent=2)+'\n')
print('Annual standard tasks',[(x['method'],x['events'],x['balanced_accuracy'],x['macro_F1'])for x in m if x['scope']=='all_three_classes']);print('Raster changes',changes)
