"""Add a true three-feature source/local panel to the selected hourly Fig1.
Run after prepare_fig1_direction_comparison.py; reads frozen saved output only.
"""
from pathlib import Path
import json,sys,copy
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R/'.build/fig1_december';D=R/'evidence/fig1/december1999_data_direction'
sys.path.insert(0,str(R/'scripts'));from scene import Scene
stem='Fig1_DataDirection';p=B/(stem+'_scene.json');base=json.loads(p.read_text())
# Idempotence for direct use; regenerate the plain source scene if necessary.
if base.get('local_panel'):
 raise SystemExit('Local panel already prepared. Run prepare_fig1_direction_comparison.py first to rebuild from source.')
s=Scene(1,base['title']);s.d.update(width=1344,height=640,notes=base['notes'],objects=[])
# Preserve every original data image. Maps use a uniform transform to retain geography.
def y(v):return v*.8 if v<490 else 430+(v-490)*.73
for obj in base['objects']:
 o=copy.deepcopy(obj);kind=o['kind']
 if kind in ['line']:
  for k in ['x1','x2']:o[k]*=.73
  for k in ['y1','y2']:o[k]=y(o[k])
 elif kind=='path':o['points']=[[x*.73,y(yy)] for x,yy in o['points']]
 else:
  o['x']*=.73;o['y']=y(obj['y']);o['w']*=.73
  o['h']*=.73 if obj['y']>=490 else .8
 if 'width'in o:o['width']=max(.7,o['width']*.9)
 if kind=='text':
  o['size']=max(14,min(18,o['size']))
  if o['text']=='RG-MTM-R20':o.update(text='(a) RG-MTM-R20',size=20,w=240,h=27)
  if o.get('name')=='a_reference_axis':o.update(x=1,w=24,h=205,size=16)
  if o['text'].startswith('d = ('):o.update(x=542,w=419,size=15,h=23)
  if o['text']=='Strong storm over Scandinavia':o.update(text='Strong storm over\nScandinavia',h=39,size=15,y=o['y']-1)
  if o['text']=='Strong storm over the British Isles and Norway':o.update(text='Strong storm over the\nBritish Isles and Norway',h=39,size=15,y=o['y']-1)
  if obj['y']>=700:o['h']=25
  if o['text']=='Time':o.update(y=382,h=24,size=15)
 if o.get('name') in ['a_event_box_1','a_event_box_2']:o['h']=42
 if o.get('name')=='a_event_box_2':o['x']-=20
 if kind=='text' and o.get('text')=='Strong storm over the\nBritish Isles and Norway':o['x']-=20
 if kind=='line' and obj.get('y1')==134 and 575<=obj.get('x1',0)<=864:o['y1']=125.2
 if o.get('name','').startswith('a_event_guide_'):o['color']='#000000';o['width']=.9
 if o.get('name')=='a_event_guide_3':o['color']='#C73A37';o['width']=1.1
 if o.get('name')=='a_event_box_4':o['x']+=20
 if kind=='text' and o.get('text')=='Cyclone Martin':o['x']+=20
 # The selected fourth snapshot is linked to the right-side detail.
 if kind=='rect' and abs(obj.get('x',0)-(65+3*253))<.1 and obj.get('y')==490:
  o['stroke']='#C73A37';o['width']=1.2
 s.d['objects'].append(o)
a=dict(np.load(D/'results.npz'));t0=610;lo=600;hi=623;labels={'A':130,'B':113,'C':133}
assert str(a['dates'][t0])=='1999-12-26 10:00:00'
def txt(t,x,y,w,h=24,size=16,bold=False,align='left',name=None):s.text(t,x,y,w,h,size,'#000000',bold,align,name)
def arrow(x0,y0,x1,y1,color='#000000',width=1.1):
 s.line(x0,y0,x1,y1,color,width);v=np.array([x1-x0,y1-y0]);v=v/np.linalg.norm(v);n=np.array([-v[1],v[0]])
 for sign in [-1,1]:s.line(x1-v[0]*7+sign*n[0]*3,y1-v[1]*7+sign*n[1]*3,x1,y1,color,width)
