"""Five observed fields, full topologies, anchor maps and matched P/R images."""
from pathlib import Path
import sys,json,hashlib
from itertools import combinations
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.patches import Rectangle
from netCDF4 import Dataset
from scipy.interpolate import RegularGridInterpolator

OUT=Path(__file__).resolve().parent;PAPER=OUT.parent;CODE=PAPER.parent/'code'
sys.path[:0]=[str(CODE/'analysis'),str(CODE),str(CODE/'src'),str(PAPER/'scripts')]
from experiments import era5 as ep
import relax_hierarchy as rh
from geo import Era5Geo
from anchor_aligned_renderer import render_display
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.load(open(OUT/'original_hashes.json'));assert all(sha(PAPER/k)==v for k,v in before.items())
a=np.load(PAPER/'evidence/fig1/december1999_data_direction/results.npz');f=np.load(PAPER/'evidence/fig1/december1999_xaxis/fields.npz');b=np.load(OUT/'positions.npz')
frames=b['frames'].tolist();labs={'A':127,'B':113,'C':130};rev={v:k for k,v in labs.items()};mark={'A':'o','B':'s','C':'^'}
INK='#26343D';GRAY='#747F86';FAINT='#C0C5C9';P='#245C8A';R='#08715E';ACC='#A35849'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.edgecolor':'#9AA1A6','axes.linewidth':.7,'xtick.color':GRAY,'ytick.color':GRAY,'svg.fonttype':'none','pdf.fonttype':42})
cm=LinearSegmentedColormap.from_list('pressure',['#315D83','#7E9FB8','#F8F8F6','#D7A18F','#B95D4C'],N=1024);norm=Normalize(-35,35)
fig=plt.figure(figsize=(18.8,7.0),facecolor='white')
def txt(x,y,s,size=14,color=INK,bold=False,**kw):return fig.text(x,y,s,fontsize=size,color=color,fontweight='bold' if bold else 'normal',**kw)
co=np.cos(np.deg2rad(52.5));radius=6371.;extent=[radius*co*np.deg2rad(-30),radius*co*np.deg2rad(40),radius*np.sin(np.deg2rad(30))/co,radius*np.sin(np.deg2rad(75))/co]
xy=lambda lon,lat:(radius*co*np.deg2rad(lon),radius*np.sin(np.deg2rad(lat))/co)
geo=Era5Geo(dict(lon=(-30,40),lat=(30,75)),f['coords']);geo.factor=1.;geo.offx=geo.bx0;geo.offy=geo.by0
txt(.040,.963,'26 December 1999 (UTC)',16,bold=True)
txt(.792,.963,'P / R temporal maps',15,bold=True)
for y,label in [(.695,'Source field'),(.360,'Topology'),(.158,'Position')]:txt(.012,y,label,13,bold=True,rotation=90,ha='center',va='center')
columns=[.040,.183,.326,.469,.612];width=.132;records=[]
source=Dataset(CODE/'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc');lat=np.asarray(source['latitude'][:]);lon=np.asarray(source['longitude'][:])
X,Y=np.meshgrid(np.linspace(extent[0],extent[1],600),np.linspace(extent[2],extent[3],600));pts=np.stack([np.clip(np.rad2deg(np.arcsin(Y*co/radius)),lat.min(),lat.max()),np.clip(np.rad2deg(X/radius/co),lon.min(),lon.max())],axis=-1)
for column,(t,left) in enumerate(zip(frames,columns)):
 n=int(np.sum(a['leaf'][t]>=0));ids=a['leaf'][t,:n];tracks=a['tracks'][t,:n];q=a['qnorm'][t,:n]
 sc=ep.scene_from_fields(f['fields'][t:t+1],f['coords'],float(f['geometry'][2]),max_leaves=None);fr=sc['frames'][0]
 assert np.array_equal(sc['ids'][0],ids)
 struct=rh.node_tree(fr,ids)
 txt(left+width/2,.908,str(a['dates'][t])[11:16],15,bold=True,ha='center')
 s=fig.add_axes([left,.492,width,.390]);i=int(f['source_indices'][t]);raw=np.asarray(source['msl'][i],float)/100-np.asarray(source['msl'][i-96:i+96],float).mean(0)/100
 z=RegularGridInterpolator((lat,lon),raw)(pts);s.imshow(z,origin='lower',extent=extent,cmap=cm,norm=norm,interpolation='bilinear',rasterized=True)
 geo.coastlines(s,CODE/'data/geo/ne_110m_coastline.geojson',color='#3D464E',lw=.6,alpha=.9);s.set(xlim=extent[:2],ylim=extent[2:],xticks=[],yticks=[],aspect='equal')
 for j,tr in enumerate(tracks):
  lab=rev.get(int(tr));pt=xy(*a['lonlat'][t,j]);s.plot(*pt,marker=mark[lab] if lab else 'o',mfc='white' if lab else FAINT,mec=INK if lab else GRAY,ms=7 if lab else 4,zorder=6)
  if lab:
   offset=(8,5)
   if t>=605:offset={'A':(6,-16),'B':(-20,7),'C':(7,4)}[lab]
   s.annotate(lab,pt,xytext=offset,textcoords='offset points',fontsize=13,fontweight='bold')
 base=np.array(xy(10,36));vec=np.array(a['direction'])*650;s.annotate('',xy=base+vec,xytext=base-vec,arrowprops=dict(arrowstyle='->',color=INK,lw=1));s.text(*(base+vec+[90,0]),'d',fontsize=12)
 # Full branching topology: unary nodes suppressed, schematic vertical spacing.
 tree=fig.add_axes([left,.280,width,.190]);tree.set(xlim=(-.6,n-.4),ylim=(-.65,4.5));tree.axis('off')
 def leaves(st):return [st] if isinstance(st,int) else sum([leaves(ch) for ch in st[1]],[])
 def sort(st):return st if isinstance(st,int) else [st[0],sorted([sort(ch) for ch in st[1]],key=lambda ch:min(q[j] for j in leaves(ch)))]
 st=sort(struct);order=leaves(st);positions={j:k for k,j in enumerate(order)}
 def draw(st):
  if isinstance(st,int):
   xx=positions[st];tr=int(tracks[st]);lab=rev.get(tr);tree.plot(xx,0,marker=mark[lab] if lab else 'o',mfc='white' if lab else FAINT,mec=INK if lab else GRAY,ms=6 if lab else 4,zorder=4)
   if lab:tree.text(xx,-.31,lab,ha='center',va='top',fontsize=13,weight='bold')
   return xx,0
  ch=[draw(c) for c in st[1]];yy=max(v for _,v in ch)+1;xx=np.mean([x for x,_ in ch]);tree.plot([min(x for x,_ in ch),max(x for x,_ in ch)],[yy,yy],color=INK,lw=1.2)
  for x,y in ch:tree.plot([x,x],[y,yy],color=INK,lw=1.2)
  return xx,yy
 draw(st)
 # Reference / P / R positions share a fixed, disclosed coordinate range.
 pos=fig.add_axes([left,.070,width,.182]);pos.set(xlim=(.10,.52),ylim=(-.55,2.5),xticks=[.1,.3,.5],yticks=[2,1,0],yticklabels=['q','P','R']);pos.tick_params(axis='both',length=0,labelsize=11,pad=4)
 for sp in pos.spines.values():sp.set_visible(False)
 for y in [2,1,0]:pos.plot([.1,.52],[y,y],color='#D5DADD',lw=.75,zorder=0)
 for j,tr in enumerate(tracks):
  lab=rev.get(int(tr));up=float(b['normP'][column,j]);ur=float(a['normR'][t,j]);qq=float(q[j])
  if lab:
   pos.plot([qq,qq],[-.18,2.15],color=GRAY,lw=.75,ls=(0,(2,3)),zorder=0)
   pos.plot([qq,up,ur],[2,1,0],color='#A9B0B5',lw=.75,zorder=1)
  for y,v,c in [(2,qq,INK),(1,up,P),(0,ur,R)]:pos.plot(v,y,marker=mark[lab] if lab else 'o',mfc='white' if lab else FAINT,mec=c if lab else GRAY,ms=7 if lab else 3.5,mew=1.3,zorder=3 if lab else 2)
  if lab:
   dx,dy=(0,10)
   if t==605 and lab=='B':dx,dy=(9,10)
   if t==605 and lab=='C':dx,dy=(-8,10)
   if t==607 and lab=='B':dx,dy=(-6,10)
   if t==607 and lab=='C':dx,dy=(8,10)
   pos.annotate(lab,(qq,2),xytext=(dx,dy),textcoords='offset points',fontsize=12,weight='bold',ha='center')
 pos.get_yticklabels()[1].set_color(P);pos.get_yticklabels()[2].set_color(R)
 M=np.array([[fr.values[fr.lca(int(i),int(j))] for j in ids] for i in ids]);metrics={}
 for key,mp,u in [('P',b['mapP'],b['normP'][column,:n]),('R',a['mapR'],a['normR'][t,:n])]:
  mt=int(np.flatnonzero(b['map_frames']==t)[0]) if key=='P' else t
  anchors=np.rint(u*(len(mp)-1)).astype(int);errors=[]
  for i,j in combinations(range(n),2):
   l,h=sorted((anchors[i],anchors[j]));errors.append(abs(float(mp[l:h+1,mt].max())-M[i,j]))
  metrics[key]=dict(max_displacement_pct_L=float(100*np.max(abs(u-q))),max_merge_error_hPa=max(errors,default=0),mean_merge_error_hPa=float(np.mean(errors)))
 records.append(dict(frame=t,date=str(a['dates'][t]),tracks=tracks.tolist(),tree=struct,references=q.tolist(),P=b['normP'][column,:n].tolist(),R=a['normR'][t,:n].tolist(),metrics=metrics))
