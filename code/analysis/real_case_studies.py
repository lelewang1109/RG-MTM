"""Linked real-data case figures, without changing scientific methods or saved results.

Run from repository: PYTHONPATH=src:analysis:. python analysis/real_case_studies.py --prepare
Then omit --prepare for a raw-data-free redraw; --verify checks frozen evidence.
"""
from pathlib import Path
from itertools import combinations
import argparse, hashlib, json, sys, csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'analysis'),str(ROOT/'src')]
OUT=ROOT/'results/real_case_studies'; DATA=OUT/'evidence'
TANG=ROOT/'results/volume3d/tangaroa-paper-p10-full201'
METHODS=['TMTM','ST-MTM','P','R']; LABELS={'P':'RG-MTM-P','R':'RG-MTM-R ($\\kappa=20\\%$)','TMTM':'TMTM','ST-MTM':'ST-MTM (reimplementation)'}
COLORS=['#0072b2','#d55e00','#009e73']; MARKS=['o','s','^']
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item())+'\n')
def padded(seq,width=None,fill=np.nan):
 width=width or max(map(len,seq));a=np.full((len(seq),width),fill)
 for t,x in enumerate(seq):a[t,:len(x)]=x
 return a

def witness(fr,ids,q):
 import relax_hierarchy as rh, theory as th
 nodes,_=th.struct_nodes(rh.node_tree(fr,ids));best=0.;arg=None
 for v,parent,leaves in nodes:
  if parent is None:continue
  outside=set(range(len(ids)))-set(leaves)
  for i in leaves:
   for j in leaves:
    for k in outside:
     if q[i]<q[k]<q[j]:
      b=min(q[k]-q[i],q[j]-q[k])/2
      if b>best:best=b;arg=(i,j,k)
 return best,arg