txt('(b) Local event and tracks',1006,6,333,28,20,True)
txt('26 Dec 1999 10:00 UTC',1010,36,324,24,16,False,'center')
mx,my,mw=1050,66,245
co=np.cos(np.deg2rad(52.5));radius=6371.
ex=[radius*co*np.deg2rad(-30),radius*co*np.deg2rad(40),radius*np.sin(np.deg2rad(30))/co,radius*np.sin(np.deg2rad(75))/co]
ratio=(ex[1]-ex[0])/(ex[3]-ex[2]);mh=mw/ratio
s.image(B/'source_610.png',mx,my,mw,mh,'b_event_source_f610')
s.rect(mx,my,mw,mh,'none','#B0B0B0',.75)
records={}
def mapxy(lon,lat):
 x=radius*co*np.deg2rad(lon);yy=radius*np.sin(np.deg2rad(lat))/co
 return mx+(x-ex[0])/(ex[1]-ex[0])*mw,my+(ex[3]-yy)/(ex[3]-ex[2])*mh
for lab,tr in labels.items():
 j=int(np.flatnonzero(a['tracks'][t0]==tr)[0]);xy=a['lonlat'][t0,j];xp,yp=mapxy(*xy)
 s.dot(xp,yp,'#000000',4.5,fill='#FFFFFF',name='b_source_marker_'+lab)
 dx,dy={'A':(8,-24),'B':(8,-24),'C':(-25,-23)}[lab]
 txt(lab,xp+dx,yp+dy,24,25,19,True,name='b_source_label_'+lab)
 records[lab]=dict(track_id=tr,frame=t0,lonlat=xy.tolist(),actual_anchor=float(a['normR'][t0,j]),reference=float(a['qnorm'][t0,j]),field_hPa=float(a['value'][t0,j]),source_position_px=[xp,yp],samples=[])
# The true projected direction is drawn through A, with its source location unchanged.
center=np.array(records['A']['source_position_px']);v=np.array([a['direction'][0],-a['direction'][1]])*24
arrow(*(center-v),*(center+v),'#333333',1.2)
txt('d',center[0]+v[0]+6,center[1]+v[1]-4,20,23,17,True,name='b_true_direction_label')
s.add('blockArrow',name='b_source_to_local_arrow',x=1163,y=332,w=24,h=27,fill='#AAB3BC',stroke='none',width=0)
txt('Local tracks · 00:00–23:00 UTC',1014,369,318,24,17,True,'center')
# Exact crop of the same dense RG-MTM scalar image used by the full temporal map.
full=Image.open(B/(stem+'_map.png'));N=full.height;factor=3
row0=0;row1=N  # Temporal selection only: retain the complete output-position axis.
ymax=1-row0/(N-1);ymin=1-(row1-1)/(N-1)
local=full.crop((lo*factor,row0,(hi+1)*factor,row1));local_path=B/'data_direction_local_full_day.png';local.save(local_path)
rx,ry,rw,rh=1054,407,264,191
s.image(local_path,rx,ry,rw,rh,'b_local_scalar_map')
s.rect(rx,ry,rw,rh,'none','#7B8790',.7)
def pos(t,u):return rx+(t-lo+.5)/(hi-lo+1)*rw,ry+(ymax-u)/(ymax-ymin)*rh
s.add('text',name='b_local_position_axis',text='Output position',x=998,y=414,w=23,h=180,size=15,color='#000000',bold=False,align='center',textOrientation='vert270')
for u in [0.,.5,1.]:
 yy=pos(lo,u)[1];s.line(rx-4,yy,rx,yy,'#000000',.7);txt(f'{u:.1f}',1017,yy-10,29,21,14,False,'right')
for t in [lo,t0,hi]:
 xx=pos(t,ymin)[0];s.line(xx,ry+rh,xx,ry+rh+4,'#000000',.7)
 txt(str(a['dates'][t])[11:16],xx-25,ry+rh+7,50,23,14,False,'center')
