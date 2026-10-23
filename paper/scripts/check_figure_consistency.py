"""Read-only checks of the main paper's numbered figure/PPT contract."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import hashlib,json,re,posixpath
R=Path(__file__).resolve().parents[1]
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reg=json.loads((R/'FIGURE_INDEX.json').read_text());count=reg['main_figure_count'];assert [f['number']for f in reg['figures']]==list(range(1,count+1))
with ZipFile(R/reg['combined_ppt'])as z:
 pr=E.fromstring(z.read('ppt/presentation.xml'));ids=pr.find(f'{{{P}}}sldIdLst');assert len(ids)==count
 rels={e.get('Id'):e.get('Target')for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 for f,sid in zip(reg['figures'],ids):
  n=f['number'];stem=f'Fig{n}';ppt=R/f['ppt'];asset=R/f['asset'];export=R/f['export'];tex=R/'manuscript/latex'/f['latex_source']
  assert ppt.name==stem+'.pptx' and asset.stem==stem and export.name==asset.name
  assert asset.exists() and export.exists() and sha(asset)==f['asset_sha256']
  if f.get('pending_manuscript_sync'):assert sha(export)==f['export_sha256']
  else:assert sha(asset)==sha(export)
  assert sha(ppt)==f['ppt_sha256']
  assert '{figures/'+asset.name+'}'in tex.read_text(),tex
  assert f['label']in tex.read_text(),f['label']
  with ZipFile(ppt)as one:
   assert one.testzip()is None
   p=E.fromstring(one.read('ppt/presentation.xml'));assert len(p.find(f'{{{P}}}sldIdLst'))==1
   if 'embedded_original_sha256' in f:
    ext=Path(f['embedded_original_asset']).suffix
    media=[one.read(x) for x in one.namelist() if x.startswith('ppt/media/') and x.endswith(ext)]
    assert any(hashlib.sha256(x).hexdigest()==f['embedded_original_sha256'] for x in media),n
  target=rels[sid.get(f'{{{RR}}}id')];part=posixpath.normpath(target.lstrip('/')if target.startswith('/')else'ppt/'+target);tree=E.fromstring(z.read(part));names=[e.get('name','')for e in tree.iter(f'{{{P}}}cNvPr')]
  assert any(x.startswith(f'Manuscript Figure {n}:')for x in names),(n,part)
 assert z.testzip()is None
for old in ['Fig1_Corrected','Prior_Work_Overview','Fig5_Selected_Frontier','bisector_three_methods_selected','Dendrogram_Transfer']:
 for f in reg['figures']:assert old not in (R/'manuscript/latex'/f['latex_source']).read_text()
assert '\\begin{figure}[t]'in(R/'manuscript/latex/figures/filling.tex').read_text()
assert '\\linewidth'in(R/'manuscript/latex/figures/filling.tex').read_text()
assert (R/'manuscript/latex/figures/Supplement_PositionScalarDiagnostic.pdf').exists()
assert 'Supplement_PositionScalarDiagnostic.pdf'in(R/'manuscript/latex/revision_evidence_supplement.tex').read_text()
print(f'PASS: {count} paper figures = Fig1–Fig{count} PPTs/assets = combined slides 1–{count}; hashes and LaTeX references agree.')
