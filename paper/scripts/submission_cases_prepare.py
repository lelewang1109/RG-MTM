"""Reproduce new case and appendix figures exclusively from stored results.
No layout/tree construction. Native scientific overlays are serialized to artifact-tool.
"""
from pathlib import Path
import json, hashlib, itertools, shutil, sys
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
from matplotlib import colormaps
from matplotlib.colors import Normalize,SymLogNorm,LinearSegmentedColormap
R=Path(__file__).resolve().parents[1]; BASE=R/'.build/case-figures-20261023'; ROOT=R.parent; C=ROOT/'code'; AS=BASE/'assets'; SC=BASE/'scenes'; CK=BASE/'checks'
for d in (AS,SC,CK):d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'scripts'))
from scene import Scene
BLACK='#000000';BLUE='#0072B2';ORANGE='#D55E00';GREEN='#009E73';GRAY='#7B8790';COL=[BLUE,ORANGE,GREEN]
SOURCES={}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def record(p):SOURCES[str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else str(p)]=sha(p)
def load(p):record(p);return json.loads(Path(p).read_text())
def raster(v,p,cm,norm):Image.fromarray(np.rint(np.clip(cm(norm(v[::-1])),0,1)*255).astype('uint8')).save(p)
def write(s,stem):
 for o in s.d['objects']:
  if o['kind']=='text':o['color']=BLACK
 (SC/(stem+'.json')).write_text(json.dumps(s.d,indent=2))
def axes(s,x,y,w,h,xlim,ylim,xticks,yticks,xlabel):
 def xy(a,b):return [x+(a-xlim[0])/(xlim[1]-xlim[0])*w,y+h-(b-ylim[0])/(ylim[1]-ylim[0])*h]
 s.rect(x,y,w,h,'none',GRAY,.7)
 for v in xticks:
  xx,yy=xy(v,ylim[0]);s.text(f'{v:g}',xx-24,yy+5,48,21,16,align='center');s.line(xx,yy,xx,yy+4,BLACK,.7)
 for v in yticks:
  xx,yy=xy(xlim[0],v);s.text(f'{v:g}',xx-55,yy-9,48,21,16,align='right');s.line(xx-4,yy,xx,yy,BLACK,.7)
 s.text(xlabel,x,y+h+30,w,24,17,align='center');return xy

