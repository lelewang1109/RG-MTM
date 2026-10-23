"""Source-linked annual PM2.5 case from verified saved arrays; no new layout fit."""
from pathlib import Path
import sys,json,pickle,hashlib,itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from PIL import Image
R=Path(__file__).resolve().parents[1];C=R.parent/'code';B=R/'.build/pm25_case20261023';O=R/'evidence/pm25_case20261023'
for x in [B/'assets',B/'scenes',B/'checks',B/'candidates',B/'final',O]:x.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(C/'analysis'),str(C/'src'),str(C),str(R/'scripts')]
import general_method as gm,pm25_annual as annual,public_scalar as ps
from real_case_studies import witness
from rgmtm.baselines.space_filling import merge_levels_on_line
from native_merge_errors import measure
from scene import Scene
from anchor_aligned_renderer import render_display
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with (annual.OUT/'dataset.pkl').open('rb')as f:ds=pickle.load(f)
sc=ds['sc'];z=np.load(annual.OUT/'landmarks.npz');maps=np.load(annual.OUT/'maps.npz');ext=[z['extrema'][t,:n]for t,n in enumerate(z['count'])];ref=gm.auto_reference(sc,ext,ds['lo'],ds['hi']);origin,L=ref['origin'],ref['extent'];qnorm=[(q-origin)/L for q in ref['qs']]
# Selection uses witness obstruction and track continuity, never motion accuracy or positional improvement.
candidates=[]
for t,(fr,ids,q)in enumerate(zip(sc['frames'],sc['ids'],ref['qs'])):
 h,w=witness(fr,ids,q)
 if w is None or h<=.02*L:continue
 tracks=[int(sc['tracks'][t][i])for i in w];lo=hi=t
 while lo>0 and set(tracks)<=set(sc['tracks'][lo-1]):lo-=1
 while hi<365 and set(tracks)<=set(sc['tracks'][hi+1]):hi+=1
 candidates.append(dict(frame=t,date=str(z['dates'][t]),indices=list(w),tracks=tracks,witness_bound_share=h/L,common_interval=[lo,hi],consecutive_frames=hi-lo+1))
eligible=[x for x in candidates if x['consecutive_frames']>=3];median=float(np.median([x['witness_bound_share']for x in eligible]));selected=min(eligible,key=lambda x:(abs(x['witness_bound_share']-median),x['frame']));t=selected['frame'];tracks=selected['tracks'];assert t==195 and tracks==[153,146,152]
window=[t-4,t+7];snaps=list(range(t-2,t+3));labels='ABC';colors=['#0072B2','#D55E00','#009E73'];ink='#000000';gray='#6A7278'
P,R20=maps['A'],maps['R 20%'];n=z['count'][t];indices=selected['indices'];fr=sc['frames'][t];ids=sc['ids'][t]
anchors={m:[np.rint(z['u'+str(i)][u,:nn]*(g.shape[0]-1)).astype(int)for u,nn in enumerate(z['count'])]for m,i,g in [('P',2,P),('R20',3,R20)]}
barriers={m:merge_levels_on_line(g[:,t],anchors[m][t],'split')for m,g in [('P',P),('R20',R20)]};pairs=[]
for name,i,j in [('AB',indices[0],indices[1]),('AC',indices[0],indices[2]),('BC',indices[1],indices[2])]:
 truth=float(fr.values[fr.lca(ids[i],ids[j])]);assert abs(barriers['P'][i,j]-truth)<1e-12;pairs.append(dict(pair=name,source=truth,P=float(barriers['P'][i,j]),R20=float(barriers['R20'][i,j])))
