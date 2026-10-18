"""Independent all-sample input, tree ownership, map barriers and RG feasibility audit."""
from pathlib import Path
from types import SimpleNamespace
import argparse,hashlib,json,re,sys,zlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from experiments.volume3d.run_paper import OUT,DATA,TREES
from experiments.volume3d.prepare import sha256
import theory
import evaluation


def read(path):return json.loads(Path(path).read_text())


def actual_barriers(values,ranks):
    order=sorted(range(len(ranks)),key=lambda i:ranks[i]);adjacent=[]
    for a,b in zip(order[:-1],order[1:]):adjacent.append(float(np.max(values[ranks[a]:ranks[b]+1])))
    result=np.diag(values[ranks]).astype(float)
    for i,a in enumerate(order):
        for j in range(i+1,len(order)):
            b=order[j];result[a,b]=result[b,a]=max(adjacent[i:j])
    return result


def verify(directory=OUT,raw_inputs=True):
    directory=Path(directory);manifest=read(directory/'manifest.json');protocol=read(directory/'protocol.json')
    for name,digest in manifest['source_sha256'].items():assert sha256(ROOT/name)==digest,name
    for name,digest in manifest['numerical_evidence_sha256'].items():assert sha256(directory/name)==digest,name
    assert not protocol['spatial_smoothing'] and not protocol['spatial_resampling'] and protocol['tree_kind']=='join'
    indices=manifest['indices'];N=6480000;p=SimpleNamespace(**read(directory/'parameters.json'))
    feature_evidence=read(directory/'features.json');feature_records=feature_evidence['frames']
    reference_evidence=read(directory/'reference.json');references=reference_evidence['qs']
    position_table=read(directory/'positions.json')
    frame_rows=read(directory/'frame_metrics.json');certs=read(directory/'certificates.json')
    tree_protocol=read(TREES/'protocol.json')
    assert sha256(TREES/'protocol.json')==manifest['tree_protocol_sha256']
    assert sha256(ROOT/'tmp/volume3d/ttk-0.9.9.tar.gz')==tree_protocol['ttk_source_archive_sha256']
    assert sha256(ROOT/'tmp/volume3d/native-build/rgmtm_ttk_volume')==tree_protocol['native_binary_sha256']
    assert sha256(ROOT/'experiments/volume3d/native/main.cpp')==tree_protocol['native_source_sha256']
    records=[];quantized_checks=[];max_primary_gap=0.;max_input_difference=0.
    for t,index in enumerate(indices):
        prefix=TREES/f'frame_{index:03d}';tree_manifest=read(str(prefix)+'.manifest.json')
        assert sha256(str(prefix)+'.manifest.json')==manifest['input_trees'][t]['manifest_sha256']
        for name,digest in tree_manifest['files'].items():assert sha256(TREES/name)==digest,name
        source_meta=read(DATA/f'scalar_{index:03d}.json');prepared=DATA/f'scalar_{index:03d}.npy'
        assert sha256(prepared)==tree_manifest['input_sha256']==source_meta['scalar_sha256']
        if raw_inputs:
            path=DATA.parent/source_meta['source_filename'];raw=path.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==source_meta['source_sha256']
            assert zlib.crc32(raw)==source_meta['source_crc32'] and len(raw)==source_meta['source_bytes']
            head,payload=raw.split(b'\n@1',1);payload=payload[2:] if payload.startswith(b'\r\n') else payload[1:]
            assert b'BINARY-LITTLE-ENDIAN' in head and b'float[3]' in head
            assert tuple(map(int,re.search(rb'define Lattice (\d+) (\d+) (\d+)',head).groups()))==(300,180,120)
            bbox=re.search(rb'BoundingBox\s+([^\r\n]+)',head).group(1).strip().rstrip(b',').split()
            np.testing.assert_array_equal([float(x) for x in bbox],[-.35,.65,-.3,.3,-.5,-.3])
            assert len(payload)==N*3*4
            vectors=np.frombuffer(payload,dtype='<f4').reshape(N,3)
            a,b,c=[vectors[:,i].astype(np.float64) for i in range(3)]
            speed=np.sqrt(a*a+b*b+c*c).astype(np.float32);speed[speed<1e-6]=1.;speed[speed>2]=2.
            actual=np.load(prepared,mmap_mode='r').ravel();assert np.array_equal(speed,actual)
            del raw,payload,vectors,a,b,c,speed,actual
        values=np.memmap(str(prefix)+'.values.f32',dtype='<f4',mode='r')
        arcs=np.fromfile(str(prefix)+'.arcs.i32',dtype='<i4').reshape(-1,4)
        nodes=np.fromfile(str(prefix)+'.nodes.i32',dtype='<i4');regular=np.fromfile(str(prefix)+'.regular.i32',dtype='<i4')
        counts=np.bincount(regular,minlength=N);np.add.at(counts,nodes,1)
        assert len(values)==N and np.array_equal(counts,np.ones(N,dtype=counts.dtype))
        del counts
        parent={int(d):int(u) for u,d,_,_ in arcs};children={int(v):[] for v in nodes}
        for u,d,start,count in arcs:
            children[int(u)].append(int(d));path=np.r_[u,regular[start:start+count],d].astype(int)
            assert np.all(np.diff(values[path])<=0),('nonmonotone augmented arc',index,int(d))
        roots=set(map(int,nodes))-set(parent);assert len(roots)==1
        leaf_ids=sorted(v for v,c in children.items() if not c);feature=feature_records[t]
        assert leaf_ids==feature['leaf_ids']
        spacing=np.array([1/299,.6/179,.2/119]);origin=np.array([-.35,-.3,-.5])
        expected_points=[];expected_centers=[];expected_counts=[]
        bychild={int(d):(int(start),int(count)) for _,d,start,count in arcs}
        for leaf in leaf_ids:
            start,count=bychild[leaf];ids=np.r_[leaf,regular[start:start+count]]
            point=np.array([leaf%300,(leaf//300)%180,leaf//54000])*spacing+origin
            center=np.array([np.mean(ids%300),np.mean((ids//300)%180),np.mean(ids//54000)])*spacing+origin
            expected_points.append(point);expected_centers.append(center);expected_counts.append(len(ids))
        np.testing.assert_allclose(feature['extrema'],expected_points,rtol=0,atol=1e-13)
        np.testing.assert_allclose(feature['centers'],expected_centers,rtol=0,atol=1e-13)
        np.testing.assert_array_equal(feature['support_counts'],expected_counts)
        np.testing.assert_allclose(feature['volumes'],np.array(expected_counts)*np.prod(spacing),rtol=1e-13,atol=0)
        def lca(a,b):
            ancestors={a}
            while a in parent:a=parent[a];ancestors.add(a)
            while b not in ancestors:b=parent[b]
            return b
        true=np.array([[float(values[lca(a,b)]) for b in leaf_ids] for a in leaf_ids])
        np.testing.assert_array_equal(true,feature['source_lca_values'])
        q=np.array(references[t]);w=p.width_scale*np.array(feature['volumes'])
        subtree={}
        def visit(v):
            ids=[leaf_ids.index(v)] if not children[v] else sum([visit(c) for c in children[v]],[])
            subtree[v]=ids;return ids
        visit(next(iter(roots)))
        cert=certs[t]['hierarchy'];max_primary_gap=max(max_primary_gap,cert['upper']-cert['lower'])
        # A different, rounded-down pixel DP gives an independent continuous
        # lower bound at fixed, uniformly spaced verification frames.
        if t in set(np.rint(np.linspace(0,len(indices)-1,min(11,len(indices)))).astype(int)):
            lower=theory.tau_lower(w,q,feature['hierarchy'],p,65536,tol=.001)
            assert lower<=cert['upper']+1e-8*p.canvas
            quantized_checks.append(dict(index=index,independent_lower=lower,primary_upper=cert['upper'],gap=cert['upper']-lower))
        nrows=0
        for row in [r for r in frame_rows if r['index']==index]:
            path=ROOT/row['full_array'];assert sha256(path)==row['full_array_sha256']
            col=np.load(path,mmap_mode='r');anchors=np.array(row['anchors'],int)
            assert np.isfinite(col).all() and len(col)==row['raster']
            got=actual_barriers(col,anchors);delta=float(np.max(abs(got-true)))/2.
            assert abs(delta-row['NMLE'])<=1e-9
            u=anchors*p.canvas/(len(col)-1)+p.canvas_origin;order=np.argsort(u,kind='stable');qq=q[order]
            np.testing.assert_allclose(u,position_table[row['method']][t],rtol=0,atol=1e-12*p.canvas)
            np.testing.assert_allclose(col[anchors],values[leaf_ids],rtol=0,atol=1e-12)
            nroe=max(0.,float(np.max(np.maximum.accumulate(qq)[:-1]-qq[1:]))/2)/p.canvas if len(q)>1 else 0.
            assert abs(nroe-row['NROE'])<1e-10
            if row['method']=='TMTM':
                sid=ROOT/row['sample_ids_array'];assert sha256(sid)==row['sample_ids_sha256']
                ids=np.load(sid,mmap_mode='r');assert len(ids)==len(col) and ids.min()>=0 and ids.max()<N
                assert np.array_equal(values[ids],col)
                counts=np.bincount(ids,minlength=N);expected=np.ones(N,int)
                for v in row['virtual_saddles']:expected[v]+=1
                np.testing.assert_array_equal(counts,expected)
                assert row['virtual_saddle_copies']==len(row['virtual_saddles'])==len(col)-N
                expected_virtuals=sum(([v]*(len(c)-2) for v,c in children.items() if len(c)>2),[])
                assert sorted(row['virtual_saddles'])==sorted(expected_virtuals)
                assert delta<=1e-6
                del counts,expected,ids
            else:
                layout=row['layout'];x=np.array(layout['x']);z=np.array(layout['z']);width=np.array(layout['w']);order=list(layout['order'])
                assert sorted(order)==list(range(len(q)))
                np.testing.assert_allclose(width,w,rtol=0,atol=1e-13*p.canvas)
                assert np.max(abs(x-q))<=layout['budget']+1e-8*p.canvas
                assert np.max(abs(x-z)-p.rho*w/2)<=1e-8*p.canvas
                np.testing.assert_array_equal(anchors,np.rint((x-p.canvas_origin)*(len(col)-1)/p.canvas).astype(int))
                assert np.min(z-w/2)>=p.canvas_origin-1e-8*p.canvas
                assert np.max(z+w/2)<=p.canvas_origin+p.canvas+1e-8*p.canvas
                assert min(np.diff(z[order])-(w[np.array(order[:-1])]+w[np.array(order[1:])])/2)>=p.gap-1e-8*p.canvas
                rank={v:i for i,v in enumerate(order)};flattened=set(row['flattened_nodes'])
                if flattened:
                    cap=float(row['method'].split()[-1])
                    for v in flattened:
                        par=parent[v]
                        while len(children[par])==1 and par in parent:par=parent[par]
                        assert abs(float(values[v])-float(values[par]))<=cap*2+1e-12
                for v,ids0 in subtree.items():
                    if v in flattened:continue
                    ranks=sorted(rank[i] for i in ids0)
                    assert ranks[-1]-ranks[0]+1==len(ranks),('noncontiguous retained subtree',index,v)
                assert not layout['secondary_global_optimum_claimed']
                if not flattened:assert delta<=1e-6
            nrows+=1
        records.append(dict(index=index,samples=N,leaves=len(leaf_ids),methods=nrows,input_max_difference=0.))
        print('independent paper experiment audit',index,'passed',flush=True)
    motion_checks=[]
    for row in read(directory/'metrics.json'):
        name=row['method'];U=[np.array(v) for v in (references if name=='Exact projection' else position_table[name])]
        extent=max(1e-12,max(float(np.max(u)) for u in U)-min(float(np.min(u)) for u in U))
        for truth in ['3d','projected']:
            actual=evaluation.windows(dict(tracks=feature_evidence['tracks']),[np.array(r['extrema']) for r in feature_records],
                U,extent,2,.02,reference_evidence['domain_diagonal'],references,.02*p.canvas,truth_mode=truth,axis_extent=p.canvas)
            expected=next(m for m in row['motion'] if m['lag']==2 and m['epsilon']==.02 and m['truth']==truth)
            count=int(actual['clear'].sum()) if actual else 0
            assert count==expected['clear']
            if count:assert abs(float((actual['rev']|actual['miss']).sum()/count)-expected['error'])<1e-12
            else:assert expected['error'] is None
            motion_checks.append(dict(method=name,truth=truth,clear=count))
    result=dict(status='passed',frames=len(indices),indices=indices,source_samples_per_frame=N,raw_source_recomputed=raw_inputs,
        all_input_samples_exactly_matched=raw_inputs,input_max_difference=max_input_difference,
        primary_certificate_max_bracket_width=max_primary_gap,independent_quantized_certificate_checks=quantized_checks,
        all_saved_full_arrays_remeasured=True,tmtm_original_sample_ids_and_declared_virtual_copies_checked=True,
        secondary_global_optimum_claimed=False,verification_source_sha256=sha256(__file__),
        default_motion_crosscheck=motion_checks,independent_helper_sha256={name:sha256(ROOT/name) for name in ['analysis/evaluation.py','analysis/theory.py']},
        manifest_sha256=sha256(directory/'manifest.json'),records=records)
    (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASSED',len(indices),'original-resolution frames');return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path,nargs='?',default=OUT)
    parser.add_argument('--skip-raw-inputs',action='store_true');args=parser.parse_args();verify(args.directory,not args.skip_raw_inputs)