def cylinder():
 p=C/'results/paper1_suite/square-cylinder3d'; d=ROOT/'data/real/paper1_suite/square-cylinder3d';f=load(p/'features.json');rows=load(p/'frame_metrics.json');pa=load(p/'parameters.json');pr=load(p/'protocol.json');fs=f['frames'];tracks=f['tracks'];L=pa['canvas'];origin=pa['canvas_origin'];rr={(r['index'],r['method']):r for r in rows}
 cand=[]
 for t in range(1,len(fs)-1):
  a=rr[t,'RG-MTM-P'];b=rr[t,'RG-MTM-R 0.02'];q=np.array(a['layout']['reference']);H=a['H_upper']/L;gain=(max(abs(np.array(a['positions'])-q))-max(abs(np.array(b['positions'])-q)))/L
  if H<=.02 or gain<=0 or b['NMLE']<=0:continue
  stable=set(tracks[t-1])&set(tracks[t])&set(tracks[t+1]);inds=[i for i,tr in enumerate(tracks[t])if tr in stable];lc=np.array(fs[t]['source_lca_values']);best=None
  for i,j in itertools.combinations(inds,2):
   for k in inds:
    if k in (i,j) or (q[i]-q[k])*(q[j]-q[k])>=0 or lc[i,j]>=min(lc[i,k],lc[j,k])-1e-8:continue
    sep=min(abs(q[i]-q[k]),abs(q[j]-q[k]))/L
    if best is None or sep>best[0]:best=(sep,i,j,k)
  if best: cand.append(dict(t=t,H=H,gain=gain,witness=best[1:],sep=best[0]))
 hs=np.array([r['H']for r in cand]);gs=np.array([r['gain']for r in cand]);hm=float(np.median(hs));gm=float(np.median(gs));hd=max(float(np.subtract(*np.quantile(hs,[.75,.25]))),1e-8);gd=max(float(np.subtract(*np.quantile(gs,[.75,.25]))),1e-8)
 for row in cand:row['score']=abs(row['H']-hm)/hd+abs(row['gain']-gm)/gd
 ev=min(cand,key=lambda a:(a['score'],a['t']));t=ev['t'];ii=list(ev['witness']);a=rr[t,'RG-MTM-P'];b=rr[t,'RG-MTM-R 0.02'];r20=rr[t,'RG-MTM-R 0.2'];q=np.array(a['layout']['reference']);field=np.load(d/'source_fields.npy',mmap_mode='r');record(d/f'input_{t:03}.npy');record(d/'source_fields.npy');arrs={}
 for key,row in [('P',a),('R2',b),('R20',r20)]:
  fp=d/'maps'/Path(row['array']).name;record(fp);arrs[key]=np.load(fp);assert sha(fp)==row['array_sha256']
 # Actual sampled pair merge in the split tree: min Q along map interval. All figures in physical Q.
 pair=[];scale=pr['scalar_scale'];lc=np.array(fs[t]['source_lca_values']);
 for ni,nj in itertools.combinations(range(3),2):
  i,j=ii[ni],ii[nj];v={'pair':'ABC'[ni]+'ABC'[nj],'source_Q':float(-lc[i,j]*scale)}
  for key,row in [('P',a),('R2',b),('R20',r20)]:
   l,h=sorted([row['anchors'][i],row['anchors'][j]]);v[key+'_Q']=float(-np.max(arrs[key][l:h+1])*scale)
  pair.append(v)
 rule='Eligible frames have H>2% of axis, positive P-to-R2 maximum-displacement reduction and NMLE>0, plus a noncontiguous hierarchy witness whose three computed overlap tracks exist at t-1,t,t+1. Choose minimum sum of H and gain distance to eligible medians, each divided by its IQR. Earliest tie. Within the frame, choose witness with largest minimum intervening reference separation. Descriptive mechanism example, not aggregate performance evidence.'
 data=dict(selection=ev,rule=rule,eligible_count=len(cand),median_H=hm,median_gain=gm,selected_leaf_indices=ii,track_ids=[tracks[t][i]for i in ii],references=q[ii].tolist(),reference_definition='x coordinate of original-grid scalar extrema, fixed physical axis; not support centroid',extrema=np.array(fs[t]['extrema'])[ii].tolist(),pair_merge_Q=pair,NMLE_R2=b['NMLE'],NMLE_R20=r20['NMLE'],max_displacement_P=max(abs(np.array(a['positions'])-q))/L,max_displacement_R2=max(abs(np.array(b['positions'])-q))/L,candidates=cand)
 (CK/'cylinder_event.json').write_text(json.dumps(data,indent=2))
 # Append three native explanation panels below unchanged original full maps and 3-D views.
 s=Scene(10,'Cylinder source reference and merge-level mechanism',json.dumps(data));s.d.update(width=1240,height=930)
 y=600;s.text('(d) Source features, frame '+str(t),18,y,385,28,22,bold=True)
 # max over physical y; x/z from cropped original grid. Mark extrema (x,z), not guessed trajectories.
 qproj=np.max(field[t],axis=1);lo=origin;hi=origin+L;cm=colormaps['coolwarm'];norm=SymLogNorm(linthresh=.02,vmin=-20.46343994140625,vmax=20.46343994140625);ip=AS/'Cylinder_local_source.png';raster(qproj,ip,cm,norm);s.image(ip,54,651,305,160,'Cylinder_original_grid_max_y_Q');proj=axes(s,54,651,305,160,[lo,hi],[0,6],[0,10,20],[0,3,6],'x (source physical coordinate)')
 ext=np.array(fs[t]['extrema'])
 for k,i in enumerate(ii):
  xx,zz=ext[i,0],ext[i,2];xp,yp=proj(xx,zz);s.dot(xp,yp,COL[k],4.5,'white',f'source_extremum_{i}');s.text('ABC'[k],xp+7,yp-17,24,21,17,bold=True)
 s.text('Q maximum over y; markers show extrema (x,z)',18,868,385,22,15)
 s.text('(e) Reference and saved anchors',421,y,398,28,22,bold=True)
 xp=lambda v:475+(v-origin)/L*300
 yrows=[662,708,754,800];names=['q','P','R2','R20']
 for row,yy in zip(names,yrows):
  s.text(row,419,yy-11,49,22,17,bold=True);s.line(475,yy,775,yy,GRAY,.7)
 for k,i in enumerate(ii):
  vv=[q[i],a['positions'][i],b['positions'][i],r20['positions'][i]];pts=[[xp(v),yy]for v,yy in zip(vv,yrows)];s.path(pts,COL[k],1.2,name='feature_'+str(tracks[t][i])+'_reference_anchors')
  for x1,y1 in pts:s.dot(x1,y1,COL[k],4,'white')
  s.text('ABC'[k],xp(vv[0])-9,635,24,21,17,bold=True)
 for v in [0,.5,1]:s.text(f'{v:g}',475+300*v-18,816,36,21,16,align='center')
 s.text('Normalized x along fixed reference axis',421,842,390,24,17,align='center')
 s.text(f'f{t}: H={100*ev["H"]:.2f}% L; NMLE(R2)={100*b["NMLE"]:.3f}%',421,886,395,23,15)
 s.text('(f) Saved scalar profiles, same frame',831,y,400,28,22,bold=True)
 # all stored samples are used, simplified only along exactly linear display segments for editability
 vmin=min(-np.max(v)*scale for v in arrs.values());vmax=max(-np.min(v)*scale for v in arrs.values());vmin=min(vmin,-.05);vmax=max(vmax,.05)
 pos=axes(s,895,651,307,160,[0,1],[vmin,vmax],[0,.5,1],[round(vmin,2),0,round(vmax,2)],'Normalized reference coordinate')
 for key,color,dash in [('P',BLUE,True),('R2',GREEN,False)]:
  ar=-arrs[key]*scale;idx=np.arange(len(ar)); # simplify with RDP in slide pixels, tolerance <0.2px
  xy=np.column_stack([895+idx/(len(ar)-1)*307,811-(ar-vmin)/(vmax-vmin)*160]);keep=rdp(xy,.18);s.path(xy[keep].tolist(),color,1.4,dash,'complete_saved_'+key+'_Q_profile')
 s.text('Q',838,647,45,25,18,bold=True);s.text('P (dashed)',870,887,120,23,16);s.line(840,896,865,896,BLUE,1.6,True);s.text('R2',1110,887,65,23,16);s.line(1073,896,1104,896,GREEN,1.6)
 # native pair callout chosen for largest R2 scalar change among witness pairs
 pp=max(pair,key=lambda o:abs(o['R2_Q']-o['source_Q']));s.text(f'{pp["pair"]}: Qmerge {pp["source_Q"]:.3f} (source/P), {pp["R2_Q"]:.3f} (R2)',831,860,400,22,15)
 write(s,'Cylinder_additions');return data

