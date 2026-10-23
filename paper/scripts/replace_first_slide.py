"""Preserve every original package entry except slide 1, its rels and CT.

New resource parts are namespaced so no resource used by slides 2–6 is edited.
This preserves original native shapes/groups/fonts and embedded images verbatim.
"""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as E
import posixpath, hashlib, json

HERE=Path(__file__).resolve().parents[1]
SOURCE=HERE/'figures_ppt/All_Figures.pptx'
NEW=HERE/'.build/fig1/Figure1_candidate.pptx'
DEST=HERE/'.build/fig1/All_Figures_candidate.pptx'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
for pre,uri in [('p',P),('a',A),('r',RR)]:E.register_namespace(pre,uri)
def encode(el):return E.tostring(el,encoding='utf-8',xml_declaration=True)
with ZipFile(SOURCE) as z:original={n:z.read(n) for n in z.namelist()}
with ZipFile(NEW) as z:new={n:z.read(n) for n in z.namelist()}
out=original.copy()
prefix='ppt/fig1_redesign'
for name,contents in new.items():
    if name in ['[Content_Types].xml','_rels/.rels']:continue
    if name.endswith('.rels'):
        el=E.fromstring(contents)
        # Relative targets resolve inside the copied namespace. Rebase absolute.
        for rel in el:
            if rel.get('TargetMode')=='External':continue
            if rel.get('Target','').startswith('/'):
                rel.set('Target','/'+prefix+rel.get('Target'))
        contents=encode(el)
    out[prefix+'/'+name]=contents

canonical='ppt/slides/slide1.xml'
out[canonical]=new[canonical]
rels=E.fromstring(new['ppt/slides/_rels/slide1.xml.rels'])
oldrels=E.fromstring(original['ppt/slides/_rels/slide1.xml.rels'])
oldlayout=next(r.get('Target') for r in oldrels if r.get('Type','').endswith('/slideLayout'))
for rel in rels:
    if rel.get('TargetMode')=='External':continue
    if rel.get('Type','').endswith('/slideLayout'):
        rel.set('Target',oldlayout)
    else:
        t=rel.get('Target')
        resolved=posixpath.normpath(t.lstrip('/') if t.startswith('/') else 'ppt/slides/'+t)
        rel.set('Target','/'+prefix+'/'+resolved)
out['ppt/slides/_rels/slide1.xml.rels']=encode(rels)

# Point new notes back at the actual first slide rather than the unused copy.
for name in list(out):
    if not name.startswith(prefix+'/') or not name.endswith('.rels'):continue
    el=E.fromstring(out[name]);parent=str(PurePosixPath(name).parent.parent)
    for rel in el:
        t=rel.get('Target','')
        if rel.get('TargetMode')=='External':continue
        resolved=posixpath.normpath(t.lstrip('/') if t.startswith('/') else parent+'/'+t)
        if resolved==prefix+'/'+canonical:rel.set('Target','/'+canonical)
    out[name]=encode(el)

ct=E.fromstring(original['[Content_Types].xml'])
for el in E.fromstring(new['[Content_Types].xml']):
    if el.tag.endswith('Override'):
        E.SubElement(ct,f'{{{CT}}}Override',PartName='/'+prefix+el.get('PartName'),ContentType=el.get('ContentType'))
    elif not any(x.get('Extension')==el.get('Extension') for x in ct):ct.append(el)
E.register_namespace('',CT)
out['[Content_Types].xml']=encode(ct)

# Actual panels are editable groups. Their children retain independent names.
tree=E.fromstring(out[canonical]);sp=tree.find(f'{{{P}}}cSld/{{{P}}}spTree')
# Data charts intentionally use independent horizontal/vertical axis scales.
# Artifact Tool's contain export adjusts a picture's actual xfrm to image aspect.
# Restore the explicitly specified scientific plotting rectangles, without
# altering source pixels, cropping rows/frames, or resampling saved values.
scene=json.loads((HERE/'evidence/fig1/scene.json').read_text())
# Keep vertical axis text as an editable PowerPoint text box with native
# DrawingML text direction, without negative/rotated off-slide geometry.
orientations={o['name']:o['textOrientation'] for o in scene['objects'] if o.get('textOrientation')}
for shape in tree.iter(f'{{{P}}}sp'):
    nv=shape.find(f'{{{P}}}nvSpPr/{{{P}}}cNvPr')
    if nv is None or nv.get('name') not in orientations:continue
    body=shape.find(f'{{{P}}}txBody/{{{A}}}bodyPr')
    assert body is not None
    body.set('vert',orientations[nv.get('name')]);body.set('anchor','ctr')
