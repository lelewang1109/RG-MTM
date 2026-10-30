from pathlib import Path
import sys,json,importlib.util,pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from matplotlib.colors import Normalize,PowerNorm,LinearSegmentedColormap
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from skimage.measure import marching_cubes
import os
W=Path(os.environ['MERGETREEMAPS_WORKSPACE']);OUT=Path(__file__).resolve().parents[1]
SW=W/'output/current_method_parameter_sweep_20261029'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
sweep=module('sweep',SW/'source/run.py')
EPS=[0,.02,.05,.1,.2,.3];NAMES=['Storms','Wildfires','PM2.5','Tangaroa','Vortex']
TIMES=dict(Storms=47,Wildfires=18,OLR=31,**{'PM2.5':180},Ring=20,Tangaroa=100,Cylinder=50,Vortex=8)
A='#b02b83';INK='#23313b';HALO=[pe.withStroke(linewidth=1.6,foreground='white')]
plt.rcParams.update({'font.family':'Arial','font.size':6,'axes.labelsize':6,'xtick.labelsize':5,'ytick.labelsize':5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.5,'pdf.fonttype':42,'svg.fonttype':'none'})
read=lambda p:json.loads(Path(p).read_text())

def load(name):
 if name=='Vortex':
  src=W/'RG-MTM/code/results/volumes20261029/vorts';fr=read(src/'features.json')['frames'];pars=read(src/'parameters.json')
  d=dict(tracks=[f['tracks'] for f in fr],references=[np.asarray(f['extrema'])[:,0].tolist() for f in fr],parameters=pars,extrema=[f['extrema'] for f in fr])
  rows={e:[read((W/'output/vortex_teaser_3d_v4_20261030/epsilon30/vorts' if e==.3 else src)/f'layouts/eps_{e:g}/frame_{t:04d}.json') for t in range(90)] for e in EPS}
  grid=np.linspace(0,127,4096)
  maps={e:np.column_stack([-2*np.interp(grid,r['profile']['x'],r['profile']['values']) for r in rows[e]]) for e in EPS}
  vr=module('vortex_tf',W/'output/vortex_teaser_3d_v4_20261030/source/volume_render.py');vmin,vmax=read(W/'output/vortex_teaser_3d_v4_20261030/evidence.json')['normalized_scalar_limits'];tf=vr.TF
  cm=LinearSegmentedColormap.from_list('vortex_original',[(0,tuple(tf[0,1:4]))]+[((r[0]-vmin)/(vmax-vmin),tuple(r[1:4])) for r in tf],N=2048)
  display=dict(cmap=cm,vmin=vmin,vmax=vmax,palette='original Vortex transfer RGB');return d,rows,maps,display
 d=sweep.load_inputs(name);folder=SW/sweep.slug(name);rows={e:read(folder/f'epsilon_{e:g}.json')['rows'] for e in EPS if e!=.3};m=np.load(folder/'maps.npz');maps={e:m[f'eps_{e:g}'] for e in EPS if e!=.3}
 extra=read(OUT/sweep.slug(name)/'epsilon_0.3.json');rows[.3]=extra['rows'];a,b=extra['window'];M=np.load(OUT/sweep.slug(name)/'epsilon_0.3.npz')['map'];full=np.full((len(M),len(d['tracks'])),np.nan);full[:,a:b+1]=M;maps[.3]=full
 display=read(folder/'protocol.json')['display']
 if name=='Wildfires':
  display.update(cmap=LinearSegmentedColormap.from_list('wildfire_warm',['#fffaf1','#fddc9c','#f9a344','#e95a26','#b52020','#681525']), palette='cream-orange-red',norm=PowerNorm(.65,vmin=display['vmin'],vmax=display['vmax']))
 if name=='PM2.5':
  cm=LinearSegmentedColormap.from_list('pm_contrast',['#253494','#2c7fb8','#41b6c4','#c7e9b4','#ffffcc','#fdae61','#d73027'],N=2048)
  display.update(cmap=cm,palette='blue-cyan-cream-orange-red',vmin=12.,vmax=80.,norm=Normalize(12.,80.,clip=True))
 if name=='Tangaroa':
  tf=np.asarray(read(W/'RG-MTM/code/results/volume3d/tangaroa-paper-p10-full201/paper_style/volume_cache.json')['inputs']['settings']['transfer_function_points'])
  cm=LinearSegmentedColormap.from_list('tangaroa_original',[(v[0],tuple(v[1:4])) for v in tf],N=2048)
  display.update(cmap=cm,vmin=0.,vmax=2.,palette='original Tangaroa transfer RGB')
 return d,rows,maps,display

def choose(d,rows,t):
 old=read(W/'output/dataset_overview_compact_20261030/manifest.json')
 record=next(r for r in old if r['snapshot']==t and len(d['tracks'])==r['frames'])
 return *record['window'],record['track']

