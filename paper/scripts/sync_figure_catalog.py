"""Synchronize numbered main-figure assets and merge all registered main figures without flattening objects."""
from _filesystem import copy_if_distinct
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import xml.etree.ElementTree as E
import posixpath,json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships';REL='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
for pre,uri in [('p',P),('a',A),('r',RR)]:E.register_namespace(pre,uri)
enc=lambda e:E.tostring(e,encoding='utf-8',xml_declaration=True)
xml=E.fromstring
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(parent,target):return posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.dirname(parent)+'/'+target)
reg=json.loads((R/'FIGURE_INDEX.json').read_text())
with ZipFile(R/reg['figures'][0]['ppt'])as z:out={n:z.read(n)for n in z.namelist()}
pr=xml(out['ppt/presentation.xml']);rels=xml(out['ppt/_rels/presentation.xml.rels']);types=xml(out['[Content_Types].xml']);size=pr.find(f'{{{P}}}sldSz');tw,th=int(size.get('cx')),int(size.get('cy'))
ids=pr.find(f'{{{P}}}sldIdLst');ids.clear();masters=pr.find(f'{{{P}}}sldMasterIdLst');masters.clear()
for e in list(rels):
 if e.get('Type','').endswith(('/slide','/slideMaster')):rels.remove(e)
serial=1000;masterid=2147483648
for f in reg['figures']:
 n=f['number'];source=R/f['ppt']
 with ZipFile(source)as z:parts={k:z.read(k)for k in z.namelist()}
 prefix=f'ppt/main_figures/Fig{n}'
 for name,data in parts.items():
  if name in ['[Content_Types].xml','_rels/.rels']:continue
  if name.endswith('.rels'):
   el=xml(data)
   for rel in el:
    if rel.get('TargetMode')!='External' and rel.get('Target','').startswith('/'):rel.set('Target','/'+prefix+rel.get('Target'))
   data=enc(el)
  out[prefix+'/'+name]=data
 for typ in xml(parts['[Content_Types].xml']):
  if typ.tag.endswith('Override'):
   nm='/'+prefix+typ.get('PartName')
   if not any(t.get('PartName')==nm for t in types):E.SubElement(types,f'{{{CT}}}Override',PartName=nm,ContentType=typ.get('ContentType'))
  elif not any(t.get('Extension')==typ.get('Extension')for t in types):types.append(deepcopy(typ))
 p=xml(parts['ppt/presentation.xml']);rd={e.get('Id'):e for e in xml(parts['ppt/_rels/presentation.xml.rels'])};sid=p.find(f'{{{P}}}sldIdLst');assert len(sid)==1
 srcpart=resolve('ppt/presentation.xml',rd[sid[0].get(f'{{{RR}}}id')].get('Target'))
 tree=xml(parts[srcpart]);sp=tree.find(f'{{{P}}}cSld/{{{P}}}spTree');sz=p.find(f'{{{P}}}sldSz');sw,sh=int(sz.get('cx')),int(sz.get('cy'));scale=min(tw/sw,th/sh)
 group=E.Element(f'{{{P}}}grpSp');nv=E.SubElement(group,f'{{{P}}}nvGrpSpPr');maxid=max(int(e.get('id'))for e in tree.iter(f'{{{P}}}cNvPr'));E.SubElement(nv,f'{{{P}}}cNvPr',id=str(maxid+1),name=f'Manuscript Figure {n}: {f["title"]}');E.SubElement(nv,f'{{{P}}}cNvGrpSpPr');E.SubElement(nv,f'{{{P}}}nvPr');xf=E.SubElement(E.SubElement(group,f'{{{P}}}grpSpPr'),f'{{{A}}}xfrm')
 for tag,attrs in [('off',dict(x=str(round((tw-sw*scale)/2)),y=str(round((th-sh*scale)/2)))),('ext',dict(cx=str(round(sw*scale)),cy=str(round(sh*scale)))),('chOff',dict(x='0',y='0')),('chExt',dict(cx=str(sw),cy=str(sh)))]:E.SubElement(xf,f'{{{A}}}{tag}',attrs)
 for child in list(sp)[2:]:sp.remove(child);group.append(child)
 for el in group.iter():
  if el.tag in [f'{{{A}}}rPr',f'{{{A}}}defRPr',f'{{{A}}}endParaRPr']and'sz'in el.attrib:el.set('sz',str(round(int(el.get('sz'))*scale)))
  if el.tag==f'{{{A}}}ln'and'w'in el.attrib:el.set('w',str(round(int(el.get('w'))*scale)))
 sp.append(group);dst=f'ppt/slides/slide{n}.xml';out[dst]=enc(tree)
 oldrels=posixpath.dirname(srcpart)+'/_rels/'+posixpath.basename(srcpart)+'.rels'
 if oldrels in parts:
  sr=xml(parts[oldrels])
  for rel in sr:
   if rel.get('TargetMode')!='External':rel.set('Target','/'+prefix+'/'+resolve(srcpart,rel.get('Target')))
  out[f'ppt/slides/_rels/slide{n}.xml.rels']=enc(sr)
 if not any(t.get('PartName')=='/'+dst for t in types):E.SubElement(types,f'{{{CT}}}Override',PartName='/'+dst,ContentType='application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
 serial+=1;rid=f'rId{serial}';E.SubElement(rels,f'{{{REL}}}Relationship',Id=rid,Type=RR+'/slide',Target=f'slides/slide{n}.xml');E.SubElement(ids,f'{{{P}}}sldId',id=str(255+n),attrib={f'{{{RR}}}id':rid})
 for mid in p.find(f'{{{P}}}sldMasterIdLst'):
  mt=resolve('ppt/presentation.xml',rd[mid.get(f'{{{RR}}}id')].get('Target'));serial+=1;rid=f'rId{serial}';E.SubElement(rels,f'{{{REL}}}Relationship',Id=rid,Type=RR+'/slideMaster',Target='/'+prefix+'/'+mt);E.SubElement(masters,f'{{{P}}}sldMasterId',id=str(masterid),attrib={f'{{{RR}}}id':rid});masterid+=1
 for e in (R/'figures_export').glob(f'Fig{n}.*'):
  if e.suffix in ['.pdf','.png','.svg'] and not f.get('pending_manuscript_sync'):copy_if_distinct(e,R/'manuscript/latex/figures'/e.name)
 f['ppt_sha256']=sha(source);f['asset_sha256']=sha(R/f['asset'])
out['ppt/presentation.xml']=enc(pr)
E.register_namespace('',REL)
out['ppt/_rels/presentation.xml.rels']=enc(rels)
for name,data in list(out.items()):
 if name.endswith('.rels'):out[name]=enc(xml(data))
E.register_namespace('',CT)
out['[Content_Types].xml']=enc(types)
staging=R/'.build/figure_catalog';staging.mkdir(parents=True,exist_ok=True)
with ZipFile(staging/'All_Figures.pptx','w',ZIP_DEFLATED)as z:
 for n,v in out.items():z.writestr(n,v)
with ZipFile(staging/'All_Figures.pptx')as z:assert z.testzip() is None
copy_if_distinct(staging/'All_Figures.pptx',R/reg['combined_ppt'])
reg['combined_sha256']=sha(R/reg['combined_ppt']);(R/'FIGURE_INDEX.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
print(f'Synchronized {len(reg["figures"])} numbered PPTs, combined slides, and matching LaTeX assets.')
