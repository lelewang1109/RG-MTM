"""Independent saved-array, geometric, motion, constraint and source checks."""
from itertools import combinations
from pathlib import Path
import sys
import numpy as np
from scipy.spatial.distance import pdist, squareform

sys.path.insert(0,str(Path(__file__).parent))
from run import ROOT, OUT, CONFIG, read, dump, sha


def metrics(centers,positions,tracks,temporal):
    sns=[];tw=[];td=0.;matches=0
    for t,(c,u) in enumerate(zip(centers,positions)):
        u=np.asarray(u);d=pdist(np.asarray(c));v=pdist(u[:,None]);n=len(u)
        if n>=2 and np.sum(d*d)>0:
            alpha=np.sum(d*v)/np.sum(v*v) if np.sum(v*v) else 0.
            sns.append(float(np.sum((d-alpha*v)**2)/np.sum(d*d)))
        if n>2:
            d0=squareform(d);d1=squareform(v)
            penalty=0
            for i in range(n):
                ids=[j for j in range(n) if j!=i]
                original=sorted(ids,key=lambda j:(d0[i,j],j))
                projected=min(ids,key=lambda j:(d1[i,j],j))
                penalty+=max(0,original.index(projected))
            tw.append(1-2*penalty/(n*(2*n-4)))
        if t:
            previous=dict(zip(tracks[t-1],positions[t-1]))
            for identity,x in zip(tracks[t],u):
                if identity in previous: td+=abs(x-previous[identity]);matches+=1
    return dict(SNS=np.mean(sns),SNS_frames=len(sns),TW1=np.mean(tw),TW1_frames=len(tw),
        TD=td if temporal else None,section_displacement=td if not temporal and len(positions)>1 else None,matched_steps=matches)


def check_motion(features,tracks,positions,diagonal,occupied):
    span=max(map(np.max,positions))-min(map(np.min,positions)) if occupied else 1.
    clear=errors=0
    for t in range(len(features)-2):
        a={identity:i for i,identity in enumerate(tracks[t])};b={identity:i for i,identity in enumerate(tracks[t+2])}
        x=np.array(features[t]['extrema']);y=np.array(features[t+2]['extrema'])
        for i,j in combinations(a.keys()&b.keys(),2):
            real=np.linalg.norm(y[b[i]]-y[b[j]])-np.linalg.norm(x[a[i]]-x[a[j]])
            if abs(real)<=.02*diagonal: continue
            clear+=1
            mapped=abs(positions[t+2][b[i]]-positions[t+2][b[j]])-abs(positions[t][a[i]]-positions[t][a[j]])
            errors+=abs(mapped)<=.02*span or np.sign(real)!=np.sign(mapped)
    return clear,int(errors)