def planar_snapshot(ax,name,d,t,i,display):
 cache=OUT/f'snapshot_{sweep.slug(name)}_{t}.npz'
 if not cache.exists() and t=={'Storms':47,'Wildfires':18,'OLR':30,'Ring':20}.get(name) and (OUT/f'snapshot_{sweep.slug(name)}.npz').exists():
  cache=OUT/f'snapshot_{sweep.slug(name)}.npz'
 if cache.exists():
  z=np.load(cache);field=z['field'];coords=z['coords'];ext=z['extrema']
 else:
  key=sweep.PLANAR[name];print('Loading original spatial scene:',name,flush=True)
  ds=pickle.loads((sweep.LOCAL/'results/pm25_2000/dataset.pkl').read_bytes()) if name=='PM2.5' else sweep.replicate.LOADERS[key]()
  sc=ds['sc'];field=np.asarray(sc['fields'][t]);coords=np.asarray(sc['coords']);ext=np.array([sc['frames'][t].coordinates[k] for k in sc['ids'][t]])
  assert len(ext)==len(d['tracks'][t]);np.testing.assert_allclose(sc['centers'][t],d['centers'][t],atol=1e-7)
  np.savez_compressed(cache,field=field,coords=coords,extrema=ext)
 coords=coords.reshape(-1,2);field=field.reshape(-1);ux=np.unique(coords[:,0]);uy=np.unique(coords[:,1]);grid=np.full((len(uy),len(ux)),np.nan)
 grid[np.searchsorted(uy,coords[:,1]),np.searchsorted(ux,coords[:,0])]=field
 ax.imshow(grid,origin='lower',extent=[ux.min(),ux.max(),uy.min(),uy.max()],cmap=display['cmap'],norm=display.get('norm',Normalize(display['vmin'],display['vmax'])),aspect='equal',interpolation='bilinear',interpolation_stage='data',rasterized=True)
 xy=ext[i];ax.plot(*xy,'o',ms=3,mfc=A,mec='white',mew=.6);ax.annotate('A',xy,xytext=(-8 if xy[0]>(ux.min()+.8*np.ptp(ux)) else 4,3),textcoords='offset points',color=A,fontsize=7,weight='bold',path_effects=HALO)
 ax.set_xticks([]);ax.set_yticks([]);return xy.tolist(),'processed 2-D field'

