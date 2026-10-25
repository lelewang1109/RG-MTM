import unittest
from dataclasses import replace
from itertools import permutations
import numpy as np
from rgmtm.error_budget import Parameters,solve_frame,InfeasibleLayout
from rgmtm.unified import Controls,solve_unified_frame,solve_unified_sequence


class UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.c=np.array([[0.,0.],[10.,0.]])
        self.p=Parameters(canvas=120,width_scale=1,gap=1,extra_budget=1)
        self.v=np.array([[0.,1.],[1.,0.]])
        self.pool=list(permutations(range(2)))

    def solve(self,q,ctrl,**kw):
        return solve_unified_frame(self.c,[6,6],(0,1),q,self.v,1,ctrl,self.p,candidate_orders=self.pool,**kw)

    def test_disabling_reference_removes_hidden_cap_and_gauge_dependence(self):
        ctrl=Controls(reference_weight=0,geometry_weight=1,motion_fraction=0)
        a=self.solve([20,100],ctrl);b=self.solve([45,55],ctrl)
        np.testing.assert_allclose(a['x'],b['x'],atol=1e-5)
        self.assertAlmostEqual(abs(np.diff(a['x'])[0]),10,places=4)
        self.assertAlmostEqual(np.mean(a['x']),60,places=4)
        old=solve_frame(self.c,[6,6],(0,1),p=replace(self.p,reference_weight=0,geometry_weight=1,motion_weight=0),reference=[20,100])
        self.assertAlmostEqual(abs(np.diff(old['x'])[0]),78,places=4)

    def test_motion_fraction_interpolates_the_same_qp(self):
        old=np.array([45.,65.]);oldq=np.array([45.,65.]);q=np.array([48.,68.])
        for eta in [0,.5,1]:
            r=self.solve(q,Controls(reference_weight=0,geometry_weight=0,eccentricity_weight=.1,motion_fraction=eta),
                         previous=old,previous_q=oldq,matched=np.array([True,True]))
            np.testing.assert_allclose(r['x'],old+eta*3,atol=1e-4)

    def test_unidentified_birth_positions_use_compact_objective_preserving_ties(self):
        r=self.solve([20,100],Controls(reference_weight=0,geometry_weight=0,motion_fraction=0))
        np.testing.assert_allclose(r['x'],[56.5,63.5],atol=1e-5)
        self.assertLess(r['normalized_objective'],1e-12)

    def test_fixed_leaf_barriers_and_budget_transition(self):
        c=np.array([[1,0],[9,0],[5,0]],float);v=np.array([[0,1,3],[1,0,3],[3,3,0]],float)
        pool=list(permutations(range(3)));p=Parameters(canvas=10,width_scale=1,gap=.1,rho=0)
        args=(c,[.2]*3,((0,1),2),[1,9,5],v,3)
        with self.assertRaises(InfeasibleLayout):
            solve_unified_frame(*args,Controls(topology_budget=.3,position_budget=0),p,candidate_orders=pool)
        r=solve_unified_frame(*args,Controls(topology_budget=1/3,position_budget=0),p,candidate_orders=pool)
        self.assertEqual(tuple(r['order']),(0,2,1));self.assertAlmostEqual(r['delta'],1)
        self.assertLess(r['position_error'],1e-8)

    def test_fixed_pool_objective_does_not_increase_with_topology_cap(self):
        c=np.array([[1,0],[9,0],[5,0]],float);v=np.array([[0,1,3],[1,0,3],[3,3,0]],float)
        pool=list(permutations(range(3)));p=Parameters(canvas=10,width_scale=1,gap=.1,rho=0)
        vals=[solve_unified_frame(c,[.2]*3,((0,1),2),[1,9,5],v,3,
             Controls(topology_budget=e),p,candidate_orders=pool)['normalized_objective'] for e in [0,1/3,1]]
        self.assertTrue(np.all(np.diff(vals)<=1e-7))

    def test_sequence_matches_ids_and_missing_frames_are_explicit(self):
        c=[self.c,self.c[::-1]];ids=[['a','b'],['b','a']];q=[[45,65],[65,45]]
        rows=solve_unified_sequence(c,[[6,6]]*2,[(0,1)]*2,q,[self.v]*2,ids,[self.pool]*2,1,
                 Controls(reference_weight=0,geometry_weight=0,motion_fraction=0),self.p)
        np.testing.assert_allclose(rows[1]['x'],rows[0]['x'][::-1],atol=1e-5)
        rows=solve_unified_sequence([self.c],[[6,6]],[(0,1)],[[0,0]],[self.v],[['a','b']],[self.pool],1,
                 Controls(position_budget=0),self.p,allow_infeasible=True)
        self.assertEqual(rows,[None])

    def test_invalid_controls_and_unreported_global_claims(self):
        with self.assertRaises(ValueError):self.solve([20,100],Controls(motion_fraction=2))
        with self.assertRaises(ValueError):self.solve([20,100],Controls(position_budget=-1))
        r=solve_unified_frame(self.c,[6,6],(0,1),[20,100],self.v,1,Controls(),self.p,candidate_orders=[(0,1)])
        self.assertFalse(r['exhaustive']);self.assertEqual(r['pool_size'],1)


if __name__=='__main__':unittest.main()
