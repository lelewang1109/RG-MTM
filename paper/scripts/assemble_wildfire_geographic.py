"""Keep the previous editable (a,b) objects and replace only (c,d,e)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import xml.etree.ElementTree as E
import posixpath, json

R = Path(__file__).resolve().parents[1]
B = R / '.build/wildfire_geo20261023'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
RR = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
for p, u in [('p', P), ('a', A), ('r', RR)]:
    E.register_namespace(p, u)
enc = lambda e: E.tostring(e, encoding='utf-8', xml_declaration=True)
with ZipFile(B/'before/Fig7.pptx') as z:
    old = {n:z.read(n) for n in z.namelist()}
with ZipFile(B/'candidates/Fig7_geographic.pptx') as z:
    out = {n:z.read(n) for n in z.namelist()}
old_tree = E.fromstring(old['ppt/slides/slide1.xml'])
tree = E.fromstring(out['ppt/slides/slide1.xml'])
sp = tree.find(f'{{{P}}}cSld/{{{P}}}spTree')
old_sp = old_tree.find(f'{{{P}}}cSld/{{{P}}}spTree')
rels = E.fromstring(out['ppt/slides/_rels/slide1.xml.rels'])
old_rels = {e.get('Id'):e for e in E.fromstring(old['ppt/slides/_rels/slide1.xml.rels'])}
id_count = max(int(e.get('id')) for e in tree.iter(f'{{{P}}}cNvPr'))
rid_count = 50000
remapped = {}
kept = []
for original in list(old_sp)[2:]:
    off = original.find(f'.//{{{A}}}xfrm/{{{A}}}off')
    if off is None or int(off.get('y')) >= 230*9525:
        continue
    el = deepcopy(original)
    for obj in el.iter():
        if obj.tag == f'{{{P}}}cNvPr':
            id_count += 1
            obj.set('id', str(id_count))
        for key in list(obj.attrib):
            if not key.startswith('{'+RR+'}'):
                continue
            rid = obj.get(key)
            if rid not in remapped:
                rel = deepcopy(old_rels[rid])
                assert rel.get('Type').endswith('/image'), rel.attrib
                rid_count += 1
                new_rid = 'rId'+str(rid_count)
                target = rel.get('Target')
                src = posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'ppt/slides/'+target)
                dest = 'ppt/media/preserved_top_'+str(rid_count)+Path(src).suffix
                out[dest] = old[src]
                rel.set('Id', new_rid)
                rel.set('Target', '/'+dest)
                rels.append(rel)
                remapped[rid] = new_rid
            obj.set(key, remapped[rid])
    sp.append(el)
    kept.append(original.find(f'.//{{{P}}}cNvPr').get('name'))
out['ppt/slides/slide1.xml'] = enc(tree)
E.register_namespace('', REL)
out['ppt/slides/_rels/slide1.xml.rels'] = enc(rels)
types = E.fromstring(out['[Content_Types].xml'])
for item in E.fromstring(old['[Content_Types].xml']):
    if item.tag.endswith('Default') and not any(x.get('Extension') == item.get('Extension') for x in types):
        types.append(deepcopy(item))
E.register_namespace('', CT)
out['[Content_Types].xml'] = enc(types)
with ZipFile(B/'candidates/Fig7.pptx', 'w', ZIP_DEFLATED) as z:
    for n, v in out.items():
        z.writestr(n, v)
(B/'checks/preserved_top_objects.json').write_text(json.dumps(dict(objects=kept, count=len(kept), semantics='Original objects, coordinates, colors, scalar raster bytes and text preserved; only package IDs remapped.'), indent=2)+'\n')
print('Retained native objects from original panels (a,b):', len(kept))