scalar=measure(sc,R20,anchors['R20']);pos={m:float(max(abs(z['u'+str(i)][t,:n]-qnorm[t])))for m,i in [('P',2),('R20',3)]}
# Reuse original array-domain coordinates for all marker projections.
phi=np.deg2rad(33.);co=np.cos(phi);rad=6371.;bx=rad*co*np.deg2rad([102.,114.]);by=rad*np.sin(np.deg2rad([28.,38.]))/co;factor=120/np.hypot(np.diff(bx)[0],np.diff(by)[0]);ex=[0.,float(np.diff(bx)[0]*factor),0.,float(np.diff(by)[0]*factor)]
def xy(lon,lat):return((rad*co*np.deg2rad(lon)-bx[0])*factor,(rad*np.sin(np.deg2rad(lat))/co-by[0])*factor)
def lonlat(point):return[float(np.rad2deg((point[0]/factor+bx[0])/(rad*co))),float(np.rad2deg(np.arcsin((point[1]/factor+by[0])*co/rad)))]
np.testing.assert_allclose(xy(*np.array([lonlat(p)for p in sc['coords']]).T),sc['coords'].T,atol=1e-10)
annual.register();lat,lon,raw,dates,source_meta=ps.read_source(annual.NAME);iy=(lat>=28)&(lat<=38);ix=(lon>=102)&(lon<=114);raw=raw[:,iy][:,:,ix];lat=lat[iy];lon=lon[ix];X,Y=xy(*np.meshgrid(lon,lat));context=R.parent/'data/geo/pm25_context/china_admin1.geojson';gj=json.loads(context.read_text())
CM=LinearSegmentedColormap.from_list('pollution',['#2ca25f','#a1d76a','#ffff73','#fdae61','#f46d43','#d73027','#762a83']);CM.set_under('#8196a6');NORM=Normalize(0,165);LOCAL_NORM=Normalize(0,100);assert raw.max()<=300 and max(P.max(),R20.max())<=165 and raw[snaps].max()<=100
# Native source sampling and existing processed fields. No smoothing added here.
def source_image(frame,processed=False,local=False):
 p=B/'assets'/f'{"local"if local else"annual"}_{"analysis"if processed else"supplied"}_{frame}.png';norm=LOCAL_NORM if local else NORM;fig=plt.figure(figsize=(4,4*(ex[3]-ex[2])/(ex[1]-ex[0])),dpi=200);ax=fig.add_axes([0,0,1,1])
 if processed:ax.imshow(sc['fields'][frame],origin='lower',extent=ex,cmap=CM,norm=norm,interpolation='nearest',aspect='equal')
 else:ax.pcolormesh(X,Y,raw[frame],shading='nearest',cmap=CM,norm=norm,rasterized=True)
 for feature in gj['features']:
  geom=feature['geometry'];poly=geom['coordinates']if geom['type']=='MultiPolygon'else[geom['coordinates']]
  for pp in poly:
   for ring in pp:
    a=np.asarray(ring);xx,yy=xy(a[:,0],a[:,1]);ax.plot(xx,yy,color='#5F6870',lw=.45,alpha=.85)
 ax.set(xlim=ex[:2],ylim=ex[2:],aspect='equal');ax.axis('off');fig.savefig(p,dpi=200);plt.close(fig);return p
# One display reconstruction shared by annual and local R20 views, preserving every original column.
dense,display=render_display(dict(mapR=R20,track=z['tracks'],normR=z['u3']),factor=5)
def raster(g,stem,local=False):
 p=B/'assets'/(stem+'.png');Image.fromarray(np.rint(CM((LOCAL_NORM if local else NORM)(g[::-1]))*255).astype('uint8')).save(p);return p
s=Scene(13,'PM2.5: annual view and source-linked hierarchy conflict');s.d.update(width=1440,height=1240)
def text(t,x,y,w,h=26,size=20,bold=False,align='left',color=ink):return s.text(t,x,y,w,h,size,color,bold,align)
def timeaxis(rect,start,stop,ticks,dates_mode=False):
 x,y,w,h=rect
 for v in [0,.5,1]:yy=y+h-v*h;s.line(x-4,yy,x,yy,ink,.8);text(f'{v:g}',x-38,yy-10,29,22,16,align='right')
 for v,label in ticks:xx=x+(v-start+.5)/(stop-start)*w;s.line(xx,y+h,xx,y+h+4,ink,.8);text(label,xx-42,y+h+7,84,24,16,align='center')
 s.rect(x,y,w,h,'none',gray,.65)
def maprect(frame,rect,processed=False,mark=False,labels_on=False,local=False):
 x,y,w,h=rect;s.image(source_image(frame,processed,local),x,y,w,h);s.rect(x,y,w,h,'none',gray,.65)
 for lo in [102,108,114]:xx=x+(xy(lo,28)[0]-ex[0])/(ex[1]-ex[0])*w;text(str(lo),xx-25,y+h+5,50,22,15,align='center')
 if labels_on:
  for la in [28,33,38]:yy=y+(ex[3]-xy(102,la)[1])/(ex[3]-ex[2])*h;text(str(la),x-37,yy-10,30,22,15,align='right')
 if mark:
  for letter,tr,color in zip(labels,tracks,colors):
   hit=np.flatnonzero(z['tracks'][frame]==tr)
   if not len(hit):continue
   point=z['extrema'][frame,hit[0]];px=x+(point[0]-ex[0])/(ex[1]-ex[0])*w;py=y+(ex[3]-point[1])/(ex[3]-ex[2])*h
   s.dot(px,py,'#FFFFFF',6,'#FFFFFF');s.dot(px,py,color,4,'#FFFFFF');dx=8 if px<x+w-24 else-24;dy=-24 if py>y+20 else 8;text(letter,px+dx,py+dy,26,26,20,True,color=color)
 return rect
