"""All-frame audit for positive-polarity reconstructed Benzene potential.

Map checks preserved from verify.py (2026-10-22); source values independently
recomputed in audit_benzene_source.py, without generator imports.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse, json, re
import numpy as np
from experiments.paper1_suite.prepare import DATA, RESULTS, ROOT, sha256
from experiments.volume3d.run_paper import dump
from experiments.paper1_suite.benzene_reconstructed import NAME
from experiments.paper1_suite.audit_benzene_source import verify_potential_source


def read(p):return json.loads(Path(p).read_text())



def verify(name=NAME):
    assert name == NAME
    out=RESULTS/name;directory=DATA/name
    protocol=read(out/'protocol.json');p=SimpleNamespace(**read(out/'parameters.json'))
    shape=protocol.get('shape_tzyx',protocol.get('shape_tyx'));N=int(np.prod(shape[1:]))
    for f,h in read(out/'source_manifest.json').items():assert sha256(ROOT/f)==h,f
    features=read(out/'features.json')['frames'];rows=read(out/'frame_metrics.json')
    assert len(features)==shape[0] and len(rows)==shape[0]*len(protocol['methods'])
    source=np.load(directory/'source_fields.npy',mmap_mode='r')
    assert list(source.shape)==shape and sha256(directory/'source_fields.npy')==protocol['source_fields_sha256']
    coords=np.load(directory/'coordinates.npz')
    input_audit=verify_potential_source(directory,protocol)
    allchecks=[];metrics={m:[] for m in protocol['methods']}
    for t in range(shape[0]):
        prefix=directory/'trees'/f'frame_{t:03d}';tree_manifest=read(str(prefix)+'.manifest.json')
        for file,h in tree_manifest['files'].items():assert sha256(prefix.parent/file)==h,file
        original=np.load(directory/f'input_{t:03d}.npy',mmap_mode='r')
        np.testing.assert_array_equal(original.ravel(),(+source[t]/protocol['scalar_scale']).astype('<f4').ravel())
        assert sha256(directory/f'input_{t:03d}.npy')==tree_manifest['input_sha256']
        values=np.fromfile(str(prefix)+'.values.f32',dtype='<f4')
        nodes=np.fromfile(str(prefix)+'.nodes.i32',dtype='<i4')
        arcs=np.fromfile(str(prefix)+'.arcs.i32',dtype='<i4').reshape(-1,4)
        regular=np.fromfile(str(prefix)+'.regular.i32',dtype='<i4')
        counts=np.bincount(np.r_[nodes,regular],minlength=N)
        assert len(values)==N and np.array_equal(counts,np.ones(N,int))
        parent={int(d):int(u) for u,d,_,_ in arcs}
        roots=set(map(int,nodes))-set(parent);assert len(roots)==1
        leaf=sorted(set(map(int,nodes))-set(int(u) for u,_,_,_ in arcs))
        assert leaf==features[t]['leaf_ids']
        nx=len(coords['x']);ny=len(coords['y']);ids=np.asarray(leaf)
        x=coords['x'][ids%nx];y=coords['y'][(ids//nx)%ny]
        points=np.c_[x,y] if 'z' not in coords else np.c_[x,y,coords['z'][ids//(nx*ny)]]
        np.testing.assert_allclose(points,features[t]['extrema'],atol=0,rtol=0)
        for u,d,start,count in arcs:
            chain=np.r_[u,regular[start:start+count],d].astype(int)
            assert np.all(np.diff(values[chain])<=0)
        def lca(a,b):
            ancestors={a}
            while a in parent:a=parent[a];ancestors.add(a)
            while b not in ancestors:b=parent[b]
            return b
        true=np.array([[values[lca(a,b)] for b in leaf] for a in leaf],float)
        np.testing.assert_array_equal(true,features[t]['source_lca_values'])
        q=np.array(features[t]['extrema'])[:,0]
        for row in [r for r in rows if r['index']==t]:
            assert sha256(ROOT/row['array'])==row['array_sha256']
            column=np.load(ROOT/row['array']);anchors=np.array(row['anchors'],int)
            assert np.isfinite(column).all() and len(set(anchors))==len(anchors)
            np.testing.assert_array_equal(column[anchors],values[leaf])
            # A different implementation from the measurement in the runner:
            # check all explicit inter-anchor slices and direct parent-chain LCAs.
            sort=np.argsort(anchors);actual=np.diag(column[anchors]).astype(float)
            adjacent=[float(column[a:b+1].max()) for a,b in zip(anchors[sort][:-1],anchors[sort][1:])]
            for ia,i in enumerate(sort):
                for ib in range(ia+1,len(sort)):
                    j=sort[ib];actual[i,j]=actual[j,i]=max(adjacent[ia:ib])
            nmle=float(np.max(abs(actual-true)))
            assert abs(nmle-row['NMLE'])<1e-9
            inversions=[max(0.,q[sort[i]]-q[sort[j]]) for i in range(len(sort)) for j in range(i+1,len(sort))]
            nroe=max(inversions,default=0.)/(2*p.canvas)
            assert abs(nroe-row['NROE'])<1e-12
            x=p.canvas_origin+anchors/(len(column)-1)*p.canvas
            np.testing.assert_allclose(x,row['positions'],atol=1e-12*p.canvas,rtol=0)
            if row['method']=='TMTM':
                ids=np.load(directory/'maps'/f'TMTM_ids_{t:03d}.npy')
                expected=np.ones(N,int)
                for v in row['virtual_saddles']:expected[v]+=1
                np.testing.assert_array_equal(np.bincount(ids,minlength=N),expected)
                np.testing.assert_array_equal(column,values[ids])
            else:
                layout=row['layout'];xx=np.array(layout['x']);z=np.array(layout['z']);w=np.array(layout['w']);order=layout['order']
                assert np.max(abs(xx-q))<=layout['budget']+1e-7*p.canvas
                assert np.max(abs(xx-z)-p.rho*w/2)<=1e-7*p.canvas
                assert np.min(z-w/2)>=p.canvas_origin-1e-7*p.canvas
                assert np.max(z+w/2)<=p.canvas_origin+p.canvas+1e-7*p.canvas
                assert all(z[b]-w[b]/2-(z[a]+w[a]/2)>=p.gap-1e-7*p.canvas for a,b in zip(order[:-1],order[1:]))
                if not row['flattened_nodes']:assert nmle<=2e-6
                else:assert abs(nmle-row['analytic_NMLE'])<2e-6
            metrics[row['method']].append((nroe,nmle))
        allchecks.append(dict(index=t,source_samples=N,leaves=len(leaf),maps_checked=len(protocol['methods'])))
    saved=read(out/'metrics.json')
    for row in saved:
        a=np.array(metrics[row['method']])
        np.testing.assert_allclose([a[:,0].mean(),a[:,1].mean(),a[:,1].max()],
                                  [row['NROE_mean'],row['NMLE_mean'],row['NMLE_max']],rtol=0,atol=1e-12)
    report=dict(passed=True,frames=len(allchecks),maps_checked=len(rows),records=allchecks,
        scope='all saved input scalar transforms, tree ownership and monotone arcs, direct parent-chain LCA, full-map barriers, TMTM sample multiplicities, RG hard constraints and independently recomputed summary metrics',
        limitation='native TTK computes input topology; this audit does not independently reimplement native TTK persistence simplification',
        verifier_sha256=sha256(__file__),reconstructed_potential_audit=input_audit)
    dump(out/'verification.json',report)
    status=read(out/'status.json');status.update(status='complete_verified',frames=shape[0]);dump(out/'status.json',status)
    print(name,'verified',shape[0],'frames',len(rows),'maps')


if __name__=='__main__':
    verify()
