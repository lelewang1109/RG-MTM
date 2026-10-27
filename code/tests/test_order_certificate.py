import sys,unittest
from itertools import permutations
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from rgmtm.framework import merge_costs
from rgmtm.order_certificate import certificate,midpoint_order,budget_order,order_errors


def random_tree(rng,n,ties=False):
    """Random join merge matrix: agglomerate clusters at increasing levels."""
    V=np.zeros((n,n));np.fill_diagonal(V,rng.uniform(0,.5,n));groups=[[i] for i in range(n)];level=.5
    while len(groups)>1:
        level+=0 if ties and rng.random()<.3 else rng.uniform(.01,1)
        a,b=sorted(rng.choice(len(groups),2,replace=False))
        for i in groups[a]:
            for j in groups[b]:V[i,j]=V[j,i]=level
        groups[a]+=groups.pop(b)
    return V


class OrderCertificate(unittest.TestCase):
    def test_closed_form_equals_enumeration_and_midpoint_attains_it(self):
        rng=np.random.default_rng(7)
        for trial in range(150):
            n=int(rng.integers(2,8));V=random_tree(rng,n,ties=trial%2==0);q=rng.uniform(0,10,n)
            P=np.array(list(permutations(range(n))));legal=P[merge_costs(P,V)<=1e-12]
            exact=order_errors(legal,q,10).min();bound=certificate(V,q,10)
            self.assertAlmostEqual(bound,exact,places=12)
            o=midpoint_order(V,q);self.assertAlmostEqual(merge_costs([o],V)[0],0,places=12)
            self.assertAlmostEqual(order_errors([o],q,10)[0],bound,places=12)

    def test_budget_order_respects_budget_and_lower_bound(self):
        rng=np.random.default_rng(11)
        for trial in range(120):
            n=int(rng.integers(2,8));V=random_tree(rng,n);q=rng.uniform(0,10,n);eps=float(rng.uniform(0,1.5))
            r=budget_order(V,q,10,eps)
            P=np.array(list(permutations(range(n))));ok=merge_costs(P,V)<=eps+1e-12
            best=order_errors(P[ok],q,10).min()
            self.assertLessEqual(r['delta'],eps+1e-12)
            self.assertLessEqual(r['lower'],best+1e-12)
            self.assertGreaterEqual(r['nroe'],best-1e-12)

    def test_tie_tolerance_stays_a_valid_lower_bound(self):
        # Chains of tiny gaps (float32 round-off) must not make the bound exceed the truth.
        rng=np.random.default_rng(3);tie=1e-3
        for trial in range(150):
            n=int(rng.integers(3,8));V=random_tree(rng,n)
            off=~np.eye(n,dtype=bool);levels=np.unique(V[off])
            squeeze=dict(zip(levels,levels[0]+np.arange(len(levels))*rng.uniform(.2,1.5)*tie))
            V[off]=[squeeze[v] for v in V[off]];np.fill_diagonal(V,np.minimum(np.diag(V),levels[0]-1))
            q=rng.uniform(0,10,n);P=np.array(list(permutations(range(n))))
            truth=order_errors(P[merge_costs(P,V)<=tie],q,10).min()
            self.assertLessEqual(certificate(V,q,10,0,tie),truth+1e-12)
            r=budget_order(V,q,10,0,tie);self.assertLessEqual(r['delta'],tie+1e-12)

    def test_three_leaf_example(self):
        V=np.array([[0,1,3],[1,0,3],[3,3,0.]]);q=[20,100,60]
        self.assertAlmostEqual(certificate(V,q,120),20/120)  # point-model displacement 20
        r=budget_order(V,q,120,1)
        self.assertEqual(r['order'],[0,2,1]);self.assertAlmostEqual(r['delta'],1);self.assertAlmostEqual(r['nroe'],0)


if __name__=='__main__':unittest.main()
