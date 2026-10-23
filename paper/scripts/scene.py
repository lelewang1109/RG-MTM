"""Native scientific drawing scene; coordinates shared by editable PPT objects."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
W,H=1344,640
INK='#263238';GRAY='#7B8790';LIGHT='#DFE4E8';BLUE='#0072B2';ORANGE='#D55E00';GREEN='#009E73';PURPLE='#CC79A7';SKY='#56B4E9'
COL=[BLUE,SKY,ORANGE,GREEN,PURPLE]
class Scene:
 def __init__(self,n,title,notes=''):
  self.d=dict(number=n,width=W,height=H,title=title,notes=notes,objects=[])
 def add(self,kind,**kw):
  self.d['objects'].append(dict(kind=kind,name=kw.pop('name',f'{kind}_{len(self.d["objects"]):03d}'),**kw));return self
 def text(self,s,x,y,w,h=30,size=20,color=INK,bold=False,align='left',name=None):return self.add('text',text=s,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,align=align,**({'name':name} if name else {}))
 def line(self,x1,y1,x2,y2,color=INK,width=1.8,dash=False,name=None):return self.add('line',x1=x1,y1=y1,x2=x2,y2=y2,color=color,width=width,dash=dash,**({'name':name} if name else {}))
 def rect(self,x,y,w,h,fill='none',stroke=LIGHT,width=1):return self.add('rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,width=width)
 def dot(self,x,y,color=BLUE,r=6,fill=None,name=None):return self.add('ellipse',x=x-r,y=y-r,w=2*r,h=2*r,fill=fill or color,stroke=color,width=1.8,**({'name':name} if name else {}))
 def path(self,pts,color=BLUE,width=2.4,dash=False,name=None):return self.add('path',points=pts,color=color,width=width,dash=dash,**({'name':name} if name else {}))
 def image(self,path,x,y,w,h,name=None):return self.add('image',path=str(path),x=x,y=y,w=w,h=h,**({'name':name} if name else {}))
 def save(self):
  p=BASE/'evidence'/f'Fig{self.d["number"]}_scene.json';p.write_text(json.dumps(self.d,indent=2));return p

def tree(s,x,y,w,h,labels=True):
 xy={0:(0,0),1:(1,0),2:(2,0),3:(3,0),4:(4,0),5:(.5,2),6:(1.25,4),7:(3.5,3),8:(2.3,8)}
 par={0:5,1:5,5:6,2:6,3:7,4:7,6:8,7:8}
 p={k:(x+v[0]/4*w,y+h-v[1]/8*h) for k,v in xy.items()}
 for c,a in par.items():s.line(*p[c],*p[a],GRAY,2,name=f'T_edge_{c}_{a}')
 for k,(xx,yy) in p.items():
  s.dot(xx,yy,COL[k] if k<5 else INK,6 if k<5 else 5,name=f'T_node_{k}')
  if labels:s.text(['A1','A2','B','C','D'][k] if k<5 else str(xy[k][1]),xx-15 if k<5 else xx+8,yy+9 if k<5 else yy-16,45,27,19,COL[k] if k<5 else INK)
 return p

def orderrow(s,order,x,y,w,label):
 s.text(label,x,y-43,w,30,20,bold=True)
 for j,k in enumerate(order):
  xx=x+(j+.5)*w/5;s.rect(xx-w/14,y-8,w/7,18,COL[k],COL[k],0);s.dot(xx,y,COL[k],6);s.text(['A1','A2','B','C','D'][k],xx-20,y+13,45,28,19,COL[k],align='center')
 return [(x+(j+.5)*w/5,y) for j in range(5)]

def axis(s,x,y,w,h,xmax=100,ymax=8,ticks=True):
 s.line(x,y,x,y+h,GRAY,1);s.line(x,y+h,x+w,y+h,GRAY,1)
 if ticks:
  for v in [0,2,4,6,8]:
   yy=y+h-v/ymax*h;s.line(x-4,yy,x+w,yy,LIGHT,1);s.text(str(v),x-29,yy-12,23,24,17,GRAY,align='right')
 return lambda a,b:(x+a/xmax*w,y+h-b/ymax*h)

def diagrams():
 f=json.loads((BASE/'evidence/existing_five_leaf.json').read_text());a,b=f['profiles'];qorder=b['order']
 s=Scene(2,'Certificate-guided construction',notes='Existing five-leaf example: results/publication2027/figure_data/domain_filling_example.json. Same identities, merge levels, source profiles and interleaved anchor targets across Fig2 and Fig3. Schematic stages do not constitute a new temporal experiment. kappa is eligibility, not an output error bound.')
 for x,title in [(22,'A   Reference & Topology'),(476,'B   Conflict & Relaxation'),(916,'C   Layout & Rendering')]:
  s.text(title,x,10,420,38,24,bold=True);s.line(x,51,x+402,51,LIGHT,1.5)
 tree(s,52,85,320,150)
 s.text('Original scalar hierarchy T',55,271,350,32,21,bold=True)
 orderrow(s,qorder,30,355,360,'Fixed reference order q')
 s.text('A1,A2,B must stay contiguous in T',30,413,395,42,19)
 s.text('Desired interleaving: A1,A2,C,B,D',30,463,405,42,19,BLUE)
 s.text('Same extrema and scalar values',30,568,405,32,19,GRAY)
 s.line(437,70,437,607,LIGHT,1);s.line(888,70,888,607,LIGHT,1)
 s.text('Diagnose unavoidable displacement',475,76,396,60,22,bold=True)
 s.rect(491,157,54,30,GRAY,GRAY,0);s.rect(545,157,243,30,ORANGE,ORANGE,0)
 s.text('packing',482,202,112,30,19,GRAY);s.text('hierarchy cost H',610,202,250,30,19,ORANGE)
 s.text('τ* = τfree + H',490,254,365,38,26,bold=True)
 s.text('H > θ activates relaxation',490,315,365,35,21)
 s.text('P  Keep original child blocks',490,379,365,42,21,BLUE,bold=True)
 s.text('R  Release eligible constraints',490,436,365,42,21,GREEN,bold=True)
 s.text('Restore constraints that fit the budget',490,489,365,60,19,GRAY)
 s.text('κ tests parent gaps; cost is measured',475,568,410,42,19,GRAY)
 orderrow(s,a['order'],923,133,375,'P: original ordering tree')
 orderrow(s,b['order'],923,267,375,'R: expanded order set')
 xy=axis(s,952,371,250,126,ticks=False)
 s.path([xy(i,v) for i,v in enumerate(b['initial'])],GRAY,1.6,True,'LCA_profile')
 s.path([xy(i,v) for i,v in enumerate(b['corrected'])],GREEN,2.4,False,'Optimal_profile')
 
 for x in [442,867]:
  s.line(x,290,x+25,290,GRAY,2);s.line(x+17,283,x+25,290,GRAY,2);s.line(x+17,297,x+25,290,GRAY,2)
 import matplotlib
 cm=matplotlib.colormaps['RdBu_r']
 for j in range(3):
  for k,v in enumerate(b['corrected'][::5]):
   rgb=cm(v/8);color='#'+''.join(f'{round(c*255):02X}' for c in rgb[:3]);s.rect(1241+21*j,371+6*k,19,6,color,color,0)
 s.text('time',1237,504,86,23,17,GRAY)
 s.text('Minimax barriers preserve extrema',923,523,390,30,20,bold=True)
 s.text('Same order: LCA error 5; optimum 2.5',923,568,404,42,19)
 s.save()
 s=Scene(3,'Why change order, and why optimize barriers?',notes='Existing five-leaf augmented tree and saved 101-sample profiles. Source tree (((A1,A2)_2,B)_4,(C,D)_3)_8. Interleaved order A1,A2,C,B,D. References shown at the saved interleaved anchor targets. Original fixed illustrated anchors give max displacement20, not a claim of minimum certificate. LCA profile worst-pair error5, optimum2.5. No new scalar dataset generated.')
 s.text('(a) Scalar hierarchy and desired order',20,8,490,34,23,bold=True)
 tree(s,53,91,322,179)
 orderrow(s,a['order'],28,378,365,'Legal tree order')
 orderrow(s,b['order'],28,513,365,'Desired reference order')
 s.text('B/C swap breaks two subtree blocks',23,583,420,32,19,ORANGE)
 s.line(446,42,446,607,LIGHT,1)
 for row,(p,y,title) in enumerate([(a,60,'(b) Keep hierarchy: merge error 0'),(b,346,'(c) Release contiguity: same order, two fillings')]):
  s.text(title,483,y-47,825,35,23,bold=True)
  tf=axis(s,518,y,779,165)
  for k,anc in zip(p['order'],p['anchors']):
   xx,_=tf(anc,0);s.rect(xx-29,y,58,165,COL[k]+'/10','none',0)
  if row:s.path([tf(i,v) for i,v in enumerate(p['initial'])],GRAY,1.8,True,'Original_LCA_filling')
  s.path([tf(i,v) for i,v in enumerate(p['corrected'])],BLUE if not row else GREEN,2.4,False,f'Scalar_profile_{row}')
  for k,anc in zip(p['order'],p['anchors']):
   xx,yy=tf(anc,0);s.dot(xx,yy,COL[k],6);s.text(['A1','A2','B','C','D'][k],xx-21,yy+8,45,25,19,COL[k],align='center')
  for i,bar in enumerate(p['barriers']):
   lo,hi=p['anchors'][i:i+2];peak=lo+int(max(range(hi-lo+1),key=lambda j:p['corrected'][lo+j]));xx,yy=tf(peak,bar);s.text(f'{bar:g}',xx-21,yy-27,43,25,17,GREEN if row else BLUE,align='center')
 s.text('Illustrated anchors: max |u − q| = 20',490,267,800,30,20,BLUE)
 s.text('Reference-aligned anchors: max |u − q| = 0',490,554,830,30,20,GREEN)
 s.text('LCA error 5   /   optimal barrier error 2.5',490,590,830,32,21,bold=True)
 s.save()
if __name__=='__main__':diagrams()