def rdp(points,eps):
 if len(points)<=2:return np.arange(len(points))
 keep={0,len(points)-1};stack=[(0,len(points)-1)]
 while stack:
  a,b=stack.pop()
  if b<=a+1:continue
  v=points[b]-points[a];den=np.dot(v,v)
  d=np.linalg.norm(points[a+1:b]-points[a],axis=1)if den==0 else np.abs(np.cross(v,points[a+1:b]-points[a]))/np.sqrt(den)
  j=int(np.argmax(d))+a+1
  if d[j-a-1]>eps:keep.add(j);stack.extend([(a,j),(j,b)])
 return np.array(sorted(keep))

def wildfire():
 ep=C/'results/real_case_studies/evidence';ev=load(ep/'wildfire_event.json');record(ep/'wildfire.npz');a=np.load(ep/'wildfire.npz');t=ev['selection']['t'];s=Scene(8,'Wildfires measured scalar exchange',json.dumps(ev));s.d.update(width=1280,height=840)
 s.text('(d) Complete saved scalar profiles, frame 18',18,556,720,30,22,bold=True)
 vr=[min(float(a['map'+k][:,t].min())for k in ['P','R']),max(float(a['map'+k][:,t].max())for k in ['P','R'])];vr=[min(-.7,vr[0]),max(4.3,vr[1])];pos=axes(s,75,618,650,140,[0,1],vr,[0,.25,.5,.75,1],[-.5,0,2,4],'Normalized reference coordinate')
 for key,col,da in [('P',BLUE,True),('R',GREEN,False)]:
  ar=a['map'+key][:,t];xy=np.array([pos(x,y)for x,y in zip(np.linspace(0,1,len(ar)),ar)]);s.path(xy[rdp(xy,.15)].tolist(),col,1.8,da,'complete_saved_'+key+'_profile')
  for k,tr in enumerate(ev['selection']['tracks']):
   j=int(np.flatnonzero(a['track'][t]==tr)[0]);u=float(a['norm'+key][t,j]);vv=float(a['value'][t,j]);xx,yy=pos(u,vv);s.dot(xx,yy,COL[k],4.5,'white',f'{key}_true_anchor_{tr}')
   s.text('ABC'[k],xx+6,yy-21,24,23,17,bold=True)
 s.text('processed log1p FRP',18,590,380,22,17)
 s.text('(e) Pair merge levels',793,556,470,30,22,bold=True)
 pairs=ev['pair_merge_levels'];head=[('Pair',794,76),('Source = P',890,165),('R20',1083,145)]
 for text,x,w in head:s.text(text,x,607,w,24,18,bold=True)
 s.line(793,636,1248,636,GRAY,.8)
 for k,row in enumerate(pairs):
  yy=647+k*38
  for v,x,w in [(row['pair'],794,76),(f'{row["true"]:.4f}',890,165),(f'{row["R"]:.4f}',1083,145)]:s.text(v,x,yy,w,25,18)
 s.text('AB sets max error 0.6351 (15.09% range)',793,774,470,23,17,bold=True)
 s.text('P',82,808,35,22,17);s.line(49,818,75,818,BLUE,1.8,True);s.text('R20',235,808,80,22,17);s.line(198,818,225,818,GREEN,1.8)
 s.text('Pair levels use sampled interval minima; negative R connections are measured output',331,807,916,24,15)
 # independent recomputation of event pair levels at native anchors in saved 2048-bin scalar map
 checks=[]
 for row in pairs:
  ki,kj=['ABC'.index(x)for x in row['pair']];trs=ev['selection']['tracks'];i=int(np.flatnonzero(a['track'][t]==trs[ki])[0]);j=int(np.flatnonzero(a['track'][t]==trs[kj])[0]);v={}
  for key in ['P','R']:
   ar=a['map'+key][:,t];l,h=sorted([int(round(a['norm'+key][t,i]*(len(ar)-1))),int(round(a['norm'+key][t,j]*(len(ar)-1)))]);v[key]=float(np.min(ar[l:h+1]))
  checks.append(dict(pair=row['pair'],sampled=v,reported=row))
 (CK/'wildfires_profile_check.json').write_text(json.dumps(checks,indent=2));write(s,'Wildfires_additions')

