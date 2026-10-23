"""Install the selected genuine hourly data-direction figure as canonical Figure1.
Preserve every existing combined-deck part outside the first-slide replacement.
"""
from _filesystem import copy_if_distinct
from pathlib import Path,PurePosixPath
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E
from copy import deepcopy
import shutil,posixpath,json,hashlib
R=Path(__file__).resolve().parents[1];B=R/'.build/fig1_selected';B.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
count=json.loads((R/'FIGURE_INDEX.json').read_text())['main_figure_count']
protected={str(p.relative_to(R)):sha(p) for n in range(2,count+1) for p in [R/f'figures_ppt/Fig{n}.pptx',R/f'figures_export/Fig{n}.pdf',R/f'figures_export/Fig{n}.png'] if p.exists()}
combined=R/'figures_ppt/All_Figures.pptx'
with ZipFile(combined) as z:old={n:z.read(n) for n in z.namelist()}
for ext,folder in [('pptx','figures_ppt'),('pdf','figures_export'),('png','figures_export')]:
 copy_if_distinct(R/'supplementary_variants'/folder/f'Fig1_DataDirection.{ext}',R/folder/f'Fig1.{ext}')
for ext in ['pdf','png']:copy_if_distinct(R/f'figures_export/Fig1.{ext}',R/f'manuscript/latex/figures/Fig1.{ext}')
for p in [R/'figures_export/Fig1.svg',R/'manuscript/latex/figures/Fig1.svg']:p.unlink(missing_ok=True)
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
for pre,uri in [('p',P),('a',A),('r',RR)]:E.register_namespace(pre,uri)
enc=lambda e:E.tostring(e,encoding='utf-8',xml_declaration=True)
with ZipFile(R/'figures_ppt/Fig1.pptx') as z:new={n:z.read(n) for n in z.namelist()}
prefix='ppt/selected_fig1_hourly';out=old.copy()
for name,data in new.items():
 if name in ['[Content_Types].xml','_rels/.rels']:continue
 if name.endswith('.rels'):
  root=E.fromstring(data)
  for rel in root:
   if rel.get('TargetMode')!='External' and rel.get('Target','').startswith('/'):rel.set('Target','/'+prefix+rel.get('Target'))
  data=enc(root)
 out[prefix+'/'+name]=data
pres=E.fromstring(old['ppt/presentation.xml']);relmap={r.get('Id'):r.get('Target') for r in E.fromstring(old['ppt/_rels/presentation.xml.rels'])};first=pres.find(f'{{{P}}}sldIdLst')[0];target=relmap[first.get(f'{{{RR}}}id')];part=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'ppt/'+target)
tree=E.fromstring(new['ppt/slides/slide1.xml']);sp=tree.find(f'{{{P}}}cSld/{{{P}}}spTree')
sz=pres.find(f'{{{P}}}sldSz');tw,th=int(sz.get('cx')),int(sz.get('cy'));nsz=E.fromstring(new['ppt/presentation.xml']).find(f'{{{P}}}sldSz');sw,sh=int(nsz.get('cx')),int(nsz.get('cy'));scale=min(tw/sw,th/sh)
group=E.Element(f'{{{P}}}grpSp');nv=E.SubElement(group,f'{{{P}}}nvGrpSpPr');mid=max(int(e.get('id')) for e in tree.iter(f'{{{P}}}cNvPr'))+1;E.SubElement(nv,f'{{{P}}}cNvPr',id=str(mid),name='Manuscript Figure 1: Storms hourly overview and local tracks');E.SubElement(nv,f'{{{P}}}cNvGrpSpPr');E.SubElement(nv,f'{{{P}}}nvPr');xf=E.SubElement(E.SubElement(group,f'{{{P}}}grpSpPr'),f'{{{A}}}xfrm')
for tag,attrs in [('off',dict(x=str(round((tw-sw*scale)/2)),y=str(round((th-sh*scale)/2)))),('ext',dict(cx=str(round(sw*scale)),cy=str(round(sh*scale)))),('chOff',dict(x='0',y='0')),('chExt',dict(cx=str(sw),cy=str(sh)))]:E.SubElement(xf,f'{{{A}}}{tag}',attrs)
for c in list(sp)[2:]:sp.remove(c);group.append(c)
for e in group.iter():
 if e.tag in [f'{{{A}}}rPr',f'{{{A}}}defRPr',f'{{{A}}}endParaRPr'] and 'sz'in e.attrib:e.set('sz',str(round(int(e.get('sz'))*scale)))
 if e.tag==f'{{{A}}}ln' and 'w'in e.attrib:e.set('w',str(round(int(e.get('w'))*scale)))