source.close()

# Matched real scalar images from all seven hourly profiles, not five irregular samples.
for key,y,color in [('P',.585,P),('R',.195,R)]:
 txt(.800,y+.315,'RG-MTM-P' if key=='P' else 'RG-MTM-R20',14,color=color,bold=True)
 ax=fig.add_axes([.800,y,.181,.285]);mp=b['mapP'] if key=='P' else a['mapR'][:,601:608]
 image=ax.imshow(mp,origin='lower',extent=[600.5,607.5,0,1],aspect='auto',cmap=cm,norm=norm,interpolation='nearest',rasterized=True)
 ax.set(xlim=(600.5,607.5),ylim=(.1,.52),yticks=[.1,.3,.5],xticks=frames);ax.tick_params(labelsize=10)
 ax.set_xticklabels([] if key=='P' else ['01','02','03','05','07'])
 ax.set_ylabel('Position',fontsize=11,labelpad=2)
 if key=='R':ax.set_xlabel('26 Dec (UTC hour)',fontsize=11,labelpad=4)
 for tt in frames:ax.axvline(tt,color='white',lw=.6,ls=':',alpha=.65,zorder=2)
 for lab,tr in labs.items():
  vals=[]
  for k,tt in enumerate(range(601,608)):
   j=int(np.flatnonzero(a['tracks'][tt]==tr)[0]);vals.append(float(b['normPmap'][k,j] if key=='P' else a['normR'][tt,j]))
  ax.plot(range(601,608),vals,color='white',lw=2.7,zorder=4);ax.plot(range(601,608),vals,color=color,lw=1.4,zorder=5)
  dy={'A':-.012,'B':-.018 if key=='P' else .005,'C':.008 if key=='P' else -.018}[lab]
  ax.text(600.58,vals[0]+dy,lab,fontsize=10,color=color,fontweight='bold',zorder=6)
