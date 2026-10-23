"""Annual PM2.5 and conservative display reconstruction of saved scientific maps."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
from matplotlib import colormaps
from matplotlib.colors import Normalize,LinearSegmentedColormap
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=R/'.build/complete20261023';AS=B/'assets';SC=B/'scenes';CK=B/'checks'
for d in [AS,SC,CK,B/'candidates',B/'final']:d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'scripts'));from scene import Scene
from anchor_aligned_renderer import render_display
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records={};arrays={};landmarks={};palettes={};ranges={};rendered={}
for name in ['olr','pm25','ring']:
 if name=='pm25':f=W/'RG-MTM/code/results/pm25_2000/maps.npz';lmf=f.parent/'landmarks.npz'
 else:f=R/f'evidence/oldbase20261023/{name}_frozen_maps.npz';lmf=W/f'RG-MTM/code/results/public_metrics_20261016/{name}_landmarks.npz'
 a=np.load(f);lm=np.load(lmf);keys=['TMTM','ST-MTM','A','R 20%'];arrays[name]={k:a[k]for k in keys};landmarks[name]=lm
 # User-authorized pollution palette, concentration units, no AQI category thresholds.
 palettes[name]=LinearSegmentedColormap.from_list('pollution',['#2ca25f','#a1d76a','#ffff73','#fdae61','#f46d43','#d73027','#762a83'])if name=='pm25'else colormaps['RdBu_r']
 ranges[name]=(0.,float(max(v.max()for v in arrays[name].values())))if name=='pm25'else(min(v.min()for v in arrays[name].values()),max(v.max()for v in arrays[name].values()))
 if name=='pm25':palettes[name].set_under('#8196a6')
 report={}
 for i,k in enumerate(keys):
  factor=3 if name=='pm25'else 15
  v,rr=render_display(dict(mapR=arrays[name][k],track=lm['tracks'],normR=lm['u'+str(i)]),factor)
  # Encode a display raster only. The saved scientific maps remain byte-identical.
  rendered[name,k]=v;report[k]=rr
 records[name]=dict(maps=str(f),maps_sha256=sha(f),landmarks=str(lmf),landmarks_sha256=sha(lmf),frames=arrays[name]['A'].shape[1],display=report,palette='user-authorized pollution sequence (concentration, not AQI)'if name=='pm25'else'existing scalar display palette; no verified release LUT')
 (CK/(name+'_display.json')).write_text(json.dumps(records[name],indent=2)+'\n')
def raster(v,p,name):
 cm=palettes[name];norm=Normalize(*ranges[name]);Image.fromarray(np.rint(np.clip(cm(norm(v[::-1])),0,1)*255).astype('uint8')).save(p)
def text(s,t,x,y,w,h=25,size=18,bold=False,align='left'):s.text(t,x,y,w,h,size,'#000000',bold,align)
def panel(s,p,x,y,w,h,T,name):
 s.image(p,x,y,w,h);s.rect(x,y,w,h,'none','#7B8790',.7)
 for v in [0,.5,1]:text(s,f'{v:g}',x-43,y+h-v*h-9,35,22,16,align='right')
 ticks=[(0,'Jan 1'),(91,'Apr 1'),(182,'Jul 1'),(274,'Oct 1'),(365,'Dec 31')]if name=='pm25'else[(v,str(v))for v in [0,(T-1)//2,T-1]]
 for v,t in ticks:text(s,t,x+(v+.5)/T*w-32,y+h+5,64,22,15,align='center')
 text(s,'2000 date'if name=='pm25'else'Frame',x,y+h+29,w,22,16,align='center')
def save(s,stem):
 s.d['notes']=json.dumps(dict(sources=records,scientific_optimization_rerun='annual PM2.5 only',display='Conservative anchor-aligned piecewise linear interpolation. Original frames remain exact. Intermediate columns are display samples only; metrics use original arrays. Per-dataset shared scales.'))
 (SC/(stem+'.json')).write_text(json.dumps(s.d,indent=2))
def bar(s,name,x,y,w):
 mn,mx=ranges[name];f=AS/(name+'_bar.png');raster(np.linspace(mn,mx,512)[None,:],f,name);s.image(f,x,y,w,11);text(s,f'{mn:.2f}',x-90,y-8,80,24,16,align='right');text(s,f'{mx:.2f}',x+w+15,y-8,100,24,16)
s=Scene(12,'Additional complete-sequence maps');s.d.update(width=1280,height=850)
for i,(name,label,unit)in enumerate([('olr','OLR','W m-2'),('pm25','PM2.5','ug m-3'),('ring','Ring','scalar units')]):
 top=i*280;T=arrays[name]['A'].shape[1];text(s,f'({chr(97+i)}) {label}: all {T} fields'+(' (2000)'if name=='pm25'else''),20,top+3,1000,29,22,True)
 for j,(key,title)in enumerate([('A','RG-MTM-P'),('R 20%','RG-MTM-R20')]):
  x=80+j*630;text(s,title,x,top+34,520,25,19,True);p=AS/f'{name}_{j}.png';raster(rendered[name,key],p,name);panel(s,p,x,top+62,520,140,T,name)
 bar(s,name,455,top+256,460);text(s,f'{label} ({unit})',30,top+247,310,26,17);text(s,'Reference position [0,1]',1030,top+247,230,24,15,align='right')
save(s,'Fig12')
for name,stem in [('olr','Supplement_OLR_Comparison'),('pm25','Supplement_PM25_Comparison'),('ring','Supplement_Ring_Comparison')]:
 s=Scene(0,name+' complete four-method comparison');s.d.update(width=1280,height=640);T=arrays[name]['A'].shape[1]
 for j,(key,title)in enumerate([('TMTM','TMTM'),('ST-MTM','ST-MTM'),('A','RG-MTM-P'),('R 20%','RG-MTM-R20')]):
  x=62+j%2*638;y=52+j//2*270;text(s,f'({chr(97+j)}) {title}',x-35,y-42,580,28,23,True);p=AS/f'{name}_full_{j}.png';raster(rendered[name,key],p,name);panel(s,p,x,y,552,181,T,name);text(s,'Normalized native sample rank'if j<2 else'Normalized fixed reference axis',x+30,y-25,492,22,16,align='center')
 bar(s,name,330,578,570);text(s,('PM2.5 concentration (ug m-3)'if name=='pm25'else name+' scalar values'),390,605,500,22,17,align='center');save(s,stem)
(CK/'dataset_map_provenance.json').write_text(json.dumps(records,indent=2)+'\n');print('Prepared complete-sequence maps',[(k,v['frames'])for k,v in records.items()])