text('(a) PM2.5 in 2000: complete RG-MTM-R20 map',18,4,1350,30,25,True)
a=(80,43,1280,145);s.image(raster(dense,'annual_R20'),*a);timeaxis(a,0,366,[(0,'Jan 1'),(91,'Apr 1'),(182,'Jul 1'),(274,'Oct 1'),(365,'Dec 31')]);text('Normalized fixed reference position',80,228,570,24,18)
x=a[0]+window[0]/366*a[2];w=(window[1]-window[0])/366*a[2];s.rect(x,a[1],w,a[3],'none','#B2182B',1.5);text('Jul 10-20',x-20,17,140,23,17,True,color='#B2182B')
for f in snaps:
 xx=a[0]+(f+.5)/366*a[2];s.line(xx,a[1],xx,a[1]+a[3],gray,.65,True)
bar=raster(np.linspace(0,165,900)[None,:],'concentration_bar');s.image(bar,810,235,510,13)
for v in [0,40,80,120,165]:text(str(v),810+v/165*510-32,251,64,24,16,align='center')
text('Panel (a): concentration (ug m-3)',810,282,510,23,17,align='center')
text('(b) Supplied concentration fields: Jul 12-16',18,282,770,31,25,True)
ratio=(ex[3]-ex[2])/(ex[1]-ex[0]);hh=235*ratio
for j,f in enumerate(snaps):
 xx=70+j*274;rect=(xx,342,235,hh);text(dates[f],xx-10,313,255,26,21,True,align='center');maprect(f,rect,mark=True,labels_on=j==0,local=True)
 if f==t:s.rect(*rect,'none','#B2182B',1.5)
text('Longitude (degrees E); latitude (degrees N). All five dates share the local 0-100 concentration scale.',70,342+hh+35,1300,25,18)
text('(c) Jul 14: supplied field and actual analysis input',18,636,710,30,24,True)
left=[(70,691,250,250*ratio),(376,691,250,250*ratio)]
for processed,rect,title in zip([False,True],left,['Supplied grid','Analysis: 100 km smoothing']):
 text(title,rect[0]-15,665,280,25,19,True,align='center');maprect(t,rect,processed,True,True,local=True)
# Fixed reference direction shown in the actual geographic projection, not north/south guessing.
rect=left[1];start=np.array([rect[0]+.78*rect[2],rect[1]+.76*rect[3]]);direction=np.array(ref['candidates']['direction']['a']);end=start+direction*np.array([1,-1])*50;s.line(*start,*end,ink,2);v=(end-start)/np.linalg.norm(end-start);normal=np.array([-v[1],v[0]]);s.line(*end,*(end-v*10+normal*5),ink,2);s.line(*end,*(end-v*10-normal*5),ink,2);text('d',end[0]-23,end[1]-24,25,24,19,True)
text('(d) Jul 10-20: same tracks, same fixed reference',735,636,700,30,24,True)
local_reports={}
for m,i,g,y,title in [('P',2,P,695,'RG-MTM-P (source hierarchy)'),('R20',3,R20,862,'RG-MTM-R20')]:
 rect=(775,y,610,101);lo,hi=window
 display_slice,local_reports[m]=render_display(dict(mapR=g[:,lo:hi],track=z['tracks'][lo:hi],normR=z['u'+str(i)][lo:hi]),factor=41)
 s.image(raster(display_slice,'local_'+m,local=True),*rect);timeaxis(rect,lo,hi,[(u,dates[u][5:])for u in range(lo,hi,2)]);text(title,775,y-29,610,25,20,True)
 xpos=lambda u:rect[0]+(u-lo+.5)/(hi-lo)*rect[2];ypos=lambda v:rect[1]+(1-v)*rect[3]
 for tr,letter,color in zip(tracks,labels,colors):
  segments=[];seg=[]
  for u in range(lo,hi):
   hit=np.flatnonzero(z['tracks'][u]==tr)
   if not len(hit):
    if seg:segments.append(seg);seg=[]
   else:seg.append((u,int(hit[0])))
  if seg:segments.append(seg)
  for seg in segments:
   for kind,dash,width in [('q',True,1.45),('u',False,2.4)]:
    points=[[xpos(u),ypos(qnorm[u][j]if kind=='q'else z['u'+str(i)][u,j])]for u,j in seg]
    if len(points)>1:s.path(points,'#FFFFFF',width+2,dash);s.path(points,color,width,dash)
   for u,j in seg:
    if u in [t,t+1,t+2]:s.dot(xpos(u),ypos(z['u'+str(i)][u,j]),color,3.3,'#FFFFFF')
  j=int(np.flatnonzero(z['tracks'][t]==tr)[0]);text(letter,xpos(t)+(10 if letter=='B' else -24),ypos(z['u'+str(i)][t,j])+(-5 if letter=='B' else -27),25,26,19,True,color=color)
 xx=xpos(t);s.line(xx,y,xx,y+rect[3],ink,.9,True)
