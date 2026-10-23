"""Independent scalar reconstruction using scalar Python arithmetic and fsum."""
import json
import lzma
import math
import numpy as np
from experiments.paper1_suite.prepare import ROOT, BINARY, sha256


def verify_potential_source(directory, protocol):
    model = json.loads((directory/'model.json').read_text())
    assert sha256(directory/'model.json') == protocol['model_sha256']
    for role in ['geometry_source', 'charge_source', 'generator_source']:
        assert sha256(ROOT/model[role+'_file']) == model[role+'_sha256'], role
    assert protocol['canonical_sign'] == 1 and protocol['tree_kind'].startswith('join')
    assert sha256(BINARY) == protocol['native_binary_sha256']
    assert model['charge_e'] == {'C': -.115, 'H': .115}
    assert not model['electron_density_used'] and model['softening_bohr'] == 0
    with lzma.open(ROOT/model['geometry_source_file'], 'rt') as f:
        lines = f.readlines()
    count = int(lines[2].split()[0])
    atoms = [line.split() for line in lines[6:6+count]]
    positions = [tuple(map(float, a[2:5])) for a in atoms]
    species = [int(a[0]) for a in atoms]
    charges = [-.115 if s == 6 else .115 for s in species]
    assert species.count(6) == 6 and species.count(1) == 6
    assert abs(math.fsum(charges)) < 1e-15
    np.testing.assert_array_equal(positions, model['atom_positions_bohr'])
    np.testing.assert_array_equal(charges, model['atom_charge_e'])
    coords = np.load(directory/'coordinates.npz')
    xs, ys, zs = coords['x'], coords['y'], coords['slice_z']
    assert len(xs) == len(ys) == 61 and len(zs) == 21
    source = np.load(directory/'source_fields.npy')
    def evaluate(x, y, z):
        return math.fsum(q/math.sqrt((x-a)**2+(y-b)**2+(z-c)**2)
                         for q,(a,b,c) in zip(charges,positions))
    expected = np.array([[[evaluate(float(x),float(y),float(z)) for x in xs]
                           for y in ys] for z in zs], dtype='<f4')
    np.testing.assert_array_equal(expected, source)
    assert float(np.ptp(source)) == protocol['scalar_scale']
    for t in range(len(zs)):
        prefix=directory/'trees'/f'frame_{t:03d}'
        manifest=json.loads(prefix.with_suffix('.manifest.json').read_text())
        field=np.load(directory/f'input_{t:03d}.npy')
        assert field.shape == (1,61,61)
        assert manifest['threshold'] == .0005*float(np.ptp(field))
        assert manifest['binary_sha256'] == protocol['native_binary_sha256']
    # Molecular z coordinates retain the tiny deviations in the public geometry;
    # record reflection discrepancy rather than imposing exact symmetry.
    reflection=float(np.max(abs(source-source[::-1])))/protocol['scalar_scale']
    return dict(passed=True, model='OPLS-AA 12-site partial-charge Coulomb reconstruction',
        independently_recomputed_samples=int(expected.size),
        independent_arithmetic='Python math.sqrt + math.fsum, all grid samples',
        float32_source_max_difference=float(np.max(abs(expected-source))),
        neutral_charge_e=math.fsum(charges), normalized_z_reflection_discrepancy=reflection,
        density_values_used=False, coordinates_unit='bohr', physical_time=False,
        original_author_dataset=False, audit_source_sha256=sha256(__file__))