def volume_snapshot(ax,name,d,t,i):
 if name=='Vortex':
  vr=module('volume_render',W/'output/vortex_teaser_3d_v4_20261030/source/volume_render.py');cache=W/f'output/vortex_teaser_3d_v4_20261030/.ppt_build/volume_{t:03d}.npz'
  ax.imshow(np.load(cache)['image'],extent=vr.EXTENT,origin='upper',rasterized=True)
  for a in range(8):
   for b in range(a+1,8):
    if np.count_nonzero(vr.CORNERS[a]!=vr.CORNERS[b])==1:
     points=vr.project(vr.CORNERS[[a,b]]);ax.plot(points[:,0],points[:,1],color='#687f8e',lw=.55,zorder=3)
  xyz=np.asarray(d['extrema'][t][i]);xy=vr.project(xyz);ax.plot(*xy,'o',ms=3,mfc=A,mec='white',mew=.6);ax.annotate('A',xy,xytext=(4,3),textcoords='offset points',color=A,weight='bold',fontsize=7,path_effects=HALO);ax.axis('off');return xyz.tolist(),'original-grid volume rendering'
 if name=='Tangaroa':
  render_cache=OUT/'tangaroa_oblique.npz'
  if not render_cache.exists():
   import ast
   from itertools import product
   from scipy.ndimage import map_coordinates
   source=W/'RG-MTM/code/experiments/volume3d/paper_style.py';tree=ast.parse(source.read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='parallel_dvr')
   env=dict(np=np,product=product,map_coordinates=map_coordinates);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),env)
   settings=read(W/'RG-MTM/code/results/volume3d/tangaroa-paper-p10-full201/paper_style/volume_cache.json')['inputs']['settings']
   settings['camera']=dict(look_from=[1.3,-1.4,.5],look_to=[.15,0,-.4],up=[0,0,1],aspect=1.2);settings['author_sampling_rate']=2
   field=np.load(W/f'RG-MTM/data/real/Tangaroa-FAU/paper_full_201/scalar_{t:03d}.npy');bounds=np.array([-.35,.65,-.3,.3,-.5,-.3])
   print('Rendering Tangaroa oblique volume',flush=True);image,corners,projected=env['parallel_dvr'](field,bounds,settings,width=320)
   np.savez_compressed(render_cache,images=image[None],corners=corners,projected=projected)
  cache=np.load(render_cache)
  xyz=np.asarray(d['features'][t]['extrema'][i]);transform=np.linalg.lstsq(np.c_[cache['corners'],np.ones(8)],cache['projected'],rcond=None)[0]
  assert np.max(abs(np.c_[cache['corners'],np.ones(8)]@transform-cache['projected']))<1e-10
  xy=np.r_[xyz,1]@transform
  ax.imshow(cache['images'][0],origin='lower',extent=[-1,1,-1,1],aspect='auto',rasterized=True)
  for a in range(8):
   for b in range(a+1,8):
    if np.count_nonzero(cache['corners'][a]!=cache['corners'][b])==1:ax.plot(cache['projected'][[a,b],0],cache['projected'][[a,b],1],lw=.55,color='#687f8e')
  ax.plot(*xy,'o',ms=3,mfc=A,mec='white',mew=.6);ax.annotate('A',xy,xytext=(3,3),textcoords='offset points',color=A,fontsize=7,weight='bold',path_effects=HALO)
  ax.set(xlim=(-1,1),ylim=(-1,1));ax.axis('off');return xyz.tolist(),'cached original-volume rendering; affine orthographic projection checked against all eight corners'
 if name=='Tangaroa_UNUSED':
  path=W/f'RG-MTM/data/real/Tangaroa-FAU/paper_full_201/scalar_{t:03d}.npy';v=np.load(path,mmap_mode='r');meta=read(path.with_suffix('.json'));b=meta['bounds_xyz'];level=.15
  xyz=np.asarray(d['features'][t]['extrema'][i]);cmap='viridis'
 else:
  path=W/'RG-MTM/data/real/paper1_suite/square-cylinder3d/source_fields.npy';v=np.load(path,mmap_mode='r')[t];c=np.load(path.parent/'coordinates.npz');b=[c['x'].min(),c['x'].max(),c['y'].min(),c['y'].max(),c['z'].min(),c['z'].max()];level=.05
  xyz=np.asarray(d['features'][t]['extrema'][i]);cmap='coolwarm'
 verts,faces,_,_=marching_cubes(np.array(v,copy=True),level=level,step_size=3);verts=verts[:,::-1]
 verts=np.array(b)[[0,2,4]]+verts/(np.array(v.shape[::-1])-1)*np.array([b[1]-b[0],b[3]-b[2],b[5]-b[4]])
 mesh=Poly3DCollection(verts[faces],facecolor='#62a5b3',edgecolor='none',alpha=.23,rasterized=True);ax.add_collection3d(mesh)
 ax.scatter(*xyz,color=A,edgecolors='white',s=10,depthshade=False);ax.text(*xyz,' A',color=A,fontsize=7,weight='bold',path_effects=HALO)
 ax.set(xlim=b[:2],ylim=b[2:4],zlim=b[4:6]);ax.set_box_aspect([b[1]-b[0],b[3]-b[2],b[5]-b[4]]);ax.view_init(22,-65);ax.set_axis_off();return xyz.tolist(),f'3-D source isosurface, level={level}'