def prepare2d(name):
 import replicate as rp, general_method as gm, relax_hierarchy as rh, filling as fl
 from experiments import era5 as ep

 print('Reading actual input:',name,flush=True)
 ds=rp.LOADERS[name]();sc=ds['sc'];T=len(sc['ids']);N=max(map(len,sc['ids']))
 cache=ROOT/f'results/publication2027/figure_data/{name}_render.npz'
 a=dict(field=np.asarray(sc['fields']),coords=sc['coords'],track=padded(sc['tracks'],fill=-1).astype(int),leaf=padded(sc['ids'],fill=-1).astype(int),dates=np.array(sc['dates']))
 a['xy']=np.full((T,N,2),np.nan);a['value']=np.full((T,N),np.nan);a['witness']=np.full((T,3),-1,int)
 trees=[]
 for t,(fr,ids) in enumerate(zip(sc['frames'],sc['ids'])):
  a['xy'][t,:len(ids)]=[fr.coordinates[i] for i in ids];a['value'][t,:len(ids)]=[fr.values[i] for i in ids]
  trees.append(dict(root=int(fr.root),children={str(k):list(v) for k,v in fr.children.items()},values={str(k):float(fr.values[k]) for k in fr.children},matches={str(k):int(v) for k,v in sc['matches'][t].items()},tracking=[v for v in sc['tracking'] if v['t']==t]))
 if cache.exists():
  z=np.load(cache);meta=read(cache.with_suffix('.json'));assert sha(cache)==meta['arrays_sha256']
  assert np.allclose(sc.get('fields_smooth',sc['fields']),z['field']);assert np.array_equal(a['track'],z['track']);assert np.allclose(a['xy'],z['xy'],equal_nan=True)
  for key in ['q','geometry','direction','H','F','delta']:a[key]=z[key]
  a['mapP']=z['mapA'];a['mapR']=z['mapR'];a['uP']=z['uA'];a['uR']=z['uR'];a['witness']=z['witness']
  p=gm.universal_parameters(*a['geometry'],ds['domain_area']);relaxlog=None
  print('Reusing frozen reference maps',flush=True)
 else:
  print('Exporting existing deterministic figure pipeline (this dataset only)',flush=True)
  r=rh.run(ds,.2,make_figure=False,return_internal=True);I=r['_internal'];p=I['p'];ref=I['ref'];relaxlog=r['frame_log']
  a.update(q=padded(ref['qs']),geometry=np.array([p.canvas_origin,p.canvas]),direction=np.array(ref['candidates']['direction']['a']),H=np.array([x['tau_hier']-x['tau_free'] for x in r['frame_log']]),F=np.array([x['tau_free'] for x in r['frame_log']]))
  for key,mode in [('A_full_hierarchy','P'),('R_relaxed','R')]:
   rows=I['results'][key]['_rows'];mat,sk,_=rh.render(sc,rows,p,ds['nominal']);mat=mat.astype(float);delta=[]
   for t,(fr,s) in enumerate(zip(sc['frames'],sk)):
    if mode=='R':mat[:,t],d=fl.optimal_fill(mat[:,t],list(s.ordering),s.anchors,fr,sc['trees'][0].kind);delta.append(d)
   a['map'+mode]=mat;a['u'+mode]=padded([x['x'] for x in rows])
   if mode=='R':a['delta']=np.array(delta)
  for t,ids in enumerate(sc['ids']):
   _,w=witness(sc['frames'][t],ids,a['q'][t,:len(ids)])
   if w:a['witness'][t]=w
 for mode in ['P','R']:
  a['norm'+mode]=(a['u'+mode]-a['geometry'][0])/a['geometry'][1]
 # Recover actual pixel domains. Do not normalize ST extrema to an occupied range.
 span=ds['native_span'];px=gm.Parameters(canvas=span,canvas_origin=float(min(ds['lo'][0],0.)),width_scale=.5*span/ds['domain_area'],gap=span/240,extra_budget=span/120,rho=.5)
 for mode in ['TMTM','ST-MTM']:
  print('Rendering unchanged baseline:',name,mode,flush=True)
  b=ep.run_method(sc,mode,px,canvas=span,length=ds['nominal'],refine_raster=False,strict_checks=False)
  a['map'+mode]=b['maps'];a['u'+mode]=padded([r['pixel_x'] for r in b['rows']])
  if mode=='TMTM':
   a['norm'+mode]=(a['u'+mode]-b['gauge']['shift'])/b['gauge']['scale']/span
   if b['gauge']['scale']<0:a['norm'+mode]=1-a['norm'+mode]
  else:
   cert=b['records']
   # Discrete anchors are stored in ordering order; map to shared leaf order.
   a['norm'+mode]=padded([[s['anchors'][list(s['ordering']).index(leaf)]/(b['maps'].shape[0]-1) for leaf in ids] for s,ids in zip(cert['discrete'],sc['ids'])])
   if b['gauge']['scale']<0:a['norm'+mode]=1-a['norm'+mode]
 a['qnorm']=(a['q']-a['geometry'][0])/a['geometry'][1]
 expected=read(ROOT/'results/eval_projection.json')[name]['dstar']['R 20%'];rng=float(np.ptp(a['field']))
 assert np.isclose(a['delta'].mean()/rng,expected['mean_share'],atol=2e-5)
 assert np.isclose(a['delta'].max()/rng,expected['max_share'],atol=2e-5)
 src=ROOT/('data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114_12h_arco_expanded.nc' if name=='era5' else 'data/real/wildfire/wildfire.json')
 meta=dict(name=name,kind=sc['trees'][0].kind,source=str(src.relative_to(ROOT)),source_sha256=sha(src),trees=trees,relaxation_log=relaxlog,protocol=sc.get('protocol',ds.get('meta')),units='hPa' if name=='era5' else 'processed log(1 + binned FRP [MW])',field_range=rng,methods=METHODS)
 if name=='wildfire':
  from datasets_extra import _wildfire_fields
  raw,dates,_=_wildfire_fields();a['raw_field']=raw
  meta['preprocessing']='Existing 2-day sums, 64x64 binning, log1p, frozen sigma and existing background regularization; unchanged. Raw FRP panel is the unsmoothed log1p binned input.'
 else:
  # Native supplied ERA5 grid in geographical coordinates, in hPa; convert exact extrema using existing projection.
  from netCDF4 import Dataset
  import geo
  with Dataset(src) as nc:
   a['raw_field']=np.array(nc['msl'][:],float)/100;a['raw_lon']=np.array(nc['longitude'][:]);a['raw_lat']=np.array(nc['latitude'][:])
  G=geo.Era5Geo(sc['window'],sc['coords']);a['lonlat']=np.full_like(a['xy'],np.nan)
  # geo conversion is separable for the frozen equal-area, unrotated grid.
  for t,ids in enumerate(sc['ids']):
   for j,leaf in enumerate(ids):
    xy=a['xy'][t,j];X=(xy[0]-G.offx)/G.factor+G.bx0;Y=(xy[1]-G.offy)/G.factor+G.by0
    a['lonlat'][t,j]=[np.rad2deg(X/G.R/G.co) if hasattr(G,'R') else np.rad2deg(X/geo.R/G.co),np.rad2deg(np.arcsin(Y*G.co/geo.R))]
  meta['preprocessing']='Native supplied ERA5 pressure shown separately from the existing projected/resampled/smoothed analysis field. Extrema belong to the analysis field.'
 np.savez_compressed(DATA/f'{name}.npz',**a);write(DATA/f'{name}.json',meta)
 print('Prepared',name,flush=True)

