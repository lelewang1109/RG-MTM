"""Keep the original native figure objects, replace registered scalar rasters."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,xml.etree.ElementTree as E,hashlib

R=Path(__file__).resolve().parents[1];B=R/'.build/temporal_display20261023'
plans=json.loads((B/'plans.json').read_text())
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main'
for pre,uri in [('p',P),('a',A)]:E.register_namespace(pre,uri)
records={}
for stem,items in plans.items():
    with ZipFile(B/'before'/(stem+'.pptx'))as z:parts={n:z.read(n)for n in z.namelist()}
    # A native Artifact Tool deck authored these image layers in the original
    # axis rectangles. The full source rasters below retain their exact time
    # sample columns, independently of the generic authorer's raster resize.
    with ZipFile(B/'candidates'/(stem+'_layers.pptx'))as z:
        authored=E.fromstring(z.read('ppt/slides/slide1.xml'))
        assert len(list(authored.iter(f'{{{P}}}pic')))==len(items)
    changed=[]
    for item in items:
        p=item['part'];assert p in parts;parts[p]=Path(item['image']).read_bytes();changed.append(p)
        item['image_sha256']=hashlib.sha256(parts[p]).hexdigest()
    for name in list(parts):
        if name.startswith('ppt/notesSlides/notesSlide')and name.endswith('.xml'):
            tree=E.fromstring(parts[name]);placeholder=tree.find(f'.//{{{P}}}sp[{{{P}}}txBody]')
            for shape in tree.iter(f'{{{P}}}sp'):
                ph=shape.find(f'{{{P}}}nvSpPr/{{{P}}}nvPr/{{{P}}}ph')
                if ph is None or ph.get('type')!='body':continue
                body=shape.find(f'{{{P}}}txBody');para=E.SubElement(body,f'{{{A}}}p');run=E.SubElement(para,f'{{{A}}}r');E.SubElement(run,f'{{{A}}}t').text='Temporal display revision: intermediate time columns interpolate existing saved profiles for display only. Integer-frame profiles, native extrema and metrics are unchanged before pixel integration. Broad bands and true order changes remain visible. See evidence/temporal_display20261023/provenance.json.'
            parts[name]=E.tostring(tree,encoding='utf-8',xml_declaration=True);changed.append(name)
    with ZipFile(B/'candidates'/(stem+'.pptx'),'w',ZIP_DEFLATED)as z:
        for n,data in parts.items():z.writestr(n,data)
    records[stem]=dict(changed_package_parts=changed,registered_images=items,all_slide_object_xml_unchanged=True)
(B/'checks/assembly.json').write_text(json.dumps(records,indent=2)+'\n')
print('Replaced only planned scientific images and appended display provenance to speaker notes.')
