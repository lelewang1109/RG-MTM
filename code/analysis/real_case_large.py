"""RG-MTM-only large figures, linked to reference-paper event TIMES.

No baseline figure panels. Reuses frozen arrays and original native observations.
Reference event times do not validate named-cyclone or flow-structure identities.
"""
from pathlib import Path
from datetime import datetime
from itertools import combinations
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.backends.backend_pdf import PdfPages
from real_case_studies import ROOT,OUT,DATA,TANG,read,write,sha
from real_case_evidence import load,tree_at,lca,select,feature_index

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'axes.linewidth':.7,'svg.fonttype':'none','svg.hashsalt':'rgmtm-only-large-20261019','pdf.fonttype':42})
ERA_EVENTS=[
 dict(id='E1',paper_time='1999-12-03 18:00:00',name='Anatol',snapshot=34,source='TMTM Fig.1; ST-MTM Fig.6',candidate=37),
 dict(id='E2',paper_time='1999-12-17 21:00:00',name='Scandinavia storm',snapshot=62,source='TMTM Fig.1; ST-MTM Fig.6',candidate=66),
 dict(id='E3',paper_time='1999-12-24 23:00:00',name='British Isles / Norway storm',snapshot=76,source='TMTM Fig.1; ST-MTM Fig.6',candidate=87),
 dict(id='E4',paper_time='1999-12-26 10:00:00',name='Lothar time window',snapshot=79,source='TMTM Fig.1; ST-MTM Fig.6',candidate=None),
 dict(id='E5',paper_time='1999-12-27 21:00:00',name='Martin time window',snapshot=82,source='TMTM Fig.1; ST-MTM Fig.6',candidate=93)]
PALETTE=['#0072b2','#009e73','#cc79a7','#d55e00','#76528b']

def measured_cost(d,meta):
 """Actual barriers including strict-extremum clearance, separate from delta*."""
 result=[]
 for t in range(len(d['track'])):
  ids=d['leaf'][t];ids=ids[ids>=0];tree=tree_at(meta,t);col=d['mapR'][:,t];ix=np.rint(d['normR'][t,:len(ids)]*(len(col)-1)).astype(int);errors=[]
  for i,j in combinations(range(len(ids)),2):
   a,b=sorted([ix[i],ix[j]]);level=(np.max if meta['kind']=='join'else np.min)(col[a:b+1]);errors.append(abs(level-tree['values'][str(lca(tree,int(ids[i]),int(ids[j])))]))
  result.append(max(errors,default=0.))
 return np.array(result)

def era_events(d):
 start=datetime.fromisoformat(str(d['dates'][0]));events=[]
 for row in ERA_EVENTS:
  r=dict(row);r['frame_time']=(datetime.fromisoformat(r['paper_time'])-start).total_seconds()/(12*3600);r['frame_interval']=[int(np.floor(r['frame_time'])),int(np.ceil(r['frame_time']))];r['correspondence']='reference-paper time window only; candidate scalar minimum is not an independently validated cyclone identity'
  if r['candidate'] is not None:
   j=feature_index(d,r['snapshot'],r['candidate']);r['candidate_lonlat']=d['lonlat'][r['snapshot'],j].tolist();r['candidate_reference_y_R']=float(d['normR'][r['snapshot'],j]);r['candidate_reference_y_P']=float(d['normP'][r['snapshot'],j])
  events.append(r)
 return events

