from pathlib import Path
import json,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
OUT=Path(__file__).resolve().parents[4]/'output/projection_conflict_schematic_20261103'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'STIXGeneral','svg.fonttype':'none'})
nx,ny=7,5
xx,yy=np.meshgrid(np.arange(nx),np.arange(ny));points=np.c_[xx.ravel(),yy.ravel()];n=len(points)
wells=np.array([[0,3],[4,4],[2,0],[6,1]])
f=np.min(np.sum((points[:,None]-wells[None])**2,axis=2),axis=1).astype(float)+8*(points[:,1]==2)+.001*np.arange(n)
edges=[];adj=[[] for _ in f]
for j in range(ny):
 for i in range(nx):
  for di,dj in [(1,0),(0,1),(1,1)]:
   if i+di<nx and j+dj<ny:
    a=j*nx+i;b=(j+dj)*nx+i+di;edges.append((a,b));adj[a].append(b);adj[b].append(a)
# Sweep the vertex-wise scalar field in increasing order. Each regular vertex
# belongs to exactly one superarc. Stable sample IDs are grid row-major indices.
parent={};tip={};pending={};arcs=[];children={};leaves=[]
def root(v):
 while parent[v]!=v:parent[v]=parent[parent[v]];v=parent[v]
 return v
order=np.argsort(f);ranks=np.empty(n,int);ranks[order]=np.arange(n)
for vv in order:
 v=int(vv);rs=sorted({root(w) for w in adj[v] if w in parent})
 parent[v]=v
 if not rs:leaves.append(v);tip[v]=v;pending[v]=[];children[v]=[]
 elif len(rs)==1:
  r=rs[0];parent[r]=v;tip[v]=tip.pop(r);pending[v]=pending.pop(r)+[v]
 else:
  children[v]=[]
  for r in rs:
   child=tip.pop(r);arcs.append({'child':child,'parent':v,'regular':pending.pop(r)});children[v].append(child);parent[r]=v
  tip[v]=v;pending[v]=[]
maximum=int(order[-1]);r=root(maximum);base=tip[r];reg=pending[r]
if base!=maximum:
 assert reg[-1]==maximum
 arcs.append({'child':base,'parent':maximum,'regular':reg[:-1]});children[maximum]=[base]
critical=set(children);regular=[v for a in arcs for v in a['regular']]
assert len(set(regular))==len(regular) and set(regular).isdisjoint(critical)
assert set(regular)|critical==set(range(n))
leafid={'A':21,'B':32,'C':2,'D':13};assert set(leafid.values())==set(leaves)
colors={'A':'#0066DD','B':'#FF8200','C':'#009D91','D':'#9455B6'}
leafname={v:k for k,v in leafid.items()};owner={v:'#B9B9B9' for v in range(n)}
for a in arcs:
 col=colors[leafname[a['child']]] if a['child'] in leafname else '#A6A6A6'
 for v in [a['child']]+a['regular']:owner[v]=col
owner[maximum]='#A6A6A6'
leaf_support={k:[v]+next(a['regular'] for a in arcs if a['child']==v) for k,v in leafid.items()}
assert sum(map(len,leaf_support.values()))==len(set(sum(leaf_support.values(),[])))
# Recursively lay out one legal tree frontier, retaining all four leaf identities.
def descendants(v):
 if v in leafname:return [leafname[v]]
 return sum((descendants(c) for c in children[v]),[])