txt('Time (UTC, 26 Dec)',1063,620,251,19,14,False,'center')
xx=pos(t0,ymin)[0];s.line(xx,ry,xx,ry+rh,'#C73A37',1.0,True,'b_local_event_guide_f610')
for lab,tr in labels.items():
 segments=[];run=[]
 for t in range(lo,hi+1):
  ix=np.flatnonzero(a['tracks'][t]==tr)
  if not len(ix):
   if run:segments.append(run);run=[]
   continue
  j=int(ix[0]);u=float(a['normR'][t,j]);assert ymin<=u<=ymax
  run.append(pos(t,u));records[lab]['samples'].append(dict(frame=t,date=str(a['dates'][t]),actual_anchor=u,reference=float(a['qnorm'][t,j]),lonlat=a['lonlat'][t,j].tolist()))
 if run:segments.append(run)
 for k,pts in enumerate(segments):
  if len(pts)>1:s.path(pts,'#FFFFFF',4.3,name=f'b_local_halo_{lab}_{k}');s.path(pts,'#000000',1.8,name=f'b_local_track_{lab}_{k}')
 point=pos(t0,records[lab]['actual_anchor']);s.dot(*point,'#000000',3.5,fill='#FFFFFF',name='b_local_event_marker_'+lab)
 end=segments[-1][-1];txt(lab,end[0]+5,end[1]-11,18,23,17,True,name='b_local_track_label_'+lab)
 # Native identity labels at the beginning also clarify the real A/B crossing.
 begin=segments[0][0]
 if lab in ['A','B']:txt(lab,begin[0]-17,begin[1]-12,16,21,14,True,name='b_local_start_label_'+lab)
assert [r['frame'] for r in records['C']['samples']]==list(range(605,611))
# Exact visible bounds of the local scalar crop in the main temporal map.
main=next(o for o in s.d['objects'] if o.get('name')=='a_temporal_map')
window=dict(x=main['x']+lo*factor/full.width*main['w'],y=main['y']+row0/full.height*main['h'],w=(hi-lo+1)*factor/full.width*main['w'],h=(row1-row0)/full.height*main['h'])
xx,yy,ww,hh=[window[k] for k in ['x','y','w','h']]
outline=dict(kind='path',name='a_local_window_outline',points=[[xx,yy],[xx+ww,yy],[xx+ww,yy+hh],[xx,yy+hh],[xx,yy]],color='#C73A37',width=1.35,dash=True)
s.d['objects'].insert(s.d['objects'].index(main)+1,outline)
for o in s.d['objects']:
 if o['kind']=='rect' and abs(o['x']-rx)<1e-6 and abs(o['y']-ry)<1e-6 and abs(o['w']-rw)<1e-6:
  o['stroke']='#C73A37';o['width']=1.2;o['name']='b_local_window_outline'
validation=dict(event_frame=t0,event_time=str(a['dates'][t0]),local_frames=[lo,hi],labels=records,direction=a['direction'].tolist(),output_anchor_tracks_native=True,map_and_track_ids_identical=True,local_raster_is_exact_full_map_crop=True,crop_pixels=[lo*factor,row0,(hi+1)*factor,row1],local_y_limits=[ymin,ymax],no_extrapolation=True,feature_C_exists_only_frames=[605,610],track_identity_scope='computed overlap-linked minima, not independently verified meteorological tracks')
validation['main_window_rectangle_px']=window
validation['matching_red_window_outlines']=True
validation['complete_output_axis']=True
validation['temporal_selection_only']=True
validation['event_guides']='black dashed; selected source event red dashed'
s.d['local_panel']=validation
s.d['notes']+=' Right panel: '+json.dumps(validation)
p.write_text(json.dumps(s.d,indent=2));(D/'local_panel.json').write_text(json.dumps(validation,indent=2)+'\n')
print('Prepared right panel at f610, tracks A130/B113/C133; no extrapolated data.',len(s.d['objects']),'native/layer objects')
