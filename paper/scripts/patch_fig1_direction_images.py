"""Keep full scientific raster bytes and explicit native layout rectangles."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,sys,posixpath,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1];B=R/'.build/fig1_december';stem=sys.argv[1]
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
for pre,uri in [('p',P),('a',A),('r',RR)]:E.register_namespace(pre,uri)
with ZipFile(B/(stem+'_candidate.pptx')) as z:parts={n:z.read(n) for n in z.namelist()}
scene=json.loads((B/(stem+'_scene.json')).read_text());tree=E.fromstring(parts['ppt/slides/slide1.xml']);rels=E.fromstring(parts['ppt/slides/_rels/slide1.xml.rels'])
for pic,o in zip(tree.iter(f'{{{P}}}pic'),[o for o in scene['objects'] if o['kind']=='image']):
 xf=pic.find(f'{{{P}}}spPr/{{{A}}}xfrm');xf.find(f'{{{A}}}off').attrib.update(x=str(round(o['x']*9525)),y=str(round(o['y']*9525)));xf.find(f'{{{A}}}ext').attrib.update(cx=str(round(o['w']*9525)),cy=str(round(o['h']*9525)))
 rid=pic.find(f'{{{P}}}blipFill/{{{A}}}blip').get(f'{{{RR}}}embed');target=next(r.get('Target') for r in rels if r.get('Id')==rid)
 target=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'ppt/slides/'+target);parts[target]=Path(o['path']).read_bytes()
for sp in tree.iter(f'{{{P}}}sp'):
 nv=sp.find(f'{{{P}}}nvSpPr/{{{P}}}cNvPr')
 if nv is not None:
  spec=next((o for o in scene['objects'] if o.get('name')==nv.get('name') and o.get('textOrientation')),None)
  if spec:sp.find(f'{{{P}}}txBody/{{{A}}}bodyPr').set('vert',spec['textOrientation'])
parts['ppt/slides/slide1.xml']=E.tostring(tree,encoding='utf-8',xml_declaration=True)
with ZipFile(B/(stem+'_patched.pptx'),'w',ZIP_DEFLATED) as z:
 for n,data in parts.items():z.writestr(n,data)
