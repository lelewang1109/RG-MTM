"""Contracts for the automatic reference -> unchanged budget-layout adapter."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np
sys.path[:0] = [str(Path(__file__).resolve().parents[1]/'analysis')]
import general_method as gm
from anchormtm import solve_anchored_sequence
from rgmtm.error_budget import Parameters, InfeasibleLayout


class AnchorReferenceTests(unittest.TestCase):
    def test_motion_scatter_and_sign_in_both_dimensions(self):
        for dim in (2, 3):
            d = np.arange(1., dim+1)
            ext = [np.zeros((2, dim)), np.array([d, 2*d])]
            r = gm.auto_reference({'tracks': [[10, 20], [10, 20]],'centers':ext}, ext,
                                  np.full(dim, -10.), np.full(dim, 10.))
            np.testing.assert_allclose(r['candidates']['direction']['a'], d/np.linalg.norm(d) if dim==2 else [0,0,1])
            self.assertAlmostEqual(r['candidates']['direction']['capture'], 1. if dim==2 else 9/14)
            self.assertEqual(r['candidates']['matched_steps'], 2)
            if dim == 2: self.assertIn('angle_deg', r['candidates']['direction'])

    def test_no_matches_and_zero_motion_use_longest_axis(self):
        for dim in (2, 3):
            for ids in ([[0], [1]], [[0], [0]]):
                r = gm.auto_reference({'tracks': ids,'centers':[np.ones((1,dim))]*2}, [np.ones((1,dim))]*2,
                                     np.zeros(dim), np.arange(1.,dim+1))
                np.testing.assert_array_equal(r['candidates']['direction']['a'], np.eye(dim)[-1])
                self.assertTrue(r['candidates']['direction']['fallback'])

    def test_balanced_motion_has_deterministic_sign(self):
        r = gm.auto_reference({'tracks': [[0,1], [0,1]]},
            [np.zeros((2,2)), np.array([[1.,-3.],[-1.,3.]])], np.zeros(2), np.ones(2)*5)
        a = np.array(r['candidates']['direction']['a'])
        self.assertGreater(a[np.argmax(abs(a))], 0)

    def solve(self, shift=0, dim=2, eta=0., direction=None, p=None):
        c = np.array([[12.,22.],[16.,25.]])
        if dim == 3: c = np.column_stack([c, [4.,6.]])
        c += shift
        ext = [c, c + np.eye(dim)[0]]
        V = np.array([[0.,2.],[2.,0.]])
        return solve_anchored_sequence(ext, [[1.,1.]]*2, [(0,1)]*2, ext, [V]*2,
            [['a','b']]*2, np.min(c,axis=0)-2, np.max(c,axis=0)+3, 2.,
            p or Parameters(width_scale=.1,gap=.1,extra_budget=.2), eta=eta,direction=direction)

    def test_fit_once_and_origin_not_subtracted_twice(self):
        for dim in (2,3):
            with patch.object(gm, 'auto_reference', wraps=gm.auto_reference) as fit:
                a = self.solve(dim=dim)
                self.assertEqual(fit.call_count, 1)
            b = self.solve(shift=40, dim=dim)
            for t, (x,y) in enumerate(zip(a['layouts'],b['layouts'])):
                np.testing.assert_allclose(np.array(x['x'])-a['parameters'].canvas_origin,
                    np.array(y['x'])-b['parameters'].canvas_origin,atol=1e-5)
                np.testing.assert_allclose(x['reference'], a['reference']['qs'][t])
                self.assertLessEqual(x['delta'], 1e-9)
                self.assertLessEqual(max(abs(x['x']-x['reference'])),x['order_search']['tau']+.2+1e-6)
            self.assertFalse(a['rendered'])

    def test_manual_direction_and_budgeted_mode_share_adapter(self):
        a = self.solve(eta=.2,direction=[0.,1.])
        np.testing.assert_array_equal(a['reference']['candidates']['direction']['a'], [0.,1.])
        np.testing.assert_array_equal(a['reference']['qs'][0], [22.,25.])
        self.assertTrue(all(r['delta'] <= .2+1e-9 for r in a['layouts']))

    def test_budget_relaxes_order_in_the_same_layout_framework(self):
        c = np.array([[1.,1.],[9.,1.],[5.,1.]])
        V = np.array([[0.,1.,3.],[1.,0.,3.],[3.,3.,0.]])
        args = ([c], [[.2]*3], [((0,1),2)], [c], [V], [['a','b','c']], [0.,0.], [10.,2.], 3.)
        p = Parameters(width_scale=1.,gap=.1,extra_budget=0.)
        exact = solve_anchored_sequence(*args,p,eta=0.,direction=[1.,0.])['layouts'][0]
        relaxed = solve_anchored_sequence(*args,p,eta=1.,direction=[1.,0.])['layouts'][0]
        self.assertAlmostEqual(exact['delta'],0.)
        self.assertLessEqual(relaxed['delta'],1.)
        self.assertLess(relaxed['order_search']['tau'], exact['order_search']['tau'])

    def test_capacity_failure_is_not_rescaled(self):
        with self.assertRaises(InfeasibleLayout):
            self.solve(p=Parameters(width_scale=100.,gap=1.))


if __name__ == '__main__': unittest.main()