for v in children:children[v].sort(key=lambda c:min('ABCD'.index(k) for k in descendants(c)))
assert descendants(maximum)==list('ABCD')
pair_sets=[set(descendants(c)) for v,cs in children.items() for c in cs if len(descendants(c))==2]
assert {'A','B'} in pair_sets and {'C','D'} in pair_sets
fig=plt.figure(figsize=(13,9),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
scene=[]
def line(a,b,c='#151515',lw=1.15,z=3,alpha=1):
 scene.append({'type':'line','a':list(a),'b':list(b),'color':c,'width':lw,'z':z,'alpha':alpha})
 ax.plot([a[0],b[0]],[a[1],b[1]],color=c,lw=lw,zorder=z,alpha=alpha)
def text(x,y,s,size=14,**kw):
 if not str(s).isdigit():
  size=29.6 if str(s).startswith('(') or str(s) in ['$d$','$x$'] else 26.3
  if x>.5 and abs(y-.524)<1e-6:y=.513
 scene.append({'type':'text','x':float(x),'y':float(y),'text':s,'size':size,'align':kw.get('ha','center'),'bold':kw.get('weight','')=='bold','color':kw.get('color','#111111'),'z':kw.get('zorder',3)})
 ax.text(x,y,s,fontsize=size,ha=kw.pop('ha','center'),va='center',**kw)
def box(x,y,w,h,fc='white',ec='#777777',r=.008):
 if ec!='none':ec='#111111'
 scene.append({'type':'box','x':x,'y':y,'w':w,'h':h,'fill':fc,'stroke':ec,'radius':r,'z':1})
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=fc,ec=ec,lw=1.1))
def polygon(pts,color,z=2):
 pts=np.asarray(pts,dtype=float)
 scene.append({'type':'polygon','points':pts.tolist(),'color':color,'z':z})
 ax.add_patch(Polygon(pts,closed=True,facecolor=color,edgecolor=color,lw=.9,zorder=z))
def title(x,y,s,w):box(x,y-.022,w,.044,'#E5E5E5','none');text(x+.012,y,s,16,ha='left',weight='bold')
def arrow(a,b,c='#111111',lw=1.1):
 a=list(a)
 if a[0]>.5 and abs(a[1]-.503)<1e-6:a[1]=.479
 scene.append({'type':'arrow','a':list(a),'b':list(b),'color':c,'width':lw,'z':4,'alpha':1})
 ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':c,'lw':lw,'shrinkA':2,'shrinkB':2},zorder=4)
box(.012,.351,.477,.635);box(.501,.351,.487,.635);box(.012,.040,.976,.295)
title(.025,.951,'(a) Spatial projection',.374);title(.514,.951,'(b) Tree mapping',.451);title(.025,.300,'(c) Order conflict',.403)
def glyph(v,pos,number=True,scale=1):
 scene.append({'type':'node','x':float(pos[0]),'y':float(pos[1]),'size':(155 if v in critical else 132)*scale,'critical':v in critical,'color':owner[v],'z':7})
 ax.scatter(*pos,s=(155 if v in critical else 132)*scale,marker='D' if v in critical else 'o',facecolor=owner[v],edgecolor='#111111',lw=.85,zorder=7)
 if number:text(*pos,str(ranks[v]),9.2*scale**.5,zorder=8,color='#111111')
# All source vertices remain visible. Only four leaf extrema are mapped.
grid=np.c_[.055+.060*points[:,0],.595+.065*points[:,1]]
ref=np.array([.035,.422]);d=np.array([1.,.18]);metric=np.diag([13**2,9**2]);t=((grid-ref)@metric@d)/(d@metric@d);proj=ref+t[:,None]*d
assert np.max(np.abs((grid-proj)@metric@d))<1e-10
# True support footprints: midpoint dual cells centered on the source vertices,
# full cells extend half a sampling step beyond the outermost vertex centers.
from matplotlib.colors import to_rgb,to_hex
# Complete sample-centered cell background, including internal-arc samples.
# This schematic uses full cells at boundary samples so every node is centered.
for v in range(n):
 i,j=points[v]
 l,r=i-.5,i+.5;bot,top=j-.5,j+.5
 corners=np.array([[l,bot],[r,bot],[r,top],[l,top]])
 footprint=np.c_[.055+.060*corners[:,0],.595+.065*corners[:,1]]
 light=to_hex(.58*np.ones(3)+.42*np.array(to_rgb(owner[v])))
 polygon(footprint,light,z=1)
 for j in range(4):line(footprint[j],footprint[(j+1)%4],'#949494',.45,z=1)
