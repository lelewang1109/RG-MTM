"""Optional regeneration of the final compact P cache from original frozen inputs."""
from pathlib import Path
import sys,numpy as np
OUT=Path(__file__).resolve().parent;PAPER=OUT.parent;CODE=PAPER.parent/'code'
sys.path[:0]=[str(CODE/'analysis'),str(CODE),str(CODE/'src')]
from experiments import era5 as ep
import general_method as gm,conflict_strategies as cs,relax_hierarchy as rh,filling
from rgmtm.reference_points import reference_points_from_frames
f=np.load(PAPER/'evidence/fig1/december1999_xaxis/fields.npz');a=np.load(PAPER/'evidence/fig1/december1999_data_direction/results.npz')
sc=ep.scene_from_fields(f['fields'],f['coords'],float(f['geometry'][2]),max_leaves=None)
origin,L=a['geometry'];p=gm.universal_parameters(origin,L,49*49*float(f['geometry'][2]))
ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum');qs=[v@a['direction'] for v in ext]
assert max(np.max(abs((q-origin)/L-a['qnorm'][t,:len(q)])) for t,q in enumerate(qs))<1e-12
rows=cs.solve_weighted_sequence(sc,qs,{},p);cs.validate_weighted(sc,rows,p)
maps,skeletons,_=rh.render(sc,rows,p,4096)
snapshots=np.array([601,602,603,605,607]);map_frames=np.arange(601,608)
for t in map_frames:
 sk=skeletons[t];maps[:,t],_=filling.optimal_fill(maps[:,t],list(sk.ordering),sk.anchors,sc['frames'][t],'join')
norm=np.full(a['normR'].shape,np.nan)
for t in map_frames:norm[t,:len(rows[t]['x'])]=(rows[t]['x']-origin)/L
np.savez_compressed(OUT/'positions.npz',frames=snapshots,map_frames=map_frames,mapP=maps[:,map_frames],normP=norm[snapshots],normPmap=norm[map_frames])
print('Regenerated final five-snapshot/seven-hour P cache; original evidence untouched.')
