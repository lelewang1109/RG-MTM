"""Add the three missing whole-sequence result maps to the user-selected old draft.
Reads frozen arrays and landmarks only; does not extract trees or solve layouts.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
from matplotlib import colormaps
from matplotlib.colors import Normalize
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=R/'.build/oldbase20261023';AS=B/'assets';SC=B/'scenes';CK=B/'checks'
for d in [AS,SC,CK,B/'candidates']:d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'scripts'));from scene import Scene
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records={};arrays={};cm=colormaps['RdBu_r']
for name in ['olr','pm25','ring']:
 paths=sorted((W/'其他/归档/历史或排除结果/visualization_cache').glob(name+'-*.npz'));assert paths
 a=np.load(paths[0]);lmfile=W/f'RG-MTM/code/results/public_metrics_20261016/{name}_landmarks.npz';lm=np.load(lmfile)
 for p in paths:
  z=np.load(p)
  assert all(np.array_equal(a[k],z[k])for k in a.files)
 errors=[]
 for t,n in enumerate(lm['count']):
  vals=[a[k][np.rint(lm['u'+str(i)][t,:n]*(a[k].shape[0]-1)).astype(int),t]for i,k in enumerate(['TMTM','ST-MTM','A','R 20%'])]
  errors.extend(np.max(vals,axis=0)-np.min(vals,axis=0))
 assert max(errors)==0
 arrays[name]={k:a[k].copy()for k in ['TMTM','ST-MTM','A','R 20%']}
 records[name]=dict(cache=str(paths[0]),cache_sha256=sha(paths[0]),landmarks=str(lmfile),landmark_sha256=sha(lmfile),frames=a['A'].shape[1],same_feature_scalar_checks=len(errors),maximum_cross_method_scalar_difference=0,cache_copies_identical=True)
 (AS/(name+'_frozen_maps.npz')).write_bytes(paths[0].read_bytes())
def raster(v,p,norm):
 Image.fromarray(np.rint(np.clip(cm(norm(v[::-1])),0,1)*255).astype('uint8')).save(p)
def text(s,t,x,y,w,h=25,size=18,bold=False,align='left'):s.text(t,x,y,w,h,size,'#000000',bold,align)
def panel(s,p,x,y,w,h,T):
 s.image(p,x,y,w,h);s.rect(x,y,w,h,'none','#7B8790',.7)
 for v in [0,.5,1]:
  yy=y+h-v*h;text(s,f'{v:g}',x-43,yy-9,35,22,16,align='right')
 for v in [0,(T-1)//2,T-1]:text(s,str(v),x+(v+.5)/T*w-20,y+h+5,40,22,16,align='center')
 text(s,'Frame',x,y+h+29,w,22,16,align='center')
def save(s,stem):
 s.d['notes']=json.dumps(dict(sources=records,scientific_optimization_rerun=False,axis='P/R fixed reference position, normalized to [0,1]; baselines in their native normalized rank. Independent scalar scales per dataset; complete sequence without temporal cropping. Numerical metrics use complete stored arrays.'))
 (SC/(stem+'.json')).write_text(json.dumps(s.d,indent=2))
s=Scene(12,'Additional complete-sequence maps');s.d.update(width=1280,height=850)
for i,(name,label,unit)in enumerate([('olr','OLR','W m-2'),('pm25','PM2.5','ug m-3'),('ring','Ring','scalar units')]):
 top=i*280;z=arrays[name];mn=min(v.min()for v in z.values());mx=max(v.max()for v in z.values());norm=Normalize(mn,mx);T=z['A'].shape[1]
 text(s,f'({chr(97+i)}) {label}: all {T} frames',20,top+3,900,29,22,True)
 for j,(key,title)in enumerate([('A','RG-MTM-P'),('R 20%','RG-MTM-R20')]):
  x=80+j*630;text(s,title,x,top+34,520,25,19,True);p=AS/f'{name}_{j}.png';raster(z[key],p,norm);panel(s,p,x,top+62,520,140,T)
 bar=AS/f'{name}_bar.png';raster(np.linspace(mn,mx,512)[None,:],bar,norm);s.image(bar,455,top+256,460,11)
 text(s,f'{label} ({unit})',30,top+247,310,26,17);text(s,f'{mn:.2f}',360,top+248,80,24,16,align='right');text(s,f'{mx:.2f}',930,top+248,100,24,16)
 text(s,'Reference position [0,1]',1030,top+247,230,24,15,align='right')
save(s,'Fig12')
# Full four-method Ring comparison accompanies the existing OLR / PM2.5 panels.
s=Scene(0,'Ring complete four-method comparison');s.d.update(width=1280,height=640);z=arrays['ring'];mn=min(v.min()for v in z.values());mx=max(v.max()for v in z.values());norm=Normalize(mn,mx);T=z['A'].shape[1]
for j,(key,title)in enumerate([('TMTM','TMTM'),('ST-MTM','ST-MTM'),('A','RG-MTM-P'),('R 20%','RG-MTM-R20')]):
 x=62+j%2*638;y=52+j//2*270;text(s,f'({chr(97+j)}) {title}',x-35,y-42,580,28,23,True);p=AS/f'ring_full_{j}.png';raster(z[key],p,norm);panel(s,p,x,y,552,181,T)
 text(s,'Normalized native sample rank'if j<2 else'Normalized fixed reference axis',x+30,y-25,492,22,16,align='center')
bar=AS/'ring_full_bar.png';raster(np.linspace(mn,mx,512)[None,:],bar,norm);s.image(bar,330,578,570,13);text(s,f'{mn:.2f}',274,598,100,22,16,align='center');text(s,f'{mx:.2f}',856,598,100,22,16,align='center');text(s,'Ring intensity (scalar units)',457,598,320,22,17,align='center');save(s,'Supplement_Ring_Comparison')
(CK/'dataset_map_provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('Prepared Fig12 and complete Ring comparison from frozen maps. Anchor scalar agreement:',[(k,v['same_feature_scalar_checks'])for k,v in records.items()])
