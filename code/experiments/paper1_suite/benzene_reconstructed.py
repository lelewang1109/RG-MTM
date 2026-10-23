"""Explicitly reconstructed Benzene potential: 21 static 2-D z sections.

This is a 12-site OPLS-AA Coulomb model, NOT the paper's author input or
an ab-initio electrostatic potential. Only atom positions are read from the
public Gaussian cube; its electron-density values are never used.
"""
from pathlib import Path
import argparse
import json
import lzma
import shutil
import numpy as np
from experiments.paper1_suite.prepare import DATA, RESULTS, ROOT, BINARY, sha256, extract
from experiments.volume3d.run_paper import dump

NAME = 'benzene-potential-reconstructed2d'
CHARGE_URL = 'https://zarbi.chem.yale.edu/doc/boss49.pdf'
GEOMETRY_URL = ('https://github.com/inviwo/modules/blob/'
    '6152a00ab100ec10c1eb36f078fb42dc949010ab/'
    'molvis/gaussian/data/volumes/benzene-dens.cube.xz')


def prepare():
    directory = DATA / NAME
    out = RESULTS / NAME
    directory.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    geometry = directory / 'benzene-geometry-source.cube.xz'
    if not geometry.exists():
        shutil.copyfile(DATA / 'benzene-density/benzene-dens.cube.xz', geometry)
    manual = directory / 'boss49.pdf'
    if not manual.exists():
        shutil.copyfile(ROOT / 'tmp/benzene-potential/boss49.pdf', manual)
    with lzma.open(geometry, 'rt') as f:
        f.readline(); f.readline()
        count = int(f.readline().split()[0])
        for _ in range(3):
            f.readline()
        atoms = [f.readline().split() for _ in range(count)]
    species = np.array([int(a[0]) for a in atoms])
    positions = np.array([a[2:5] for a in atoms], float)
    assert count == 12 and sorted(species.tolist()) == [1]*6 + [6]*6
    charges = np.where(species == 6, -.115, .115)
    assert abs(charges.sum()) < 1e-14
    # Prespecified grid, selected before examining any layout scores. No
    # softening, clipping, smoothing, fitted charge or outcome-dependent grid.
    x = np.linspace(-6., 6., 61)
    y = np.linspace(-6., 6., 61)
    slice_z = np.linspace(-2., 2., 21)
    zz, yy, xx = np.meshgrid(slice_z, y, x, indexing='ij')
    samples = np.stack([xx, yy, zz], axis=-1)
    potential = np.zeros(xx.shape)
    minimum_distance = np.inf
    for charge, atom in zip(charges, positions):
        distance = np.linalg.norm(samples - atom, axis=-1)
        minimum_distance = min(minimum_distance, float(distance.min()))
        assert np.all(distance > 0), 'grid contains a singular charge site'
        potential += charge / distance
    fields = potential.astype('<f4')
    assert np.isfinite(fields).all()
    scale = float(np.ptp(fields))
    np.save(directory / 'source_fields.npy', fields)
    # Positive sign: minima of physical V, as opposed to the density pilot's
    # maxima. z is only the sequence coordinate; native extraction is nx*ny*1.
    for t, field in enumerate(fields):
        np.save(directory / f'input_{t:03d}.npy', (field[None]/scale).astype('<f4'))
    np.savez(directory / 'coordinates.npz', x=x, y=y, slice_z=slice_z)
    model = dict(model='OPLS-AA 12-site fixed point charges; vacuum Coulomb potential',
        charge_e={'C': -.115, 'H': .115}, charge_source_url=CHARGE_URL,
        charge_source_page=67, charge_source_table=1,
        charge_source_sha256=sha256(manual), charge_source_file=str(manual.relative_to(ROOT)),
        geometry_source_url=GEOMETRY_URL, geometry_source_sha256=sha256(geometry),
        geometry_source_file=str(geometry.relative_to(ROOT)),
        atom_species=species, atom_positions_bohr=positions, atom_charge_e=charges,
        net_charge_e=float(charges.sum()),
        formula='V(r) = sum_i q_i / ||r-R_i||; r in bohr, q in elementary charge, V in atomic units',
        dielectric_relative=1., softening_bohr=0., clipping=False,
        electron_density_used=False, geometry_optimized=False,
        minimum_grid_distance_to_charge_bohr=minimum_distance,
        generator_source_file=str(Path(__file__).relative_to(ROOT)),
        generator_source_sha256=sha256(__file__))
    dump(directory/'model.json', model)
    dump(out/'model.json', model)
    protocol = dict(name=NAME, label='Benzene electrostatic potential reconstruction (OPLS-AA); NOT author original',
        reconstruction=True, exact_paper_dataset=False, original_file_available=False,
        user_authorization='user accepted explicitly labeled reconstructed potential; clarified Benzene is 2-D',
        correspondence='same molecule and scalar type; independently chosen 12-site model, geometry and domain',
        scalar='electrostatic potential of OPLS-AA partial charges, not electron density or ab-initio potential',
        scalar_unit='atomic unit of electrostatic potential (Hartree/e)',
        shape_tyx=list(fields.shape), spatial_dimensions_per_frame=2,
        x_bounds_bohr=[-6., 6.], y_bounds_bohr=[-6., 6.], slice_z_bohr=slice_z,
        scalar_scale=scale, canonical_sign=1,
        canonical_transform='f_join = +V_source / fixed_sequence_scalar_range',
        tree_kind='join tree of physical potential minima',
        source_fields_sha256=sha256(directory/'source_fields.npy'),
        model_sha256=sha256(directory/'model.json'),
        native_binary_sha256=sha256(BINARY),
        persistence_fraction=.0005,
        persistence_threshold_scope='0.05% of each frame range; applied identically for all methods',
        grid_adjacency='TTK implicit regular-grid triangulation; nonperiodic 2-D sections',
        spatial_resampling=False, spatial_smoothing=False, per_frame_normalization=False,
        leaf_filter=False, physical_time=False,
        time_semantics='21 parallel 2-D sections of a static 3-D point-charge field; z is not time',
        original_paper_shape_tyx=[21,61,61], original_paper_nodes=[14,68],
        difference_from_original='not the author potential file or fractional-charge construction; node counts not fitted',
        original_342_frame_table_modified=False)
    dump(directory/'protocol.json', protocol)
    dump(out/'input_protocol.json', protocol)
    return directory, protocol


def run():
    from experiments.paper1_suite.run import run as run_layout
    run_layout(NAME)
    manifest_path=RESULTS/NAME/'source_manifest.json'
    manifest=json.loads(manifest_path.read_text())
    for name in ['benzene_reconstructed.py', 'audit_benzene_source.py',
                 'verify_benzene_reconstructed.py', 'report_benzene_reconstructed.py']:
        source=Path(__file__).with_name(name)
        manifest[str(source.relative_to(ROOT))]=sha256(source)
    dump(manifest_path,manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'run'])
    args = parser.parse_args()
    if args.action == 'prepare':
        extract(*prepare())
    else:
        run()
