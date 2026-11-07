from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E
O=Path(__file__).resolve().parent;source=O/'.build/candidate.pptx';ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
for k,v in ns.items():E.register_namespace(k,v)
a=lambda t:'{'+ns['a']+'}'+t;p=lambda t:'{'+ns['p']+'}'+t
with ZipFile(source) as src:
 r=E.fromstring(src.read('ppt/slides/slide1.xml'));tree=r.find('p:cSld/p:spTree',ns)
 def shape(id,name,x,y,w,h):
  sp=E.SubElement(tree,p('sp'));nv=E.SubElement(sp,p('nvSpPr'));E.SubElement(nv,p('cNvPr'),{'id':str(id),'name':name});E.SubElement(nv,p('cNvSpPr'));E.SubElement(nv,p('nvPr'));pr=E.SubElement(sp,p('spPr'));xf=E.SubElement(pr,a('xfrm'));E.SubElement(xf,a('off'),{'x':str(round(x*9525)),'y':str(round(y*9525))});E.SubElement(xf,a('ext'),{'cx':str(round(w*9525)),'cy':str(round(h*9525))});g=E.SubElement(pr,a('prstGeom'),{'prst':'rect'});E.SubElement(g,a('avLst'));E.SubElement(pr,a('noFill'));return sp,pr
 maxid=max(int(x.get('id')) for x in r.findall('.//p:cNvPr',ns));sp,pr=shape(maxid+1,'Ours editable dashed group frame',5,1.5,1148,220);ln=E.SubElement(pr,a('ln'),{'w':'11430'});fill=E.SubElement(ln,a('solidFill'));E.SubElement(fill,a('srgbClr'),{'val':'555555'});E.SubElement(ln,a('prstDash'),{'val':'dash'})
 sp,pr=shape(maxid+2,'Ours editable label',11,7,48,25);ln=E.SubElement(pr,a('ln'));E.SubElement(ln,a('noFill'));body=E.SubElement(sp,p('txBody'));E.SubElement(body,a('bodyPr'),{'anchor':'ctr','lIns':'0','rIns':'0','tIns':'0','bIns':'0'});E.SubElement(body,a('lstStyle'));para=E.SubElement(body,a('p'));E.SubElement(para,a('pPr'),{'algn':'ctr'});run=E.SubElement(para,a('r'));rp=E.SubElement(run,a('rPr'),{'sz':'1350'});E.SubElement(rp,a('latin'),{'typeface':'Times New Roman'});E.SubElement(run,a('t')).text='Ours'
 with ZipFile(O/'.build/ours_candidate.pptx','w',ZIP_DEFLATED) as out:
  for item in src.infolist():out.writestr(item,E.tostring(r,encoding='utf-8',xml_declaration=True) if item.filename=='ppt/slides/slide1.xml' else src.read(item.filename))