cbax=fig.add_axes([.800,.068,.181,.015]);cb=fig.colorbar(image,cax=cbax,orientation='horizontal',ticks=[-35,0,35]);cb.ax.tick_params(labelsize=10);cb.outline.set_visible(False)
txt(.800,.103,'Pressure anomaly (hPa)',11)
txt(.040,.018,'q  Reference     P  Preserve topology     R  Local relaxation',11)
txt(.435,.018,'●  Other extrema',10,color=GRAY)
txt(.744,.018,'Range: 0.10–0.52 L',10,ha='right',color=GRAY)

for fmt in ['png','pdf','svg']:fig.savefig(OUT/f'Fig1_RG_MTM_v3.{fmt}',dpi=240 if fmt=='png' else 300,facecolor='white')
plt.close(fig)
assert all(sha(PAPER/k)==v for k,v in before.items())
report=dict(selected_frames=frames,selection='Five snapshots at 01:00,02:00,03:00,05:00,07:00 cover sustained conflict and the subsequent topology changes',labels=labs,source_population='744-hour hourly anomaly experiment; independent of 118-frame quantitative sequence',topology_encoding='complete branching structure, unary nodes suppressed; vertical spacing schematic, not scalar height',gray_markers='all other extracted extrema, retained in topology and position maps',position_limits=[.1,.52],metric_scope='all leaves and all leaf pairs at each selected frame, not only A/B/C',records=records,original_files_unchanged=True,protected_hashes=before,right_maps=dict(frames=list(range(601,608)),hourly_scalar_columns_unchanged=True,shared_position_limits=[.1,.52],P_source='positions.npz',R_source='frozen original R20 output'))
(OUT/'evidence.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([dict(frame=r['frame'],metrics=r['metrics']) for r in records],indent=2))
