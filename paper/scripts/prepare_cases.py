"""Render saved scientific arrays; never run experimental construction or selection."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LinearSegmentedColormap
from PIL import Image
from scene import *
ROOT=BASE.parent/'code'; DATA=ROOT/'results/real_case_studies/evidence';LAY=BASE/'evidence/layers';LAY.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'analysis'))
ABC=[BLUE,ORANGE,GREEN]; CHECK=[]
FILE_STEMS={'era5':'storms','wildfire':'wildfires','gaussians':'gaussian'}
def file_stem(name):return FILE_STEMS.get(name,name)
def load(n):
 a=np.load(DATA/f'{n}.npz');m=json.loads((DATA/f'{n}.json').read_text());e=json.loads((DATA/f'{n}_event.json').read_text());v=BASE/'checks/verified_case_metrics.json'
 if v.exists():
  row=json.loads(v.read_text())[n];e['frame_metrics']['actual_max_merge_error']=row['measured_max_merge_error'];e['frame_metrics']['actual_NMLE']=row['measured_NMLE']
 return a,m,e
def ix(a,t,tr):
 j=np.flatnonzero(a['track'][t]==tr);return int(j[0]) if len(j) else None
def style(n,a):
 if n=='era5':return plt.get_cmap('RdBu_r'),Normalize(min(a['mapR'].min(),a['mapP'].min()),max(a['mapR'].max(),a['mapP'].max()))
 if n=='wildfire':
  c=plt.get_cmap('inferno').copy();c.set_under(SKY);return c,Normalize(0,a['field'].max())
 tf=json.loads((ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json').read_text())['transfer_function_points']
 return LinearSegmentedColormap.from_list('original',[(v[0],tuple(v[1:4])) for v in tf],N=2048),Normalize(0,2)
def raster(v,p,c,n):Image.fromarray((c(n(v[::-1]))*255).astype('uint8')).save(p)
def fit(rect,ratio):
 x,y,w,h=rect
 if w/h>ratio:w=h*ratio;x+=(rect[2]-w)/2
 else:h=w/ratio;y+=(rect[3]-h)/2
 return x,y,w,h

def image_field(s,n,a,t,rect,e):
 p=LAY/f'{file_stem(n)}_field_{t}.png'
 if n=='tangaroa':
  v=np.load(DATA/'tangaroa_volumes.npz');j=e['selection']['snapshots'].index(t);Image.fromarray(np.rint(np.clip(v['images'][j][::-1],0,1)*255).astype('uint8')).save(p);r=fit(rect,650/237)
  uv=lambda xyz:np.r_[xyz,1]@v['transform']
  residual=float(np.max(np.abs(np.c_[v['corners'],np.ones(8)]@v['transform']-v['projected'])))
  assert residual<1e-8
  project=lambda xyz:(r[0]+(uv(xyz)[0]+1)/2*r[2],r[1]+(1-uv(xyz)[1])/2*r[3])
  coord='xyz'
 else:
  from geo import Era5Geo
  if n=='era5':
   g=Era5Geo(dict(lon=(-40,50),lat=(25,80)),a['coords']);ext=g.extent;lon,lat=np.meshgrid(a['raw_lon'],a['raw_lat']);X,Y=g.xy(lon,lat)
  else:ext=[0,120,0,120]
  ratio=(ext[1]-ext[0])/(ext[3]-ext[2]);r=fit(rect,ratio)
  fig=plt.figure(figsize=(r[2]/100,r[3]/100),dpi=300);ax=fig.add_axes([0,0,1,1])
  if n=='era5':
   c,no=style(n,a);ax.pcolormesh(X,Y,a['raw_field'][t],shading='nearest',cmap=c,norm=no);g.coastlines(ax,ROOT/'data/geo/ne_110m_coastline.geojson',lw=.5)
  else:ax.imshow(a['raw_field'][t],origin='lower',extent=ext,cmap='inferno',vmin=0,vmax=float(a['raw_field'].max()),interpolation='nearest')
  ax.set(xlim=ext[:2],ylim=ext[2:],aspect='auto');ax.axis('off');fig.savefig(p,dpi=300);plt.close(fig)
  project=lambda xy:(r[0]+(xy[0]-ext[0])/(ext[1]-ext[0])*r[2],r[1]+(ext[3]-xy[1])/(ext[3]-ext[2])*r[3]);coord='xy';residual=0
 s.image(p,*r,name=f'{n}_source_frame_{t}')
 if n!='tangaroa':
  origin=np.array([ext[0]+.16*(ext[1]-ext[0]),ext[2]+.16*(ext[3]-ext[2])]);tip=origin+a['direction']*.20*min(ext[1]-ext[0],ext[3]-ext[2]);p0=project(origin);p1=project(tip);ac='white'if n=='wildfire'else INK;s.line(*p0,*p1,ac,1.8)
  vec=np.array(p1)-np.array(p0);vec=vec/np.linalg.norm(vec);perp=np.array([-vec[1],vec[0]])
  for sign in [-1,1]:
   tail=np.array(p1)-vec*6+sign*perp*3;s.line(*tail,*p1,ac,1.5)
  s.text('d',p1[0]+3,p1[1]-13,24,23,17,ac,True)
 for k,tr in enumerate(e['selection']['tracks']):
  j=ix(a,t,tr)
  if j is None:continue
  x,y=project(a[coord][t,j]);s.dot(x,y,ABC[k],4.3,fill='white',name=f'{n}_space_{tr}_t{t}');dx=9 if x<r[0]+r[2]*.8 else -21;dy=-23 if y>r[1]+22 else 6
  s.text('ABC'[k],x+dx,y+dy,28,25,18,ABC[k],True)
  CHECK.append(dict(case=n,frame=t,track=tr,source_coordinate=a[coord][t,j].tolist(),ppt=[x,y],image_rect=r,projection_corner_maxresidual=residual))
 s.text(f'f{t}  {str(a["dates"][t])[:16]}',rect[0],rect[1]-25,rect[2],24,17,GRAY)
 return r

def map_panel(s,n,a,e,method,rect,window=None,mark=True):
 x,y,w,h=rect;T=len(a['track']);lo,hi=window or (0,T);arr=a['map'+method][:,lo:hi];yl,yh=0.,1.
 if window:
  yy=[float(a['norm'+method][t,j]) for t in range(lo,hi) for tr in e['selection']['tracks'] if (j:=ix(a,t,tr)) is not None]
  if method in ['P','R']:yy +=[float(a['qnorm'][t,j]) for t in range(lo,hi) for tr in e['selection']['tracks'] if (j:=ix(a,t,tr)) is not None]
  yl=max(0,min(yy)-.05);yh=min(1,max(yy)+.05);N=arr.shape[0];i0=int(np.floor(yl*(N-1)));i1=int(np.ceil(yh*(N-1)))+1;yl=i0/(N-1);yh=(i1-1)/(N-1);arr=arr[i0:i1]
 p=LAY/f'{file_stem(n)}_{method}_{lo}_{hi}.png';c,no=style(n,a);raster(arr,p,c,no);im=Image.open(p);im.resize((round(w*3),round(h*3)),Image.Resampling.NEAREST).save(p);s.image(p,x,y,w,h,name=f'{n}_{method}_saved_scalar_layer_{lo}_{hi}')
 # Raster display uses row-bin edges; exact anchor coordinates are independent overlays.
 def pos(t,v):return (x+(t-lo+.5)/(hi-lo)*w,y+(yh-v)/(yh-yl)*h)
 key=e['selection']['t'];xx,_=pos(key,yl);s.line(xx,y,xx,y+h,INK,1,True)
 s.rect(x,y,w,h,'none',GRAY,.7)
 for v in [yl,yh]:s.text(f'{v:.2f}'if window else f'{v:g}',x-39,y+(yh-v)/(yh-yl)*h-10,33,21,15,GRAY,align='right')
 for t in [lo,hi-1]:s.text(str(t),pos(t,yl)[0]-20,y+h+3,40,22,16,GRAY,align='center')
 if mark:
  for k,tr in enumerate(e['selection']['tracks']):
   pts=[];refs=[]
   for t in range(lo,hi):
    j=ix(a,t,tr)
    if j is not None:
     pts.append(pos(t,float(a['norm'+method][t,j])));refs.append(pos(t,float(a['qnorm'][t,j])))
   if window and len(pts)>1:s.path(pts,'white',4);s.path(pts,ABC[k],1.8,name=f'{n}_{method}_track_{tr}_trace')
   if window and method in ['P','R'] and len(refs)>1:s.path(refs,ABC[k],1,True,name=f'{n}_{method}_true_reference_{tr}')
   j=ix(a,key,tr);xp,yp=pos(key,float(a['norm'+method][key,j]));s.dot(xp,yp,ABC[k],4,fill='white',name=f'{n}_{method}_{tr}_exact_anchor')
   if window:
    lx=x+w+9;ly=y+5+k*(h-20)/3;s.line(xp,yp,lx-3,ly+10,ABC[k],.8);s.text('ABC'[k],lx,ly,28,22,17,ABC[k],True)
   CHECK.append(dict(case=n,frame=key,track=tr,method=method,anchor=float(a['norm'+method][key,j]),ppt=[xp,yp],rect=rect,frame_domain=[lo-.5,hi-.5],y_domain=[yl,yh]))
 return pos

def colorbar(s,n,a,x,y,w,label):
 c,no=style(n,a);v=np.linspace(no.vmin,no.vmax,256)[None,:];p=LAY/f'{file_stem(n)}_bar.png';raster(v,p,c,no);im=Image.open(p);im.resize((round(w*3),30),Image.Resampling.NEAREST).save(p);s.image(p,x,y,w,10)
 s.text(f'{no.vmin:.2f}',x,y+12,85,22,15,GRAY);s.text(f'{no.vmax:.2f}',x+w-80,y+12,80,22,15,GRAY,align='right');s.text(label,x,y-25,w,24,17,GRAY,align='center')
 if n=='wildfire':s.rect(x-19,y,10,10,SKY,SKY,0);s.text('<0',x-28,y+12,35,22,15,GRAY)

def witness_tree(s,e,x,y,w,h):
 pairs=e['pair_merge_levels'];a=pairs[0]['true'];b=pairs[1]['true'];join=e['case']!='wildfire'
 # Scalar ordinate is mapped from true values, not freely shifted.
 vals=[o['scalar'] for o in e['observations']if o['frame']==e['selection']['t']];mn=min(vals+[a,b]);mx=max(vals+[a,b]);
 if mx==mn:mx+=1
 sc=lambda v:y+h-(v-mn)/(mx-mn)*h
 pts=[(x,sc(vals[0])),(x+w*.4,sc(vals[1])),(x+w,sc(vals[2]))];p=(x+w*.2,sc(a));r=(x+w*.6,sc(b))
 for v in pts[:2]:s.line(*v,*p,GRAY,1.7)
 s.line(*p,*r,GRAY,1.7);s.line(*pts[2],*r,GRAY,1.7)
 for k,v in enumerate(pts):s.dot(*v,ABC[k],5);s.text('ABC'[k],v[0]-8,v[1]+9,25,25,18,ABC[k],True)
 for v,val in [(p,a),(r,b)]:s.dot(*v,INK,4);s.text(f'{val:.3f}'if e['case']!='era5'else f'{val:.1f}',v[0]+8,v[1]-16,100,23,17,GRAY)

def teaser():
 n='era5';a,m,e=load(n);s=Scene(1,'From hierarchy conflict to measured trade-off',notes=json.dumps({'source':'frozen real_case_studies/evidence','case':n,'selection':e['selection'],'semantics':e['baseline_vertical_semantics']}))
 s.text('(a) Real pressure minima, frame 48',22,8,405,32,23,bold=True);image_field(s,n,a,48,(25,82,360,285),e)
 s.text('A60   B38   C56: computed feature IDs',25,391,400,28,19)
 d=a['direction'];start=np.array([55.,40.]);end=start+d*25
 # The reference direction is shown on the same scientific coordinate transform via a separate labelled axis.
 s.text('One fixed reference direction d',25,441,395,28,20,bold=True)
 s.line(45,490,345,490,INK,1.5);s.line(337,484,345,490,INK,1.5);s.line(337,496,345,490,INK,1.5)
 for k,tr in enumerate(e['selection']['tracks']):
  j=ix(a,48,tr);xx=45+300*a['qnorm'][48,j];s.dot(xx,490,ABC[k],5);s.text(f'{"ABC"[k]} {a["qnorm"][48,j]:.3f}',xx-23,510,90,27,17,ABC[k],True)
 s.text('Desired order A, C, B',25,572,398,30,21,bold=True)
 s.line(420,52,420,615,LIGHT,1)
 s.text('(b) A/B form one source subtree',446,8,422,32,23,bold=True);witness_tree(s,e,465,79,255,199)
 s.text('A, C, B separates the A/B block',447,328,415,32,20,ORANGE,bold=True)
 s.text('Minimum unavoidable displacement',447,393,412,30,21,bold=True)
 s.text('packing 0   +   hierarchy 8.45% L',447,440,420,35,23,ORANGE)
 s.text('Retain the block → displace B/C',447,511,418,30,20,BLUE)
 s.text('Release it → change merge levels',447,561,425,30,20,GREEN)
 s.line(879,52,879,615,LIGHT,1)
 s.text('(c) Same features, measured output',902,8,420,32,23,bold=True)
 for meth,y,title in [('P',102,'P: hierarchy preserved'),('R',311,'R20: relaxed ordering')]:
  s.text(title,940,y-35,365,30,21,bold=True);map_panel(s,n,a,e,meth,(950,y,304,120),tuple(e['selection']['window']))
 s.text('Max |u−q| / L: 8.87% → 0.83%',902,501,430,30,21,bold=True)
 s.text('Merge cost: 12.557 hPa (13.21%)',902,544,430,30,20)
 colorbar(s,n,a,949,600,304,'pressure (hPa)');s.save()

def cases(n,num):
 a,m,e=load(n);sel=e['selection'];key=sel['t'];T=len(a['track']);methods=m['methods'];methods=['TMTM','P','R'] if n=='tangaroa'else ['TMTM','ST-MTM','P','R'];N=len(methods)
 s=Scene(num,f'{n}: source features and temporal maps',notes=json.dumps({'source':'saved real_case_studies/evidence','case':n,'selection':sel,'identity':e['identity_scope'],'baseline_vertical_semantics':e['baseline_vertical_semantics'],'rendering':'exact saved anchors over native scalar maps; 3D display map is subsampled; no scientific values recomputed'}))
 s.text({'era5':'ERA5: a hierarchy-forced position conflict','wildfire':'Wildfire: source evolution versus layout displacement','tangaroa':'Tangaroa: 201 original-grid frames, fixed 10% persistence'}[n],18,4,1230,32,24,bold=True)
 s.text(f'Full sequence ({T} frames); vertical guide: f{key}',151,41,650,26,18,bold=True);s.text('Local window; circles: exact saved anchors',879,41,460,26,18,bold=True)
 rh=70 if N==4 else 94;gap=23
 for k,meth in enumerate(methods):
  y=80+k*(rh+gap);name={'P':'RG-P','R':'RG-R20'}.get(meth,meth);s.text(name,16,y+5,111,26,20,bold=True)
  s.text('native rank'if meth in ['TMTM','ST-MTM']else'fixed q axis',16,y+36,113,22,16,GRAY)
  map_panel(s,n,a,e,meth,(153,y,618,rh));map_panel(s,n,a,e,meth,(886,y,396,rh),tuple(sel['window']))
  lx=153+(sel['window'][0])/T*618;ww=(sel['window'][1]-sel['window'][0])/T*618;s.rect(lx,y,ww,rh,'none',INK,1.2)
 bottom=491 if N==4 else 457;h=118 if N==4 else 145
 for j,t in enumerate(sel['snapshots']):image_field(s,n,a,t,(15+j*265,bottom,248,h),e)
 xx=829;s.text('A/B/C IDs: '+', '.join(map(str,sel['tracks'])),xx,454 if N==4 else 416,490,26,19,bold=True)
 fm=e['frame_metrics'];s.text(f'f{key}: max displacement (% L)',xx,490 if N==4 else 452,490,26,19,bold=True)
 s.text(f'P {100*fm["achieved_max_P"]:.2f} → R {100*fm["achieved_max_R"]:.2f}',xx,519 if N==4 else 481,490,27,22,GREEN,bold=True)
 s.text(f'Hierarchy {100*fm["H"]:.2f}% L; NMLE {100*fm["actual_NMLE"]:.2f}%',xx,552 if N==4 else 514,490,27,19)
 colorbar(s,n,a,xx,605,410,'pressure (hPa)'if n=='era5'else'processed log1p FRP'if n=='wildfire'else'processed speed [0, 2]')
 if n=='wildfire':s.text(f'Raw source snapshots: log1p FRP 0–{a["raw_field"].max():.2f} (fixed)',15,614,780,24,17,GRAY)
 s.save()

def frontier():
 a,m,e=load('era5');f=json.loads((ROOT/'results/attainable_era5.json').read_text());s=Scene(4,'Certificates, attainable trade-off and scalar correction',notes='All values from frozen attainable_era5.json and frozen event arrays. Frontiers are frame means at one common budget D. Working points use the mean fixed-order positional optimum and the maximum fixed-order scalar optimum over frames; they are not final achieved anchor errors. Bars compare same selected order and frame-mean analytical scalar costs.')
 s.text('(a) Diagnose the conflict',22,9,420,32,24,bold=True);s.text('ERA5: packing + hierarchy cost',22,53,423,28,20)
 x,y,w,h=70,110,350,325
 def xy(t,v):return(x+t/117*w,y+h-v/.30*h)
 for v in [0,.1,.2,.3]:
  xx,yy=xy(0,v);s.line(x-3,yy,x+w,yy,LIGHT,1);s.text(f'{100*v:.0f}',x-41,yy-12,34,24,17,GRAY,align='right')
 s.text('% L',22,79,70,24,17,GRAY)
 s.path([xy(i,float(v))for i,v in enumerate((a['F']+a['H'])/a['geometry'][1])],ORANGE,2.2,False,'Exact_original_tree_certificate')
 s.path([xy(i,float(v))for i,v in enumerate(a['F']/a['geometry'][1])],GRAY,1.8,False,'Free_packing_cost')
 xp,yp=xy(48,float(a['H'][48]/a['geometry'][1]));s.dot(xp,yp,ORANGE,5);s.line(xp,y,xp,y+h,GRAY,1,True);s.text('f48',xp+8,yp-28,70,26,19,ORANGE,True)
 for t in [0,48,117]:s.text(str(t),xy(t,0)[0]-17,y+h+7,55,24,18,GRAY)
 s.text('orange: τ* = packing + H',24,496,418,28,20,ORANGE);s.text('gray: free packing cost',24,534,418,28,20,GRAY);s.text('f48: H = 8.45% L; packing = 0',24,579,430,28,20,bold=True)
 s.text('(b) Position–scalar exchange',476,9,455,32,24,bold=True);s.text('ERA5: all 118 frames',476,53,430,28,20)
 x,y,w,h=526,110,342,325;maxD=1.;maxE=.046
 def pt(d,v):return(x+d/maxD*w,y+h-v/maxE*h)
 for v in [0,.01,.02,.03,.04]:
  xx,yy=pt(0,v);s.line(x,yy,x+w,yy,LIGHT,1);s.text(f'{100*v:.0f}',x-35,yy-12,30,24,17,GRAY,align='right')
 for d in [0,.25,.5,.75,1.]:s.text(f'{100*d:.0f}',pt(d,0)[0]-20,y+h+7,45,24,18,GRAY,align='center')
 s.text('mean position cost (% L)',476,81,416,24,17,GRAY);s.text('Common scalar budget D (% range)',501,477,414,24,17,GRAY)
 for key,c,da in [('F',BLUE,False),('Phi',GRAY,True)]:s.path([pt(row['delta'],row[key]) for row in f['frontier']],c,2.2,da,name=f'Mean_{key}_under_common_budget')
 for idx,o in enumerate(f['ours']):
  if o['cap'] not in [0,.02,.2]:continue
  px,py=pt(o['D_opt_share'],o['E_share']);s.dot(px,py,GREEN,5);label='P'if o['cap']==0 else'R2'if o['cap']==.02 else'R20';s.text(label,px+7,py-21 if label!='R2'else py+6,75,25,18,GREEN,True)
 s.text('blue: exact mean attainable F',477,524,445,28,19,BLUE);s.text('dashed: necessary lower bound Φ',477,559,450,28,19,GRAY);s.text('green: selected-order optima',477,594,450,28,19,GREEN)
 s.text('(c) Same order, better filling',948,9,390,32,24,bold=True);s.text('Frame-mean scalar cost (% range)',948,53,385,28,19)
 xx,yy,ww,hh=1022,110,250,325
 for v in [0,2,4,6]:
  py=yy+hh-v/6*hh;s.line(xx,py,xx+ww,py,LIGHT,1);s.text(str(v),xx-28,py-12,22,24,17,GRAY)
 for k,name in enumerate(['era5','fire','ring']):
  fn=ROOT/f'results/attainable_{name}.json'
  if not fn.exists():fn=ROOT/f'results/attainable_{"wildfire"if name=="fire"else name}.json'
  data=json.loads(fn.read_text());o=next(v for v in data['ours']if abs(v['cap']-.2)<1e-9)
  for j,(key,c) in enumerate([('mean_d_lca_share',GRAY),('mean_d_opt_share',GREEN)]):
   v=o[key]*100;bx=xx+12+k*81+j*29;s.rect(bx,yy+hh-v/6*hh,26,v/6*hh,c,c,0);s.text(f'{v:.2f}',bx-4,yy+hh-v/6*hh-26,45,24,16,c)
  s.text(['ERA5','Fire','Ring'][k],xx+k*81,yy+hh+8,90,24,18,GRAY)
 s.text('gray: original-LCA filling',950,524,380,28,19,GRAY);s.text('green: minimax barriers',950,559,380,28,19,GREEN);s.text('No change of selected leaf order',950,594,390,28,18,bold=True);s.save()
if __name__=='__main__':
 teaser();cases('era5',5);cases('wildfire',6);cases('tangaroa',7);frontier();(BASE/'checks/real_case_coordinate_transforms.json').write_text(json.dumps(CHECK,indent=2));print('Saved scientific layers, native overlays, and coordinate records',len(CHECK))
