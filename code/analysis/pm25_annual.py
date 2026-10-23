"""Full-calendar 2000 PM2.5 input, fixed region/grid/smoothing as January.
Separate experiment identity; historical January/seasonal records remain unchanged.
"""
from pathlib import Path
from functools import partial
import public_scalar as ps
NAME='pm25_2000'
OUT=ps.ROOT/'results/pm25_2000'
def register():
 ps.SPECS[NAME]=dict(ps.SPECS['pm25'],start='2000-01-01',end='2000-12-31',fixed_sigma_km=100.)
 import replicate as rp
 rp.LOADERS[NAME]=partial(ps.load,NAME)
 return ps.SPECS[NAME]