support_intervals={}
for k,ids in leaf_support.items():
 intervals=[]
 for v in ids:
  i,j=points[v]
  l,r=i-.5,i+.5;bot,top=j-.5,j+.5
  corners=np.array([[l,bot],[r,bot],[r,top],[l,top]])
  footprint=np.c_[.055+.060*corners[:,0],.595+.065*corners[:,1]]
  ts=((footprint-ref)@metric@d)/(d@metric@d)
  intervals.append([float(ts.min()),float(ts.max())])
 intervals.sort();merged=[]
 for l,r in intervals:
  if merged and l<=merged[-1][1]+1e-12:merged[-1][1]=max(merged[-1][1],r)
  else:merged.append([l,r])
 support_intervals[k]=merged
for v in leafid.values():line(grid[v],proj[v],owner[v],1.35,z=2,alpha=1)
for a,b in edges:line(grid[a],grid[b],lw=.9)
for v in range(n):glyph(v,grid[v])
arrow(ref-.005*d,ref+(max(t)+.020)*d,lw=1.6);text(.470,.490,'$d$',19)
# Compact illustrative support-width bars sit below the direction axis.
# They do not cross the extremum projection paths and do not claim exact extent.
normal=np.array([-d[1]*(9/13)**2,d[0]]);normal/=np.linalg.norm(normal)
illustrative_width={k:.009*len(ids) for k,ids in leaf_support.items()}
for k,v in leafid.items():
 center=proj[v]-.014*normal
 half=illustrative_width[k]/2
 a=center-half*d;b=center+half*d;thick=.003*normal
 polygon([a-thick,b-thick,b+thick,a+thick],colors[k],z=2)
for k,v in leafid.items():
 glyph(v,proj[v],False,.58)
 text(proj[v][0],proj[v][1]-.046,k,17,weight='bold',color=colors[k])
for k,v in leafid.items():
 xy=grid[v];text(xy[0]+(-.022 if k=='A' else .019),xy[1]+.023,k,16,weight='bold',color=colors[k])
# Full augmented tree: every source vertex appears once with the same number.
leafx={'A':.555,'B':.675,'C':.80,'D':.92};nodepos={}
arcbychild={a['child']:a for a in arcs}
levels={}
def height(v):
 levels[v]=max((height(c)+len(arcbychild[c]['regular'])+1 for c in children[v]),default=0)
 return levels[v]
height(maximum)
step=.353/levels[maximum]
def locate(v):
 cs=children[v]
 x=leafx[leafname[v]] if not cs else np.mean([locate(c)[0] for c in cs])
 y=.550+step*levels[v];nodepos[v]=np.array([x,y]);return nodepos[v]
locate(maximum)
for a in arcs:
 lo=nodepos[a['child']];hi=nodepos[a['parent']];regs=a['regular']
 for j,v in enumerate(regs):nodepos[v]=np.array([lo[0],lo[1]+(hi[1]-lo[1])*(j+1)/(len(regs)+1)])
 bend=np.array([lo[0],hi[1]]);line(lo,bend);line(bend,hi)
# A stable tree traversal assigns a unique 1D slot to every augmented vertex.
arcbychild={a['child']:a for a in arcs};slots=[]
def traversal(v):
 if not children[v]:slots.append(v);return
 cs=children[v]
 for i,c in enumerate(cs):
  traversal(c);slots.extend(arcbychild[c]['regular'])
  if i==0:slots.append(v)
traversal(maximum)
assert len(slots)==n and len(set(slots))==n
# Only the four leaf extrema are mapped to the topology-constrained axis.
# Positions illustrate the legal leaf order; these are not optimized x values.
# Topological extrema map straight down. Widths are compact visual cues only.
mapped={v:np.array([nodepos[v][0],.425]) for k,v in leafid.items()}
mapped_support={}
for k,v in leafid.items():
 center=mapped[v][0];half=illustrative_width[k]/2
 l,r=center-half,center+half
 mapped_support[k]=[l,r]
 polygon([[l,.405],[r,.405],[r,.411],[l,.411]],colors[k],z=2)
