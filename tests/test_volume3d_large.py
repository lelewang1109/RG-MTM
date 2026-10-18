import unittest
from itertools import permutations
import numpy as np
from rgmtm.error_budget import Parameters,leaf_orders
from analysis.certificate_core import order_tau
from experiments.volume3d.scalable_layout import continuous_certificate,milp_certificate,legal,free_bounds,solve_candidates
from experiments.volume3d.compact_tmtm import CompactTMTM,barrier_matrix
from experiments.volume3d.paper_trees import Arc
from rgmtm.baselines import tmtm
from types import SimpleNamespace


class ContinuousTreeCertificateTests(unittest.TestCase):
    def test_large_qp_matches_original_objective_terms(self):
        c=np.array([[.1,.2,.3],[.4,.3,.2],[.8,.1,.6]])
        q=np.array([.2,.5,.7]);w=np.array([.08,.05,.1]);tree=(0,(1,2))
        p=Parameters(canvas=1,width_scale=1,gap=.02,rho=.5,extra_budget=.03)
        cert=continuous_certificate(tree,w,q,p)
        previous=np.array([.18,.51,.72]);oldq=q-.01;mask=np.array([True,False,True])
        row=solve_candidates(c,w,q,tree,p,cert,previous,oldq,mask,maximum_orders=1)
        x,z=np.array(row['x']),np.array(row['z']);o=row['order']
        pairs=[(i,j) for k,i in enumerate(o) for j in o[k+1:]]
        original=(p.geometry_weight*np.mean([(x[j]-x[i]-np.linalg.norm(c[i]-c[j]))**2 for i,j in pairs])+
            p.reference_weight*np.mean((x-q)**2)+p.eccentricity_weight*np.mean((z-x)**2)+
            p.motion_weight*np.mean((x[mask]-(previous+q-oldq)[mask])**2))
        self.assertAlmostEqual(row['objective'],original,11)
        self.assertLess(row['convex_first_order_gap'],1e-6)
        self.assertFalse(row['secondary_global_optimum_claimed'])

    def test_workload_bounds_are_sound_against_all_permutations(self):
        rng=np.random.default_rng(881)
        p=Parameters(canvas=1,gap=.025,rho=.5)
        for _ in range(30):
            w=rng.uniform(.005,.12,6);q=rng.uniform(-.1,1.1,6)
            exact=float(order_tau(list(permutations(range(6))),w,q,0,1,p.gap,p.rho).min())
            got=free_bounds(w,q,p)
            self.assertLessEqual(got['lower'],exact+1e-10)
            self.assertGreaterEqual(got['upper'],exact-1e-10)

    def test_pareto_certificate_against_all_orders(self):
        rng=np.random.default_rng(1849)
        for tree in [0,(0,1),((0,1),(2,(3,4))),((0,1),(2,3),(4,5)),tuple(range(6))]:
            n=len(leaf_orders(tree)[0])
            for _ in range(8):
                w=rng.uniform(.02,.08,n);q=rng.uniform(-.15,1.15,n)
                p=Parameters(canvas=1,width_scale=1,gap=.015,rho=.5)
                exact=float(order_tau(leaf_orders(tree),w,q,0,1,p.gap,p.rho).min())
                got=continuous_certificate(tree,w,q,p)
                self.assertLessEqual(got['lower'],exact+1e-10)
                self.assertLessEqual(exact,got['upper']+1e-10)
                self.assertLess(got['upper']-got['lower'],1e-8)
                self.assertTrue(legal(tree,got['order']))

    def test_milp_free_order_against_every_permutation(self):
        w=np.array([.13,.02,.07,.16,.03]);q=np.array([.24,.26,.3,.29,.85]);p=Parameters(canvas=1,gap=.035,rho=.5)
        exact=float(order_tau(list(permutations(range(5))),w,q,0,1,p.gap,p.rho).min())
        got=milp_certificate(tuple(range(5)),w,q,p,time_limit=10)
        self.assertLessEqual(got['lower'],exact+1e-7)
        self.assertAlmostEqual(got['upper'],exact,7)
        self.assertTrue(got['exact_to_tolerance'])


class FullVolumeTMTMTests(unittest.TestCase):
    def adapter(self,tree):
        for node in tree.nodes.values():node.child_arcs.sort(key=lambda a:tree.arcs[a].child)
        arcs={a:Arc(a,v.parent,v.child,np.array(v.regular_vertices[::-1],int)) for a,v in tree.arcs.items()}
        child_arcs={arc.child:arc for arc in arcs.values()}
        owner=np.full(len(tree.values),-1,int)
        for a,arc in arcs.items():owner[np.r_[arc.child,arc.regular_vertices]]=a
        owner[tree.root]=tree.root_arcs[0]
        return SimpleNamespace(values=tree.values,root=tree.root,arcs=arcs,
            children={k:tuple(tree.arcs[a].child for a in v.child_arcs) for k,v in tree.nodes.items()},
            arc_for_child=lambda v:child_arcs[v],owner=owner)

    def test_binary_array_algorithm_matches_existing_tmtm(self):
        tree=tmtm.build_augmented_merge_tree(np.array([8.,3.,7.,1.,6.,2.,5.,0.]),'join')
        frame=self.adapter(tree);compact=CompactTMTM(frame)
        for decisions in [{},{k:True for k in frame.children}]:
            old=tmtm.linearize_tree(tree,decisions);new=compact.layout(decisions,render=True)
            np.testing.assert_array_equal(new['sample_ids'],old.vertex_at_position)
            for a in compact.objective_arcs:self.assertEqual(tuple(new['intervals'][a]),old.subtree_intervals[a])
        overlap=compact.overlap(compact)
        expected=tmtm.spatial_overlap_matrix(tree,tree)
        for (a,b),value in expected.items():self.assertEqual(overlap[a,b],value)

    def test_multiway_output_discloses_only_equal_saddle_copies(self):
        arcs={0:Arc(0,4,3,np.array([],int)),1:Arc(1,3,0,np.array([],int)),
            2:Arc(2,3,1,np.array([],int)),3:Arc(3,3,2,np.array([],int))}
        bychild={a.child:a for a in arcs.values()}
        frame=SimpleNamespace(values=np.array([0.,1.,2.,8.,10.]),root=4,arcs=arcs,
            children={4:(3,),3:(0,1,2),0:(),1:(),2:()},arc_for_child=lambda v:bychild[v])
        result=CompactTMTM(frame).layout(render=True)
        self.assertEqual(result['virtual_copies'],[(3,4)])
        self.assertEqual(len(result['values']),6)
        anchors=[result['positions'][v] for v in [0,1,2]]
        barriers=barrier_matrix(result['values'],anchors)
        np.testing.assert_array_equal(barriers,np.array([[0.,8.,8.],[8.,1.,8.],[8.,8.,2.]]))


if __name__=='__main__':unittest.main()