def map_style(name,d):
 if name=='tangaroa':
  tf=np.array(read(ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json')['transfer_function_points']);cmap=LinearSegmentedColormap.from_list('author-tangaroa',[(v[0],tuple(v[1:4]))for v in tf],N=2048);norm=Normalize(0,2)
 elif name=='era5':cmap=plt.get_cmap('RdBu_r');norm=Normalize(min(d['mapR'].min(),d['mapP'].min()),max(d['mapR'].max(),d['mapP'].max()))
 else:cmap=plt.get_cmap('inferno').copy();cmap.set_under('#56b4e9');norm=Normalize(0,d['field'].max())
 return cmap,norm

def draw_map(ax,d,name,mode,events,cmap,norm):
 T=len(d['track']);ax.imshow(d['map'+mode],origin='lower',aspect='auto',extent=(-.5,T-.5,0,1),cmap=cmap,norm=norm,interpolation='nearest')
 # A single complete fixed reference domain is shared by P and R.
 ax.set(xlim=(-.5,T-.5),ylim=(0,1),yticks=[0,.25,.5,.75,1],ylabel='fixed reference position / axis extent',xlabel='frame index')
 for e,color in zip(events,PALETTE):
  x=e['frame_time'];ax.axvline(x,color=color,lw=1.15,ls='--');ax.text(x,.985,e['id'],transform=ax.get_xaxis_transform(),va='top',ha='center',color=color,fontsize=10,weight='bold',bbox=dict(fc='white',alpha=.9,ec='none',pad=1.5))
  if name=='era5' and e.get('candidate')is not None:
   ix=feature_index(d,e['snapshot'],e['candidate']);ax.plot(e['snapshot'],d['norm'+mode][e['snapshot'],ix],'o',mec=color,mfc='none',ms=9,mew=1.5)
 if name=='wildfire':
  # This triple is a scalar-feature witness, not fire-entity truth.
  sel=read(DATA/'wildfire_selection.json')['chosen']
  for tr,color in zip(sel['tracks'],PALETTE[:3]):
   ts=np.arange(T);ys=[d['norm'+mode][t,feature_index(d,t,tr)]if feature_index(d,t,tr)is not None else np.nan for t in ts]
   ax.plot(ts,ys,color='white',lw=2,alpha=.8);ax.plot(ts,ys,color=color,lw=1)
 ax.set_title('RG-MTM-P: hierarchy preserved'if mode=='P'else'RG-MTM-R: relaxed hierarchy, $\\kappa=20\\%$',loc='left',fontsize=12,pad=6)


def spatial(ax,d,name,t,event=None):
 coords=d['coords'];extent=[coords[:,0].min(),coords[:,0].max(),coords[:,1].min(),coords[:,1].max()]
 if name=='era5':
  import geo
  G=geo.Era5Geo(dict(lon=(-40,50),lat=(25,80)),coords);lon,lat=np.meshgrid(d['raw_lon'],d['raw_lat']);X,Y=G.xy(lon,lat);ax.pcolormesh(X,Y,d['raw_field'][t],shading='nearest',cmap=map_style(name,d)[0],norm=map_style(name,d)[1],rasterized=True);G.coastlines(ax,ROOT/'data/geo/ne_110m_coastline.geojson',lw=.45);extent=G.extent
 else:ax.imshow(d['raw_field'][t],origin='lower',extent=extent,cmap='inferno',vmin=0,vmax=d['raw_field'].max(),interpolation='nearest')
 for j,xy in enumerate(d['xy'][t]):
  if not np.isfinite(xy).all():continue
  tr=int(d['track'][t,j]);color=PALETTE[ERA_EVENTS.index(next(e for e in ERA_EVENTS if e['id']==event['id']))]if name=='era5' and event and event.get('candidate')==tr else'white'
  ax.plot(*xy,'o',mec=color,mfc='none',ms=4,mew=.8)
  if name=='era5' and event and event.get('candidate')==tr:
   ax.text(xy[0]+1,xy[1]+1,f'track {tr}',color=color,fontsize=7,bbox=dict(fc='white',alpha=.9,ec='none',pad=1))
  if name=='wildfire':
   chosen=read(DATA/'wildfire_selection.json')['chosen']
   if tr in chosen['tracks']:
    k=chosen['tracks'].index(tr);ax.plot(*xy,'o',mec=PALETTE[k],mfc='white',ms=5);ax.text(xy[0]+2,xy[1]+2,'ABC'[k],color=PALETTE[k],weight='bold',fontsize=8)
 ax.set(xlim=extent[:2],ylim=extent[2:],xticks=[],yticks=[],aspect='equal');ax.set_title((event['id']+' | 'if event else'')+f'frame {t}\n'+str(d['dates'][t])[:16],fontsize=8)


def tangaroa_volumes(frames):
 """Reuse original 0/100/200 DVR cache and render only additional event times."""
 from experiments.volume3d.paper_style import parallel_dvr,fit_author_camera,BOUNDS
 from experiments.volume3d.prepare_tangaroa_paper import OUT as rawdir
 settings=read(ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json');settings['camera']=fit_author_camera(read(ROOT/'experiments/volume3d/inputs/tangaroa_closer_camera.json')['camera'])[0]
 p=DATA/'tangaroa_event_volumes.npz';mp=p.with_suffix('.json');inputs={str((rawdir/f'scalar_{t:03d}.npy').relative_to(ROOT)):sha(rawdir/f'scalar_{t:03d}.npy')for t in frames}
 key=dict(inputs=inputs,settings=settings,frames=frames,renderer_sha256=sha(ROOT/'experiments/volume3d/paper_style.py'))
 if p.exists()and read(mp)['key']==key:return np.load(p)
 oldpath=TANG/'paper_style/volume_cache.npz';oldmeta=read(oldpath.with_suffix('.json'));assert sha(oldpath)==oldmeta['sha256'];assert oldmeta['inputs']['settings']==settings
 old=np.load(oldpath);images=[]
 for t in frames:
  if t in [0,100,200]:images.append(old['images'][[0,100,200].index(t)])
  else:
   print('DVR of original frame',t,flush=True);field=np.load(rawdir/f'scalar_{t:03d}.npy',mmap_mode='r');img,_,_=parallel_dvr(field,BOUNDS,settings,width=800);images.append(img)
 np.savez_compressed(p,images=images,corners=old['corners'],projected=old['projected']);write(mp,dict(key=key,sha256=sha(p)));return np.load(p)


def make(name,d,meta,book):
 T=len(d['track']);cmap,norm=map_style(name,d);fig=plt.figure(figsize=(16,10));fig.text(.065,.967,{'era5':'ERA5 pressure','wildfire':'Australian fire radiative power','tangaroa':'Tangaroa: original 300 x 180 x 120 grid, 201 frames'}[name],fontsize=18,weight='bold')
 if name=='era5':events=era_events(d);frames=[e['snapshot']for e in events];line='E1-E5 indicate event times reported in TMTM Fig. 1 / ST-MTM Fig. 6. Rings indicate nearby scalar minima; named-cyclone identities are unverified.'
 elif name=='tangaroa':
  frames=[0,25,100,145,200];events=[dict(id='T1',frame_time=25,name='paper: feature-group separation'),dict(id='T2',frame_time=100,name='paper: spatial group context'),dict(id='T3',frame_time=145,name='paper: departing group leaves domain')];line='T1-T3 mark the times discussed in TMTM Fig. 15. They are temporal reference guides; no feature-group identity is inferred from a matching time.'
 else:
  sel=read(DATA/'wildfire_selection.json')['chosen'];frames=sel['snapshots'];events=[dict(id='W1',frame_time=sel['t'],name='computed scalar-feature conflict')];line='W1 marks the verified scalar-feature conflict at frame 18. Wildfire has no matching named event in the requested reference figures.'
 fig.text(.065,.935,line,fontsize=9,color='.3')
 # Event legend deliberately uses a readable list, not crowded long labels at adjacent times.
 text='    |    '.join(f'{e["id"]}: {e["name"]}'for e in events)
 fig.text(.065,.905,text,fontsize=9)
 axes=[]
 for mode,y in [('P',.585),('R',.265)]:
  ax=fig.add_axes([.065,y,.84,.28]);draw_map(ax,d,name,mode,events,cmap,norm);axes.append(ax)
  ax.set_xlabel('')
  if mode=='P':ax.tick_params(labelbottom=False)
  if name=='era5':
   ticks=[0,28,48,68,88,117];ax.set_xticks(ticks,[str(d['dates'][t])[:10]+'\n'+f't={t}'for t in ticks])
 cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=fig.add_axes([.925,.30,.013,.53]),extend='min'if name=='wildfire'else'neither');cb.set_label('pressure [hPa]'if name=='era5'else'processed log(1 + FRP [MW])'if name=='wildfire'else'processed speed')
 if name=='wildfire':fig.text(.065,.216,'Cyan in R: artificial negative barrier values from existing optimal filling; these are not negative observed FRP.',fontsize=9,color='#0072b2')
 else:fig.text(.065,.216,'Time axis: frame index. Original spatial data below (same input protocol; full spatial window):',fontsize=9)
 if name=='wildfire':
  cb_raw=fig.colorbar(ScalarMappable(norm=Normalize(0,d['raw_field'].max()),cmap='inferno'),cax=fig.add_axes([.925,.055,.013,.13]));cb_raw.ax.tick_params(labelsize=8);cb_raw.set_label('raw log1p FRP',fontsize=8)
 n=len(frames);totalwidth=.84;gap=.018;w=(totalwidth-gap*(n-1))/n
 if name=='tangaroa':vol=tangaroa_volumes(frames)
 for j,t in enumerate(frames):
  ax=fig.add_axes([.065+j*(w+gap),.055,w,.13])
  if name=='tangaroa':
   ax.imshow(vol['images'][j],origin='lower',extent=(-1,1,-1,1),aspect='auto');corners=vol['corners'];xy=vol['projected']
   for a,b in combinations(range(8),2):
    if np.count_nonzero(corners[a]!=corners[b])==1:ax.plot(xy[[a,b],0],xy[[a,b],1],c='.75',lw=.35)
   ax.set(xticks=[],yticks=[],xlim=(-1,1),ylim=(-1,1));ax.set_title(f'frame {t} | source time {t*.01:.2f}',fontsize=8)
  else:spatial(ax,d,name,t,events[j]if name=='era5'else None)
 fig.text(.065,.012,'P/R share the complete fixed reference axis. A directional projection does not encode complete 2-D/3-D geometry. No baseline method panels are included.',fontsize=9,color='.3')
 stem=name+'_rgmtm_large';paths=[]
 for ext in ['pdf','svg','png']:
  p=OUT/f'{stem}.{ext}';fig.savefig(p,dpi=300,facecolor='white');paths.append(p)
 book.savefig(fig);plt.close(fig);print('Completed',stem,flush=True)
 return paths,dict(dataset=name,frames=T,events=events,snapshots=frames,methods=['RG-MTM-P','RG-MTM-R'],reference_direction=d['direction'].tolist(),reference_origin=float(d['geometry'][0]),reference_extent=float(d['geometry'][1]),full_vertical_domain=True,numerical_results_modified=False)


def build(names):
 OUT.mkdir(exist_ok=True);paths=[];reports={}
 with PdfPages(OUT/'rgmtm_large_figures.pdf')as book:
  for name in names:
   d,meta=load(name)
   if name=='wildfire'and not(DATA/'wildfire_selection.json').exists():select(name,d,meta)
   files,record=make(name,d,meta,book);paths+=files;reports[name]=record
 paths.append(OUT/'rgmtm_large_figures.pdf');write(OUT/'event_correspondence.json',reports)
 documentation(reports)
 sources=[ROOT/'analysis/real_case_studies.py',ROOT/'analysis/real_case_evidence.py',Path(__file__)]+[DATA/f'{n}.{ext}'for n in names for ext in ['json','npz']]
 for name in ['README.md','event_correspondence_zh.md','captions_en.md','event_correspondence.json']:paths.append(OUT/name)
 write(OUT/'manifest.json',dict(datasets=names,source_sha256={str(p.relative_to(ROOT)):sha(p)for p in sources},files={str(p.relative_to(OUT)):sha(p)for p in paths},methods=['RG-MTM-P','RG-MTM-R'],baseline_panels=False,scientific_parameters_changed=False))
 verify()


def documentation(reports):
 text=['# RG-MTM 大图与参考论文事件对应','', '最终图片仅包含 RG-MTM-P/R，不补画 TMTM 或 ST-MTM。两图使用同一完整参考轴，未按特征占据范围裁剪。','', '## ERA5','', '| 标记 | 原论文描述及快照时间 | 本项目对应帧 | 可以确认的对应 |','|---|---|---|---|']
 for e in reports.get('era5',{}).get('events',[]):
  interval=e['frame_interval'];candidate=('；邻近标量低压 track '+str(e['candidate'])+f'，R 图 y≈{e["candidate_reference_y_R"]:.3f}'if e['candidate']is not None else'；该帧没有可确认为 Lothar 的独立叶特征')
  text.append(f'| {e["id"]} | {e["name"]}，{e["paper_time"]} | t={e["frame_time"]:.3f}，相邻离散帧 {interval}；空间快照 t={e["snapshot"]} | 时间窗对应{candidate} |')
 text += ['', '上述时间来自第一篇 Fig. 1；第二篇 Fig. 6 讨论同月 Storms。原论文为 744 个逐小时压力异常场；本项目是 118 个半日 MSLP 场，区域、250 km 平滑和极小值处理也不同。因此环圈只表示同时间窗、邻近区域的算法极值候选，不能当作已核实的命名气旋身份。尤其第 79 帧只有两个叶极值，不能为了对照原文而凭空补一条 Lothar 轨迹。', '', '## Tangaroa','', '| 标记 | 原文位置 | 本项目图上位置 | 对应范围 |','|---|---|---|---|','| T1 | 第一篇 Fig. 15 及第 5 节：约 t=25 两大特征组分开 | P/R 的第 25 帧虚线、对应体渲染 | 原序列时间一致；未完成特征组身份逐一验证 |','| T2 | Fig. 15(b)：t=100 体渲染可见两个组 | 第 100 帧虚线及体渲染 | 时间、体数据上下文对应 |','| T3 | 第 5 节：分离组约 t=145 离域消失 | 第 145 帧虚线及体渲染 | 仅时间对照；不能认定某条 RG 线就是原文离域组 |','', '第一篇 Fig. 14 是 Cylinder，不是 Tangaroa，不能将其 Phase I/II/III 直接标在本序列。第二篇所要求的 Fig. 2 和 Fig. 7 是机制示例，Fig. 6 是 Storms，均没有 Tangaroa 事件可一一对应。','', '当前 Tangaroa 使用完整 300×180×120、201 帧，速度模长近零替换/截断、TTK 10% 简化和 join tree 与已保存协议一致。派生节点数 36–186 与作者报告的 50–186 仍不同，因此不声称作者最终树精确复现。图上 P/R 的纵轴是单方向投影，不能直接用原文 TMTM 图的纵坐标定位特征组。','', '## Wildfire','', 'W1 是本项目第 18 帧（2019-12-07 开始的双日汇总）处的真实标量特征冲突。所选 A/B/C 为计算轨迹 ID 3/48/52，均有前后正重叠匹配。它对应第二篇讨论的“层次与空间关系可能不一致”这一现象，但所要求参考图没有相同的已命名火灾事件，不能建立实体级对应。原始空间图显示未平滑 log1p 双日 FRP；圈点来自既有平滑后的 split-tree 极大值。','', 'R 图中的青色表示已有最优填充产生的负标量连接值，不表示观测 FRP 为负。原始实验与指标不改动。','', '## 复现','', '从 RG 仓库运行 `PYTHONPATH=src:analysis:. ../.venv/bin/python analysis/real_case_studies.py`。已有派生数组可直接重绘；`--prepare` 只在需要重建派生绘图输入时使用。`--verify` 核对输出哈希、坐标投影、原始特征身份和时间转换。','']
 (OUT/'event_correspondence_zh.md').write_text('\n'.join(text))
 captions=[]
 for name,r in reports.items():
  captions += [f'**{name}_rgmtm_large.** Complete RG-MTM-P and RG-MTM-R maps with the same full fixed reference domain. The relaxation eligibility setting is kappa=20%. Spatial snapshots use existing original observations or original-grid volume renderings. Event guides identify the reference-paper time windows described in the accompanying correspondence table, rather than independently validated physical-feature identities. No TMTM/ST-MTM baseline panel is included. The reference is a directional projection and does not retain complete spatial geometry. '+('E1-E5 link the December 1999 times in TMTM Fig. 1 and the Storms discussion in ST-MTM Fig. 6. Native pressure and processed extrema differ from the hourly anomaly protocol in those papers. In particular, a distinct Lothar feature is not asserted.'if name=='era5'else'T1-T3 mark frames 25, 100 and 145 discussed for Tangaroa in TMTM Fig. 15. All 201 original-grid frames use fixed 10% persistence. These marks do not assert feature-group identity or exact reproduction of the authors\' final trees.'if name=='tangaroa'else'W1 marks the computed scalar-feature conflict at frame 18. Cyan indicates negative artificial connection values in the existing relaxed filling, not negative observed FRP. Matched extrema are not validated fire entities.'),'']
 (OUT/'captions_en.md').write_text('# Captions\n\n'+'\n'.join(captions))
 lines=['# RG-MTM 真实数据大图','', '按最新要求：只展示自己的 RG-MTM-P/R；参考论文的事件对应单独说明。','', '[三页 PDF 合集](rgmtm_large_figures.pdf) · [事件对应说明](event_correspondence_zh.md) · [English captions](captions_en.md)','']
 for n in reports:lines += [f'## {n}','','[PDF]('+n+'_rgmtm_large.pdf) · [SVG]('+n+'_rgmtm_large.svg)','','!['+n+']('+n+'_rgmtm_large.png)','']
 (OUT/'README.md').write_text('\n'.join(lines))


def verify():
 m=read(OUT/'manifest.json');summary={}
 for group,root in [('source_sha256',ROOT),('files',OUT)]:
  for p,h in m[group].items():assert sha(root/p)==h,p
 records=read(OUT/'event_correspondence.json')
 for name in m['datasets']:
  d,meta=load(name);coord=d['xyz']if name=='tangaroa'else d['xy'];mask=np.isfinite(d['q']);assert np.allclose((coord@d['direction'])[mask],d['q'][mask],atol=2e-8)
  for mode in ['P','R']:
   assert np.allclose(((d['u'+mode]-d['geometry'][0])/d['geometry'][1])[mask],d['norm'+mode][mask]);assert np.all((d['norm'+mode][mask]>=0)&(d['norm'+mode][mask]<=1))
  if name!='tangaroa':
   for t in range(len(d['track'])):
    count=int((d['leaf'][t]>=0).sum())
    for mode in ['P','R']:
     col=d['map'+mode][:,t];ix=np.rint(d['norm'+mode][t,:count]*(len(col)-1)).astype(int);assert np.allclose(col[ix],d['value'][t,:count],atol=2e-6)
  if name=='era5':
   assert era_events(d)==records[name]['events']
   for e in records[name]['events']:
    assert e['frame_interval'][0]<=e['frame_time']<=e['frame_interval'][1]
    if e['candidate']is not None:assert e['candidate']in d['track'][e['snapshot']]
  if name=='tangaroa':
   vm=read(DATA/'tangaroa_event_volumes.json');assert sha(DATA/'tangaroa_event_volumes.npz')==vm['sha256']
   for p,h in vm['key']['inputs'].items():assert sha(ROOT/p)==h
  summary[name]=dict(frames=len(d['track']),coordinate_projection='passed',shared_full_reference_axis='passed',event_identity_claim='temporal context only',baseline_panels=False)
 write(OUT/'verification.json',dict(status='passed',cases=summary,scope='Figure inputs/output hashes, all-frame feature-coordinate projections, fixed axes and reference-event time conversions; no physical identity ground truth asserted.'))
 print('Large-figure verification passed',flush=True)
