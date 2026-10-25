"""Package the current LaTeX source and refresh the current-file manifest.
No historical snapshots or full-folder ZIP copies are produced.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];L=R/'manuscript/latex'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'manuscript/RG-MTM_LaTeX.zip'
excluded={'.log','.blg','.aux','.brf','.out','.toc','.fls','.fdb_latexmk'}
with ZipFile(source,'w',ZIP_DEFLATED) as z:
 for p in sorted(L.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts and 'revision_docs' not in p.relative_to(L).parts and p.suffix not in excluded and p.name not in ['main.pdf','supplement.pdf','.DS_Store']:
   z.write(p,str(p.relative_to(L)))
 for name in ['MANUSCRIPT_OUTLINE.md','COMPREHENSIVE_REVIEW.md','OLD_BASE_REVISION.md','COLOR_AND_DISPLAY_POLICY.md']:
  if (R/name).exists():z.write(R/name,'revision_docs/'+name)
with ZipFile(source) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist())),'Duplicate ZIP entries'
files={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and not any(x in p.relative_to(R).parts for x in ['.build','.validated','__pycache__']) and p.name!='DELIVERY_MANIFEST.json' and p.suffix not in excluded}
catalog=json.loads((R/'FIGURE_INDEX.json').read_text()) if (R/'FIGURE_INDEX.json').exists() else None
prior_added=(R/'checks/prior_work_overview_20261020.json').exists()
dendrogram_added=(L/'figures/dendrogram_transfer.tex').exists()
(R/'DELIVERY_MANIFEST.json').write_text(json.dumps(dict(date=datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat(),main_figures=catalog['main_figure_count'] if catalog else (8 if prior_added else 7)+int(dendrogram_added),editable_deck_slides=len(catalog['figures']) if catalog else 7 if prior_added else 6,canonical_deck='figures_ppt/All_Figures.pptx',source_result_files_changed='new unified20261025 common-QP and framework20261025 frontier results; historical numerical evidence retained',files=files),ensure_ascii=False,indent=2)+'\n')
print('Current LaTeX package:',source,'; manifest:',len(files),'files')
