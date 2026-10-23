"""Check actual figure fonts, lowercase panels, palette and asset synchronization.
Requires PyMuPDF (the project .venv provides pymupdf).
"""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E,json,hashlib,re
import pymupdf as fitz
R=Path(__file__).resolve().parents[1];N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
reg=json.loads((R/'FIGURE_INDEX.json').read_text());report=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
style=json.loads((R/'UNIFIED_FIGURE_STYLE.json').read_text())
records=reg['figures']+reg['supplementary_figures']
for item in records:
 ppt=R/item['ppt'];pdf=R/item['asset'];stem=item['stem']
 if item.get('pending_manuscript_sync'):assert sha(R/item['export'])==item['export_sha256']
 else:assert sha(pdf)==sha(R/'figures_export'/pdf.name)
 with ZipFile(ppt)as z:
  root=E.fromstring(z.read('ppt/slides/slide1.xml'))
  families={e.get('typeface')for k in ['latin','ea','cs','sym']for e in root.findall('.//a:'+k,N)}
  assert families=={'Arial'},(stem,families)
  assert not any(e.get('i')in ['1','true']for k in ['rPr','defRPr','endParaRPr']for e in root.findall('.//a:'+k,N))
  texts=[''.join(s.itertext())for s in root.findall('.//a:t',N)]
  joined=' '.join(texts);panels=re.findall(r'\(([a-z])\)',joined)
  assert not re.search(r'\([A-Z]\)|^[A-Z]  (?:TMTM|ST-MTM)$',joined),(stem,joined)
  if stem=='Fig3':assert all('('+c+')'in joined for c in 'abcde')
  for token in ['A_title','leaf_label_A','leaf_label_B','leaf_label_C']:
   if stem!='Fig4':break
   shapes=[s for s in root.findall('.//p:sp',N)if s.find('p:nvSpPr/p:cNvPr',N).get('name')==token]
   if token.startswith('leaf_label'):
    color=style.get('feature_label_color_overrides',{}).get(stem,{}).get(token[-1],{'A':'0072B2','B':'D55E00','C':'009E73'}[token[-1]]).lstrip('#')
    assert any(x.get('val')==color for x in shapes[0].findall('.//a:srgbClr',N))
 doc=fitz.open(pdf);assert len(doc)==1
 fonts={x[3].split('+')[-1]for x in doc[0].get_fonts()}
 assert fonts and fonts <= {'ArialMT','Arial-BoldMT'},(stem,fonts)
 report.append(dict(stem=stem,native_font_families=sorted(families),embedded_pdf_fonts=sorted(fonts),native_panel_labels=panels,ppt_sha256=sha(ppt),pdf_sha256=sha(pdf)))
for f in reg['figures']:
 assert sha(R/f['ppt'])==f['ppt_sha256']
 assert sha(R/f['asset'])==f['asset_sha256']
assert len(reg['figures'])==reg['main_figure_count'] and len(reg['supplementary_figures'])==reg['supplementary_figure_count']
out={'figures_checked':len(records),'all_actual_pdf_fonts_Arial_regular_or_bold':True,'all_native_text_Arial_without_italic':True,'main_and_supplement_assets_synchronized_except_declared_pending':True,'pending_manuscript_sync':[f['stem'] for f in records if f.get('pending_manuscript_sync')],'figures':report}
(R/'checks/unified_style_20261021.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(f'PASS: {len(records)} figure PDFs embed only Arial regular/bold; native text, numbering, identities and registered asset versions agree.')
