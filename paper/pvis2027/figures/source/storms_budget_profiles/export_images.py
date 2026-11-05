from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Ellipse,Polygon
from PIL import Image
O=Path(__file__).resolve().parent;d=json.loads((O/'scene.json').read_text());(O/'delivery').mkdir(exist_ok=True)
for i,slide in enumerate(d['slides']):
 fig=plt.figure(figsize=(d['width']/96,d['height']/96),dpi=150);ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,d['width']),ylim=(d['height'],0));ax.set_axis_off()
 for z,s in enumerate(slide['shapes']):
  if s['kind']=='image':ax.imshow(Image.open(O/s['path']),extent=[s['x'],s['x']+s['w'],s['y']+s['h'],s['y']],origin='upper',aspect='auto',zorder=z)
  elif s['kind']=='text':ax.text(s['x']+s['w']/2,s['y']+s['h']/2,s['text'],ha='center',va='center',fontsize=s['size']*.75,fontfamily='Times New Roman',weight='bold' if s['bold'] else 'normal',zorder=z)
  elif s['kind']=='path':
   pts=s['points'];ls={'solid':'-','dashed':'--','dotted':':'}.get(s['style'],'-');ax.plot([p[0] for p in pts],[p[1] for p in pts],color=s['color'],lw=s['width']*.75,ls=ls,zorder=z)
  elif s['kind']=='rect':ax.add_patch(Rectangle((s['x'],s['y']),s['w'],s['h'],fill=False,ec=s['color'],lw=s['width']*.75,zorder=z))
  elif s['kind']=='marker':
   x,y,w,h=[s[k] for k in ['x','y','w','h']];fill=s['fill'];fill='none' if fill=='none' else fill
   if s['shape']=='diamond':p=Polygon([(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)],facecolor=fill,edgecolor=s['color'],lw=.6,zorder=z)
   else:p=Ellipse((x+w/2,y+h/2),w,h,facecolor=fill,edgecolor=s['color'],lw=.6,zorder=z)
   ax.add_patch(p)
 stem='Storms_参数剖面与事件地图' if i==0 else slide['name']+'_左下角放大'
 fig.savefig(O/'delivery'/f'{stem}.png',dpi=150,facecolor='white')
 if i==0:fig.savefig(O/'delivery'/f'{stem}.pdf',facecolor='white')
 plt.close(fig)
print('Static images exported from the same PPT scene coordinates.')
