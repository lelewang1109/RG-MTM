from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E,copy,shutil
O=Path(__file__).resolve().parent;P=O.parents[2];src=P/'最新论文与三张PPT/Fig6_Storms_参数与方法对比_可编辑.pptx';shutil.copy2(src,O/'.build/before.pptx');ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for k,v in ns.items():E.register_namespace(k,v)
a=lambda x:'{'+ns['a']+'}'+x;p=lambda x:'{'+ns['p']+'}'+x
with ZipFile(src) as z:
 r=E.fromstring(z.read('ppt/slides/slide1.xml'));tree=r.find('p:cSld/p:spTree',ns);nodes={v.find('.//p:cNvPr',ns).get('id'):v for v in tree if v.find('.//p:cNvPr',ns) is not None};U=9525
 def pos(el,x,y,w,h):
  xf=el.find('.//a:xfrm',ns);xf.attrib.clear();xf.find('a:off',ns).attrib.update(x=str(round(x*U)),y=str(round(y*U)));xf.find('a:ext',ns).attrib.update(cx=str(round(w*U)),cy=str(round(h*U)))
 for key,el in list(nodes.items()):
  i=int(key)
  if i in [102,103,104,107,108,109]:continue
  if i in [111,112,114,118,122,124] or i>124:tree.remove(el);continue
  xf=el.find('.//a:xfrm',ns)
  if xf is not None:off=xf.find('a:off',ns);off.set('y',str(int(off.get('y'))+120*U))
 for i in [103,104]:pos(nodes[str(i)],900,370,200,168)
 for i in [108,109]:pos(nodes[str(i)],400,370,200,168)
 pos(nodes['102'],900,543,200,28);pos(nodes['107'],400,543,200,28)
 uid=130
 def shape(x,y,w,h,kind='rect',fill=None,stroke='222222',width=1,dash=False):
  global uid
  uid+=1;sp=E.SubElement(tree,p('sp'));nv=E.SubElement(sp,p('nvSpPr'));E.SubElement(nv,p('cNvPr'),{'id':str(uid),'name':f'Editable diagram {uid}'});E.SubElement(nv,p('cNvSpPr'));E.SubElement(nv,p('nvPr'));pr=E.SubElement(sp,p('spPr'));xf=E.SubElement(pr,a('xfrm'));E.SubElement(xf,a('off'));E.SubElement(xf,a('ext'));pos(sp,x,y,max(w,.1),max(h,.1));g=E.SubElement(pr,a('prstGeom'),{'prst':kind});E.SubElement(g,a('avLst'))
  if fill:f=E.SubElement(pr,a('solidFill'));E.SubElement(f,a('srgbClr'),{'val':fill})
  else:E.SubElement(pr,a('noFill'))
  ln=E.SubElement(pr,a('ln'),{'w':str(round(width*U))});f=E.SubElement(ln,a('solidFill'));E.SubElement(f,a('srgbClr'),{'val':stroke})
  if dash:E.SubElement(ln,a('prstDash'),{'val':'dash'})
  return sp
 def text(t,x,y,w,h=25,size=18,bold=False):
  sp=shape(x,y,w,h,stroke='FFFFFF',width=0);body=E.SubElement(sp,p('txBody'));E.SubElement(body,a('bodyPr'),{'anchor':'ctr','lIns':'0','rIns':'0','tIns':'0','bIns':'0'});E.SubElement(body,a('lstStyle'))
  for s in t.split('\n'):
   para=E.SubElement(body,a('p'));E.SubElement(para,a('pPr'),{'algn':'ctr'});run=E.SubElement(para,a('r'));rp=E.SubElement(run,a('rPr'),{'sz':str(round(size*75)),'b':'1' if bold else '0'});E.SubElement(rp,a('latin'),{'typeface':'Times New Roman'});E.SubElement(run,a('t')).text=s
 def line(x,y,X,Y,arrow=False,color='222222',lw=1.5):
  sp=shape(min(x,X),min(y,Y),abs(X-x),abs(Y-y),'line',stroke=color,width=lw);xf=sp.find('.//a:xfrm',ns)
  if (X-x)*(Y-y)<0:xf.set('flipV','1')
  if arrow:ln=sp.find('.//a:ln',ns);E.SubElement(ln,a('headEnd' if X<x or (X==x and Y<y) else 'tailEnd'),{'type':'triangle'})
 shape(5,73,1148,270,stroke='333333',dash=True)
 text('Ours',8,219,48,30,19,True)
 shape(420,55,330,32,'roundRect','F0F0F0');text('AnchorMTM',420,55,330,32,23,True)
 shape(78,90,215,25,'roundRect','F0F0F0',width=0);text('Exact Topology (ε = 0%)',78,90,215,25,17,True)
 shape(870,90,265,25,'roundRect','F0F0F0',width=0);text('Bounded Topology (ε > 0%)',870,90,265,25,17,True);line(310,103,850,103,True,'0067C7',2)
 for x,title,subtitle in [(640,'Improvement 1','+ Spatial Awareness'),(120,'Improvement 2','+ Topology Budget')]:
  shape(x,395,220,140,'roundRect','FFFFFF');text(title,x,403,220,30,21,True);text(subtitle,x,438,220,25,18)
 line(900,454,860,454,True);line(640,454,600,454,True);line(400,454,340,454,True);line(120,454,112,454);line(112,454,112,332,True)
 # Native editable spatial-grid and profile icons.
 for i in range(4):line(667+i*14,476,667+i*14,518,lw=.7);line(667,476+i*14,709,476+i*14,lw=.7)
 shape(681,490,14,14,fill='7EB9E5',stroke='777777',width=.5);text('→',718,477,35,30,26);line(760,516,840,516,lw=.8)
 for x,y,X,Y in [(762,510,780,509),(780,509,790,493),(790,493,800,486),(800,486,809,494),(809,494,819,508),(819,508,838,510)]:line(x,y,X,Y,color='0067C7',lw=2)
 for dx in [0,110]:
  line(155+dx,478,140+dx,510);line(155+dx,478,175+dx,510)
  for xx,yy,c in [(155+dx,478,'D3C6EB'),(140+dx,510,'BEE0EF'),(175+dx,510,'FFF0B7' if dx else 'BEE0EF')]:shape(xx-6,yy-6,12,12,'ellipse',c,'333333',1)
 text('→',195,480,35,30,26)
 out=O/'.build/candidate.pptx'
 with ZipFile(out,'w',ZIP_DEFLATED) as dst:
  for item in z.infolist():dst.writestr(item,E.tostring(r,encoding='utf-8',xml_declaration=True) if item.filename=='ppt/slides/slide1.xml' else z.read(item.filename))