s.image(raster(np.linspace(0,100,700)[None,:],'local_concentration_bar',local=True),350,1021,720,13)
for v in [0,25,50,75,100]:text(str(v),350+v/100*720-25,1038,50,23,16,align='center')
text('Panels (b,c,d): concentration (ug m-3), shared 0-100 scale',350,1065,720,23,18,align='center')
text('A=153, B=146, C=152: extrema of the processed field, projected onto both source views.',70,1091,1320,25,19)
text('Solid traces: saved anchors. Dashed traces: fixed references. Gaps retain saved births and deaths.',70,1122,1320,25,19)
text(f'Jul 14: max displayed anchor error  P {100*pos["P"]:.2f}% L  to  R20 {100*pos["R20"]:.2f}% L; measured NMLE {100*scalar["per_frame_share"][t]:.2f}% (window max {100*max(scalar["per_frame_share"][window[0]:window[1]]):.2f}%).',70,1153,1320,25,19,True)
text('Pair merge levels (ug m-3): source = P  AB 25.94, AC 22.63, BC 22.63; R20  AB = AC = BC = 24.28.',70,1184,1320,25,19)
# Precise records for both the selection and every plotted coordinate.
markers=[]
for f in sorted(set(snaps+[t,t+1,t+2])):
 for tr,letter in zip(tracks,labels):
  hit=np.flatnonzero(z['tracks'][f]==tr)
  if not len(hit):continue
  i=int(hit[0]);point=z['extrema'][f,i];markers.append(dict(frame=f,date=dates[f],label=letter,track=tr,leaf=int(z['feature_ids'][f,i]),layout_xy=point.tolist(),lonlat=lonlat(point),reference=float(qnorm[f][i]),anchor_P=float(z['u2'][f,i]),anchor_R20=float(z['u3'][f,i])))
cjump=[]
for m,i in [('reference',None),('P',2),('R20',3)]:
 j0=int(np.flatnonzero(z['tracks'][t]==tracks[2])[0]);j1=int(np.flatnonzero(z['tracks'][t+1]==tracks[2])[0]);v0=qnorm[t][j0]if i is None else z['u'+str(i)][t,j0];v1=qnorm[t+1][j1]if i is None else z['u'+str(i)][t+1,j1];cjump.append(dict(method=m,change_L=float(v1-v0)))
record=dict(dataset='pm25_2000',frames=366,selection_rule='Among frames whose strongest 3-feature interleaving witness exceeds 2% L and whose three tracks coexist for at least 3 consecutive saved dates, choose the frame closest to the median witness obstruction; earliest tie. No error, motion, or gain criterion.',candidate_frames=len(candidates),eligible_frames=len(eligible),median_witness_share=median,candidates=candidates,selected=selected,local_window=window,snapshot_frames=snaps,source_window=dict(lon=[102,114],lat=[28,38]),concentration_scales={'annual_panel_a':[0,165],'local_panels_bcd':[0,100]},local_max_concentration=float(max(raw[snaps].max(),P[:,window[0]:window[1]].max(),R20[:,window[0]:window[1]].max())),local_NMLE=[dict(frame=u,date=dates[u],share=scalar['per_frame_share'][u])for u in range(*window)],source_max=float(raw.max()),displayed_anchor_error=pos,measured_NMLE=scalar['per_frame_share'][t],scalar_normalization_range=float(np.ptp(sc['fields'])),pair_merges=pairs,track_C_Jul14_to_15=cjump,markers=markers,annual_motion=dict(P='42/95',R20='47/95'),interpretation='Selected mechanism witness, not an independently validated pollution episode or representative estimate. The concentration timestamps are 10:30; daily averaging is not established.',source_sha256={str(p):sha(p)for p in [annual.OUT/'dataset.pkl',annual.OUT/'maps.npz',annual.OUT/'landmarks.npz',context,context.with_name('source.json'),Path(__file__),ps.path_for(annual.NAME)]})
s.d['notes']=json.dumps(record);(B/'scenes/Fig13.json').write_text(json.dumps(s.d,indent=2)+'\n');(O/'case.json').write_text(json.dumps(record,indent=2)+'\n');(O/'display_reconstruction.json').write_text(json.dumps(dict(annual_R20=display,local=local_reports),indent=2)+'\n')
np.savez_compressed(O/'case_arrays.npz',reference=np.array([np.pad(x,(0,7-len(x)),constant_values=np.nan)for x in qnorm]),tracks=z['tracks'],counts=z['count'],source_snapshots=raw[snaps],source_lon=lon,source_lat=lat,processed_case=sc['fields'][t],coords=sc['coords'],local_P=P[:,window[0]:window[1]],local_R20=R20[:,window[0]:window[1]])
print(json.dumps(dict(selection=selected,eligible=len(eligible),error=pos,NMLE=record['measured_NMLE'],C_jump=cjump,pair_merges=pairs),indent=2))
