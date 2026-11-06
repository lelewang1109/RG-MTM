"""Extract editable contour geometry from the approved reference (no raster output)."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_dilation
from scipy.interpolate import splprep, splev
from skimage.morphology import skeletonize, remove_small_objects
from skimage.measure import find_contours, approximate_polygon

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'open_mechanisms_20261106'
a=np.asarray(Image.open(SRC/'01_direction.png').convert('RGB')).astype(float)
lum=a.mean(axis=2)
chroma=a.max(axis=2)-a.min(axis=2)
# Thin gray contour strokes are locally darker than the smooth scalar-field wash.
hp=gaussian_filter(lum,2)-lum
mask=(hp>3)&(lum>105)&(lum<241)&(chroma<125)
# Explicit foreground exclusion. The q axis/fan are outside the field contour support.
Y,X=np.indices(lum.shape)
mask &= ~(Y>900)
for x0,y0,x1,y1 in [(420,315,461,364),(632,485,675,534),(930,330,981,380),(1210,147,1260,198)]:
    mask[y0:y1,x0:x1]=False
mask=remove_small_objects(mask,min_size=24)
sk=skeletonize(mask)
pts=set(zip(*np.where(sk)))
def neighbors(p):
    y,x=p
    return [(y+dy,x+dx) for dy in (-1,0,1) for dx in (-1,0,1) if (dy or dx) and (y+dy,x+dx) in pts]
adj={p:neighbors(p) for p in pts}
visited=set(); paths=[]
def edge(a,b):return tuple(sorted((a,b)))
for start in sorted(pts,key=lambda p:(len(adj[p])==2,p)):
    for nxt in adj[start]:
        if edge(start,nxt) in visited:continue
        seq=[start];prev=start;cur=nxt
        visited.add(edge(prev,cur))
        while True:
            seq.append(cur)
            options=[v for v in adj[cur] if v!=prev and edge(cur,v) not in visited]
            if len(adj[cur])!=2 or not options:break
            prev,cur=cur,options[0];visited.add(edge(prev,cur))
        if len(seq)<25:continue
        xy=np.array(seq)[:,::-1].astype(float)
        length=np.linalg.norm(np.diff(xy,axis=0),axis=1).sum()
        tck,_=splprep(xy.T,s=len(xy)*.20,k=3)
        ts=np.linspace(0,1,max(3,int(length/15)))
        pp=np.array(splev(ts,tck)).T;dd=np.array(splev(ts,tck,der=1)).T
        cmd=[['M',*pp[0]]]
        for j in range(1,len(ts)):
            dt=(ts[j]-ts[j-1])/3
            cmd.append(['C',*(pp[j-1]+dt*dd[j-1]),*(pp[j]-dt*dd[j]),*pp[j]])
        vals=np.array([a[y,x] for y,x in seq])
        c=np.percentile(vals,20,axis=0).astype(int)
        # Match line tint but avoid making anti-alias pixels into overly pale strokes.
        c=np.clip(c,125,205)
        paths.append({'commands':[[v[0],*[round(float(x),2) for x in v[1:]]] for v in cmd],'color':'#'+''.join(f'{v:02x}' for v in c)})

# Reconstruct smooth washes as nested editable freeform regions, not pixel mosaics.
fills=[]
for key,box,base in [('A',(110,220,580,580),(0,127,255)),('C',(180,430,735,800),(0,180,175)),('D',(650,255,1080,620),(164,54,195)),('B',(930,65,1390,370),(255,132,0))]:
    x0,y0,x1,y1=box
    im=a[y0:y1,x0:x1]
    r,gg,b=im[:,:,0],im[:,:,1],im[:,:,2]
    density={'A':(b-gg)/128,'C':(2*gg-r-b)/185,'D':(r-gg)/110,'B':(r-b)/255}[key]
    density=np.maximum(0,density)
    bad=(im.min(axis=2)<145)|(density>.44)
    bad=binary_dilation(bad,iterations=4)
    inds=distance_transform_edt(bad,return_distances=False,return_indices=True)
    density=np.where(bad,density[tuple(inds)],density)
    density=gaussian_filter(density,8)
    density=np.pad(density,1)
    for lev in np.arange(.012,.365,.012):
        for contour in find_contours(density,lev):
            if len(contour)<40:continue
            xy=approximate_polygon(contour[:,::-1],tolerance=.7)
            xy+=np.array([x0-1,y0-1])
            fill=np.round(255*(1-lev)+np.array(base)*lev).astype(int)
            fills.append({'name':key,'points':xy.round(2).tolist(),'color':'#'+''.join(f'{v:02x}' for v in fill)})
(HERE/'direction_geometry.json').write_text(json.dumps({'strokes':paths,'fills':fills},separators=(',',':')))
print(f'Extracted {len(paths)} contour paths and {len(fills)} smooth field regions.')
