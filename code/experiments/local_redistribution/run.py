"""Reproduce all-point local budget-response diagnostics from bound continuous inputs."""
from pathlib import Path
import json,csv,hashlib,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/local_redistribution20261030';TOL=1e-6

def main(out=OUT):
 manifest=json.loads((out/'input_manifest.json').read_text());stats=[];points=[];datasets={};cases=[]
 for name in ['Vortex','Storms-hourly']:
  spec=manifest[name];p=out/'inputs'/spec['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'];archive=np.load(p);d={k:archive[k] for k in archive.files};archive.close();E=d['epsilon'];counts=d['count'];n=int(counts.sum());error=abs(d['x']-d['q']);global_metrics=[dict(epsilon=float(e),mean=float(np.nanmean(error[j])),maximum=float(np.nanmax(error[j]))) for j,e in enumerate(E)]
  datasets[name]=dict(frames=len(counts),samples=n,epsilon=E.tolist(),metrics=global_metrics)
  for j in range(len(E)-1):
   flat=np.concatenate([(error[j+1,t,:n0]-error[j,t,:n0]) for t,n0 in enumerate(counts)]);fm=np.nanmean(error[j+1],axis=1)-np.nanmean(error[j],axis=1);fx=np.nanmax(error[j+1],axis=1)-np.nanmax(error[j],axis=1);strict=(fm<-TOL)&(fx<-TOL);same=np.array([np.array_equal(d['orders'][j,t,:n0],d['orders'][j+1,t,:n0]) for t,n0 in enumerate(counts)])
   rec=dict(dataset=name,epsilon_from=float(E[j]),epsilon_to=float(E[j+1]),samples=n,improved=int(np.sum(flat<-TOL)),worsened=int(np.sum(flat>TOL)),unchanged=int(np.sum(abs(flat)<=TOL)),worsened_fraction=float(np.mean(flat>TOL)),worsened_ge_0p5pp=int(np.sum(flat>=.005)),worsened_ge_1pp=int(np.sum(flat>=.01)),max_worsening=float(flat.max()),mean_change=float(flat.mean()),frame_max_worsened=int(np.sum(fx>TOL)),both_frame_metrics_improve_frames=int(strict.sum()),both_improve_samples=int(counts[strict].sum()),both_improve_worsened_points=sum(int(np.sum(error[j+1,t,:n0]-error[j,t,:n0]>TOL)) for t,n0 in enumerate(counts) if strict[t]),same_order_frames=int(same.sum()),same_order_worsened_points=sum(int(np.sum(error[j+1,t,:n0]-error[j,t,:n0]>TOL)) for t,n0 in enumerate(counts) if same[t]))
   assert rec['improved']+rec['worsened']+rec['unchanged']==n;assert abs(rec['mean_change']-(global_metrics[j+1]['mean']-global_metrics[j]['mean']))<1e-12;stats.append(rec)
   for t,n0 in enumerate(counts):
    for i in range(n0):
     row=dict(dataset=name,epsilon_from=float(E[j]),epsilon_to=float(E[j+1]),frame=t,track=int(d['tracks'][t,i]),reference=float(d['q'][t,i]),x_from=float(d['x'][j,t,i]),x_to=float(d['x'][j+1,t,i]),error_from=float(error[j,t,i]),error_to=float(error[j+1,t,i]),change=float(error[j+1,t,i]-error[j,t,i]),both_frame_metrics_improve=bool(strict[t]),same_order=bool(same[t]));points.append(row)
     if strict[t] and row['change']>=.01:cases.append(row)
  print(name,spec['frames'],n,'samples',flush=True)
 cases.sort(key=lambda r:(-r['change'],r['dataset'],r['frame'],r['track']));selected=max((r for r in cases if r['dataset']=='Vortex' and r['epsilon_from']==.2),key=lambda r:r['change'])
 result=dict(tolerance=TOL,material_thresholds=[.005,.01],classification='change in absolute per-feature reference error / L between budgets at the SAME time, NOT time displacement',datasets=datasets,transitions=stats,example=selected,example_selection='largest Vortex 20-to-30% local increase among frames whose mean AND maximum errors both decrease; illustrative extreme, not a prevalence estimate',source_manifest=manifest)
 (out/'results.json').write_text(json.dumps(result,indent=2))
 for file,rows in [('transitions.csv',stats),('point_changes.csv',points)]:
  with (out/file).open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('example',selected)
if __name__=='__main__':main()