def supplements():
 ev=load(C/'results/eval_projection.json')
 for name,label,stem,unit in [('olr','OLR','Supplement_OLR_Comparison','W m-2'),('pm25','PM2.5','Supplement_PM25_Comparison','ug m-3')]:
  paths=sorted((ROOT.parent/'其他/归档/历史或排除结果/visualization_cache').glob(name+'-*.npz'));assert paths
  ar=[np.load(p)for p in paths];a=ar[0];
  for p,z in zip(paths,ar):
   record(p)
   for k in a.files:assert np.array_equal(a[k],z[k]),(name,k,p)
  # restore one canonical frozen cache as reproducibility evidence, without overwriting archived input
  shutil.copyfile(paths[0],AS/(name+'_frozen_full_comparison.npz'))
  if name=='olr':
   fp=C/'results/publication2027/figure_data/olr_render.npz';record(fp);ref=np.load(fp);assert np.array_equal(ref['mapA'],a['A']);assert np.array_equal(ref['mapR'],a['R 20%'])
  rep=load(C/f'results/replicate_{name}.json')
  if name=='pm25':
   sys.path[:0]=[str(C/'analysis'),str(C/'src'),str(C)]
   import public_scalar as ps
   fields,coords,*_=ps.prepare_fields('pm25')
   metrics=load(C/'results/public_metrics_20261016/pm25.json');lmfile=C/'results/public_metrics_20261016/pm25_landmarks.npz';record(lmfile);lm=np.load(lmfile)
   ah=lambda z:hashlib.sha256(str((z.shape,z.dtype.str)).encode()+z.tobytes()).hexdigest()
   assert ah(fields)==metrics['input_sha256']['fields'];assert ah(coords)==metrics['input_sha256']['coords']
   audit={'input_array_hashes_match':True,'dates':[str(lm['dates'][0]),str(lm['dates'][-1])],'frames':len(fields),'anchor_residuals':{},'anchor_counts':{}}
   for j,key in enumerate(['TMTM','ST-MTM','A','R 20%']):
    errors=[]
    for t,n in enumerate(lm['count']):
     u=lm['u'+str(j)][t,:n];truth=fields[t].ravel()[lm['feature_ids'][t,:n]];samples=a[key][np.rint(u*(a[key].shape[0]-1)).astype(int),t];errors.extend(samples-truth)
    assert max(abs(np.array(errors)))==0;audit['anchor_residuals'][key]=0.;audit['anchor_counts'][key]=len(errors)
   (CK/'pm25_current_input_cache_audit.json').write_text(json.dumps(audit,indent=2))
  s=Scene(0,label+' full method comparison');s.d.update(width=1280,height=830)
  mn=min(float(a[k].min())for k in ['TMTM','ST-MTM','A','R 20%']);mx=max(float(a[k].max())for k in ['TMTM','ST-MTM','A','R 20%']);cm=colormaps['RdBu_r'];norm=Normalize(mn,mx);T=a['A'].shape[1]
  for j,(key,title)in enumerate([('TMTM','TMTM'),('ST-MTM','ST-MTM'),('A','RG-MTM-P'),('R 20%','RG-MTM-R20')]):
   x=62+(j%2)*638;y=52+(j//2)*270;w=552;h=181
   s.text('('+chr(97+j)+') '+title,x-35,y-42,580,28,23,bold=True);ip=AS/(name+'_'+key.replace(' ','_').replace('%','')+'.png');raster(a[key],ip,cm,norm);s.image(ip,x,y,w,h,name+'_'+key+'_all_saved_frames');axes(s,x,y,w,h,[-.5,T-.5],[0,1],[0,(T-1)//2,T-1],[0,.5,1],'Frame')
   coord='Normalized native sample rank'if j<2 else'Normalized fixed reference axis';s.text(coord,x+30,y-25,w-60,22,16,align='center')
  # shared scalar colorbar and native labels
  bar=AS/(name+'_bar.png');raster(np.linspace(mn,mx,512)[None,:],bar,cm,norm);s.image(bar,330,578,570,13)
  s.text(f'{mn:.2f}',274,598,100,22,16,align='center');s.text(f'{mx:.2f}',856,598,100,22,16,align='center');s.text(label+' ('+unit+')',457,598,320,22,17,align='center')
  s.text('(e) Complete-sequence motion proxy at lag 2, epsilon 2%',25,641,1230,27,22,bold=True)
  cols=[25,280,540,800,1060];ws=[230,245,245,245,200];heads=['Method','TMTM','ST-MTM','RG-MTM-P','RG-MTM-R20']
  for txt,x,w in zip(heads,cols,ws):s.text(txt,x,683,w,23,18,bold=True)
  proxy=[]
  for key in ['TMTM','ST-MTM','ours: auto direction','ours: relaxed']:proxy.append(next(x for x in rep['misreading']if x['method']==key and x['k']==2 and x['eps_frac']==.02))
  for txt,x,w in zip(['Reversals / clear']+[str(round(v['T2D_reversal_rate']*v['T2D_clear']))+' / '+str(v['T2D_clear'])for v in proxy],cols,ws):s.text(txt,x,716,w,24,18)
  for txt,x,w in zip(['Misses / clear']+[str(round(v['T2D_missed_rate']*v['T2D_clear']))+' / '+str(v['T2D_clear'])for v in proxy],cols,ws):s.text(txt,x,748,w,24,18)
  note='OLR: P has 0 reversals and 3 misses. R20 has 1 reversal and 2 misses.'if name=='olr' else'PM2.5: 7 clear events. Retained replicate diagnostic: R20 2 reversals + 1 miss; primary frozen proxy: 2/7.'
  s.text(note,25,795,1230,24,17,bold=True)
  metadata=dict(dataset=label,frames=T,cache_files=[str(p)for p in paths],cache_arrays_all_identical=True,OLR_PR_match_publication_render=name=='olr',range=[mn,mx],units=unit,scalar_palette='RdBu_r',axis_semantics='Baselines show their complete saved native rank domain. P/R share the fixed reference axis. Each axis normalized separately to [0,1], so baseline ordinate is not a geographic coordinate.',construction='No layouts recomputed. All four complete saved arrays, no temporal crop. Maps native scalar raster, all text and axes editable.',proxy=proxy,selection='Whole sequence only, no event selection')
  s.d['objects']=[o for o in s.d['objects'] if o.get('y',o.get('y1',0))<640];s.d['height']=640;s.d['notes']=json.dumps(metadata);write(s,stem);(CK/(name+'_restored_cache.json')).write_text(json.dumps(metadata,indent=2))

if __name__=='__main__':
 c=cylinder();print('Cylinder selected frame',c['selection']['t'], 'H',c['selection']['H'],'gain',c['selection']['gain'],'pairs',c['pair_merge_Q']);wildfire();supplements();(CK/'frozen_input_sha256.json').write_text(json.dumps(SOURCES,indent=2));print('Prepared four cases from unchanged saved results')