for v in leafid.values():
 start=nodepos[v].copy();start[1]-=.047
 arrow(start,mapped[v]+np.array([0,.012]),owner[v],1.35)
for v in range(n):glyph(v,nodepos[v],True,.72)
arrow((.525,.425),(.965,.425),lw=1.4);text(.970,.425,'$x$',18)
for k,v in leafid.items():
 glyph(v,mapped[v],False,.58)
 text(mapped[v][0],.380,k,17,weight='bold',color=colors[k])
for k,v in leafid.items():text(nodepos[v][0],nodepos[v][1]-.026,k,16,weight='bold',color=colors[k])
# The conflict concerns leaf identity order, not the ordinary sample IDs.
text(.039,.231,'Tree order',17,ha='left',weight='bold');text(.039,.119,'Spatial order',17,ha='left',weight='bold')
bx=np.linspace(.39,.91,4);ys=[.236,.120];spatial=sorted(leafid,key=lambda k:t[leafid[k]])
assert spatial==list('ACBD')
for y,seq in zip(ys,[list('ABCD'),spatial]):
 for x,k in zip(bx,seq):box(x-.057,y-.025,.114,.05,colors[k],colors[k],.007);text(x,y,k,19,color='white',weight='bold')
for k in 'ABCD':arrow((bx[list('ABCD').index(k)],ys[0]-.029),(bx[spatial.index(k)],ys[1]+.029),colors[k],1.65)
for a,b in [(bx[0],bx[1]),(bx[2],bx[3])]:
 line((a-.056,.272),(b+.056,.272),'#777777',1);line((a-.056,.267),(a-.056,.272),'#777777',1);line((b+.056,.267),(b+.056,.272),'#777777',1)
for name in ['preview.png','schematic.svg']:
 fpath=OUT/name
 if fpath.exists():
  bak=OUT/'before_complete_mapping';bak.mkdir(exist_ok=True);shutil.copy2(fpath,bak/name)
fig.savefig(OUT/'preview.png',dpi=220,facecolor='white');fig.savefig(OUT/'schematic.svg',facecolor='white')
report={'grid_shape':[ny,nx],'sample_count':n,'critical_count':len(critical),'regular_count':len(regular),'all_vertices_in_tree_once':True,'mapped_sample_ids':list(leafid.values()),'mapped_extrema_count':4,'ordinary_sample_mapping_shown':False,'tree_mapping':'schematic topology-consistent leaf positions, not optimized layout','rank_labels':'0..34 ordered by scalar value; stable IDs are row-major grid IDs','spatial_leaf_order':spatial,'tree_leaf_order':list('ABCD'),'arcs':arcs,'samples':[{'id':v,'label':int(ranks[v]),'grid':points[v].tolist(),'scalar':float(f[v]),'critical':v in critical,'tree':nodepos[v].tolist(),'projection':proj[v].tolist() if v in leafname else None} for v in range(n)]}
report['leaf_supports']={k:{'sample_ids':ids,'sample_count':len(ids),'spatial_projected_interval_union':support_intervals[k],'illustrative_tree_width_bar':mapped_support[k]} for k,ids in leaf_support.items()}
report['width_semantics']='Compact approximate width cues below the axes. Not quantitative spatial extents or algorithmic interval widths. Extremum positions remain distinct; panel b maps extrema vertically downward.'
report['tree_spacing_min_normalized']=float(min(float(np.min(np.diff(sorted([nodepos[v][1] for v in [a['child']]+a['regular']+[a['parent']]])))) for a in arcs))
(OUT/'correspondence.json').write_text(json.dumps(report,indent=2))
(OUT/'source').mkdir(exist_ok=True)
(OUT/'source'/'scene.json').write_text(json.dumps(scene))
plt.close(fig)