sp.append(group);out[part]=enc(tree)
rels=E.fromstring(new['ppt/slides/_rels/slide1.xml.rels'])
for rel in rels:
 if rel.get('TargetMode')=='External':continue
 t=rel.get('Target');resolved=posixpath.normpath(t.lstrip('/') if t.startswith('/') else 'ppt/slides/'+t);rel.set('Target','/'+prefix+'/'+resolved)
relpart=posixpath.dirname(part)+'/_rels/'+posixpath.basename(part)+'.rels';out[relpart]=enc(rels)
for name,data in list(out.items()):
 if not name.startswith(prefix+'/') or not name.endswith('.rels'):continue
 root=E.fromstring(data);parent=str(PurePosixPath(name).parent.parent)
 for rel in root:
  if rel.get('TargetMode')=='External':continue
  t=rel.get('Target');resolved=posixpath.normpath(t.lstrip('/') if t.startswith('/') else parent+'/'+t)
  if resolved==prefix+'/ppt/slides/slide1.xml':rel.set('Target','/'+part)
 out[name]=enc(root)
ct=E.fromstring(old['[Content_Types].xml'])
for el in E.fromstring(new['[Content_Types].xml']):
 if el.tag.endswith('Override'):
  nm='/'+prefix+el.get('PartName')
  if not any(t.get('PartName')==nm for t in ct):E.SubElement(ct,f'{{{CT}}}Override',PartName=nm,ContentType=el.get('ContentType'))
 elif not any(t.get('Extension')==el.get('Extension') for t in ct):ct.append(deepcopy(el))
E.register_namespace('',CT)
out['[Content_Types].xml']=enc(ct)
changed=[n for n in old if old[n]!=out[n]];assert all(n in {part,relpart,'[Content_Types].xml'} or n.startswith(prefix+'/') for n in changed)
for t in range(2,count+1):assert old[f'ppt/slides/slide{t}.xml']==out[f'ppt/slides/slide{t}.xml']
candidate=B/'All_Figures_candidate.pptx'
with ZipFile(candidate,'w',ZIP_DEFLATED) as z:
 for n,v in out.items():z.writestr(n,v)
with ZipFile(candidate) as z:assert z.testzip() is None
copy_if_distinct(candidate,combined)
reg=json.loads((R/'FIGURE_INDEX.json').read_text());f=reg['figures'][0];f.update(title='Storms hourly overview, source event and local tracks',ppt_sha256=sha(R/'figures_ppt/Fig1.pptx'),asset_sha256=sha(R/'figures_export/Fig1.pdf'),selected_variant='Fig1_DataDirection',frame_count=744,period=['1999-12-01 00:00','1999-12-31 23:00'],direction=[0.94783175,-0.31877104]);reg['combined_sha256']=sha(combined);reg['updated']='2026-10-22';(R/'FIGURE_INDEX.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
for name,h in protected.items():assert sha(R/name)==h,name
receipt=dict(selected_variant='Fig1_DataDirection',frame_count=744,direction=f['direction'],combined_slide_count=count,changed_existing_combined_parts=changed,other_original_package_parts_byte_identical=True,protected_other_figures_sha256=protected,selected_assets={str(p.relative_to(R)):sha(p) for p in [R/'figures_ppt/Fig1.pptx',R/'figures_export/Fig1.png',R/'figures_export/Fig1.pdf',combined]})
(R/'checks/selected_fig1_data_direction.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Installed selected Fig1; only first-slide parts changed in the current combined deck.')