def prepare3d():
 print('Loading frozen Tangaroa feature, layout and matching records',flush=True)
 f=read(TANG/'features.json');ref=read(TANG/'reference.json');pos=read(TANG/'positions.json');metrics=read(TANG/'frame_metrics.json');cert=read(TANG/'certificates.json')
 lookup={(r['method'],r['index']):r for r in metrics};a={};N=max(map(len,f['tracks']));T=len(f['frames']);a['track']=padded(f['tracks'],fill=-1).astype(int);a['leaf']=padded([r['leaf_ids'] for r in f['frames']],fill=-1).astype(int)
 a.update(q=padded(ref['qs']),qnorm=(padded(ref['qs'])-ref['origin'])/ref['extent'],geometry=np.array([ref['origin'],ref['extent']]),direction=np.array(ref['direction']),dates=np.array([f'{i*.01:.2f}' for i in range(T)]))
 a['xyz']=np.full((T,N,3),np.nan);a['value']=np.full((T,N),np.nan)
 for t,r in enumerate(f['frames']):
  a['xyz'][t,:len(r['leaf_ids'])]=r['extrema'];a['value'][t,:len(r['leaf_ids'])]=[r['source_node_values'][str(k)] for k in r['leaf_ids']]
 z=np.load(TANG/'paper_style/display_samples.npz');a['H']=np.array([r['H_lower'] for r in cert]);a['Hupper']=np.array([r['H_upper'] for r in cert]);a['F']=np.array([r['free']['lower'] for r in cert]);a['delta']=np.array([lookup['RG-MTM-R 0.2',t]['measured_topology_absolute'] for t in range(T)])
 for key,name in [('TMTM','TMTM'),('P','RG-MTM-P'),('R','RG-MTM-R 0.2')]:
  a['map'+key]=z[name];a['u'+key]=padded(pos[name]);a['norm'+key]=(a['u'+key]-ref['origin'])/ref['extent'];a['nroe'+key]=np.array([lookup[name,t]['NROE'] for t in range(T)])
  a['mae'+key]=np.nanmean(abs(a['u'+key]-a['q']),axis=1)/ref['extent']
 np.savez_compressed(DATA/'tangaroa.npz',**a)
 write(DATA/'tangaroa.json',dict(name='tangaroa',kind='join',field_range=2.,units='speed (author processed [0, 2])',methods=['TMTM','P','R'],features=f,certificates=cert,reference=ref,source_evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in [TANG/'features.json',TANG/'positions.json',TANG/'frame_metrics.json',TANG/'certificates.json',TANG/'manifest.json',TANG/'verification.json',TANG/'paper_style/display_samples.npz']}))
 print('Prepared Tangaroa without rerunning layout/tree/experiment',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--verify',action='store_true');ap.add_argument('--datasets',nargs='+',default=['era5','wildfire','tangaroa']);args=ap.parse_args();DATA.mkdir(parents=True,exist_ok=True)
 if args.prepare:
  for n in args.datasets:
   if n=='tangaroa':prepare3d()
   else:prepare2d(n)
 else:
  from real_case_large import build,verify
  if args.verify:verify()
  else:build(args.datasets)
