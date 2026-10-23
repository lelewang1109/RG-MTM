"""Rebuild source trees and independently remeasure saved 3-D map evidence."""
from pathlib import Path
import json
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from experiments import era5 as ep
from experiments.volume3d.prepare import sha256


def verify(directory):
    directory=Path(directory)
    read=lambda name:json.loads((directory/name).read_text())
    manifest=read('manifest.json');status=read('status.json');features=read('features.json')
    metadata=read('input_protocol.json');metrics=read('metrics.json');render=read('render_manifest.json')
    assert status['status']=='complete',status
    for name,expected in manifest['source_sha256'].items():assert sha256(ROOT/name)==expected,name
    for name,expected in manifest['artifact_sha256'].items():assert sha256(directory/name)==expected,name
    assert sha256(Path(__file__).with_name('report.py'))==render['source_sha256']
    for name,expected in {**render['input_sha256'],**render['files']}.items():assert sha256(directory/name)==expected,name
    input_audit=None
    if (directory/'input_verification.json').exists():
        input_audit=read('input_verification.json');assert input_audit['status']=='passed'
        assert sha256(Path(__file__).with_name('verify_tangaroa_input.py'))==input_audit['audit_source_sha256']
        for name,expected in input_audit['artifact_sha256'].items():assert sha256(directory/name)==expected,name
    with np.load(directory/'processed_fields.npz',allow_pickle=False) as source:
        fields,coords=source['fields'],source['coords']
    assert list(fields.shape)==manifest['shape_tzyx']
    for start in metadata.get('break_before',[]):
        assert set(features['tracks'][start-1]).isdisjoint(features['tracks'][start])
    trees=[ep.b1.build_augmented_merge_tree(field,'split') for field in fields]
    true_matrices=[];signatures=[]
    for tree,ids,ext in zip(trees,features['ids'],features['extrema']):
        parents={a.child:a.parent for a in tree.arcs.values()}
        def lineage(node):
            result=[node]
            while node in parents:node=parents[node];result.append(node)
            return result
        paths={node:lineage(node) for node in ids}
        matrix=np.empty((len(ids),len(ids)))
        for i,a in enumerate(ids):
            np.testing.assert_allclose(coords[a],ext[i],rtol=0,atol=0)
            for j,b in enumerate(ids):
                lca=next(node for node in paths[a] if node in set(paths[b]))
                matrix[i,j]=tree.values[lca]
        true_matrices.append(matrix);signatures.append(ep.signature(tree))
    measured=[]
    for row in metrics:
        name=row['method']
        if name=='Exact projection':continue
        with np.load(directory/(name.replace(' ','_')+'_map.npz'),allow_pickle=False) as source:
            maps=source['map'];flat=source['anchors'];counts=source['anchor_counts']
        assert maps.shape[1]==len(fields) and np.isfinite(maps).all()
        anchors=np.split(flat,np.cumsum(counts)[:-1]);costs=[];exact=[];order_errors=[]
        for t,(col,ranks,true,q) in enumerate(zip(maps.T,anchors,true_matrices,features['references'])):
            matrix=np.empty_like(true)
            for i,a in enumerate(ranks):
                for j,b in enumerate(ranks):
                    lo,hi=sorted((int(a),int(b)));matrix[i,j]=col[lo:hi+1].min()
            costs.append(float(abs(matrix-true).max())/manifest['scalar_range'])
            try:exact.append(ep.signature(col,'split')==signatures[t])
            except ValueError:exact.append(False)
            order=np.argsort(ranks,kind='stable');ordered=np.asarray(q)[order]
            inversions=[max(0.,float(ordered[i]-ordered[j]))/2 for i in range(len(q)) for j in range(i+1,len(q))]
            order_errors.append(max([0.]+inversions)/manifest['parameters']['canvas'])
            if name in ('Hilbert','Morton','TMTM'):
                np.testing.assert_array_equal(np.sort(col),np.sort(fields[t].ravel()))
        np.testing.assert_allclose([np.mean(costs),max(costs)],[row['NMLE_mean'],row['NMLE_max']],rtol=0,atol=1e-12)
        np.testing.assert_allclose(np.mean(order_errors),row['NROE_mean'],rtol=0,atol=1e-12)
        assert sum(exact)==row['topology_exact_frames']
        if name in ('TMTM','ST-MTM','RG-MTM-P'):assert all(exact) and max(costs)<1e-7
        measured.append(dict(method=name,frames=len(fields),NMLE_max=max(costs),exact_frames=sum(exact)))
    record=dict(status='passed',frames=len(fields),methods=measured,verification_source_sha256=sha256(Path(__file__)),
        checks=['exact source/input/output hashes','source-grid tree reconstruction','independent parent-chain LCA barriers',
                'saved-raster topology signatures','independent reference-order inversions','native sample multisets','tracking reset across gaps'])
    if input_audit:record['checks'].append('independent official-speed preprocessing audit source and artifact hashes')
    (directory/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2));return record


if __name__=='__main__':verify(Path(sys.argv[1]))
