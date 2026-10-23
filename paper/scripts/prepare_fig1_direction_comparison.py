"""Two independent editable experiment figures from hourly RG-MTM results.
Event names/times follow TMTM Fig1. Arrows identify computed minima, not ground-truth tracks.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.interpolate import RegularGridInterpolator
from netCDF4 import Dataset
R=Path(__file__).resolve().parents[1];ROOT=R.parent/'code';sys.path[:0]=[str(ROOT/'analysis'),str(R/'scripts')]
from scene import Scene
from geo import Era5Geo
from anchor_aligned_renderer import render_display
D=R/'evidence/fig1/december1999_xaxis';fields=np.load(D/'fields.npz');B=R/'.build/fig1_december';B.mkdir(exist_ok=True,parents=True)
geo=Era5Geo(dict(lon=(-30,40),lat=(30,75)),fields['coords']);geo.factor=1.;geo.offx=geo.bx0;geo.offy=geo.by0
cm=plt.get_cmap('RdBu_r');norm=Normalize(-35,35)
frames=[66,405,575,610,645]
names=['Cyclone Anatol','Strong storm over Scandinavia','Strong storm over the British Isles and Norway','Cyclone Lothar','Cyclone Martin']
regions=np.array([[10,56],[15,61],[-2,56],[8,50],[4,47]])
# Maps are original 0.25-degree observations with the same 192-hour anomaly baseline.
source=ROOT/'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc'
with Dataset(source) as ds:
 lat=np.asarray(ds['latitude'][:]);lon=np.asarray(ds['longitude'][:]);raw=[]
 for t in frames:
  i=int(fields['source_indices'][t]);v=np.asarray(ds['msl'][i],float)/100
  mean=np.asarray(ds['msl'][i-96:i+96],float).mean(axis=0)/100
  raw.append(v-mean)
co=np.cos(np.deg2rad(52.5));radius=6371
extent=[radius*co*np.deg2rad(-30),radius*co*np.deg2rad(40),radius*np.sin(np.deg2rad(30))/co,radius*np.sin(np.deg2rad(75))/co]
ratio=(extent[1]-extent[0])/(extent[3]-extent[2]);mx=55;my=42;mw=1260;mh=390
# Original full-resolution anomaly snapshots are identical for both directional experiments.
for k,t in enumerate(frames):
 p=B/f'source_{t}.png'
 fig=plt.figure(figsize=(3.4,3.4/ratio),dpi=300);ax=fig.add_axes([0,0,1,1])
 x=np.linspace(extent[0],extent[1],1024);y=np.linspace(extent[2],extent[3],round(1024/ratio));yy,xx=np.meshgrid(y,x,indexing='ij')
 pts=np.stack([np.rad2deg(np.arcsin(yy*co/radius)),np.rad2deg(xx/radius/co)],axis=-1)
 pts[...,0]=np.clip(pts[...,0],lat.min(),lat.max());pts[...,1]=np.clip(pts[...,1],lon.min(),lon.max())
 im=RegularGridInterpolator((lat,lon),raw[k])(pts)
 ax.imshow(im,origin='lower',extent=extent,cmap=cm,norm=norm,interpolation='bilinear')
 geo.coastlines(ax,ROOT/'data/geo/ne_110m_coastline.geojson',color='#1A1A1A',lw=.65,alpha=1)
 ax.set(xlim=extent[:2],ylim=extent[2:],aspect='equal');ax.axis('off');fig.savefig(p,dpi=300);plt.close(fig)
from PIL import Image
Image.fromarray((cm(np.linspace(0,1,600))[None,:,:]*255).astype('uint8')).resize((600,20)).save(B/'colorbar.png')
for stem,folder in [('Fig1_XAxis','december1999_xaxis'),('Fig1_DataDirection','december1999_data_direction')]:
 a=np.load(D.parent/folder/'results.npz');direction=a['direction'];angle=float(np.rad2deg(np.arctan2(direction[1],direction[0])))
 dense,validation=render_display(dict(mapR=a['mapR'],track=a['tracks'],normR=a['normR']),factor=3)
 # The saved hourly columns remain exact; no dark trajectory overlay or scalar enhancement.
 Image.fromarray((cm(norm(dense[::-1]))*255).astype('uint8'),'RGBA').save(B/(stem+'_map.png'))
 s=Scene(1,stem);s.d['width']=1344;s.d['height']=760
 s.d['notes']=('New authorized experiment: ERA5 December 1 00:00–December31 23:00 1999, 744 actual hourly observations. '+
  f'd={direction.tolist()}, angle={angle:.6f} degrees in equal-area coordinates. '+
  'RG-MTM-R20 recomputed with the existing solver and optimal scalar barriers. Analysis:49x49 grid,250km smoothing,192-hour centered pressure anomaly baseline. This differs from the reference papers spatial preprocessing. '+
  'Five published event dates/names follow TMTM Fig1, https://www.csc.kth.se/~weinkauf/publications/documents/koepp22.pdf . '+
  'Annotation targets are actual computed minima nearest the published event region; identities are not independently validated cyclone tracks. '+
  'Maps are native 0.25degree ERA5 hourly anomaly fields. Intermediate display columns use conservative anchor alignment; original744 scalar columns unchanged. '+
  'This is an additional experiment; existing manuscript numbers and the118-frame main suite are unchanged.')
 def text(t,x,y,w,h=24,size=17,bold=False,align='left',name=None):s.text(t,x,y,w,h,size,'#000000',bold,align,name)
 def arrow(x0,y0,x1,y1,color='#000000',width=1.1):
  s.line(x0,y0,x1,y1,color,width);v=np.array([x1-x0,y1-y0]);v=v/np.linalg.norm(v);n=np.array([-v[1],v[0]])
  for sign in [-1,1]:s.line(x1-v[0]*7+sign*n[0]*3,y1-v[1]*7+sign*n[1]*3,x1,y1,color,width)
 text('RG-MTM-R20',55,8,240,25,20,True)
 text('d = (1, 0) · eastward' if stem=='Fig1_XAxis' else f'd = ({direction[0]:.3f}, {direction[1]:.3f}) · {angle:.1f}°',800,8,515,25,18,False,'right')
 s.image(B/(stem+'_map.png'),mx,my,mw,mh,'a_temporal_map')
 s.rect(mx,my,mw,mh,'none','#000000',.9)
 # Axes and native text follow the reference annotation structure.
 arrow(mx,my+mh+7,mx+mw+4,my+mh+7,width=.9)
 arrow(mx-14,my+mh,mx-14,my-8,width=.9)
 text('Time',1265,455,65,24,17,False,'right')
 s.add('text',name='a_reference_axis',text='Reference position along d',x=6,y=130,w=24,h=240,size=18,color='#000000',bold=False,align='center',textOrientation='vert270')
 for day in [1,8,15,22,31]:
  t=(day-1)*24;x=mx+(t+.5)/744*mw;s.line(x,my+mh+3,x,my+mh+11,'#000000',.9);text(f'{day} Dec',x-30,445,60,22,15,False,'center')
 # Shared anomaly legend, exact same limits in both figures and the maps.
 s.add('roundRect',name='a_pressure_legend',x=71,y=57,w=240,h=71,fill='#FFFFFF/85',stroke='#000000',width=.8)
 text('MSLP anomaly [hPa]',84,63,215,23,16)
 s.image(B/'colorbar.png',85,92,210,9,'a_colorbar')
 for t,x in [('-35',85),('0',190),('35',285)]:text(t,x-13,102,28,20,14,False,'center')
 callouts=[(125,294,161,30),(575,104,289,30),(674,363,416,30),(872,216,155,30),(1090,85,158,30)]
 events=[];sw=225;sh=sw/ratio;sy=490
 for k,(t,label,region,box) in enumerate(zip(frames,names,regions,callouts)):
  x=mx+(t+.5)/744*mw;s.line(x,my,x,my+mh,'#7B8790',1,True,name=f'a_event_guide_{k}')
  ids=np.flatnonzero(a['leaf'][t]>=0);j=int(ids[np.argmin(np.sum(((a['lonlat'][t,ids]-region)*[.65,1])**2,axis=1))])
  anchor=float(a['normR'][t,j]);target=(x,my+(1-anchor)*mh);bx,by,bw,bh=box
  s.add('roundRect',name=f'a_event_box_{k}',x=bx,y=by,w=bw,h=bh,fill='#FFFFFF/88',stroke='#000000',width=.8)
  text(label,bx+9,by+5,bw-18,bh-5,15)
  # Draw only from the nearest edge of the callout; exact endpoint is the saved anchor.
  ox=np.clip(target[0],bx+9,bx+bw-9);oy=by+bh if target[1]>by+bh else by
  arrow(float(ox),oy,*target)
  sx=65+k*253
  s.path([[x,my+mh+12],[x,476+k*2],[sx+sw/2,476+k*2],[sx+sw/2,sy]],'#8B8B8B',.8)
  s.image(B/f'source_{t}.png',sx,sy,sw,sh,f'b_source_{t}')
  s.rect(sx,sy,sw,sh,'none','#000000',.9)
  stamp=str(a['dates'][t])[:16];text(stamp,sx-9,sy+sh+9,sw+18,24,16,False,'center')
  # Draw the real projected direction through the selected source extremum.
  lon0,lat0=a['lonlat'][t,j];px=radius*co*np.deg2rad(lon0);py=radius*np.sin(np.deg2rad(lat0))/co
  center=np.array([sx+(px-extent[0])/(extent[1]-extent[0])*sw,sy+(extent[3]-py)/(extent[3]-extent[2])*sh])
  vec=np.array([direction[0],-direction[1]])*26
  # The direction axis passes through the actual computed extremum in source coordinates.
  origin=center;arrow(*(origin-vec),*(origin+vec),'#333333',1.6)
  text('d',origin[0]+vec[0]+4,origin[1]+vec[1]-11,20,24,17,True)
  events.append(dict(frame=t,date=stamp,label=label,computed_track_id=int(a['tracks'][t,j]),computed_minimum_lonlat=a['lonlat'][t,j].tolist(),anchor=anchor,value_hPa=float(a['value'][t,j]),association='nearest computed extremum to published event region; no independently verified physical tracking identity'))
 s.d['notes']+=' Events: '+json.dumps(events)
 (B/(stem+'_scene.json')).write_text(json.dumps(s.d,indent=2))
 (D.parent/folder/'display_validation.json').write_text(json.dumps(validation,indent=2))
 (D.parent/folder/'event_annotations.json').write_text(json.dumps(events,indent=2))
 print(stem,'direction',direction,'angle',angle,'objects',len(s.d['objects']),flush=True)
