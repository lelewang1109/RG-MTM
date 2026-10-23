"""Prepare real local Nucleon, Benzene-density and 2-D cylinder inputs.

All source copies are read-only. Dataset variants are named explicitly. No
layout-dependent preprocessing or leaf-count filtering is performed.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, json, lzma, shutil, subprocess
import numpy as np
from netCDF4 import Dataset
from experiments.volume3d.prepare import ROOT, sha256
from experiments.volume3d.run_paper import dump

DATA = ROOT / 'data/real/paper1_suite'
RESULTS = ROOT / 'results/paper1_suite'
BINARY = ROOT / 'tmp/volume3d/native-build/rgmtm_ttk_volume'
SOURCES = Path(__file__).parent / 'source'
BENZENE = Path('/Users/lele/Desktop/pvis项目/9-15实验/inviwo-modules/molvis/gaussian/data/volumes/benzene-dens.cube.xz')
CYLINDER = Path('/Users/lele/Desktop/SpreadMap/SpreadMap_clean/data/raw/cylinder/cylinder2d.nc')


def save_input(name, fields, x, y, protocol):
    directory = DATA/name
    directory.mkdir(parents=True, exist_ok=True)
    fields = np.ascontiguousarray(fields, dtype=np.float32)
    assert fields.ndim == 3 and np.isfinite(fields).all()
    # Fixed affine sign/scale transform shared by every frame: max features
    # become join-tree minima; original scalar values remain recoverable.
    scale = float(np.ptp(fields))
    assert scale > 0
    canonical = -fields/scale
    np.save(directory/'source_fields.npy', fields)
    for t, f in enumerate(canonical):
        np.save(directory/f'input_{t:03d}.npy', np.ascontiguousarray(f[None], dtype='<f4'))
    np.savez(directory/'coordinates.npz', x=x, y=y)
    protocol.update(name=name, shape_tyx=list(fields.shape), scalar_scale=scale,
                    canonical_transform='f_join = -f_source / fixed_sequence_scalar_range',
                    tree_kind='join of negated field = split of source field',
                    spatial_resampling=False, spatial_smoothing=False,
                    per_frame_normalization=False, leaf_filter=False,
                    persistence_threshold_scope='fraction of each source frame scalar range; no frame-wise scalar normalization',
                    native_binary_sha256=sha256(BINARY),
                    source_fields_sha256=sha256(directory/'source_fields.npy'))
    dump(directory/'protocol.json', protocol)
    out = RESULTS/name
    out.mkdir(parents=True, exist_ok=True)
    dump(out/'input_protocol.json', protocol)
    return directory, protocol


def prepare_nucleon():
    p = SOURCES/'nucleon41x41x41_centerslice_padded.raw'
    f = np.fromfile(p, np.uint8).reshape(1, 64, 64).astype(np.float32)
    return save_input('nucleon', f, np.arange(64), np.arange(64), dict(
        source=str(p.relative_to(ROOT)), source_sha256=sha256(p),
        source_url='https://github.com/Wiebke/TemporalMergeTreeMaps',
        author_commit='2c75a10ed2cd55177a25ff751e0c0a8261200717',
        scalar='Nucleon uint8 scalar, original author padded 64x64 slice',
        persistence_fraction=0., original_paper_nodes=28,
        time_semantics='one static frame; temporal metrics not applicable',
        correspondence='same author input; different TTK execution environment'))


def prepare_benzene():
    directory = DATA/'benzene-density'
    directory.mkdir(parents=True, exist_ok=True)
    local = directory/BENZENE.name
    if not local.exists(): shutil.copyfile(BENZENE, local)
    with lzma.open(local, 'rt') as stream:
        stream.readline(); stream.readline()
        row = stream.readline().split(); atoms = int(row[0]); origin = np.array(row[1:4], float)
        axes = [stream.readline().split() for _ in range(3)]
        shape = [int(a[0]) for a in axes]; basis = np.array([a[1:] for a in axes], float)
        atom_rows = [stream.readline().split() for _ in range(atoms)]
        a = np.fromstring(stream.read(), sep=' ').reshape(shape)
    assert np.allclose(basis, np.diag(np.diag(basis)))
    assert [int(r[0]) for r in atom_rows].count(6) == 6
    assert [int(r[0]) for r in atom_rows].count(1) == 6
    # The entire cube is used. z is a slice index, never physical time.
    fields = a.transpose(2, 1, 0)
    x = origin[0]+np.arange(shape[0])*basis[0,0]
    y = origin[1]+np.arange(shape[1])*basis[1,1]
    return save_input('benzene-density', fields, x, y, dict(
        source=str(local.relative_to(ROOT)), source_sha256=sha256(local),
        source_url='https://github.com/inviwo/modules/blob/6152a00ab100ec10c1eb36f078fb42dc949010ab/molvis/gaussian/data/volumes/benzene-dens.cube.xz',
        scalar='Gaussian cube Total SCF electron density; NOT electrostatic potential',
        units='cube atomic units; spatial coordinates in bohr', atoms=atom_rows,
        original_shape_xyz=shape, origin=origin, basis=basis,
        persistence_fraction=.0005, source_z_indices=list(range(shape[2])),
        time_semantics='static molecular volume sliced along z; not molecular dynamics',
        correspondence='Benzene molecule variant: density rather than the paper electrostatic potential',
        exact_paper_dataset=False))


def prepare_cylinder():
    directory = DATA/'cylinder2d'
    directory.mkdir(parents=True, exist_ok=True)
    local = directory/CYLINDER.name
    if not local.exists(): shutil.copyfile(CYLINDER, local)
    with Dataset(local) as ds:
        x = np.asarray(ds['xdim'][:]); y = np.asarray(ds['ydim'][:])
        # Fixed, outcome-independent temporal stride across the FULL time span.
        indices = np.arange(0, len(ds.dimensions['tdim']), 10)
        u = np.asarray(ds['u'][indices], float); v = np.asarray(ds['v'][indices], float)
        fields = np.hypot(u, v).astype(np.float32)
        times = np.asarray(ds['tdim'][indices])
        reynolds = float(ds['Re'][0]); radius = float(ds['radius'][0])
    return save_input('cylinder2d', fields, x, y, dict(
        source=str(local.relative_to(ROOT)), source_sha256=sha256(local),
        source_url='https://cgl.ethz.ch/Downloads/Data/ScientificData/cylinder2d_nc.zip',
        scalar='speed = sqrt(u*u+v*v)', reynolds=reynolds, radius=radius,
        persistence_fraction=.02, source_time_indices=indices, times=times,
        temporal_stride=10, source_frames=1501, spatial_grid='full native 640x80',
        obstacle_handling='retain provided source velocities including obstacle; no holes or imputed scalar values',
        time_semantics='physical simulation time',
        correspondence='related cylinder-flow benchmark, 2-D circular cylinder speed; NOT 3-D square-cylinder Q',
        exact_paper_dataset=False, volumetric_evidence=False))


def extract(directory, protocol, workers=4):
    tree_dir = directory/'trees'; tree_dir.mkdir(exist_ok=True)
    nt, ny, nx = protocol['shape_tyx']
    def one(t):
        prefix = tree_dir/f'frame_{t:03d}'
        record = Path(str(prefix)+'.manifest.json')
        input_path = directory/f'input_{t:03d}.npy'
        threshold = protocol['persistence_fraction']*float(np.ptp(np.load(input_path)))
        expected = dict(input_sha256=sha256(input_path), binary_sha256=sha256(BINARY), threshold=threshold)
        if record.exists():
            old = json.loads(record.read_text())
            if all(old.get(k) == v for k,v in expected.items()) and all(
                    (tree_dir/k).exists() and sha256(tree_dir/k)==v for k,v in old['files'].items()):
                return json.loads(Path(str(prefix)+'.json').read_text())
        with Path(str(prefix)+'.log').open('w') as log:
            subprocess.run([str(BINARY),str(input_path),str(prefix),str(nx),str(ny),'1',
                            str(threshold),'1','0'],check=True,stdout=log,stderr=subprocess.STDOUT)
        suffixes=['.json','.pairs.csv','.nodes.i32','.arcs.i32','.regular.i32','.owner.i32','.values.f32','.offsets.i32']
        dump(record,{**expected,'files':{prefix.name+s:sha256(Path(str(prefix)+s)) for s in suffixes}})
        return json.loads(Path(str(prefix)+'.json').read_text())
    rows=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for t,row in enumerate(pool.map(one,range(nt))):
            rows.append(row)
            print(protocol['name'],'tree',t,'nodes',row['nodes'],'leaves',row['leaves'],flush=True)
    dump(RESULTS/protocol['name']/'tree_summary.json',dict(frames=nt,
        nodes_range=[min(r['nodes'] for r in rows),max(r['nodes'] for r in rows)],
        leaves_range=[min(r['leaves'] for r in rows),max(r['leaves'] for r in rows)],
        records=rows))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', choices=['nucleon','benzene-density','cylinder2d'])
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    prepare={'nucleon':prepare_nucleon,'benzene-density':prepare_benzene,'cylinder2d':prepare_cylinder}[args.dataset]
    extract(*prepare(),workers=args.workers)