def main():
 fig=plt.figure(figsize=(7.4,5.5),facecolor='white');manifest=[]
 left=.04;snapw=.128;stripx=.181;stripw=.013;mapleft=.245;mapright=.993;gap=.006;mapw=(mapright-mapleft-5*gap)/6;rowh=.155
 for r,name in enumerate(NAMES):
  print('Building',name,flush=True);d,rows,maps,display=load(name);t=TIMES[name];lo,hi,k=choose(d,rows,t);i=d['tracks'][t].index(k);p=d['parameters'];L=p['canvas'];origin=p.get('canvas_origin',0);norm=display.get('norm',Normalize(display['vmin'],display['vmax']))
  bottom=.776-r*.181;samples=[lo,t,hi];labels=['A1','A2','A3']
  fig.text(.015,bottom+rowh/2,name if name!='PM2.5' else r'PM$_{2.5}$',fontsize=7,weight='bold',color='black',rotation=90,ha='center',va='center')
  ax=fig.add_axes([left,bottom,snapw,rowh])
  xyz,note=planar_snapshot(ax,name,d,t,i,display) if name in ['Storms','Wildfires','PM2.5'] else volume_snapshot(ax,name,d,t,i)
  for text in ax.texts:
   if text.get_text().strip()=='A':text.set_text('A2')
  ax.text(.025,.975,f't = {t}',transform=ax.transAxes,ha='left',va='top',fontsize=5,color='black',bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=.6))
  # Exact-layout single-column profile, sharing the map colour scale and [0,1] axis.
  strip=fig.add_axes([stripx,bottom,stripw,rowh]);strip.imshow(maps[0][:,t:t+1],origin='lower',aspect='auto',extent=[0,1,0,1],cmap=display['cmap'],norm=norm,interpolation='bilinear',interpolation_stage='data')
  y0=(rows[0][t]['x'][i]-origin)/L;q0=(d['references'][t][i]-origin)/L
  strip.plot([.5,.5],[y0,q0],color=A,lw=.8);strip.plot(.5,q0,'D',mfc='white',mec='#25313b',ms=2.8,mew=.55,clip_on=False);strip.plot(.5,y0,'o',mfc=A,mec='white',ms=2.8,mew=.5,clip_on=False)
  strip.annotate('q',(.5,q0),xytext=(-6,5 if abs(q0-y0)<.08 else 0),textcoords='offset points',fontsize=5,color='black',ha='right',va='center',path_effects=HALO)
  strip.annotate('A2',(.5,y0),xytext=(5,0),textcoords='offset points',fontsize=5.6,color=A,va='center',path_effects=HALO);strip.set(xticks=[],yticks=[],ylim=(0,1))
  if r==0:strip.set_title('0%',fontsize=6,pad=4)
  row=dict(dataset=name,dimension=2 if name in ['Storms','Wildfires','PM2.5'] else 3,frames=len(d['tracks']),window=[lo,hi],snapshot=t,track=k,source_extremum=xyz,snapshot_note=note,palette=display.get('palette',str(display['cmap'])),display_range=[display['vmin'],display['vmax']],sample_times=samples,labels=labels,strip=dict(epsilon=0,mapped=y0,reference=q0),parameters=[])
  for j,e in enumerate(EPS):
   ax=fig.add_axes([mapleft+j*(mapw+gap),bottom,mapw,rowh]);M=maps[e];assert np.isfinite(M[:,lo:hi+1]).all()
   ax.imshow(M[:,lo:hi+1],origin='lower',aspect='auto',extent=[lo-.5,hi+.5,0,1],cmap=display['cmap'],norm=norm,interpolation='bilinear',interpolation_stage='data',resample=True,rasterized=True)
   ts=np.arange(lo,hi+1);ys=[];qs=[]
   for tt in ts:
    ii=d['tracks'][tt].index(k);ys.append((rows[e][tt]['x'][ii]-origin)/L);qs.append((d['references'][tt][ii]-origin)/L)
    assert rows[e][tt]['measured_topology']<=e+1.1e-7
   ys=np.asarray(ys);qs=np.asarray(qs);ax.plot(ts,qs,'--',color='#262c31',lw=.5,path_effects=HALO,zorder=4)
   ax.plot(ts,ys,'-',color=A,lw=.9,path_effects=HALO,zorder=5)
   # Highlight the entire profile at the exact snapshot time, without a white dashed line.
   box=Rectangle((t-.5,0),1,1,fill=False,ec='#b37814',lw=.75,zorder=7);ax.add_patch(box)
   for jj,(tt,label) in enumerate(zip(samples,labels)):
    yy=ys[tt-lo];qq=qs[tt-lo];ax.plot(tt,yy,'o',ms=2.3,mfc=A,mec='white',mew=.45,zorder=8)
    if tt==t:ax.plot(tt,qq,'D',ms=2.4,mfc='white',mec='#25313b',mew=.5,zorder=8)
    dx=2 if jj<2 else -2;ha='left' if jj<2 else 'right';dy=(10 if jj==1 else 3) if yy<.8 else -9
    ax.annotate(label,(tt,yy),xytext=(dx,dy),textcoords='offset points',ha=ha,fontsize=5.1,color=A,path_effects=HALO,zorder=9)
   ax.set(xlim=(lo-.5,hi+.5),ylim=(0,1),xticks=[lo,hi],yticks=[0,1] if j==0 else [])
   ax.tick_params(length=1.2,pad=.8,labelsize=4.5);ax.get_xticklabels()[0].set_ha('left');ax.get_xticklabels()[-1].set_ha('right')
   if r==0:ax.set_title(r'$\varepsilon=%g\%%$'%(100*e),fontsize=6.8,pad=4)
   row['parameters'].append(dict(epsilon=e,mapped_positions=ys.tolist(),references=qs.tolist(),measured_merge_error=rows[e][t]['measured_topology'],selection_box=[t-.5,t+.5,0,1]))
  manifest.append(row)
  if r<4:fig.add_artist(plt.Line2D([.03,.996],[bottom-.018,bottom-.018],transform=fig.transFigure,color='#b5b9bd',lw=.35))
 fig.text(left+snapw/2,.962,'Snapshot',fontsize=7,ha='center',color='black',va='top')
 for ext in ['pdf','svg','png']:fig.savefig(OUT/f'dataset_overview_extended.{ext}',dpi=450,bbox_inches='tight',pad_inches=.025)
 plt.close(fig);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Saved extended overview',flush=True)
if __name__=='__main__':main()