def main():
    frames_checked=0;geometry_checked=0;objective_checks=[];max_barrier=0.;max_constraint=0.
    for key,(label,folder,dimension,temporal) in CONFIG.items():
        out=OUT/key; protocol=read(out/'protocol.json');source=ROOT/'results'/folder
        assert read(out/'status.json')['status']=='complete'
        for name,digest in {**protocol['source_sha256'],**protocol['code_sha256']}.items():
            assert sha(ROOT/name)==digest,name
        features=read(source/'features.json')['frames'];landmarks=read(out/'landmarks.json');sk=read(out/'skeletons.json')
        rows=read(out/'frame_metrics.json');diagnostics=read(out/'solver_checks.json');summaries=read(out/'metrics.json')
        assert len(rows)==len(features)==len(sk['continuous'])==len(diagnostics)
        for i,(row,feature,continuous,discrete,diagnostic) in enumerate(zip(rows,features,sk['continuous'],sk['discrete'],diagnostics)):
            assert row['index']==i and row['leaf_ids']==feature['leaf_ids']
            array=ROOT/row['full_array'];assert sha(array)==row['full_array_sha256']
            column=np.load(array);anchors=np.array(row['anchors']);source_levels=np.array(feature['source_lca_values'])
            assert np.isfinite(column).all() and len(set(anchors))==len(anchors)
            # Direct interval maxima, independently sampled for every labelled pair.
            for a in range(len(anchors)):
                for b in range(a,len(anchors)):
                    lo,hi=sorted([anchors[a],anchors[b]])
                    error=abs(float(np.max(column[lo:hi+1]))-source_levels[a,b]);max_barrier=max(max_barrier,error)
                    assert error<2e-6,(key,i,a,b,error)
            order=continuous['ordering'];x=np.array(continuous['anchors']);s=np.array(continuous['starts']);e=np.array(continuous['ends'])
            assert set(order)==set(feature['leaf_ids']) and np.all(s<x) and np.all(x<e)
            assert np.all(s[1:]>e[:-1]) and np.all(np.diff(x)>=.01-1e-7)
            K=protocol['settings']['total_leaf_extent_k']
            assert abs(sum(e-s)-K)<1e-7
            for diag in diagnostic.values():
                if isinstance(diag,dict):
                    for name in ['primal_residual','stationarity_residual','complementarity_residual']:
                        assert diag[name]<1e-7;max_constraint=max(max_constraint,diag[name])
            # Independently reconstruct Eq.1 gradient and the saved dual stationarity.
            if len(x)>1:
                n=len(x);centers=np.array(feature['centers'])[[feature['leaf_ids'].index(v) for v in order]]
                distances=squareform(pdist(centers));gradient=np.zeros(n)
                for a,b in combinations(range(n),2):
                    r=2*((x[b]-x[a])-distances[a,b]);gradient[a]-=r;gradient[b]+=r
                D=np.diff(np.eye(n),axis=0);A=D
                if i:
                    previous=sk['continuous'][i-1];prev_leaf=dict(zip(previous['ordering'],previous['anchors']))
                    track_to_leaf=dict(zip(landmarks['tracks'][i-1],features[i-1]['leaf_ids']))
                    current_tracks=dict(zip(feature['leaf_ids'],landmarks['tracks'][i]))
                    matched=0
                    for a,leaf in enumerate(order):
                        prev=track_to_leaf.get(current_tracks[leaf])
                        if prev is not None: gradient[a]+=2*.5*(x[a]-prev_leaf[prev]);matched+=1
                else: matched=0
                if not matched: A=np.vstack([D,np.ones(n)])
                diag=diagnostic['projection'];res=max(abs(gradient/diag['scale']+np.sum(A.T*np.array(diag['dual']),axis=1)))
                assert res<1e-7,(key,i,res)
            # Eq.2 objective is also retained in unscaled native units.
            sizes=np.array(feature['support_counts'])[[feature['leaf_ids'].index(v) for v in order]]
            target=K*sizes/sum(sizes);loss=float(sum(((e-s-target)/target)**2))
            if diagnostic['intervals'].get('solver')=='zero-objective feasible target-width witness':
                assert loss<1e-12
            objective_checks.append(dict(dataset=label,index=i,Eq2_relative_width_loss=loss))
            frames_checked+=1
        for summary in summaries:
            computed=metrics(landmarks['centers'],landmarks['positions'][summary['method']],landmarks['tracks'],temporal)
            for metric,value in computed.items():
                if value is None: assert summary[metric] is None
                else: assert np.isclose(summary[metric],value,rtol=1e-10,atol=1e-10),(key,summary['method'],metric)
            geometry_checked+=1
        if temporal:
            if key=='tangaroa': diagonal=read(source/'reference.json')['domain_diagonal']
            else:
                coords=np.load(ROOT/'data/real/paper1_suite'/key/'coordinates.npz')
                diagonal=np.linalg.norm([np.ptp(coords[v]) for v in ['x','y','z']])
            clear,errors=check_motion(features,landmarks['tracks'],landmarks['positions']['ST-MTM'],diagonal,key=='tangaroa')
            assert (clear,errors)==(summaries[0]['motion']['clear'],summaries[0]['motion']['errors'])
        print(label,'verified',len(rows),'frames',flush=True)
    assert frames_checked==325 and geometry_checked==16
    # All original data and method cells are byte-equivalent numeric values.
    old=read(ROOT/'results/submission20261023/unified_metrics.json')['datasets']
    current=read(OUT/'unified_metrics.json')['datasets']
    assert [d['dimension'] for d in current]==[2]*7+[3]*2
    for d in current:
        previous=next(x for x in old if x['name']==d['name'])
        for method,m in previous['methods'].items():
            if m is not None: assert d['methods'][method]==m,(d['name'],method)
        assert all(m is not None for m in d['methods'].values())
    report=dict(status='passed',new_ST_MTM_frames=frames_checked,geometry_summaries_checked=geometry_checked,
        max_scalar_barrier_error=max_barrier,max_recorded_QP_residual=max_constraint,
        checks=['source and code hashes','all labelled pairs on complete scalar arrays','extrema and intervals',
                'independent SNS/TW/TD reconstruction','independent Eq.1 gradient and dual stationarity',
                'native Eq.2 relative width losses','independent 3D motion events and errors','unchanged historical primary numbers','2-D before 3-D'])
    dump(OUT/'independent_validation.json',report);dump(OUT/'interval_objectives.json',objective_checks)
    print(report)


if __name__=='__main__': main()
