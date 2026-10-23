"""Prepare the original 3-D square-cylinder simulation on its native grid.

The public author archive has 102 time steps rather than the paper's 508.
Compute Q on the full 192x64x48 velocity grid, then retain x indices 57..191
as in the author's spatial subset. Never turn z slices into time steps.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse, json, subprocess
import numpy as np
from experiments.paper1_suite.prepare import DATA, RESULTS, BINARY
from experiments.volume3d.prepare import ROOT, DATA as CYLINDER_DATA, read_amira_vector, q_criterion, sha256, validate_archive
from experiments.volume3d.run_paper import dump


def extract(name,workers=4):
    directory=DATA/name;protocol=json.loads((directory/'protocol.json').read_text())
    tree_dir=directory/'trees';tree_dir.mkdir(exist_ok=True)
    nt,nz,ny,nx=protocol['shape_tzyx']
    def one(t):
        prefix=tree_dir/f'frame_{t:03d}';source=directory/f'input_{t:03d}.npy'
        threshold=protocol['persistence_fraction']*float(np.ptp(np.load(source,mmap_mode='r')))
        expected=dict(input_sha256=sha256(source),binary_sha256=sha256(BINARY),threshold=threshold)
        manifest=Path(str(prefix)+'.manifest.json')
        valid=False
        if manifest.exists():
            old=json.loads(manifest.read_text())
            valid=all(old.get(k)==v for k,v in expected.items()) and all(
                (tree_dir/k).exists() and sha256(tree_dir/k)==v for k,v in old['files'].items())
        if not valid:
            with Path(str(prefix)+'.log').open('w') as log:
                subprocess.run([str(BINARY),str(source),str(prefix),str(nx),str(ny),str(nz),str(threshold),'1','0'],
                    stdout=log,stderr=subprocess.STDOUT,check=True)
        suffixes=['.json','.pairs.csv','.nodes.i32','.arcs.i32','.regular.i32','.owner.i32','.values.f32','.offsets.i32']
        dump(manifest,{**expected,'files':{prefix.name+s:sha256(Path(str(prefix)+s)) for s in suffixes}})
        return json.loads(Path(str(prefix)+'.json').read_text())
    rows=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for t,r in enumerate(pool.map(one,range(nt))):
            rows.append(r);print(name,'3D tree',t,'nodes',r['nodes'],'leaves',r['leaves'],flush=True)
    dump(RESULTS/name/'tree_summary.json',dict(frames=nt,nodes_range=[min(r['nodes'] for r in rows),max(r['nodes'] for r in rows)],
        leaves_range=[min(r['leaves'] for r in rows),max(r['leaves'] for r in rows)],records=rows))


def cylinder():
    archive=CYLINDER_DATA/'SquareCylinder.7z'
    validate_archive(archive)
    unpacked=CYLINDER_DATA/'unpacked'
    files=[]
    for p in unpacked.rglob('*'):
        if p.suffix.lower()=='.am':
            with p.open('rb') as f:header=f.read(2048)
            if b'define Lattice' in header and b'float[3]' in header:files.append(p)
    # Amira members contain numeric timestamps; filename lexicographic ordering
    # is not sufficient when timestamps are not zero padded.
    import re
    def key(p):return [float(v) if re.fullmatch(r'\d+(?:\.\d+)?',v) else v for v in re.split(r'(\d+(?:\.\d+)?)',p.stem)]
    files.sort(key=key)
    if len(files)!=102:raise ValueError(f'expected 102 vector fields; found {len(files)}')
    name='square-cylinder3d';directory=DATA/name;directory.mkdir(parents=True,exist_ok=True)
    out=RESULTS/name;out.mkdir(parents=True,exist_ok=True)
    field_path=directory/'source_fields.npy'
    fields=np.lib.format.open_memmap(field_path,mode='w+',dtype='<f4',shape=(102,48,64,135))
    sources=[];bounds=None
    for t,path in enumerate(files):
        velocity,bounds=read_amira_vector(path)
        assert velocity.shape==(48,64,192,3)
        spacing=(bounds[1::2]-bounds[::2])/(np.array([192,64,48])-1)
        q=q_criterion(velocity,spacing)
        fields[t]=q[:,:,57:192]
        sources.append(dict(index=t,filename=str(path.relative_to(ROOT)),sha256=sha256(path)))
        print('source 3D Q',t,float(fields[t].min()),float(fields[t].max()),flush=True)
    fields.flush();scale=float(fields.max()-fields.min())
    for t in range(102):np.save(directory/f'input_{t:03d}.npy',np.ascontiguousarray(-fields[t]/scale,dtype='<f4'))
    xyz=[np.linspace(bounds[2*i],bounds[2*i+1],n) for i,n in enumerate([192,64,48])]
    np.savez(directory/'coordinates.npz',x=xyz[0][57:192],y=xyz[1],z=xyz[2])
    protocol=dict(name=name,shape_tzyx=[102,48,64,135],original_velocity_shape_tzyxc=[102,48,64,192,3],
        scalar='Q = -0.5 trace(J^2), computed from original 3-component 3-D velocities before crop',
        source_url='https://people.kth.se/~weinkauf/datasets/SquareCylinder.7z',
        source_page='https://tinoweinkauf.net/notes/squarecylinder.html',source_archive_sha256=sha256(archive),
        sources=sources,scalar_scale=scale,source_fields_sha256=sha256(field_path),
        canonical_transform='f_join=-Q/fixed_sequence_Q_range; split tree of Q via join tree of -Q',
        persistence_fraction=.02,persistence_threshold_scope='2% of each frame scalar range; no per-frame normalization',
        source_bounds=bounds.tolist(),crop='original x grid indices [57,192); y,z unchanged',
        spatial_resampling=False,spatial_smoothing=False,leaf_filter=False,per_frame_normalization=False,
        derivatives='central finite differences, second order one-sided at domain boundaries',
        periodic_boundary_note='source flow is periodic in z; derivative uses provided endpoints with one-sided boundaries; boundary features flagged',
        time_semantics='physical time sequence, author public archive full 102 frames; each frame is a 3-D volume',
        correspondence='same original square-cylinder DNS/public author resampling; 102 frames rather than paper 508',
        volumetric_evidence=True,exact_paper_dataset=False,
        native_binary_sha256=sha256(BINARY))
    dump(directory/'protocol.json',protocol);dump(out/'input_protocol.json',protocol)
    return name


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();extract(cylinder(),args.workers)
