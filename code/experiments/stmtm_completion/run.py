"""Complete the four omitted native ST-MTM comparisons without rewriting old runs.

Run from code/: PYTHONPATH=src:. ../../.venv/bin/python experiments/stmtm_completion/run.py
The same saved augmented trees, feature IDs and overlap tracks are reused.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time

import numpy as np
import osqp
from scipy import sparse
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
from rgmtm.baselines import stmtm as st
from experiments.paper1_suite.run import Frame as GridFrame
from experiments.volume3d.paper_trees import Frame as VolumeFrame, Arc, TREES
from experiments.volume3d.compact_tmtm import barrier_matrix

OUT = ROOT/'results/stmtm_completion20261026'
CONFIG = {
    'nucleon': ('Nucleon', 'paper1_suite/nucleon', 2, False),
    'benzene-potential-reconstructed2d': ('Benzene', 'paper1_suite/benzene-potential-reconstructed2d', 2, False),
    'tangaroa': ('Tangaroa', 'volume3d/tangaroa-paper-p10-full201', 3, True),
    'square-cylinder3d': ('Cylinder', 'paper1_suite/square-cylinder3d', 3, True),
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text())


def dump(path, obj):
    def convert(x):
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.generic): return x.item()
        raise TypeError(type(x))
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, default=convert, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


class Values:
    """Read source samples lazily; negative IDs denote equal-level virtual saddles."""
    def __init__(self, source, virtual): self.source, self.virtual = source, virtual
    def __getitem__(self, index):
        if np.isscalar(index):
            return self.virtual[int(index)] if index < 0 else self.source[index]
        index = np.asarray(index)
        if not np.any(index < 0): return self.source[index]
        return np.array([self[i] for i in index])


class Adapter:
    """Feature-level facade for the existing ST-MTM equations and scalar filler.

    Stable-ID right-chain refinement of multifurcations adds no scalar samples
    and preserves every labelled LCA level, checked against the original tree.
    This extension imposes a binary subhierarchy and is disclosed in the protocol.
    """
    parent = VolumeFrame.parent
    arc_for_child = VolumeFrame.arc_for_child
    lca = VolumeFrame.lca
    nonleaf_path_to_ancestor = VolumeFrame.nonleaf_path_to_ancestor

    def __init__(self, native, feature):
        self.timestep, self.root, self.leaves = native.timestep, native.root, native.leaves
        self.domain_min, self.domain_max = native.domain_min, native.domain_max
        self.children = dict(native.children)
        self._arc_for_child = dict(native._arc_for_child)
        self.centers = dict(zip(self.leaves, np.asarray(feature['centers'])))
        self.counts = dict(zip(self.leaves, feature['support_counts']))
        virtual = {}; next_id = -1
        for node, children in list(self.children.items()):
            if len(children) <= 2: continue
            parent = node
            for j in range(len(children)-2):
                v = next_id; next_id -= 1; virtual[v] = float(native.values[node])
                self.children[parent] = (children[j], v)
                self._arc_for_child[children[j]] = replace(self._arc_for_child[children[j]], parent=parent)
                self._arc_for_child[v] = Arc(v, parent, v, np.empty(0, dtype=np.int64))
                parent = v
            self.children[parent] = children[-2:]
            for child in children[-2:]:
                self._arc_for_child[child] = replace(self._arc_for_child[child], parent=parent)
        self.values = Values(native.values, virtual)
        self.virtual_count = len(virtual)
        actual = np.array([[self.values[self.lca(a,b)] for b in self.leaves] for a in self.leaves])
        np.testing.assert_array_equal(actual, native.lca_values())

    def leaf_centroid(self, leaf): return self.centers[leaf]
    def leaf_size(self, leaf): return self.counts[leaf]


def geometry(centers, positions, tracks, temporal):
    """ST-MTM Sec. 5.2, Euclidean source dimension 2 or 3, common k=1."""
    records = []; sns = []; tw = []; steps = []
    for t, (c, u, identities) in enumerate(zip(centers, positions, tracks)):
        c, u = np.asarray(c), np.asarray(u)
        assert c.ndim == 2 and c.shape[0] == len(u) == len(identities)
        assert len(set(identities)) == len(identities) and np.isfinite(u).all()
        d = squareform(pdist(c)); n = len(u)
        s = st.scale_normalized_stress(d, u) if n >= 2 and np.sum(d*d) > 0 else None
        w = st.trustworthiness(c, u, 1) if n > 2 else None
        if s is not None: sns.append(s)
        if w is not None: tw.append(w)
        delta = []
        if t:
            previous = dict(zip(tracks[t-1], positions[t-1]))
            delta = [abs(float(u[i]-previous[identity])) for i, identity in enumerate(identities) if identity in previous]
            steps.extend(delta)
        records.append(dict(index=t,features=n,SNS=s,TW1=w,matched_steps=len(delta),adjacent_displacement=sum(delta)))
    return dict(SNS=float(np.mean(sns)) if sns else None, SNS_frames=len(sns),
                TW1=float(np.mean(tw)) if tw else None, TW1_frames=len(tw),
                TD=float(sum(steps)) if temporal else None,
                section_displacement=float(sum(steps)) if not temporal and len(positions)>1 else None,
                matched_steps=len(steps)), records


def motion(features, tracks, positions, q, diagonal, canvas, occupied=True):
    clear = reverse = miss = 0
    span = (max(map(np.max,positions))-min(map(np.min,positions))) if occupied else canvas
    for t in range(len(features)-2):
        a, b = dict(zip(tracks[t],range(len(tracks[t])))), dict(zip(tracks[t+2],range(len(tracks[t+2]))))
        p, r = np.asarray(features[t]['extrema']), np.asarray(features[t+2]['extrema'])
        for first, second in combinations(sorted(a.keys() & b.keys()),2):
            i,j,k,l = a[first],a[second],b[first],b[second]
            truth = np.linalg.norm(r[k]-r[l])-np.linalg.norm(p[i]-p[j])
            if abs(truth) <= .02*diagonal: continue
            clear += 1
            display = abs(positions[t+2][k]-positions[t+2][l])-abs(positions[t][i]-positions[t][j])
            if abs(display) <= .02*span: miss += 1
            elif np.sign(display) != np.sign(truth): reverse += 1
    return dict(clear=clear, errors=reverse+miss, reversals=reverse, misses=miss,
                error_fraction=(reverse+miss)/clear if clear else None,
                display_threshold='2% occupied anchor range' if occupied else '2% fixed canvas (retained Cylinder protocol)')


def nroe(u,q,extent):
    order = np.argsort(u,kind='stable'); x = np.asarray(q)[order]
    return max(0.,float(np.max(np.maximum.accumulate(x)-x)))/(2*extent)


def qp(P,linear,A,lower,upper):
    """Solve unchanged convex equations with exact linear constraints."""
    P, A = np.asarray(P), np.asarray(A)
    scale = max(1.,float(np.max(abs(P))))
    solver = osqp.OSQP()
    solver.setup(P=sparse.csc_matrix(np.triu(P/scale)),q=np.asarray(linear)/scale,
        A=sparse.csc_matrix(A),l=np.asarray(lower),u=np.asarray(upper),
        eps_abs=1e-9,eps_rel=1e-9,max_iter=200000,polishing=True,verbose=False)
    result = solver.solve()
    if result.info.status not in ('solved','solved inaccurate','maximum iterations reached'):
        raise RuntimeError(result.info.status)
    x,y = result.x,result.y
    primal = max(0.,float(np.max(np.asarray(lower)-A@x)),float(np.max(A@x-np.asarray(upper))))
    stationarity = float(np.max(abs(P@x/scale+np.asarray(linear)/scale+A.T@y)))
    slack = np.where(y>=0,np.asarray(upper)-A@x,A@x-np.asarray(lower))
    active = abs(y)>1e-12
    complementarity = float(np.max(abs(y[active]*slack[active]))) if np.any(active) else 0.
    assert primal < 1e-7 and stationarity < 1e-7 and complementarity < 1e-7, (primal,stationarity,complementarity)
    return x,dict(primal_residual=primal,stationarity_residual=stationarity,
        complementarity_residual=complementarity,dual=y,scale=scale,status=result.info.status)


def project(frame,order,parameters,temporal):
    n = len(order)
    if n == 1: return st.project_leaf_anchors(frame,order,parameters,temporal),None
    d = squareform(pdist(np.array([frame.leaf_centroid(v) for v in order])))
    D = np.zeros((n-1,n))
    for i in range(n-1): D[i,i:i+2] = [-1,1]
    P = 2*(n*np.eye(n)-np.ones((n,n))); linear = np.zeros(n)
    for i,j in combinations(range(n),2):
        linear[i] += 2*d[i,j]; linear[j] -= 2*d[i,j]
    matched = temporal or {}
    for i,v in enumerate(order):
        if v in matched:
            P[i,i] += 2*parameters.temporal_lambda
            linear[i] -= 2*parameters.temporal_lambda*matched[v]
    A = D; low = np.full(n-1,parameters.min_spacing_delta); high = np.full(n-1,np.inf)
    if not matched:
        A = np.vstack([A,np.ones(n)]); low = np.r_[low,0.]; high = np.r_[high,0.]
    return qp(P,linear,A,low,high)


def intervals(frame,order,anchors,parameters):
    n = len(order); sizes = np.array([frame.leaf_size(v) for v in order],float)**parameters.alpha
    target = parameters.total_leaf_extent_k*sizes/sum(sizes)
    eps = min(max(parameters.min_spacing_delta*.1,1e-9),parameters.total_leaf_extent_k/(8*n),min(target)/4)
    if n>1: eps = min(eps,min(np.diff(anchors))/8)
    # The objective is nonnegative. A feasible exact-target-width allocation
    # therefore certifies the global minimum zero, avoiding badly scaled QPs.
    starts = anchors-target/2
    if n>1 and np.any(starts[1:]-(starts+target)[:-1]<eps):
        D=np.diff(np.eye(n),axis=0)
        feasible=linprog(np.zeros(n),A_ub=-D,b_ub=-target[:-1]-eps,
            bounds=list(zip(anchors-target+eps,anchors-eps)),method='highs',
            options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        starts=feasible.x if feasible.success else None
    if starts is not None:
        ends=starts+target
        loss=float(np.sum(((ends-starts-target)/target)**2))
        assert loss<1e-12 and np.all(starts<anchors) and np.all(ends>anchors)
        assert n==1 or np.all(ends[:-1]<starts[1:])
        return starts,ends,dict(solver='zero-objective feasible target-width witness',
            objective_upper_bound=loss,primal_residual=max(0.,abs(sum(ends-starts)-parameters.total_leaf_extent_k)),
            stationarity_residual=0.,complementarity_residual=0.)
    M = np.c_[-np.eye(n),np.eye(n)]; weight = np.diag(1/target**2)
    P = 2*M.T@weight@M; linear = -2*M.T@weight@target
    A = [*np.eye(2*n)]; low = [*np.full(n,-np.inf),*(anchors+eps)]
    high = [*(anchors-eps),*np.full(n,np.inf)]
    for i in range(n-1):
        row = np.zeros(2*n); row[i+1] = 1; row[n+i] = -1
        A.append(row); low.append(eps); high.append(np.inf)
    A.append(np.r_[-np.ones(n),np.ones(n)]);low.append(parameters.total_leaf_extent_k);high.append(parameters.total_leaf_extent_k)
    x,diagnostic = qp(P,linear,A,low,high)
    assert np.all(x[:n]<anchors) and np.all(x[n:]>anchors)
    assert n==1 or np.all(x[n:-1]<x[1:n])
    return x[:n],x[n:],diagnostic


def run(key):
    label, folder, dimension, temporal = CONFIG[key]
    source = ROOT/'results'/folder; out = OUT/key; out.mkdir(parents=True,exist_ok=True)
    feat = read(source/'features.json'); features, tracks = feat['frames'], feat['tracks']
    params = read(source/'parameters.json'); canvas = params['canvas']
    old = read(source/'frame_metrics.json')
    if key == 'tangaroa':
        native = [VolumeFrame(i) for i in range(len(features))]
        ref = read(source/'reference.json'); qs = ref['qs']; diagonal = ref['domain_diagonal']
        tree_dir = TREES
    else:
        data = ROOT/'data/real/paper1_suite'/key
        coordinates = np.load(data/'coordinates.npz')
        z = coordinates['z'] if 'z' in coordinates else None
        native = [GridFrame(i,data/'trees',coordinates['x'],coordinates['y'],z) for i in range(len(features))]
        qs = [np.asarray(f['extrema'])[:,0] for f in features]
        diagonal = float(np.linalg.norm(native[0].domain_max-native[0].domain_min))
        tree_dir = data/'trees'
    frames = [Adapter(f,record) for f,record in zip(native,features)]
    # Same generic shared-input settings as the existing planar ST-MTM runner.
    # No parameter search. Single slice uses base; Benzene links adjacent sections.
    measures = features[0].get('volumes',features[0]['support_counts'])
    parameters = st.LayoutParameters('uniform',params['width_scale']*sum(measures),
        .95,.5,32768,0,mode='temporal' if len(frames)>1 else 'base',
        min_spacing_delta=.01,optimizer_tolerance=1e-11)
    input_files = [source/n for n in ['features.json','parameters.json','frame_metrics.json','protocol.json']]
    input_files += sorted(tree_dir.glob('frame_*.manifest.json'))
    protocol = dict(dataset=label,frames=len(frames),dimension=dimension,physical_time=temporal,
        solver=f'OSQP {osqp.__version__} for Eq.1; Eq.2 exact feasible target-width witnesses certify zero minimum, otherwise QP; exact linear constraints',
        settings=asdict(parameters),parameter_selection='fixed generic shared-input settings; no tuning',
        K_rule='saved width_scale times first-frame support measure (physical voxel volumes for Tangaroa, sample counts for other inputs)',
        static_semantics='Nucleon single slice; Benzene adjacent sections are spatial, not time',
        binary_refinement='stable original child ID right chain; equal scalar virtual saddles, empty new arcs; unchanged leaf supports and pairwise LCA levels',
        virtual_saddles=[f.virtual_count for f in frames],
        geometry='unweighted source leaf-support centroids; Euclidean distance in native spatial dimension; SNS mean; TW k=1',
        stability='full sequence canvas [0,1]; TD null on static inputs; Benzene section displacement separately named',
        reflection='one global reflection from first frame with nonzero anchor/reference covariance above 1e-12 relative tolerance; no per-frame fitting',
        motion='reuse original extrema and overlap tracks; lag=2; source threshold=2% domain diagonal; retain original occupied-range Tangaroa / fixed-canvas Cylinder display thresholds',
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in input_files},
        code_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(st.__file__)]})
    dump(out/'protocol.json',protocol)
    skeletons = []; diagnostics = []; started = time.perf_counter()
    for t, frame in enumerate(frames):
        if t:
            previous = dict(zip(tracks[t-1],frames[t-1].leaves))
            matches = {leaf:previous[identity] for leaf,identity in zip(frame.leaves,tracks[t]) if identity in previous}
            order = st.choose_temporal_order(frame,skeletons[-1].ordering,matches,.95)
            anchors,projection_check = project(frame,order,parameters,st._temporal_positions(order,matches,skeletons[-1]))
        else:
            order = st.optimal_hierarchical_leaf_order(frame)
            anchors,projection_check = project(frame,order,parameters,None)
            anchors += np.asarray(features[0]['centers'])[:,0].mean()-anchors.mean()
        start,end,interval_check = intervals(frame,order,anchors,parameters)
        diagnostics.append(dict(index=t,projection=projection_check,intervals=interval_check))
        skeletons.append(st.ContinuousSkeleton(tuple(order),anchors,start,end))
        dump(out/'status.json',dict(status='layout',completed=t+1,total=len(frames)))
        print(label,'ST-MTM layout',t+1,'/',len(frames),flush=True)
    discrete,padding = st.discretize_skeletons(frames,skeletons,parameters.layout_length)
    positions = []; rows = []; previews = []
    flip = False; reflection_frame = None
    for t,(frame,sk) in enumerate(zip(frames,discrete)):
        a=sk.anchors[[sk.ordering.index(v) for v in frame.leaves]].astype(float)
        a-=a.mean();q=np.array(qs[t],float);q-=q.mean()
        cov=float(np.sum(a*q));tolerance=1e-12*np.linalg.norm(a)*np.linalg.norm(q)
        if abs(cov)>max(tolerance,1e-15):
            flip=cov<0;reflection_frame=t;break
    for t,(frame,sk) in enumerate(zip(frames,discrete)):
        column = st.fill_frame(frame,sk,parameters.layout_length)
        anchors = sk.anchors[[sk.ordering.index(v) for v in frame.leaves]]
        if flip: column,anchors = column[::-1],len(column)-1-anchors
        u = anchors/(len(column)-1)
        original = np.asarray(features[t]['source_lca_values'])
        measured = float(np.max(abs(barrier_matrix(column,anchors)-original)))
        assert measured < 2e-6, (key,t,measured)
        path = out/'maps'/f'ST-MTM_{t:03d}.npy'; path.parent.mkdir(exist_ok=True); np.save(path,column)
        positions.append(u)
        previews.append(column[np.rint(np.linspace(0,len(column)-1,2048)).astype(int)])
        rows.append(dict(index=t,method='ST-MTM',leaf_ids=list(frame.leaves),anchors=anchors,
            positions_unit=u,NROE=nroe(u,qs[t],canvas),NMLE=measured,
            full_array=str(path.relative_to(ROOT)),full_array_sha256=sha(path)))
    centers = [f['centers'] for f in features]
    summary, frame_geometry = geometry(centers,positions,tracks,temporal)
    summary.update(method='ST-MTM',NROE=100*np.mean([r['NROE'] for r in rows]),
        NMLE_mean=100*np.mean([r['NMLE'] for r in rows]),NMLE_max=100*max(r['NMLE'] for r in rows))
    if temporal:
        summary['motion'] = motion(features,tracks,positions,qs,diagonal,1.,occupied=key!='square-cylinder3d')
        expected = 6755 if key=='tangaroa' else 3196
        assert summary['motion']['clear'] == expected
    results = [summary]; saved_positions = {'ST-MTM':positions}
    for original,method in [('TMTM','TMTM'),('RG-MTM-P','RG-MTM-P'),('RG-MTM-R 0.2','RG-MTM-R')]:
        selected = sorted([r for r in old if r['method']==original],key=lambda r:r['index'])
        assert len(selected)==len(frames)
        u = []
        for r in selected:
            array = ROOT/r.get('array',r.get('full_array'))
            length = np.load(array,mmap_mode='r').size
            u.append(np.asarray(r['anchors'])/(length-1))
        m,fg = geometry(centers,u,tracks,temporal); m['method'] = method
        results.append(m); saved_positions[method]=u
    dump(out/'frame_metrics.json',rows)
    dump(out/'geometry_frames.json',frame_geometry)
    dump(out/'skeletons.json',dict(continuous=[asdict(s) for s in skeletons],discrete=[asdict(s) for s in discrete],padding=padding,flip=flip,reflection_frame=reflection_frame))
    dump(out/'solver_checks.json',diagnostics)
    dump(out/'landmarks.json',dict(centers=centers,tracks=tracks,positions=saved_positions))
    dump(out/'metrics.json',results)
    np.savez_compressed(out/'display_maps.npz',ST_MTM=np.column_stack(previews))
    dump(out/'status.json',dict(status='complete',frames=len(frames),seconds=time.perf_counter()-started))
    print(label,'COMPLETE',summary,flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('datasets',nargs='*',default=list(CONFIG))
    args = parser.parse_args()
    if any(key not in CONFIG for key in args.datasets): parser.error('unknown dataset')
    for key in args.datasets: run(key)
