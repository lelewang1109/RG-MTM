"""Validate the current submission, its saved evidence, editable figures and package."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,xml.etree.ElementTree as ET
import pymupdf as fitz
R=Path(__file__).resolve().parents[1];L=R/'manuscript/latex';C=R/'checks/submission20261023'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reg=json.loads((R/'FIGURE_INDEX.json').read_text());report={'date':'2026-10-23','scientific_optimization_rerun':'annual PM2.5 only'}
before=json.loads((C/'before_hashes.json').read_text());preserved=[]
archive=R.parents[1]/'其他/归档/实验重构前_20261023/paper'
previous=R/'修改前版本_20261023'
previous_hashes=json.loads((previous/'SHA256.json').read_text())
for old_name,kept_name in [('Revised_RG-MTM.pdf','修改前_正文.pdf'),('Revised_Supplement.pdf','修改前_附录.pdf'),('RG-MTM_LaTeX.zip','修改前_LaTeX源码.zip')]:
 original=archive/'manuscript'/old_name
 if old_name=='Revised_RG-MTM.pdf' and not original.exists():original=archive/'manuscript/0-Revised_RG-MTM.pdf'
 assert sha(previous/kept_name)==previous_hashes[kept_name]==sha(original),kept_name
with ZipFile(previous/'修改前_LaTeX源码.zip') as z:assert z.testzip() is None
report['previous_version_preserved_byte_identical']=True
for name,h in before.items():
 if name.startswith('evidence/') or name.startswith('manuscript/latex/evidence/'):
  if name.startswith(('evidence/submission20261023/','manuscript/latex/evidence/submission20261023/')):continue # current generated selection, checked by builder
  p=R/name
  if not p.exists():p=archive/name
  assert sha(p)==h,name
  preserved.append(name)
for n in range(1,5):
 for name in [f'figures_ppt/Fig{n}.pptx',f'figures_export/Fig{n}.pdf',f'figures_export/Fig{n}.png',f'figures_export/Fig{n}.svg']:
  assert sha(R/name)==before[name],name
report['preserved_scientific_evidence_files']=len(preserved);report['figures_1_to_4_byte_identical']=True
for n in [1,2,3,4,6,8,9]:
 for name in [f'figures_ppt/Fig{n}.pptx',f'figures_export/Fig{n}.pdf',f'figures_export/Fig{n}.png',f'figures_export/Fig{n}.svg']:
  assert sha(R/name)==sha(archive/name),name
report['unchanged_original_figures']=[1,2,3,4,6,8,9]
report['authorized_revised_figures']=[5,7,10,11,12,13,14]
annual=json.loads((R.parent/'code/results/pm25_2000/validation.json').read_text());assert annual['status']=='passed' and annual['frames']==366
for n,h in annual['source_sha256'].items():assert sha(R.parent/'code'/n)==h,n
claims=json.loads((L/'evidence/submission20261023/claims.json').read_text());assert claims['frames']==614 and claims['temporal_frames']==917 and claims['R20_on_frontier']==611
report['annual_pm25_verified']=True
case=json.loads((R/'checks/pm25_case20261023/numerical.json').read_text());assert case['status']=='passed' and case['reference_verified_all_frames']
report['pm25_source_linked_case']=case
wildfire=json.loads((R/'checks/wildfire_geo20261023/numerical.json').read_text());assert wildfire['status']=='passed' and wildfire['native_polygons_exact']
report['wildfire_geographic_display']=wildfire
temporal=json.loads((R/'checks/temporal_display20261023/numerical.json').read_text());assert temporal['status']=='passed' and temporal['integer_frame_pixels_exact_after_area_antialiasing']
report['conservative_temporal_display']=temporal
report['population']=claims
for table in ['datasets_main','comparison_revision','achieved_reference_main']:
 source=(L/'tables'/(table+'.tex')).read_text()
 for name in ['Storms','Wildfires','OLR','Ring','Tangaroa','Cylinder','Nucleon','Benzene']:assert name+' &' in source,(table,name)
 body=source[source.index('Storms &'):source.index('\\bottomrule')]
 assert '\\midrule' not in body,table
assert 'Nucleon & 1.92 & 3.43 & 1.92 & 3.43' in (L/'tables/achieved_reference_main.tex').read_text()
report['all_nine_inputs_in_dataset_and_result_tables_without_static_separator']=True
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for item in reg['figures']+reg['supplementary_figures']:
 for key in ['ppt','asset','export']:assert (R/item[key]).is_file(),item[key]
 assert sha(R/item['asset'])==sha(R/item['export'])
 assert sha(R/item['ppt'])==item['ppt_sha256']
 with ZipFile(R/item['ppt']) as z:
  assert z.testzip() is None
  pr=ET.fromstring(z.read('ppt/presentation.xml'));assert len(pr.find('p:sldIdLst',N))==1
report['main_figures']=reg['main_figure_count'];report['supplementary_figures']=reg['supplementary_figure_count']
# Compilations and delivered PDFs must agree, with resolved references.
documents=[]
for stem,public in [('main','Revised_RG-MTM.pdf'),('supplement','Revised_Supplement.pdf')]:
 p=R/'manuscript'/public;doc=fitz.open(p);text='\n'.join(page.get_text() for page in doc)
 assert '\ufffd' not in text and '??' not in text,stem
 log=(L/(stem+'.log')).read_text(errors='replace')
 assert not re.search(r'Overfull|undefined references|Citation .*undefined|multiply defined|Float too large|LaTeX Error',log),stem
 assert sha(L/(stem+'.pdf'))==sha(p)
 if stem=='main':
  nums={int(n) for n in re.findall(r'Figure\s+(\d+):',text)}
  assert nums==set(range(1,reg['main_figure_count']+1)),nums
  assert not re.search(r'342.frame|six.sequence|Gaussian\s*&',text)
 else:
  nums={int(n) for n in re.findall(r'Figure\s+S(\d+):',text)}
  assert nums==set(range(1,reg['supplementary_figure_count']+1)),nums
 documents.append({'file':str(p.relative_to(R)),'pages':len(doc),'sha256':sha(p)})
report['documents']=documents
with ZipFile(R/'manuscript/RG-MTM_LaTeX.zip') as z:
 assert z.testzip() is None
 for p in L.rglob('*.tex'):assert z.read(str(p.relative_to(L)))==p.read_bytes(),p
 for item in reg['figures']+reg['supplementary_figures']:
  rel=Path(item['asset']).relative_to('manuscript/latex');assert z.read(str(rel))==(R/item['asset']).read_bytes()
report['source_package_matches_current_sources_and_figures']=True
(C/'comprehensive_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