images=[o for o in scene['objects'] if o['kind']=='image']
pics=list(tree.iter(f'{{{P}}}pic'))
assert len(images)==len(pics)
for pic,o in zip(pics,images):
    nv=pic.find(f'{{{P}}}nvPicPr/{{{P}}}cNvPr')
    nv.set('name',o['name']);nv.set('descr',o['name'])
    xf=pic.find(f'{{{P}}}spPr/{{{A}}}xfrm')
    xf.find(f'{{{A}}}off').attrib.update(x=str(round(o['x']*9525)),y=str(round(o['y']*9525)))
    xf.find(f'{{{A}}}ext').attrib.update(cx=str(round(o['w']*9525)),cy=str(round(o['h']*9525)))
    # Preserve original full-resolution scientific pixels. The temporary
    # presentation exporter may otherwise resample an image to its fit size.
    rid=pic.find(f'{{{P}}}blipFill/{{{A}}}blip').get(f'{{{RR}}}embed')
    target=next(r.get('Target') for r in rels if r.get('Id')==rid)
    assert target.startswith('/'+prefix+'/')
    out[target.lstrip('/')]=Path(o['path']).read_bytes()
panel_groups={}
maxid=max(int(n.get('id')) for n in tree.iter(f'{{{P}}}cNvPr'))
for panel in ['a','b','c']:
    maxid+=1
    group=E.Element(f'{{{P}}}grpSp')
    nv=E.SubElement(group,f'{{{P}}}nvGrpSpPr')
    group_names={'a':'Panel (a) - temporal map','b':'Panel (a) - source snapshots','c':'Panel (b) - conflict event and local tracks'}
    E.SubElement(nv,f'{{{P}}}cNvPr',id=str(maxid),name=group_names[panel])
    E.SubElement(nv,f'{{{P}}}cNvGrpSpPr');E.SubElement(nv,f'{{{P}}}nvPr')
    gp=E.SubElement(group,f'{{{P}}}grpSpPr');xf=E.SubElement(gp,f'{{{A}}}xfrm')
    for tag,attrs in [('off',dict(x='0',y='0')),('ext',dict(cx='12801600',cy='6096000')),('chOff',dict(x='0',y='0')),('chExt',dict(cx='12801600',cy='6096000'))]:
        E.SubElement(xf,f'{{{A}}}{tag}',attrs)
    panel_groups[panel]=group
for child in list(sp)[2:]:
    nv=next(child.iter(f'{{{P}}}cNvPr'),None)
    name=nv.get('name','') if nv is not None else ''
    panel='b' if name.startswith(('b_','ab_')) else 'c' if name.startswith(('c_','shared_')) else 'a'
    if not name.startswith(('a_','b_','ab_','c_','shared_')):
        off=next(child.iter(f'{{{A}}}off'),None)
        if off is not None and int(off.get('x','0'))>=1000*9525:panel='c'
    if name.startswith('rect_'):panel='b'
    sp.remove(child);panel_groups[panel].append(child)
for group in panel_groups.values():
    boxes=[]
    for child in list(group)[2:]:
        xf=next(child.iter(f'{{{A}}}xfrm'),None)
        if xf is None:continue
        off=xf.find(f'{{{A}}}off');ext=xf.find(f'{{{A}}}ext')
        if off is None or ext is None:continue
        x,y=int(off.get('x')),int(off.get('y'));w,h=int(ext.get('cx')),int(ext.get('cy'))
        boxes.append((x,y,x+w,y+h))
    if boxes:
        x=min(q[0] for q in boxes);y=min(q[1] for q in boxes)
        w=max(q[2] for q in boxes)-x;h=max(q[3] for q in boxes)-y
        xf=group.find(f'{{{P}}}grpSpPr/{{{A}}}xfrm')
        for tag,attrs in [('off',dict(x=str(x),y=str(y))),('ext',dict(cx=str(w),cy=str(h))),('chOff',dict(x=str(x),y=str(y))),('chExt',dict(cx=str(w),cy=str(h)))]:xf.find(f'{{{A}}}{tag}').attrib.update(attrs)
    sp.append(group)
out[canonical]=encode(tree)
with ZipFile(DEST,'w',ZIP_DEFLATED) as z:
    for name,contents in out.items():z.writestr(name,contents)

changed=[n for n in original if original[n]!=out[n]]
allowed={'ppt/slides/slide1.xml','ppt/slides/_rels/slide1.xml.rels','[Content_Types].xml'}
assert all(n in allowed or n.startswith('ppt/fig1_redesign/') for n in changed)
slide_count=len(E.fromstring(original['ppt/presentation.xml']).find(f'{{{P}}}sldIdLst'))
for t in range(2,slide_count+1):
    assert original[f'ppt/slides/slide{t}.xml']==out[f'ppt/slides/slide{t}.xml']
pres=E.fromstring(out['ppt/presentation.xml'])
assert len(pres.find(f'{{{P}}}sldIdLst'))==slide_count
report=dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    original_entry_count=len(original),original_entries_preserved=len(original)-len(changed),
    changed_original_parts=changed,added_parts=len(out)-len(original),
    slide_2_to_6_and_original_resources_byte_identical=True,
    slide_count=slide_count,groups=3,
    native_shapes=len(list(tree.iter(f'{{{P}}}sp'))),
    raster_data_layers=len(list(tree.iter(f'{{{P}}}pic'))))
(HERE/'evidence/fig1/package_preservation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
