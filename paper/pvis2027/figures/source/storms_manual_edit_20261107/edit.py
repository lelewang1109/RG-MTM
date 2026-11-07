from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E,shutil,json,copy
O=Path(__file__).resolve().parent;P=O.parents[2];source=P/'最新论文与三张PPT/Fig6_Storms_参数与方法对比_可编辑.pptx';backup=O/'.build/user_modified_before.pptx'
if not backup.exists():shutil.copy2(source,backup)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
for prefix,url in ns.items():E.register_namespace(prefix,url)
a=lambda t:'{'+ns['a']+'}'+t
with ZipFile(backup) as z:
 root=E.fromstring(z.read('ppt/slides/slide1.xml'));nodes={s.find('.//p:cNvPr',ns).get('id'):s for s in root.findall('.//p:spTree/*',ns) if s.find('.//p:cNvPr',ns) is not None};before={i:E.tostring(v) for i,v in nodes.items()};u=9525
 def pos(i,x,y,w,h):
  xf=nodes[str(i)].find('.//a:xfrm',ns);xf.attrib.clear();xf.find('a:off',ns).attrib.update(x=str(round(x*u)),y=str(round(y*u)));xf.find('a:ext',ns).attrib.update(cx=str(round(w*u)),cy=str(round(h*u)))
 def text(i,value,x,y,w,h):
  pos(i,x,y,w,h);body=nodes[str(i)].find('p:txBody',ns)
  for p in list(body.findall('a:p',ns)):body.remove(p)
  for line in value.split('\n'):
   par=E.SubElement(body,a('p'));pr=E.SubElement(par,a('pPr'),{'algn':'ctr'});run=E.SubElement(par,a('r'));rp=E.SubElement(run,a('rPr'),{'sz':'1350','lang':'en-US'});E.SubElement(rp,a('latin'),{'typeface':'Times New Roman'});E.SubElement(run,a('t')).text=line
 # Preserve the manually chosen x and y positions, match original top map extents.
 for i in [103,104]:pos(i,2570480/u,2236470/u,200,168)
 for i in [108,109]:pos(i,6590665/u,2236470/u,200,168)
 pos(102,2570480/u,409,200,28);pos(107,6590665/u,409,200,28)
 text(114,'+ Temporal\nalignment',20,246,140,50)
 text(118,'+ Spatial\ngeometry',506,262,150,50)
 # Native editable connectors, retaining the user's L route and straight-arrow arrangement.
 first=nodes['122'];xf=first.find('.//a:xfrm',ns);old_off=xf.find('a:off',ns);old_ex=xf.find('a:ext',ns)
 # Replace only connector geometry with a native custom path through the same routing region.
 def connector(i,pts):
  el=nodes[str(i)];sp=el.find('p:spPr',ns);x=min(p[0] for p in pts);y=min(p[1] for p in pts);w=max(p[0] for p in pts)-x;h=max(p[1] for p in pts)-y;pos(i,x,y,max(w,.01),max(h,.01))
  for g in list(sp):
   if g.tag in [a('prstGeom'),a('custGeom')]:sp.remove(g)
  geom=E.Element(a('custGeom'))
  for name in ['avLst','gdLst','ahLst','cxnLst']:E.SubElement(geom,a(name))
  E.SubElement(geom,a('rect'),{'l':'0','t':'0','r':'r','b':'b'});pl=E.SubElement(geom,a('pathLst'));path=E.SubElement(pl,a('path'),{'w':str(round(max(w,.01)*u)),'h':str(round(max(h,.01)*u)),'fill':'none'})
  for j,(xx,yy) in enumerate(pts):cmd=E.SubElement(path,a('moveTo' if j==0 else 'lnTo'));E.SubElement(cmd,a('pt'),{'x':str(round((xx-x)*u)),'y':str(round((yy-y)*u))})
  sp.insert(1,geom)
  nv=el.find('p:nvCxnSpPr/p:cNvCxnSpPr',ns)
  if nv is not None:
   for c in list(nv):nv.remove(c)
 connector(122,[(112,211),(112,319),(2570480/u,319)])
 connector(124,[(2570480/u+200,319),(6590665/u,319)])
 changed=[i for i in nodes if before[i]!=E.tostring(nodes[i])];assert set(changed)==set(map(str,[103,104,108,109,102,107,114,118,122,124]))
 out=O/'.build/candidate.pptx'
 with ZipFile(out,'w',ZIP_DEFLATED) as dst:
  for item in z.infolist():dst.writestr(item,E.tostring(root,encoding='utf-8',xml_declaration=True) if item.filename=='ppt/slides/slide1.xml' else z.read(item.filename))
 (O/'audit.json').write_text(json.dumps(dict(source='user-edited PPT backup',changed_shape_ids=changed,all_other_shapes_unchanged=True,all_media_unchanged=True,baseline_size_css_px=[200,168],top_map_size_css_px=[200,168],labels=['+ Temporal alignment','+ Spatial geometry']),indent=2))
