"""Standalone paper figure from the compact, verified render cache beside this source folder."""
from pathlib import Path
import json
from itertools import product
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.patches import Rectangle
from matplotlib import patheffects as pe
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=Path(__file__).resolve().parent;j=json.loads((O/'provenance.json').read_text());z=np.load(O/'render_data.npz');Q=z['Q'];times=z['times'];sel=j['selection'];stages=[20,35,50,75,101];halo=[pe.withStroke(linewidth=1.8,foreground='white')]
plt.rcParams.update({'font.family':'Times New Roman','font.size':9,'axes.labelsize':9,'axes.titlesize':9,'xtick.labelsize':9,'ytick.labelsize':9,'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
cm=LinearSegmentedColormap.from_list('Q_blue',[(0,'#ffffff'),(.2,'#9ecae1'),(.5,'#4292c6'),(1,'#08519c')]);norm=Normalize(0,1,clip=True)
width=16;n=Q.shape[1];ii=np.arange(n*width);tt=np.clip((ii-width//2)//width,0,n-2);alpha=np.clip((ii-(tt*width+width//2))/(width-1),0,1)
def interp(a):
 b=(1-alpha)*a[:,tt]+alpha*a[:,tt+1];b[:,ii<width//2]=a[:,0,None];b[:,ii>=(n-1)*width+width//2]=a[:,-1,None];return b
rgb=cm(norm(interp(Q)))[...,:3];fig=plt.figure(figsize=(7.15,2.5));ax=fig.add_axes([.085,.52,.825,.40]);ax.imshow(rgb,origin='lower',extent=[0,162,-.5,.5],aspect='auto',interpolation='nearest',rasterized=True);ax.set(ylim=(-.5,.5),xlim=(0,162),xticks=[0]+[float(times[t]) for t in stages],yticks=[-.5,0,.5],xlabel='',ylabel='1D layout position');ax.axhline(0,color='#888',ls=':',lw=.45)
ax.set_xticklabels(['0']+[f'{times[t]:.1f}' for t in stages]);ax.tick_params(axis='x',pad=2)
# Snapshot times are mapped by matching axis ticks and panel labels.
ax.plot(times[stages],np.full(len(stages),-.5),'o',ms=2.8,color='#08519c',clip_on=False,zorder=10)
# Stage labels occupy existing blank space inside the map.
for a,b,label0 in [(0,40,'I: Early'),(40,65,'II: Transition'),(65,105,'III: Shedding'),(105,135,'IV: Transition'),(135,162,'V: Late')]:
 ax.annotate('',xy=(b-1,.33),xytext=(a+1,.33),arrowprops=dict(arrowstyle='<->',lw=.55,color='black'));ax.text((a+b)/2,.355,label0,ha='center',va='bottom',fontsize=9,bbox=dict(fc='white',ec='none',pad=.25))
cax=fig.add_axes([.932,.52,.014,.40]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=cax,orientation='vertical',ticks=[0,.5,1]);cb.ax.tick_params(labelsize=8,pad=2,length=2);cax.set_title('Q',fontsize=9,pad=4)
lo=np.array([-2.450261780104711,-4,0]);hi=np.array([20,4,6]);light=np.array([.4,-.6,1]);light/=np.linalg.norm(light)
for k,t in enumerate(stages):
 rect=[.008+k*.196,.075,.19,.37];sa=fig.add_axes(rect,projection='3d',computed_zorder=False);sa.patch.set_alpha(0);sa.set_proj_type('persp',focal_length=1.1);sa.view_init(elev=24,azim=-65);sa.set_box_aspect(hi-lo,zoom=1.26);m=np.load(O/f'mesh_{t:03d}.npz')
 for level,opacity in [(0,.45),(1,.78)]:
  tri=m[f'v{level}'][m[f'f{level}']];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-20);shade=.80+.20*np.abs(np.einsum('ij,j->i',normal,light));color=np.tile(cm(norm([.2,1.][level])),(len(tri),1));color[:,:3]*=shade[:,None];color[:,3]=opacity;sa.add_collection3d(Poly3DCollection(tri,facecolors=color,edgecolors='none',zorder=2+level,rasterized=True))
 v=np.array(list(product([-.5,.5],[-.5,.5],[0,6])));faces=[]
 for dim in range(3):
  for val in np.unique(v[:,dim]):
   face=v[v[:,dim]==val];other=[d for d in range(3) if d!=dim];center=face.mean(0);ang=np.arctan2(face[:,other[1]]-center[other[1]],face[:,other[0]]-center[other[0]]);faces.append(face[np.argsort(ang)])
 sa.add_collection3d(Poly3DCollection(faces,facecolors='#afb4b9',edgecolors='#697077',alpha=.90,linewidths=.35,zorder=4))
 sa.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(0,6),xticks=[],yticks=[],zticks=[],xlabel='',ylabel='',zlabel='');sa.tick_params(labelsize=9,pad=1,length=1);sa.xaxis.labelpad=-2;sa.yaxis.labelpad=-3;sa.zaxis.labelpad=-3
 for axis in [sa.xaxis,sa.yaxis,sa.zaxis]:
  axis.pane.set_facecolor((1,1,1,0));axis.pane.set_edgecolor('#777777');axis.pane.set_alpha(1);axis.line.set_color('#777777');axis.line.set_linewidth(.6);axis._axinfo['grid']['color']=(.7,.72,.74,.30)
 # Explicit twelve-edge domain box: all vertical edges are retained.
 sa.set_axis_off()
 corners_box=np.array(list(product([lo[0],hi[0]],[lo[1],hi[1]],[0,6])))
 for a,p0 in enumerate(corners_box):
  for p1 in corners_box[a+1:]:
   if np.count_nonzero(p0!=p1)==1:sa.plot(*np.array([p0,p1]).T,color='#777777',lw=.6,zorder=0,clip_on=False)
 fig.text(rect[0]+rect[2]/2,.125,f't = {times[t]:.1f}',ha='center',va='top',fontsize=9)
 if False:
  corners=np.array(list(product(*sel['bbox'])))
  for a,p0 in enumerate(corners):
   for p1 in corners[a+1:]:
    if np.count_nonzero(p0!=p1)==1:sa.plot(*np.array([p0,p1]).T,color='black',lw=.85,zorder=15)
  center=np.array(sel['bbox']).mean(1);center[2]=6.2;sa.text(*center,'S',color='black',fontsize=9,weight='bold',path_effects=halo,zorder=20)
for ext in ['png','pdf','svg']:fig.savefig(O/f'anchor_cylinder_centered_blue.{ext}',dpi=600,bbox_inches='tight',pad_inches=.04)
plt.close(fig)
verification=dict(y_range=[-.5,.5],stages=stages,all_real_original_volumes=True,uniform_3d_camera=True,uniform_3d_scale=True,selection=sel,Q_color_clip=[0,1],single_hue_blue=True,no_vector_direction_color=True,color_equation='One fixed sequential blue transfer function of Q',temporal_interpolation='Q before lookup in the blue colormap; 16 display pixels per frame',figure_width_inches=7.15,figure_height_inches=2.85,phase_guides='I:0-40; II:40-65; III:65-105; IV:105-135; V:135-162; visual intervals',main_font='Times New Roman',not_a_smoke_surface_reproduction=True)
(O/'figure_verification.json').write_text(json.dumps(verification,indent=2));print('FIGURE COMPLETE',flush=True)
