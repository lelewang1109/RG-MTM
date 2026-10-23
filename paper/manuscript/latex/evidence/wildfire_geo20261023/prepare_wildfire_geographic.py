"""Draw supplied FRP cell geometry and the unchanged saved analysis input.

This is a display revision, not a new experiment. Never infer a burn perimeter
from a positive FRP cell or from the smoothed field.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize
from scipy.ndimage import gaussian_filter
from PIL import Image

R = Path(__file__).resolve().parents[1]
C = R.parent / 'code'
B = R / '.build/wildfire_geo20261023'
O = R / 'evidence/wildfire_geo20261023'
sys.path.insert(0, str(R / 'scripts'))
from scene import Scene, BLUE, ORANGE, GREEN

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source = R.parent / 'data/real/wildfire/wildfire.json'
saved = C / 'results/real_case_studies/evidence/wildfire.npz'
meta_path = saved.with_suffix('.json')
event_path = saved.with_name('wildfire_event.json')
d = json.loads(source.read_text())
a = np.load(saved)
meta = json.loads(meta_path.read_text())
event = json.loads(event_path.read_text())
assert sha(source) == meta['source_sha256']
cells = [c for top in d['data'] for c in top.get('children', [])]
lat = np.array([c['lat'] for c in cells], float)
lon = np.array([c['lng'] for c in cells], float)
i0 = d['timeseries']['series'].index('2019-11-01')
values = np.array([c['data'][i0:i0 + 60] for c in cells], float)
values = values.reshape(len(cells), 30, 2).sum(-1)
active = values.sum(1) > 0
co = np.cos(np.deg2rad(lat[active].mean()))
X, Y = lon * co * 111.32, lat * 110.57
side = max(np.ptp(X[active]), np.ptp(Y[active])) * 1.02
cx = (X[active].min() + X[active].max()) / 2
cy = (Y[active].min() + Y[active].max()) / 2
x0, y0 = cx - side / 2, cy - side / 2

def layout_xy(lon, lat):
    return (np.asarray(lon) * co * 111.32 - x0) / side * 120, (np.asarray(lat) * 110.57 - y0) / side * 120

def lonlat(point):
    return [(x0 + point[0] / 120 * side) / (co * 111.32), (y0 + point[1] / 120 * side) / 110.57]

ix = np.clip(((X - x0) / side * 64).astype(int), 0, 63)
iy = np.clip(((Y - y0) / side * 64).astype(int), 0, 63)
raw = np.zeros((30, 64, 64))
for k in np.where(active)[0]:
    raw[:, iy[k], ix[k]] += values[k]
raw = np.log1p(raw)
np.testing.assert_array_equal(raw, a['raw_field'])
smoothed = np.array([gaussian_filter(f, 2.5) for f in raw])
background = np.array([gaussian_filter(f, 16., truncate=50.) for f in raw])
smoothed += 1e-3 * np.ptp(smoothed) * background / max(background.max(), 1e-12)
np.testing.assert_array_equal(smoothed, a['field'])
corner_order = ['point_bl', 'point_br', 'point_tr', 'point_tl']
polygons = np.array([[c['area'][k] for k in corner_order] for c in cells], float)
px, py = layout_xy(polygons[:, :, 0], polygons[:, :, 1])
polygons_xy = np.stack([px, py], axis=-1)
geo = R.parent / 'data/geo/wildfire_context/australia_admin1.geojson'
geo_json = json.loads(geo.read_text())
CM = plt.get_cmap('YlOrBr')
NORMS = [Normalize(0, float(raw.max())), Normalize(0, float(a['field'].max()))]
tracks, colors = [3, 48, 52], [BLUE, ORANGE, GREEN]
frames = [17, 18, 19]
s = Scene(7, 'Wildfires: supplied FRP cells and analysis input')
s.d.update(width=1280, height=1030)
ink, gray = '#000000', '#65727C'

def text(t, x, y, w, h=25, size=18, bold=False, align='left', color=ink):
    s.text(t, x, y, w, h, size, color, bold, align)

def geographic_image(t, processed):
    p = B / 'assets' / f'{"analysis" if processed else "supplied"}_{t}.png'
    fig = plt.figure(figsize=(3.2, 3.2), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#EDF4F8')
    for feature in geo_json['features']:
        geometry = feature['geometry']
        pp = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        for polygon in pp:
            # Outer rings suffice for this coastal context. No lakes occur in
            # the selected comparison at a scale that supports their display.
            ring = np.asarray(polygon[0])
            x, y = layout_xy(ring[:, 0], ring[:, 1])
            ax.fill(x, y, color='#F3F1EA', zorder=1)
    if processed:
        ax.imshow(a['field'][t], origin='lower', extent=[0, 120, 0, 120],
                  cmap=CM, norm=NORMS[1], interpolation='nearest', zorder=2)
    else:
        nonzero = values[:, t] > 0
        pc = PolyCollection(polygons_xy[nonzero], array=np.log1p(values[nonzero, t]),
                            cmap=CM, norm=NORMS[0], edgecolors='none', zorder=3)
        ax.add_collection(pc)
    for feature in geo_json['features']:
        geometry = feature['geometry']
        pp = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        for polygon in pp:
            ring = np.asarray(polygon[0])
            x, y = layout_xy(ring[:, 0], ring[:, 1])
            ax.plot(x, y, color='#687984', lw=.48, zorder=4)
    ax.set(xlim=[0, 120], ylim=[0, 120], aspect='equal')
    ax.axis('off')
    fig.savefig(p, dpi=300)
    plt.close(fig)
    return p

markers = []
def map_panel(t, processed, rect, latitude=False):
    x, y, w, h = rect
    s.image(geographic_image(t, processed), *rect, name=f'actual_{"analysis" if processed else "supplied_cells"}_f{t}')
    s.rect(*rect, 'none', gray, .7)
    point = lambda p: (x + p[0] / 120 * w, y + (120 - p[1]) / 120 * h)
    for lo in [142, 148, 154]:
        xx, _ = point(layout_xy(lo, -30))
        s.line(xx, y+h, xx, y+h+4, gray, .8)
        text(f'{lo} E', xx-22, y+h+6, 44, 23, 15, align='center')
    if latitude:
        for la in [-28, -32, -36]:
            _, yy = point(layout_xy(145, la))
            s.line(x-4, yy, x, yy, gray, .8)
            text(f'{-la} S', x-49, yy-9, 40, 23, 15, align='right')
    # Geographic locations are fixed facts, not inferred from scalar colors.
    for name, lo, la in [('QLD', 143.7, -28.5), ('NSW', 143.7, -33.3), ('VIC', 142.8, -37.4)]:
        xx, yy = point(layout_xy(lo, la))
        text(name, xx-18, yy-10, 45, 20, 12, color=gray)
    # A 200 km bar in exactly the same equirectangular coordinates as the data.
    length = 200 / side * w
    bx, by = x + w - length - 12, y + h - 15
    s.line(bx, by, bx+length, by, ink, 1.6)
    s.line(bx, by-3, bx, by+3, ink, 1.3)
    s.line(bx+length, by-3, bx+length, by+3, ink, 1.3)
    text('200 km', bx-7, by-21, length+14, 21, 12, align='center')
    for letter, tr, color in zip('ABC', tracks, colors):
        j = int(np.flatnonzero(a['track'][t] == tr)[0])
        p = a['xy'][t, j]
        xx, yy = point(p)
        s.dot(xx, yy, '#FFFFFF', 5.9, '#FFFFFF')
        s.dot(xx, yy, color, 4.1, '#FFFFFF', f'{letter}_f{t}_{processed}')
        dx = 8 if xx < x+w-26 else -27
        text(letter, xx+dx, yy-24, 28, 26, 20, True, color=color)
        markers.append(dict(frame=t, analysis=processed, label=letter, track=tr,
                            layout_xy=p.tolist(), lonlat=lonlat(p), slide_xy=[xx, yy]))

text('(c) Actual FRP records and corresponding analysis fields', 18, 242, 860, 31, 23, True)
text('Supplied 10 km cells: two-date FRP sums', 60, 279, 800, 26, 20, True)
for k, t in enumerate(frames):
    start = str(a['dates'][t]); stop = d['timeseries']['series'][i0+2*t+1]
    x = 60 + k*283
    text(f'f{t}: {start[5:]} to {stop[5:]}', x-8, 306, 238, 25, 18, True, 'center')
    map_panel(t, False, (x, 335, 220, 220), latitude=k == 0)
    text(f'{int((values[:,t]>0).sum())} cells with positive FRP', x-12, 588, 244, 24, 16, align='center')
text('Analysis input: 64 x 64 grid, 50.7 km Gaussian smoothing', 60, 640, 820, 26, 20, True)
for k, t in enumerate(frames):
    map_panel(t, True, (60+k*283, 680, 220, 220), latitude=k == 0)

for row, y in [(0, 618), (1, 955)]:
    norm = NORMS[row]
    p = B/'assets'/f'colorbar_{row}.png'
    Image.fromarray(np.rint(CM(norm(np.linspace(norm.vmin, norm.vmax, 600)[None,:]))*255).astype('uint8')).save(p)
    s.image(p, 410, y, 340, 10)
    text('log(1 + FRP sum / MW)' if row == 0 else 'Processed log-FRP', 60, y-6, 330, 24, 17)
    text('0', 383, y-6, 22, 23, 15, align='right')
    text(f'{norm.vmax:.2f}', 759, y-6, 76, 23, 15)

text('(d) Frame 18: saved profiles', 898, 246, 370, 29, 22, True)
text('Processed log-FRP', 935, 293, 320, 24, 17)
rect = (935, 337, 312, 178)
def profile_xy(u, v):
    x, y, w, h = rect
    return x+u*w, y+(4.3-v)/5.*h
for v in [0, 2, 4]:
    xx, yy = profile_xy(0, v)
    s.line(xx, yy, xx+rect[2], yy, '#DEE3E7', .6)
    text(str(v), xx-35, yy-10, 27, 24, 16, align='right')
for u in [0, .5, 1]:
    xx, yy = profile_xy(u, -.7)
    text(f'{u:g}', xx-20, yy+6, 40, 24, 16, align='center')
s.rect(*rect, 'none', gray, .7)
for method, color, dash in [('P', BLUE, True), ('R', GREEN, False)]:
    v = a['map'+method][:,18]
    s.path([profile_xy(u, val) for u, val in zip(np.linspace(0,1,len(v)),v)], color, 1.6, dash, 'complete_saved_'+method+'_profile')
    for letter, tr, cc in zip('ABC', tracks, colors):
        j = int(np.flatnonzero(a['track'][18] == tr)[0])
        xx, yy = profile_xy(float(a['norm'+method][18,j]), float(a['value'][18,j]))
        s.dot(xx, yy, cc, 3.5, 'white')
        dx = -23 if method == 'R' and letter == 'A' else 5
        text(letter, xx+dx, yy-22, 23, 23, 16, True, color=cc)
text('Normalized reference coordinate', 925, 557, 340, 23, 16, align='center')
s.line(950, 601, 981, 601, BLUE, 1.8, True); text('P', 990, 589, 45, 24, 18)
s.line(1080, 601, 1111, 601, GREEN, 1.8); text('R20', 1120, 589, 100, 24, 18)
text('(e) Pair merge levels, frame 18', 898, 641, 370, 29, 22, True)
for t, x, w in [('Pair', 900, 60), ('Source = P', 969, 130), ('R20', 1125, 115)]:
    text(t, x, 689, w, 24, 18, True)
s.line(900, 722, 1250, 722, gray, .8)
pairs = []
for k, row in enumerate(event['pair_merge_levels']):
    measured = {}
    for method in ['P', 'R']:
        js = [int(np.flatnonzero(a['track'][18] == tracks['ABC'.index(letter)])[0]) for letter in row['pair']]
        indices = np.rint(a['norm'+method][18,js]*(len(a['map'+method])-1)).astype(int)
        l, h = sorted(indices)
        measured[method] = float(a['map'+method][l:h+1,18].min())
        assert measured[method] == row[method]
    pairs.append(dict(pair=row['pair'], source=row['true'], **measured))
    for t, x, w in [(row['pair'], 900, 60), (f'{row["true"]:.4f}', 969, 130), (f'{row["R"]:.4f}', 1125, 120)]:
        text(t, x, 740+k*37, w, 25, 18)
text('Measured NMLE: 15.09% of range', 900, 864, 370, 25, 18, True)
text('Max anchor error: 14.75% to 2.63% L', 900, 900, 370, 25, 18)
text('Negative R connections are artificial', 900, 940, 370, 24, 17)
text('values in the one-dimensional map.', 900, 963, 370, 24, 17)
text('A/B/C: extrema of the analysis field, located on both rows. Positive FRP cells describe detections, not a burn perimeter.', 60, 996, 1200, 25, 18)

record = dict(display_revision_only=True, frames=frames, tracks=tracks,
              source='Franke et al., hierarchically aggregated satellite FRP, supplied 10 km cells',
              source_sha256={str(p):sha(p) for p in [source,saved,meta_path,event_path,geo,geo.with_name('source.json')]},
              projection=dict(type='existing equirectangular coordinates',cos_phi0=float(co),x0_km=float(x0),y0_km=float(y0),side_km=float(side),extent_lonlat=[lonlat([0,0]),lonlat([120,120])]),
              analysis=dict(grid=64,cell_km=float(side/64),sigma_cells=2.5,sigma_km=float(2.5*side/64),background='1e-3 * ptp(smoothed) * Gaussian(raw_log, sigma=16, truncate=50) / maximum',raw_grid_exact=True,processed_exact=True),
              snapshots=[dict(frame=t,date_start=str(a['dates'][t]),date_end=d['timeseries']['series'][i0+2*t+1],positive_source_cells=int((values[:,t]>0).sum()),positive_64_grid_cells=int((raw[t]>0).sum()))for t in frames],
              source_color_range=[0,float(raw.max())],analysis_color_range=[0,float(a['field'].max())],markers=markers,pairs=pairs,
              interpretation='Actual supplied cell polygons, no interpolation of source observations. Analysis smoothing is explicitly separate. Zero source cells are omitted. No fire boundary or burned area is inferred.',
              basemap_source=json.loads(geo.with_name('source.json').read_text()))
s.d['notes']=json.dumps(record)
(B/'scenes/Fig7_geographic.json').write_text(json.dumps(s.d,indent=2)+'\n')
(O/'geographic_provenance.json').write_text(json.dumps(record,indent=2)+'\n')
np.savez_compressed(O/'display_source_subset.npz',frames=frames,cell_lonlat_polygons=polygons,source_two_date_FRP=values[:,frames].T,raw_grid=raw[frames],analysis=a['field'][frames])
print(json.dumps(dict(snapshots=record['snapshots'],side_km=side,cell_km=side/64,sigma_km=2.5*side/64,raw_and_analysis_exact=True),indent=2))
