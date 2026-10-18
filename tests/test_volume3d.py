"""Independent scientific contracts for volume inputs and projection limits."""
from pathlib import Path
import sys
import unittest
import tempfile
import importlib.util
import struct
import zlib
import numpy as np
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'analysis')]
from experiments import era5 as ep
from experiments.volume3d.prepare import q_criterion,read_amira_vector,validate_archive
from general_method import directional_reference
from evaluation import windows
from rgmtm.baselines.space_filling import sample_order,linearize,inverse_order
from rgmtm.reference_points import reference_points_from_frames


class Volume3DTests(unittest.TestCase):
    def test_truncated_archive_is_never_accepted_as_complete(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'example.7z';body=b'data';tail=b'header'
            start=struct.pack('<QQI',len(body),len(tail),zlib.crc32(tail))
            header=b'7z\xbc\xaf\x27\x1c'+bytes([0,3])+struct.pack('<I',zlib.crc32(start))+start
            path.write_bytes(header+body+tail)
            self.assertEqual(validate_archive(path),len(header+body+tail))
            path.write_bytes(header+body+tail[:-1])
            with self.assertRaisesRegex(ValueError,'truncated'):validate_archive(path)

    def test_amira_components_and_xyz_order(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'velocity.am'
            header=b'# AmiraMesh BINARY-LITTLE-ENDIAN 2.1\ndefine Lattice 5 4 3\nParameters {\nBoundingBox -2 2 -1 1 0 3\n}\nLattice { float[3] Data } @1\n\n# Data section follows\n@1\n'
            expected=np.arange(3*4*5*3,dtype='<f4').reshape(3,4,5,3)
            path.write_bytes(header+expected.tobytes())
            values,bounds=read_amira_vector(path)
            np.testing.assert_array_equal(values,expected)
            np.testing.assert_array_equal(bounds,[-2,2,-1,1,0,3])

    def test_q_physical_derivatives_rotation_and_strain(self):
        z,y,x=np.meshgrid(np.linspace(0,3,5),np.linspace(-2,2,7),np.linspace(-3,3,9),indexing='ij')
        spacing=(6/8,4/6,3/4)
        np.testing.assert_allclose(q_criterion(np.stack([-2*y,2*x,0*z],axis=-1),spacing),4.,atol=1e-12)
        np.testing.assert_allclose(q_criterion(np.stack([2*x,-2*y,0*z],axis=-1),spacing),-4.,atol=1e-12)

    def test_native_curves_retain_each_volume_sample(self):
        for shape in [(1,1,1),(3,5,7),(4,4,4)]:
            fields=np.arange(2*np.prod(shape)).reshape(2,*shape)
            curves=['Morton']+(['Hilbert'] if importlib.util.find_spec('hilbertcurve') else [])
            for curve in curves:
                line=linearize(fields,curve)
                np.testing.assert_array_equal(line[inverse_order(shape,curve)].T.reshape(fields.shape),fields)

    @unittest.skipUnless(importlib.util.find_spec('hilbertcurve'),'install optional volume3d dependencies')
    def test_hilbert_volume_cube_is_face_adjacent(self):
        order=sample_order((4,4,4),'Hilbert');cells=np.array(np.unravel_index(order,(4,4,4))).T
        np.testing.assert_array_equal(np.abs(np.diff(cells,axis=0)).sum(axis=1),1)

    def test_z_motion_uses_all_eight_box_corners(self):
        ext=[np.array([[1.,1.,3.],[8.,7.,4.]]),np.array([[1.,1.,5.],[8.,7.,6.]])]
        ref=directional_reference({'tracks':[[0,1],[0,1]]},ext,np.array([0.,0.,2.]),np.array([10.,9.,8.]))
        np.testing.assert_allclose(ref['candidates']['direction']['a'],[0,0,1])
        self.assertEqual(ref['origin'],2.);self.assertEqual(ref['extent'],6.)

    def test_boundary_and_temporal_gap_in_volume_scene(self):
        z,y,x=np.indices((4,5,6));field=-((x-2.1)**2+(y-2.2)**2+(z-1.2)**2)
        coords=np.c_[x.ravel(),y.ravel(),z.ravel()]
        scene=ep.scene_from_fields(np.stack([field,field,field]),coords,2.,'split',break_before=[2])
        self.assertEqual(scene['tracks'][0],scene['tracks'][1])
        self.assertTrue(set(scene['tracks'][1]).isdisjoint(scene['tracks'][2]))
        self.assertTrue(scene['boundary'][0][0])
        points=reference_points_from_frames(scene['frames'],scene['ids'],kind='extremum')
        self.assertEqual(points[0].shape,(1,3))

    def test_projection_can_reverse_actual_three_dimensional_motion(self):
        ext=[np.array([[0.,0.,0.],[2.,0.,10.]]),np.array([[0.,0.,0.],[3.,0.,0.]])]
        qs=[e[:,0] for e in ext];sc={'tracks':[[0,1],[0,1]]}
        full=windows(sc,ext,qs,3.,1,.02,20.,qs,.1,truth_mode='3d')
        projected=windows(sc,ext,qs,3.,1,.02,20.,qs,.1,truth_mode='projected',axis_extent=10.)
        self.assertEqual(full['truth'].tolist(),[-1]);self.assertEqual(projected['truth'].tolist(),[1])
        self.assertEqual(full['rev'].tolist(),[True])


if __name__=='__main__':unittest.main()
