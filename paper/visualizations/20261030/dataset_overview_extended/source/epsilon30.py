from pathlib import Path
import sys,importlib.util,json
import numpy as np
import os
W=Path(os.environ['MERGETREEMAPS_WORKSPACE']);OUT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sweep',W/'output/current_method_parameter_sweep_20261029/source/run.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
name=sys.argv[1];lo,hi={'Storms':(36,53),'Wildfires':(0,27),'PM2.5':(160,187),'Tangaroa':(80,120)}[name]
folder=OUT/s.slug(name);folder.mkdir(exist_ok=True);output=folder/'epsilon_0.3.json'
if output.exists():print('Cached',name);sys.exit()
d=s.load_inputs(name);keys=['centers','measures','hierarchies','references','merge','tracks']
cut={**d,**{k:d[k][:hi+1] for k in keys}}
print('Solving',name,'0 through',hi,'with full temporal prefix',flush=True);rows,orders=s.solve(cut,.3)
frames,ids,kind,display=s.source_frames(name,d)
win={**d,**{k:d[k][lo:hi+1] for k in keys}}
M,check=s.render(frames[lo:hi+1],ids[lo:hi+1],kind,rows[lo:hi+1],win)
s.dump(output,dict(dataset=name,epsilon=.3,computed_prefix=[0,hi],window=[lo,hi],rows=rows,orders=orders,render=check))
np.savez_compressed(folder/'epsilon_0.3.npz',map=M)
print('DONE',name,'max merge',max(r['measured_topology'] for r in rows),flush=True)
