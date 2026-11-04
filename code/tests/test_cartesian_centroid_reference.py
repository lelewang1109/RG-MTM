import unittest
import numpy as np
from rgmtm.cartesian_reference import centroid_axis_reference as fit
class ReferenceTests(unittest.TestCase):
 def test_extremum_jitter_does_not_choose_axis_and_q_remains_extremum(self):
  c=[[[0.,0,0]],[[1.,0,0]]];e=[[[0.,0,0]],[[0.,5,0]]]
  r=fit(c,[[1],[1]],e,[-1,-1,-1],[10,10,10]);self.assertEqual(r['candidates']['direction']['a'],[1,0,0]);np.testing.assert_array_equal(r['qs'][1],[0])
 def test_periodic_seam_is_not_large_motion(self):
  c=[[[0.,0,.1]],[[1.,0,5.9]]]
  r=fit(c,[[1],[1]],c,[-1,-1,0],[10,10,6],{2:6})
  self.assertEqual(r['candidates']['direction']['a'],[1,0,0]);self.assertAlmostEqual(r['candidates']['axis_capture'][0],1/1.04)
 def test_ties_are_deterministic_and_bad_period_rejected(self):
  c=[[[0.,0,0]],[[1.,1,0]]];self.assertEqual(fit(c,[[1],[1]],c,[0,0,0],[3,3,3])['candidates']['direction']['a'],[1,0,0])
  with self.assertRaises(ValueError):fit(c,[[1],[1]],c,[0,0,0],[3,3,3],{2:0})
