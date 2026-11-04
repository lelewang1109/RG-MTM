"""Make a compact, single-column paper figure from the editable diagram scene.
Grid/tree correspondences come from source/build_complete.py in the recorded
output directory. Numeric sample IDs are omitted for single-column readability.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Polygon
ROOT=Path(__file__).resolve().parents[4]
FIG=Path(__file__).resolve().parents[1]
source=Path(__file__).with_name('projection_conflict_scene.json')
scene=json.loads(source.read_text())
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic','pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(6.6,6.6*9/13),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
scale=6.6/13
short={'(a) Spatial reference mapping':'(a) Spatial projection','(b) Augmented merge tree mapping':'(b) Tree mapping','(c) Hierarchy–position conflict':'(c) Order conflict'}
for o in sorted(scene,key=lambda o:o['z']):
 typ=o['type']
 if typ=='box':
  ax.add_patch(FancyBboxPatch((o['x'],o['y']),o['w'],o['h'],boxstyle=f"round,pad=0,rounding_size={o['radius']}",fc=o['fill'],ec='#111111' if o['stroke']!='none' else 'none',lw=.8,zorder=o['z']))
 elif typ=='polygon':ax.add_patch(Polygon(o['points'],closed=True,facecolor=o['color'],edgecolor=o['color'],lw=.3,zorder=o['z']))
 elif typ=='line':ax.plot([o['a'][0],o['b'][0]],[o['a'][1],o['b'][1]],color=o['color'],lw=max(.45,o['width']*scale),zorder=o['z'],alpha=o.get('alpha',1))
 elif typ=='arrow':
  start=list(o['a'])
  if start[0]>.5 and abs(start[1]-.503)<1e-6:start[1]=.479
  ax.annotate('',xy=o['b'],xytext=start,arrowprops={'arrowstyle':'->','color':o['color'],'lw':max(.6,o['width']*scale),'shrinkA':1,'shrinkB':1,'mutation_scale':7},zorder=o['z'])
 elif typ=='node':ax.scatter(o['x'],o['y'],s=o['size']*scale**2,marker='D' if o['critical'] else 'o',facecolor=o['color'],edgecolor='#111111',lw=.5,zorder=o['z'])
 elif typ=='text':
  if o['text'].isdigit():continue
  label=short.get(o['text'],o['text'])
  size=15.0 if label.startswith('(') or label in ['$d$','$x$'] else 13.34
  if label in ['Tree order','Spatial order']:size=13.34
  label_y=.513 if o['x']>.5 and abs(o['y']-.524)<1e-6 else o['y']
  ax.text(o['x'],label_y,label,fontsize=size,ha=o['align'],va='center',weight='bold' if o['bold'] else 'normal',color=o['color'],zorder=o['z'])
for ext in ['pdf','png','svg']:fig.savefig(FIG/f'anchor_projection_conflict.{ext}',dpi=400,facecolor='white')
plt.close(fig)
