from pathlib import Path
import json,copy,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;P=O.parents[2];S=P/'figures/source/storms_budget_profiles';old=json.loads((S/'scene.json').read_text());sh=[]
for raw in old['slides'][0]['shapes']:
 s=copy.deepcopy(raw);kind=s['kind']
 if kind=='text':
  if s['text'].startswith('ε ='):sh.append(s)
  elif s['text']=='Storms':s['y']-=174;sh.append(s)
  continue
 keep=min(p[1] for p in s['points'])>=218-1e-8 if kind=='path' else s.get('y',0)>=218-1e-8
 if not keep:continue
 if kind=='path':s['points']=[[x,y-174] for x,y in s['points']]
 else:s['y']-=174
 if kind=='image':s['path']=str((S/s['path']).resolve())
 sh.append(s)
base=np.load(O/'baseline_maps.npz')
def text(t,x,y,w,h=30,size=18):sh.append(dict(kind='text',text=t,x=x,y=y,w=w,h=h,size=size,bold=False,rotation=0))
def path(pts,name,width=1.7):sh.append(dict(kind='path',points=pts,color='#111111',width=width,style='solid',name=name))
def arrow(pts,name):
 path(pts,name);x,y=pts[-1];path([[x-9,y-5],[x,y],[x-9,y+5]],name+' arrowhead')
for x,key,title in [(300,'TMTM','(6) TMTM'),(820,'STMTM','(7) ST-MTM')]:
 file=O/f'{key}_scalar_background.png';plt.imsave(file,base[key][:,355:461],origin='lower',cmap='RdBu_r',vmin=-35,vmax=35)
 text(title,x,245,300,28,19);sh.append(dict(kind='image',path=str(file.resolve()),x=x,y=280,w=300,h=110,name=key+' scalar field'))
 sh.append(dict(kind='rect',x=x,y=280,w=300,h=110,color='#111111',width=1.1));text('355',x-15,393,40,20,14);text('460',x+275,393,40,20,14)
arrow([[164,214],[164,233],[270,233],[270,335],[300,335]],'Module8 replacement connector')
text('(8) Replace placement\nby overlap alignment',5,270,245,52,18);text('Fixed spatial anchoring off',5,327,245,28,15)
arrow([[600,335],[820,335]],'Module9 replacement connector')
text('(9) Replace / add',603,237,214,28,17);text('Geometry ordering\n+ spatial/temporal\nplacement',605,270,210,55,16)
text('Time step: shared window 355–460; common scalar scale −35 to 35 hPa',300,417,820,24,15)
scene=dict(width=1160,height=448,slides=[dict(name='Storms Figure 6',shapes=sh,notes='Top row preserves the approved original lower event-map row exactly: titles, scalar backgrounds, editable trajectories, ROI rectangles, crop backgrounds, markers, dashed references and connectors. Baselines use the same 744 fields and augmented trees; actual baseline rasters are separate scalar image layers. Module captions and arrows are native editable objects. Source configuration and adapters: baseline_protocol.json. No complete figure is flattened into an image.')]);(O/'editable_scene.json').write_text(json.dumps(scene,ensure_ascii=False));print('native scene',len(sh),'objects')

# Match the intended scientific display aspect ratio before native PPT insertion.
from PIL import Image
(O/'ppt_assets').mkdir(exist_ok=True)
for i,item in enumerate(scene['slides'][0]['shapes']):
 if item['kind']=='image':
  dest=O/'ppt_assets'/f'scalar_{i}.png';Image.open(item['path']).resize((round(item['w']*4),round(item['h']*4)),Image.Resampling.BILINEAR).save(dest);item['path']=str(dest.resolve())
(O/'editable_scene.json').write_text(json.dumps(scene,ensure_ascii=False))
