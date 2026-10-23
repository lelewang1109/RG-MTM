"""Validate final render, preserve other slides, against the unchanged current source."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageChops
from pypdf import PdfReader
from pypdf.generic import ContentStream
import hashlib,json,subprocess

r=Path(__file__).resolve().parents[1]
BIN=Path('/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override')
source=r/'figures_ppt/All_Figures.pptx'
profile='-env:UserInstallation='+(r/'.build/fig1/lo_profile').as_uri()
subprocess.run([str(BIN/'soffice'),profile,'--headless','--convert-to','pdf','--outdir',str(r/'.build/fig1'),str(source)],check=True)
subprocess.run([str(BIN/'pdftoppm'),'-f','2','-l',str(len(PdfReader(r/'.build/fig1/All_Figures.pdf').pages)),'-r','100','-png',str(r/'.build/fig1/All_Figures.pdf'),str(r/'.build/fig1/source')],check=True)
subprocess.run([str(BIN/'pdftoppm'),'-f','2','-l',str(len(PdfReader(r/'.build/fig1/All_Figures.pdf').pages)),'-r','100','-png',str(r/'.build/fig1/All_Figures_Fig1_Revised.pdf'),str(r/'.build/fig1/revised')],check=True)
checks=[]
for t in range(2,len(PdfReader(r/'.build/fig1/All_Figures.pdf').pages)+1):
    a=Image.open(r/f'.build/fig1/source-{t}.png').convert('RGB')
    b=Image.open(r/f'.build/fig1/revised-{t}.png').convert('RGB')
    same=a.size==b.size and ImageChops.difference(a,b).getbbox() is None
    assert same
    checks.append(dict(slide=t,pixels_identical=True,size=a.size))
pdf=PdfReader(r/'.build/fig1/RG_MTM_Fig1_Revised.pdf');pg=pdf.pages[0]
ops=ContentStream(pg.get_contents(),pdf).operations
vector_ops=sum(op in [b'm',b'l',b'c',b're'] for args,op in ops)
text_ops=sum(op in [b'Tj',b'TJ'] for args,op in ops)
assert len(pdf.pages)==1 and vector_ops>50 and text_ops>30
report=dict(slides_after_first_render_comparison=checks,first_slide_pdf_pages=1,
    first_slide_vector_path_operations=vector_ops,first_slide_vector_text_operations=text_ops,
    first_slide_png=Image.open(r/'.build/fig1/RG_MTM_Fig1_Revised.png').size,
    native_powerpoint_execution=False,render_engine='LibreOffice Impress and Poppler',
    display_interpolation=json.loads((r/'evidence/fig1/data_provenance.json').read_text())['display_interpolation'])
provenance=json.loads((r/'evidence/fig1/data_provenance.json').read_text())
assert provenance['selected_event_frames']==[20,48,64,80,100]
assert [v['frame'] for v in provenance['snapshots']]==provenance['selected_event_frames']
report['five_snapshots_and_main_event_guides_agree']=True
assert len(provenance['event_annotations'])==5
assert [r['frame'] for r in provenance['event_annotations']]==[20,48,64,80,100]
assert provenance['selected_main_minimum_tracks']==[]
assert provenance['display_interpolation']['aligned_intervals']==93
assert len(provenance['display_interpolation']['fallback_intervals'])==24
report['event_callouts_on_saved_anchors']=True
report['dark_overlay_scope']='No main-panel trajectory overlays; scalar raster uses disclosed conservative anchor-aligned display reconstruction. Native A/B/C tracks remain in local panel.'
(r/'evidence/fig1/render_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
