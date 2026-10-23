"""Bilinear display of the existing source Q projection; no field smoothing."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,posixpath,xml.etree.ElementTree as E
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import SymLogNorm
from PIL import Image

R=Path(__file__).resolve().parents[1];B=R/'.build/temporal_display20261023';O=R/'evidence/temporal_display20261023'
p=R.parent/'data/real/paper1_suite/square-cylinder3d/source_fields.npy'
v=np.max(np.load(p,mmap_mode='r')[86],axis=1)
factor=9;ny,nx=v.shape;x=np.clip((np.arange(nx*factor)+.5)/factor-.5,0,nx-1);y=np.clip((np.arange(ny*factor)+.5)/factor-.5,0,ny-1)
tmp=np.array([np.interp(x,np.arange(nx),row)for row in v]);dense=np.array([np.interp(y,np.arange(ny),col)for col in tmp.T]).T
np.testing.assert_array_equal(dense[factor//2::factor,factor//2::factor],v)
assert dense.min()>=v.min() and dense.max()<=v.max()
metadata=json.loads((R.parent/'code/results/paper1_suite/square-cylinder3d/display_metadata.json').read_text());cm=colormaps['coolwarm'];norm=SymLogNorm(linthresh=.02,vmin=metadata['vmin'],vmax=metadata['vmax'])
image=B/'assets/Fig11_source_projection_bilinear.png';Image.fromarray(np.rint(cm(norm(dense[::-1]))*255).astype(np.uint8)).save(image)
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
with ZipFile(B/'before/Fig11.pptx')as z:
 tree=E.fromstring(z.read('ppt/slides/slide1.xml'));rels={r.get('Id'):r.get('Target')for r in E.fromstring(z.read('ppt/slides/_rels/slide1.xml.rels'))}
 for pic in tree.iter(f'{{{P}}}pic'):
  if pic.find(f'{{{P}}}nvPicPr/{{{P}}}cNvPr').get('name')!='Cylinder_original_grid_max_y_Q':continue
  xf=pic.find(f'{{{P}}}spPr/{{{A}}}xfrm');off=xf.find(f'{{{A}}}off');ext=xf.find(f'{{{A}}}ext');target=rels[pic.find(f'.//{{{A}}}blip').get(f'{{{RR}}}embed')];part=posixpath.normpath(target.lstrip('/')if target.startswith('/')else'ppt/slides/'+target)
  item=dict(part=part,x=int(off.get('x'))/9525,y=int(off.get('y'))/9525,w=int(ext.get('cx'))/9525,h=int(ext.get('cy'))/9525,image=str(image),report_key='Fig11_source_projection')
  break
 else:raise AssertionError('Existing source projection not found')
plans=json.loads((B/'plans.json').read_text());plans['Fig11']=[x for x in plans['Fig11']if x['report_key']!=item['report_key']]+[item];(B/'plans.json').write_text(json.dumps(plans,indent=2)+'\n')
sc=B/'scenes/Fig11_layers.json';s=json.loads(sc.read_text());s['objects']=[x for x in s['objects']if x['name']!=item['report_key']]+[dict(kind='image',name=item['report_key'],path=str(image),x=item['x'],y=item['y'],w=item['w'],h=item['h'])];sc.write_text(json.dumps(s,indent=2)+'\n')
j=json.loads((O/'provenance.json').read_text());j['source_sha256'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();j['spatial_projection']=dict(frame=86,method='separable bilinear display reconstruction',source_shape=[ny,nx],factor=factor,original_cell_centers_exact=True,no_scalar_overshoot=True,source_range=[float(v.min()),float(v.max())],source_field_smoothing_added=False);(O/'provenance.json').write_text(json.dumps(j,indent=2)+'\n')
print('Bilinear source projection retains all',v.size,'original cell-center values exactly.')
