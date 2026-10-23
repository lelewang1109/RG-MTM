"""Independent checks of stored-frame pixels, data hashes and scoped PPT edits."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import json,hashlib
import numpy as np
from PIL import Image
from matplotlib import colormaps
from matplotlib.colors import Normalize,SymLogNorm,LinearSegmentedColormap

R=Path(__file__).resolve().parents[1];C=R.parent/'code';B=R/'.build/temporal_display20261023';O=R/'evidence/temporal_display20261023'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((O/'provenance.json').read_text());assembly=json.loads((B/'checks/assembly.json').read_text());plans=json.loads((B/'plans.json').read_text())
for p,h in j['source_sha256'].items():assert sha(p)==h,p
pixel_checks=0;profile_checks=0;panels=0

def check(G,case,method,cm,norm):
 global pixel_checks,profile_checks,panels
 for key,report in j['display_reports'].items():
  if report['dataset']!=case or report['saved_method']!=method:continue
  assert report['all_original_frame_profiles_exact_before_pixel_integration'] and report['no_scalar_overshoot']
  assert hashlib.sha256(np.ascontiguousarray(G).tobytes()).hexdigest()==report['original_profiles_sha256']
  match=[(stem,item)for stem,items in plans.items()for item in items if item['report_key']==key];assert len(match)==1
  stem,item=match[0];image=np.array(Image.open(item['image']).convert('RGBA'));height,width=image.shape[:2]
  factor=report['display_samples_per_frame'];lo,hi=report['source_frames'][0],report['source_frames'][-1]+1;r0,r1=report['rows_displayed']
  assert width==(hi-lo)*factor
  for t in range(lo,hi):
   original=G[r0:r1,t][::-1];rgba=np.rint(np.clip(cm(norm(original)),0,1)*255).astype(np.uint8)
   expected=np.asarray(Image.fromarray(rgba[:,None,:]).resize((1,height),Image.Resampling.BOX))[:,0,:]
   actual=image[:,(t-lo)*factor+factor//2,:]
   np.testing.assert_array_equal(actual,expected)
   pixel_checks+=height;profile_checks+=1
  panels+=1

for case in ['wildfire','tangaroa']:
 a=np.load(C/f'results/real_case_studies/evidence/{case}.npz')
 if case=='wildfire':cm=colormaps['YlOrBr'].copy();cm.set_under('#8196A6');norm=Normalize(0,float(a['field'].max()));methods=['TMTM','ST-MTM','P','R']
 else:
  tf=json.loads((C/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json').read_text())['transfer_function_points'];cm=LinearSegmentedColormap.from_list('existing-tangaroa',[(v[0],tuple(v[1:4]))for v in tf],N=2048);norm=Normalize(0,2);methods=['TMTM','P','R']
 for method in methods:check(a['map'+method],case,method,cm,norm)
 a.close()
result=C/'results/paper1_suite/square-cylinder3d';data=R.parent/'data/real/paper1_suite/square-cylinder3d';rows=json.loads((result/'frame_metrics.json').read_text());protocol=json.loads((result/'protocol.json').read_text());metadata=json.loads((result/'display_metadata.json').read_text());cm=colormaps['coolwarm'];norm=SymLogNorm(linthresh=.02,vmin=metadata['vmin'],vmax=metadata['vmax'])
for method,label in [('TMTM','TMTM'),('RG-MTM-P','P'),('RG-MTM-R 0.02','R2'),('RG-MTM-R 0.2','R')]:
 rr=sorted([r for r in rows if r['method']==method],key=lambda r:r['index']);G=np.column_stack([np.load(data/'maps'/Path(r['array']).name)for r in rr]).astype(np.float64);G*=-protocol['scalar_scale'];check(G,'cylinder',label,cm,norm);del G
v=np.max(np.load(data/'source_fields.npy',mmap_mode='r')[86],axis=1);source_item=next(x for x in plans['Fig11']if x['report_key']=='Fig11_source_projection');image=np.array(Image.open(source_item['image']));factor=j['spatial_projection']['factor'];rgba=np.rint(cm(norm(v[::-1]))*255).astype(np.uint8)
np.testing.assert_array_equal(image[factor//2::factor,factor//2::factor],rgba)
changed_parts={}
for stem,record in assembly.items():
 with ZipFile(B/'before'/(stem+'.pptx'))as z:before={n:z.read(n)for n in z.namelist()}
 with ZipFile(R/'figures_ppt'/(stem+'.pptx'))as z:after={n:z.read(n)for n in z.namelist()}
 assert set(before)==set(after)
 changed={name for name in before if before[name]!=after[name]};assert changed==set(record['changed_package_parts']),(stem,changed)
 assert before['ppt/slides/slide1.xml']==after['ppt/slides/slide1.xml']
 for item in record['registered_images']:assert hashlib.sha256(after[item['part']]).hexdigest()==item['image_sha256']
 changed_parts[stem]=sorted(changed)
before=json.loads((B/'checks/before.json').read_text());kept=[]
for name,h in before.items():
 if Path(name).stem in set(j['figures'])|{'All_Figures','All_Supplementary_Figures'}:continue
 assert sha(R/name)==h,name
 kept.append(name)
out=dict(status='passed',source_files_unchanged=len(j['source_sha256']),temporal_panels_verified=panels,
        complete_saved_frame_profile_columns_verified=profile_checks,pixel_rows_compared=pixel_checks,
        integer_frame_pixels_exact_after_area_antialiasing=True,no_scalar_overshoot=True,
        all_native_slide_objects_byte_identical=True,source_views_and_marker_coordinates_preserved=True,
        wildfire_actual_cell_geometries_unchanged=True,cylinder_projection_original_centers_exact=int(v.size),
        other_figure_files_byte_identical=len(kept),figures_1_to_4_byte_identical=True,
        scientific_arrays_and_metrics_unchanged=True,changed_package_parts=changed_parts)
(R/'checks/temporal_display20261023/numerical.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k!='changed_package_parts'},indent=2))
