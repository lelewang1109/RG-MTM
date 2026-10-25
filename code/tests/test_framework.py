import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from rgmtm.framework import cost_table,select_budget,minimum_topology_budget
from rgmtm.error_budget import Parameters,InfeasibleLayout
class BudgetFramework(unittest.TestCase):
    def setUp(self):
        self.p=Parameters(canvas=10,gap=.1,rho=0,width_scale=1)
        self.V=np.array([[0,1,3],[1,0,3],[3,3,0.]])
        self.t=cost_table([.2]*3,[1,9,5],self.V,self.p)
    def test_budget_boundary_and_independent_three_leaf_value(self):
        a=select_budget(self.t,0);b=select_budget(self.t,1)
        self.assertGreater(a['tau'],0);self.assertAlmostEqual(b['tau'],0)
        self.assertEqual(b['order'],[0,2,1]);self.assertAlmostEqual(b['delta'],1)
        self.assertAlmostEqual(select_budget(self.t,.999)['delta'],0)
    def test_inverse_and_infeasibility_do_not_relax_caps(self):
        self.assertAlmostEqual(minimum_topology_budget(self.t,0),1)
        with self.assertRaises(InfeasibleLayout):select_budget(self.t,0,0)
    def test_nested_frontiers_and_lp_witness(self):
        rows=[select_budget(self.t,e) for e in [0,.5,1,3,np.inf]]
        self.assertTrue(np.all(np.diff([r['tau'] for r in rows])<=1e-9))
        for r in rows:
            self.assertLessEqual(r['actual_position_error'],r['tau']+1e-8)
            self.assertAlmostEqual(r['measured_merge_error'],r['delta'])
    def test_candidate_search_is_labelled_bounded(self):
        t=cost_table([.2]*3,[1,9,5],self.V,self.p,candidate_orders=[(0,1,2),(0,2,1)])
        self.assertFalse(t['exact'])
        self.assertEqual(select_budget(t,1)['optimality'],'candidate-set feasible upper bound')
    def test_fixed_leaf_values_can_raise_the_threshold(self):
        V=np.array([[0,1,3],[1,0,3],[3,3,2.5]])
        t=cost_table([.2]*3,[1,9,5],V,self.p)
        self.assertAlmostEqual(minimum_topology_budget(t,0),1.5)
        with self.assertRaises(InfeasibleLayout):select_budget(t,1,0)
    def test_resource_limit_is_explicit(self):
        with self.assertRaises(RuntimeError):cost_table([.2]*3,[1,9,5],self.V,self.p,max_orders=5)
    def test_single_leaf_and_invalid_budget(self):
        t=cost_table([.2],[1],[[0]],self.p)
        self.assertEqual(select_budget(t,0)['delta'],0)
        with self.assertRaises(ValueError):select_budget(t,-1)
if __name__=='__main__':unittest.main()
