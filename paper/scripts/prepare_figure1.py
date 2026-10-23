"""Redraw Figure 1 from frozen scientific arrays, without rerunning experiments.

Run with the project .venv Python. The following JS script authors native PPT
objects. replace_first_slide.py then patches only slide 1 into All_Figures.pptx.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
from scipy.interpolate import RegularGridInterpolator

HERE = Path(__file__).resolve().parents[1]
REV = HERE
ROOT = REV.parent / 'code'
sys.path.insert(0, str(ROOT/'analysis'))
sys.path.insert(0, str(REV/'scripts'))
from geo import Era5Geo
from scene import Scene, BLUE, ORANGE, GREEN
from anchor_aligned_renderer import render_display

DATA = ROOT/'results/real_case_studies/evidence'
ASSETS = HERE/'evidence/fig1/assets'
ASSETS.mkdir(exist_ok=True)
a = np.load(DATA/'era5.npz')
meta = json.loads((DATA/'era5.json').read_text())
event = json.loads((DATA/'era5_event.json').read_text())
assert a['mapR'].shape == (4096, 118)
assert a['raw_field'].shape == (118, 281, 441)
assert event['selection']['tracks'] == [60, 38, 56]
assert np.allclose(a['direction'], event['reference_direction'])
CM = plt.get_cmap('RdBu_r')
NORM = Normalize(min(a['mapR'].min(),a['mapP'].min()), max(a['mapR'].max(),a['mapP'].max()))
DENSE,RECONSTRUCTION=render_display(a)
(HERE/'evidence/fig1/display_reconstruction.json').write_text(json.dumps(RECONSTRUCTION,indent=2))
INK, GRAY, LIGHT = '#000000', '#66717A', '#CDD3D7'
COLORS = [BLUE, ORANGE, GREEN]
g = Era5Geo(dict(lon=(-40,50), lat=(25,80)), a['coords'])
ex = list(map(float,g.extent))
ratio = (ex[1]-ex[0])/(ex[3]-ex[2])
lon, lat = np.meshgrid(a['raw_lon'], a['raw_lat'])
X, Y = g.xy(lon,lat)
s = Scene(1, 'ERA5: RG-MTM-R20 temporal map and source-space event')

def text(t,x,y,w,h=24,size=18,color=INK,bold=False,align='left',name=None):
    if color in [GRAY,'#87929A','#263238']:
        color='#000000'
    return s.text(t,x,y,w,h,size,color,bold,align,name)

def raster(arr,name,frame_start=0,row_start=0):
    """Crop from one shared full-domain reconstructed display, without overlays."""
    factor=41
    values=DENSE[row_start:row_start+arr.shape[0],frame_start*factor:(frame_start+arr.shape[1])*factor]
    assert np.allclose(values[:,factor//2::factor],arr,rtol=0,atol=2e-12)
    rgba=np.round(CM(NORM(values[::-1]))*255).astype(np.uint8)
    p=ASSETS/name
    Image.fromarray(rgba).save(p)
    return p

def source(t):
    p=ASSETS/f'storms_source_f{t}.png'
    # Same Lambert cylindrical equal-area projection, extent and pixel size.
    fig=plt.figure(figsize=(4,4/ratio),dpi=300)
    ax=fig.add_axes([0,0,1,1])
    # Bilinear rendering in the original equal-area projected coordinates.
    # No spatial smoothing kernel and no change to source extrema/locations.
    nx,ny=1200,round(1200/ratio)
    xs=ex[0]+(np.arange(nx)+.5)/nx*(ex[1]-ex[0])
    ys=ex[2]+(np.arange(ny)+.5)/ny*(ex[3]-ex[2])
    yy,xx=np.meshgrid(ys,xs,indexing='ij')
    sampler=RegularGridInterpolator((Y[:,0],X[0,:]),a['raw_field'][t],method='linear',bounds_error=True)
    field=sampler(np.stack([yy,xx],axis=-1))
    ax.imshow(field,origin='lower',extent=ex,interpolation='none',cmap=CM,norm=NORM)
    assert g.coastlines(ax,ROOT/'data/geo/ne_110m_coastline.geojson',color='#354149',lw=.48,alpha=.85)
    ax.set(xlim=ex[:2],ylim=ex[2:],aspect='equal')
    ax.axis('off')
    fig.savefig(p,dpi=300)
    plt.close(fig)
    return p

def idx(t,tr):
    hit=np.flatnonzero(a['track'][t]==tr)
    return int(hit[0]) if len(hit) else None

def map_point(rect,xy):
    x,y,w,h=rect
    return (x+(xy[0]-ex[0])/(ex[1]-ex[0])*w,
            y+(ex[3]-xy[1])/(ex[3]-ex[2])*h)

def axis(rect,lo,hi,yl,yh,ticks,full=False):
    x,y,w,h=rect
    pos=lambda t,v:(x+(t-lo+.5)/(hi-lo)*w,y+(yh-v)/(yh-yl)*h)
    s.line(x,y,x,y+h,INK,.8)
    s.line(x,y+h,x+w,y+h,INK,.8)
    for v in ([0,.5,1] if full else [.2,.6,1.]):
        if not yl<=v<=yh: continue
        yy=pos(lo,v)[1]
        s.line(x-4,yy,x,yy,INK,.8)
        text(f'{v:g}',x-35,yy-10,28,21,16,GRAY,align='right',name=f'axis_y_{lo}_{v}')
    for t in ticks:
        xx=pos(t,yl)[0]
        s.line(xx,y+h,xx,y+h+4,INK,.8)
        text(str(t),xx-23,y+h+6,46,22,16,INK,align='center',name=f'axis_frame_{lo}_{t}')
    if full:
        s.line(x+w,y+h,x+w+7,y+h,INK,.8,name='a_time_axis_extension')
        for sign in [-1,1]:
            s.line(x+w+3,y+h+sign*2.5,x+w+7,y+h,INK,.8,name=f'a_time_axis_arrow_{sign}')
        s.line(x,y,x,y-7,INK,.8,name='a_reference_axis_extension')
        for sign in [-1,1]:
            s.line(x+sign*2.5,y-3,x,y-7,INK,.8,name=f'a_reference_axis_arrow_{sign}')
    return pos

# Left 74%, right 26%, on the original 1344 x 640 canvas.
main=(60,65,920,282)
text('(a) RG-MTM temporal map',18,8,520,30,22,bold=True,name='a_panel_title')
text('Reference position',5,105,24,202,18,INK,align='center',name='a_reference_axis_title')
s.d['objects'][-1]['textOrientation']='vert270'
s.image(raster(a['mapR'],'storms_R20_full_f0_f117.png'),*main,name='a_R20_saved_scalar_map_4096x118')
pos=axis(main,0,118,0,1,[0,20,40,60,80,100,117],True)
text('Time (frame)',60,377,150,24,18,INK,name='a_time_axis_title')

# Colour mapping is unchanged; its on-figure legend is removed per review.

# Matching top frame markers, orthogonal leaders and bottom date captions.
EVENT_FRAMES=[20,48,64,80,100]
snap_h=(920-4*14)/5/ratio
snap_w=snap_h*ratio
centers=np.linspace(60+snap_w/2,980-snap_w/2,len(EVENT_FRAMES))
snapshot_records=[]
for t,cx in zip(EVENT_FRAMES,centers):
    col=ORANGE if t==48 else '#87929A'
    xx=pos(t,0)[0]
    s.line(xx,main[1],xx,main[1]+main[3],col,1.25 if t==48 else .9,True,name=f'a_event_f{t}_true_time')
    text(f'f{t}',xx-28,40,56,24,16,INK,False,'center',name=f'a_event_label_f{t}')
    s.path([[xx,379],[xx,403],[float(cx),403],[float(cx),414]],'#A3ADB5',.8,False,name=f'ab_snapshot_leader_f{t}')
    rect=(float(cx)-snap_w/2,420,snap_w,snap_h)
    s.image(source(t),*rect,name=f'b_ERA5_actual_source_f{t}')
    s.rect(*rect,'none',ORANGE if t==48 else '#D6DCE0',1.45 if t==48 else .5)
    date_label=str(a['dates'][t])[:16]
    text(date_label,rect[0]-2,596,rect[2]+4,24,16,INK,False,'center',name=f'b_snapshot_date_f{t}')
    snapshot_records.append(dict(frame=t,date=str(a['dates'][t]),rect=rect,raw_frame_sha256=hashlib.sha256(a['raw_field'][t].tobytes()).hexdigest()))

# Main-panel line contrast comes from the scalar reconstruction itself.
main_trace_records=[]

# Small white event callouts, with native arrows terminating at saved anchors.
# Geographic labels describe a saved minimum, not a validated named cyclone.
event_annotations=[]
def callout(t,tr,label,rect,color=INK):
    j=idx(t,tr);assert j is not None
    target=np.asarray(pos(t,float(a['normR'][t,j])))
    x,y,w,h=rect
    origin=np.array([x+w/2,y+h if target[1]>y+h/2 else y])
    vector=target-origin;length=np.linalg.norm(vector)
    unit=vector/length;perp=np.array([-unit[1],unit[0]])
    end=target-unit*2.5
    s.line(*origin,*end,color,.85,name=f'a_event_callout_f{t}_leader')
    for sign in [-1,1]:
        tail=end-unit*5+sign*perp*2
        s.line(*tail,*end,color,.85,name=f'a_event_callout_f{t}_arrow_{sign}')
    s.add('rect',name=f'a_event_callout_f{t}_box',x=x,y=y,w=w,h=h,fill='#FFFFFF',stroke=color,width=.6)
    text(label,x+6,y+4,w-12,h-8,16,color,False,'center',name=f'a_event_callout_f{t}_text')
    event_annotations.append(dict(frame=t,date=str(a['dates'][t]),track=tr,label=label,anchor=float(a['normR'][t,j]),scalar=float(a['value'][t,j]),lonlat=a['lonlat'][t,j].tolist(),target=target.tolist(),rect=rect,identity_scope='computed minimum; no named-cyclone identity claim'))

callout(20,19,'Norwegian Sea low',(79,285,174,30))
callout(48,56,'Reference-order conflict',(278,87,195,30))
callout(64,73,'Northern Europe low',(511,175,178,30))
callout(80,78,'North Atlantic low',(618,285,169,30))
callout(100,93,'January low',(811,99,158,30))
# Right panel: one title, source map above local tracks.
text('(b) Conflict and local tracks',1012,8,322,30,22,bold=True,name='c_panel_title')
text('1999-12-11 00:00 (f48)',1012,42,320,24,16,INK,False,'center',name='c_event_frame')
event_h=289
event_rect=(1012+(320-event_h*ratio)/2,75,event_h*ratio,event_h)
s.image(ASSETS/'storms_source_f48.png',*event_rect,name='c_ERA5_actual_source_f48')
coordinate_records=[]
for k,tr in enumerate([60,38,56]):
    j=idx(48,tr);assert j is not None
    xy=map_point(event_rect,a['xy'][48,j])
    s.dot(*xy,INK,4.5,'white',name=f'c_extremum_{"ABC"[k]}_track{tr}_f48')
    dx,dy=([9,-24],[9,-24],[10,-23])[k]
    text('ABC'[k],xy[0]+dx,xy[1]+dy,30,26,18,INK,True,name=f'c_source_label_{"ABC"[k]}')
    coordinate_records.append(dict(label='ABC'[k],track=tr,leaf=int(a['leaf'][48,j]),xy=a['xy'][48,j].tolist(),lonlat=a['lonlat'][48,j].tolist(),slide_xy=xy))
origin=np.array([ex[0]+.16*(ex[1]-ex[0]),ex[2]+.16*(ex[3]-ex[2])])
tip=origin+a['direction']*.22*min(ex[1]-ex[0],ex[3]-ex[2])
p0=np.array(map_point(event_rect,origin));p1=np.array(map_point(event_rect,tip))
s.line(*p0,*p1,INK,1.9,name='c_fixed_projection_direction_d')
unit=(p1-p0)/np.linalg.norm(p1-p0);perp=np.array([-unit[1],unit[0]])
for sign in [-1,1]:s.line(*(p1-unit*7+sign*perp*3.5),*p1,INK,1.8,name=f'c_d_arrowhead_{sign}')
text('d',p1[0]+5,p1[1]-16,25,25,18,INK,True,name='c_direction_label')

text('Local tracks (f43–53)',1012,410,320,26,18,INK,True,'center',name='c_local_title')
# Native filled block arrow, independently editable in PowerPoint.
s.add('blockArrow',name='c_source_to_local_arrow',x=1160,y=372,w=24,h=30,
      rotation=0,fill='#A5AEB6',stroke='none',width=0)
local=(1052,446,260,140)
# Integer source rows define this crop. Exact anchors are continuous overlays.
i0=int(np.floor(.13*4095));i1=int(np.ceil(.97*4095))+1
yl,yh=i0/4095,(i1-1)/4095
s.image(raster(a['mapR'][i0:i1,43:54],'storms_R20_local_f43_f53.png',43,i0),*local,name='c_R20_saved_local_scalar_map')
lp=axis(local,43,54,yl,yh,[43,48,53])
text('Time (frame)',1082,618,200,22,16,INK,False,'center',name='c_time_axis_title')
fx=lp(48,yl)[0]
s.line(fx,local[1],fx,local[1]+local[3],GRAY,.95,True,name='c_f48_true_time_guide')
traces=[]
for k,tr in enumerate([60,38,56]):
    # Do not bridge missing identities. A starts at f48, C spans f47–49.
    runs=[];run=[];rows=[]
    for t in range(43,54):
        j=idx(t,tr)
        if j is None:
            if run:runs.append(run);run=[]
            continue
        anchor=float(a['normR'][t,j]);q=float(a['qnorm'][t,j])
        run.append(lp(t,anchor));rows.append(dict(frame=t,anchor=anchor,reference=q,leaf=int(a['leaf'][t,j])))
    if run:runs.append(run)
    for ri,points in enumerate(runs):
        if len(points)>1:
            s.path(points,'white',3.9,name=f'c_actual_track_{tr}_halo_{ri}')
            s.path(points,INK,2.0,name=f'c_actual_track_{tr}_polyline_{ri}')
    j=idx(48,tr);anchor=float(a['normR'][48,j]);xp,yp=lp(48,anchor)
    s.dot(xp,yp,INK,4.3,'white',name=f'c_actual_f48_anchor_{"ABC"[k]}_track{tr}')
    # Endpoint labels attach to actual endpoints, without crossing callout lines.
    end=rows[-1];tx,ty=lp(end['frame'],end['anchor'])
    label_x=tx+8 if end['frame']<53 else tx-23
    label_y=ty-22 if k!=1 else ty+8
    text('ABC'[k],label_x,label_y,24,25,18,INK,True,name=f'c_local_label_{"ABC"[k]}')
    traces.append(dict(label='ABC'[k],track=tr,rows=rows))

provenance=dict(source=str(DATA/'era5.npz'),source_sha256=hashlib.sha256((DATA/'era5.npz').read_bytes()).hexdigest(),
    original_ppt=str(REV/'figures_ppt/All_Figures.pptx'),method='RG-MTM-R20',full_frames=[0,117],local_frames=[43,53],
    color_map='RdBu_r',pressure_hPa=[float(NORM.vmin),float(NORM.vmax)],
    projection='Lambert cylindrical equal-area, standard parallel 52.5 degrees',
    source_geographic_bounds=dict(lon=[-40,50],lat=[25,80]),projected_extent=ex,
    map_aspect_ratio=ratio,direction=a['direction'].tolist(),snapshots=snapshot_records,extrema_f48=coordinate_records,
    actual_tracks=traces,source_semantics=meta['preprocessing'],
    selected_main_minimum_tracks=main_trace_records,event_annotations=event_annotations,
    annotation_scope='Five real saved feature/frame locations; no main-panel dark trajectory overlays. Line contrast comes from scalar display reconstruction. No attribution to Anatol, Lothar or Martin. Five snapshots and event guides remain f20/48/64/80/100.',
    rendering='Saved scalar arrays re-rendered with conservative anchor-aligned display interpolation in 93 of 117 intervals; crossings and jumps over 0.2L retain fixed-position interpolation. All 118 original frame centers and 4096 rows are unchanged. Intermediate columns are display reconstruction, not new observations. Source maps use bilinear scalar display interpolation. Main and local map use one shared full-domain reconstruction. No main-panel dark trajectory overlays, Gaussian blur, changes to frozen arrays or experimental rerun.',
    display_interpolation=dict(temporal='conservative anchor-aligned piecewise linear display reconstruction',samples_per_frame=41,aligned_intervals=RECONSTRUCTION['aligned_intervals'],fallback_intervals=RECONSTRUCTION['fallback_intervals'],spatial='bilinear on original projected raw-field grid',original_frame_centers_exact=True,original_scalar_rows=4096,gaussian_blur=False,main_panel_trajectory_overlays=False,shared_full_and_local_reconstruction=True),
    selected_event_frames=EVENT_FRAMES,frame_time_mapping='frame t is centered at (t+0.5)/118 of the main map',
    missing_identity_intervals='A60 absent f43–47; C56 absent f43–46 and f50–53. No synthetic continuation.')
s.d['notes']=json.dumps(provenance,ensure_ascii=False)
(HERE/'evidence/fig1/scene.json').write_text(json.dumps(s.d,indent=2))
(HERE/'evidence/fig1/data_provenance.json').write_text(json.dumps(provenance,indent=2))
full_rgba=np.asarray(Image.open(ASSETS/'storms_R20_full_f0_f117.png'))
local_rgba=np.asarray(Image.open(ASSETS/'storms_R20_local_f43_f53.png'))
expected=np.round(CM(NORM(a['mapR'][::-1]))*255).astype(np.uint8)
assert np.array_equal(full_rgba[:,20::41],expected)
assert np.array_equal(local_rgba,full_rgba[4096-i1:4096-i0,43*41:54*41])
checks=dict(all_118_original_frame_centers_rgba_exact=True,
    all_4096_scalar_rows_retained=True,local_raster_is_exact_crop_of_full_display=True,
    source_sha256_unchanged=True,actual_tracks_and_event_coordinates_unchanged=True,
    main_panel_trajectory_overlays=False,aligned_intervals=93,fallback_intervals=24,
    note='Only inter-frame display samples reconstructed. Frozen scientific arrays and metrics unchanged.')
(HERE/'evidence/fig1/interpolation_validation.json').write_text(json.dumps(checks,indent=2))
print('Prepared',len(s.d['objects']),'editable/layer objects; source records verified.')
