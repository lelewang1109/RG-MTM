import sys,unittest
from itertools import permutations
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from rgmtm.error_budget import Parameters
from rgmtm.framework import merge_costs,interval_costs
from rgmtm.order_certificate import certificate,chain_certificate,budget_order
from rgmtm.interval_order import interval_scores,width_certificate,width_chain_certificate,width_order
from test_order_certificate import random_tree

P=Parameters(canvas=10.,gap=.1,rho=.5)


class IntervalOrder(unittest.TestCase):
    def test_scores_match_interval_costs(self):
        rng=np.random.default_rng(5)
        for n in range(1,9):
            O=np.array([rng.permutation(n) for _ in range(6)]);w=rng.uniform(0,.8,n);q=rng.uniform(0,10,n)
            np.testing.assert_allclose(interval_scores(O,w,q,P)[0],interval_costs(O,w,q,P),atol=1e-12)

    def test_zero_width_reduces_to_theorem_a(self):
        rng=np.random.default_rng(9);p=Parameters(canvas=10.,gap=0.,rho=.5)
        for trial in range(100):
            n=int(rng.integers(2,8));V=random_tree(rng,n,ties=trial%2==0);q=rng.uniform(0,10,n)
            self.assertAlmostEqual(width_certificate(V,q,np.zeros(n),p),10*certificate(V,q,10),places=12)

    def test_bound_valid_and_order_feasible_against_enumeration(self):
        rng=np.random.default_rng(13)
        for trial in range(160):
            n=int(rng.integers(2,8));V=random_tree(rng,n,ties=trial%3==0);q=rng.uniform(0,10,n)
            w=rng.uniform(0,1.2,n)*(trial%4!=0);eps=float(rng.choice([0,0,.2,.6,1.5]))
            Q=np.array(list(permutations(range(n))));ok=merge_costs(Q,V)<=eps+1e-12
            truth=interval_costs(Q[ok],w,q,P).min()
            lower=width_certificate(V,q,w,P,2*eps)
            self.assertLessEqual(lower,truth+1e-12)
            pt=budget_order(V,q,P.canvas,eps);r=width_order(V,q,w,P,eps,point=pt)
            self.assertLessEqual(r['delta'],eps+1e-12)
            self.assertAlmostEqual(merge_costs([r['order']],V)[0],r['delta'],places=12)
            self.assertAlmostEqual(interval_costs([r['order']],w,q,P)[0],r['tau'],places=12)
            self.assertGreaterEqual(r['tau'],truth-1e-12)
            self.assertLessEqual(r['tau'],interval_costs([pt['order']],w,q,P)[0]+1e-12)

    def test_chain_bound_zero_width_equals_theorem_c(self):
        rng=np.random.default_rng(21);p=Parameters(canvas=10.,gap=0.,rho=.5)
        for trial in range(120):
            n=int(rng.integers(3,8));V=random_tree(rng,n,ties=trial%3==0);q=rng.uniform(0,10,n)
            eps=float(rng.choice([0,.05,.2,.5,1.]));tie=float(rng.choice([0,1e-3]))
            self.assertAlmostEqual(width_chain_certificate(V,q,np.zeros(n),p,eps,tie),10*chain_certificate(V,q,10,eps,tie),places=12)

    def test_chain_bound_valid_against_enumeration(self):
        rng=np.random.default_rng(23)
        for trial in range(250):
            n=int(rng.integers(3,8));V=random_tree(rng,n,ties=trial%3==0);q=rng.uniform(0,10,n)
            w=rng.uniform(0,1.5,n);eps=float(rng.choice([0,.05,.2,.5,1.,2.]))*rng.uniform(.5,1.5)
            Q=np.array(list(permutations(range(n))));ok=merge_costs(Q,V)<=eps+1e-12
            truth=interval_costs(Q[ok],w,q,P).min()
            self.assertLessEqual(width_chain_certificate(V,q,w,P,eps),truth+1e-12)
            r=width_order(V,q,w,P,eps)
            self.assertLessEqual(r['lower'],truth+1e-12);self.assertGreaterEqual(r['tau'],r['lower']-1e-12)

    def test_wide_feature_changes_the_best_order(self):
        # Siblings X={0} (wide) and Y={1,2}: the midpoint order puts X first, but
        # X's width pushes Y away; width-aware search places X last.
        V=np.array([[0,3,3],[3,0,1],[3,1,0.]]);q=[4.,3.,5.];w=[6.,.2,.2]
        p=Parameters(canvas=20.,gap=.1,rho=0.)
        pt=budget_order(V,q,p.canvas,0);r=width_order(V,q,w,p,0,point=pt)
        self.assertLess(r['tau'],r['point_tau']-1e-9)
        self.assertGreaterEqual(r['tau'],width_certificate(V,q,w,p)-1e-12)


if __name__=='__main__':unittest.main()
