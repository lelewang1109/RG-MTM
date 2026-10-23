"""Independently verify provenance, displayed geometry and preserved evidence."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import json, hashlib, posixpath
import numpy as np
from scipy.ndimage import gaussian_filter

R=Path(__file__).resolve().parents[1]; B=R/'.build/wildfire_geo20261023'
O=R/'evidence/wildfire_geo20261023'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((O/'geographic_provenance.json').read_text())
for p,h in j['source_sha256'].items():assert sha(p)==h,p
source=R.parent/'data/real/wildfire/wildfire.json'
d=json.loads(source.read_text());cells=[c for top in d['data'] for c in top.get('children',[])]
i=d['timeseries']['series'].index('2019-11-01')
v=np.array([c['data'][i:i+60]for c in cells],float).reshape(len(cells),30,2).sum(-1)
active=v.sum(1)>0;lat=np.array([c['lat']for c in cells],float);lon=np.array([c['lng']for c in cells],float)
co=np.cos(np.deg2rad(lat[active].mean()));x=lon*co*111.32;y=lat*110.57
side=max(np.ptp(x[active]),np.ptp(y[active]))*1.02
x0=(x[active].max()+x[active].min()-side)/2;y0=(y[active].max()+y[active].min()-side)/2
ix=np.clip(((x-x0)/side*64).astype(int),0,63);iy=np.clip(((y-y0)/side*64).astype(int),0,63)
raw=np.zeros((30,64,64))
for k in np.where(active)[0]:raw[:,iy[k],ix[k]]+=v[k]
log=np.log1p(raw);a=np.load(R.parent/'code/results/real_case_studies/evidence/wildfire.npz')
np.testing.assert_array_equal(log,a['raw_field'])
processed=np.array([gaussian_filter(f,2.5)for f in log]);bg=np.array([gaussian_filter(f,16,truncate=50)for f in log]);processed+=1e-3*np.ptp(processed)*bg/bg.max()
np.testing.assert_allclose(processed,a['field'],atol=1e-15,rtol=1e-15)
subset=np.load(O/'display_source_subset.npz')
np.testing.assert_array_equal(subset['source_two_date_FRP'],v[:,j['frames']].T)
np.testing.assert_array_equal(subset['raw_grid'],log[j['frames']])
np.testing.assert_array_equal(subset['analysis'],a['field'][j['frames']])
np.testing.assert_array_equal(subset['cell_lonlat_polygons'],np.array([[c['area'][key]for key in ['point_bl','point_br','point_tr','point_tl']]for c in cells],float))
for marker in j['markers']:
 t=marker['frame'];jj=int(np.flatnonzero(a['track'][t]==marker['track'])[0]);p=a['xy'][t,jj]
 np.testing.assert_array_equal(marker['layout_xy'],p)
 lo,la=marker['lonlat'];np.testing.assert_allclose([(lo*co*111.32-x0)/side*120,(la*110.57-y0)/side*120],p,atol=1e-11)
for frame,native,binned in [(17,283,141),(18,221,120),(19,206,111)]:
 assert (v[:,frame]>0).sum()==native
 assert (log[frame]>0).sum()==binned
for row in j['pairs']:
 indices=[int(np.flatnonzero(a['track'][18]==j['tracks']['ABC'.index(k)])[0])for k in row['pair']]
 for method in ['P','R']:
  ar=a['map'+method][:,18];l,h=sorted(np.rint(a['norm'+method][18,indices]*(len(ar)-1)).astype(int));assert float(ar[l:h+1].min())==row[method]
 assert row['source']==row['P']
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def panel_objects(path,normalize_temporal_images=False):
 with ZipFile(path)as z:
  tree=E.fromstring(z.read('ppt/slides/slide1.xml'));sp=tree.find(f'{{{P}}}cSld/{{{P}}}spTree');rels={r.get('Id'):r.get('Target')for r in E.fromstring(z.read('ppt/slides/_rels/slide1.xml.rels'))};out=[]
  for el in list(sp)[2:]:
   off=el.find(f'.//{{{A}}}xfrm/{{{A}}}off')
   if off is None or int(off.get('y'))>=230*9525:continue
   for obj in el.iter():
    if obj.tag==f'{{{P}}}cNvPr':obj.set('id','normalized')
    for key in list(obj.attrib):
     if key.startswith('{'+RR+'}'):
      target=rels[obj.get(key)];p=posixpath.normpath(target.lstrip('/')if target.startswith('/')else'ppt/slides/'+target);obj.set(key,'temporal-image-checked-separately'if normalize_temporal_images else hashlib.sha256(z.read(p)).hexdigest())
   out.append(E.tostring(el))
  return out
temporal=R/'checks/temporal_display20261023/numerical.json'
later=set()
if temporal.exists():
 revision=json.loads(temporal.read_text());assert revision['status']=='passed' and revision['all_native_slide_objects_byte_identical']
 later=set(revision['changed_package_parts'])|{'All_Supplementary_Figures'}
assert panel_objects(B/'before/Fig7.pptx',bool(later))==panel_objects(R/'figures_ppt/Fig7.pptx',bool(later))
before=json.loads((B/'checks/before.json').read_text());preserved=[]
for name,h in before.items():
 if Path(name).name.startswith('Fig7.')or Path(name).name=='All_Figures.pptx'or Path(name).stem in later:continue
 assert sha(R/name)==h,name
 preserved.append(name)
out=dict(status='passed',source_hashes_verified=True,source_aggregation_exact=True,analysis_input_unchanged=True,native_polygons_exact=True,positive_native_cells=[283,221,206],positive_binned_cells=[141,120,111],marker_projections_verified=len(j['markers']),profiles_and_pair_levels_unchanged=True,original_panels_a_b_preserved_objects=len(panel_objects(R/'figures_ppt/Fig7.pptx')),other_figure_files_byte_identical=len(preserved),interpretation='Detected FRP cell records and declared smoothed analysis field are distinct. No burn perimeter inferred.')
p=R/'checks/wildfire_geo20261023/numerical.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
