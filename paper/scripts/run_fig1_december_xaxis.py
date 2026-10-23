"""Authorized Figure 1 experiment: genuine hourly December 1999, fixed eastward d.
No original experiment/output is overwritten. Save new scientific results separately.
"""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np
from netCDF4 import Dataset,num2date
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter,uniform_filter1d
R=Path(__file__).resolve().parents[1];ROOT=R.parent/'code'
sys.path[:0]=[str(ROOT/'analysis'),str(ROOT),str(ROOT/'src')]
from experiments import era5 as ep
import era5_expanded as ex
OUT=R/'evidence/fig1/december1999_xaxis';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ep.SOURCE
N=49;co=np.cos(np.deg2rad(ep.PHI));bx=ep.R*co*np.deg2rad([-30,40]);by=ep.R*np.sin(np.deg2rad([30,75]))/co
X,Y=np.meshgrid(np.linspace(bx[0],bx[1],N,endpoint=False)+np.diff(bx)[0]/N/2,np.linspace(by[0],by[1],N,endpoint=False)+np.diff(by)[0]/N/2)
pts=np.c_[np.rad2deg(np.arcsin(Y.ravel()*co/ep.R)),np.rad2deg(X.ravel()/ep.R/co)]
dx=np.diff(bx)[0]/N;dy=np.diff(by)[0]/N;fac=120/np.hypot(np.ptp(bx),np.ptp(by));coords=np.c_[(X.ravel()-bx.mean())*fac+60,(Y.ravel()-by.mean())*fac+60];area=dx*dy*fac**2
start=time.perf_counter()
with Dataset(SOURCE) as ds:
 dates=np.array([str(v) for v in num2date(ds['valid_time'][:],ds['valid_time'].units)])
 lat=np.asarray(ds['latitude'][:]);lon=np.asarray(ds['longitude'][:]);hours=[]
 for i in range(len(dates)):
  field=np.asarray(ds['msl'][i],float)/100
  hours.append(RegularGridInterpolator((lat,lon),field)(pts).reshape(N,N))
  if i%240==0:print('read',i,len(dates),flush=True)
pressure=np.asarray(hours);baseline=uniform_filter1d(pressure,size=192,axis=0,mode='nearest')
select=np.flatnonzero((dates>='1999-12-01 00:00:00')&(dates<='1999-12-31 23:00:00'));assert len(select)==744
anomaly=pressure[select]-baseline[select]
smooth=np.asarray([gaussian_filter(f,(250/dy,250/dx),mode='reflect') for f in anomaly])
filled=[]
for f in smooth:
 mk=ex.strict_minima(f)
 if not mk.any():mk[np.unravel_index(f.argmin(),f.shape)]=True
 filled.append(ex.impose_minima(f,mk))
filled=np.asarray(filled)
np.savez_compressed(OUT/'fields.npz',fields=filled,smooth=smooth,anomaly=anomaly,coords=coords,dates=dates[select],source_indices=select,lonlat=pts[:,::-1],geometry=np.array([dx,dy,area]))
print('preprocessed',filled.shape,'leaves:',min(ex.strict_minima(f).sum() for f in smooth),max(ex.strict_minima(f).sum() for f in smooth),flush=True)
protocol=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),period=[str(dates[select][0]),str(dates[select][-1])],frames=744,step_hours=1,direction=[1.,0.],field='mean sea level pressure anomaly',units='hPa',baseline='centered 192-hour moving average, indices t-96 through t+95; actual surrounding hourly source observations',projection='Lambert cylindrical equal area, standard parallel52.5',extent_lon=[-30,40],extent_lat=[30,75],grid=[49,49],smoothing_sigma_km=250,boundary='reflect for smoothing; non-interior minima removed by existing priority-flood minima imposition',same_as_reference='time range and hourly sampling only; 49x49 analysis grid and 250km smoothing follow RG-MTM, not an exact replication of the papers preprocessing',seconds=time.perf_counter()-start)
(OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
print(json.dumps(protocol,indent=2),flush=True)
