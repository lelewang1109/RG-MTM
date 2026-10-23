"""Measure additional dataset variants with the existing audited layout code."""
from dataclasses import asdict
from pathlib import Path
import argparse, csv, json, time
import numpy as np
from scipy.optimize import linear_sum_assignment
from experiments.paper1_suite.prepare import DATA, RESULTS, ROOT, sha256
from experiments.volume3d.paper_trees import Frame as NativeFrame
from experiments.volume3d.compact_tmtm import CompactTMTM, barrier_matrix
from experiments.volume3d import scalable_layout as sl
from experiments.volume3d.run_paper import dump, nroe, history
from rgmtm.error_budget import Parameters, constraints
from rgmtm.reference_guided import render_sequence
from analysis import relax_hierarchy as rh, filling

RASTER=32768
CAPS=[.02,.2,1.]


class Frame(NativeFrame):
    def __init__(self,index,directory,x,y,z=None):
        super().__init__(index,directory)
        self.kind='join'
        self.x=x; self.y=y; self.z=z
        axes=[x,y]+([] if z is None else [z])
        self.domain_min=np.array([a.min() for a in axes])
        self.domain_max=np.array([a.max() for a in axes])
    def coordinates_for(self,ids):
        planes,i=np.divmod(np.asarray(ids),len(self.x))
        if self.z is None:return np.c_[self.x[i],self.y[planes]]
        k,j=np.divmod(planes,len(self.y))
        return np.c_[self.x[i],self.y[j],self.z[k]]
    def feature(self):
        centers=[];counts=[];boundary=[]
        for leaf in self.leaves:
            ids=self.leaf_feature_vertices(leaf);xy=self.coordinates_for(ids)
            centers.append(xy.mean(axis=0));counts.append(len(ids))
            boundary.append(bool(np.any((xy==self.domain_min)|(xy==self.domain_max))))
        return dict(index=self.timestep,leaf_ids=list(self.leaves),centers=np.array(centers),
                    extrema=self.coordinates_for(self.leaves),support_counts=counts,boundary=boundary,
                    hierarchy=self.hierarchy(),source_lca_values=self.lca_values())


def tracked(frames,records):
    tracks=[];next_id=0
    for t,f in enumerate(frames):
        ids=[None]*len(f.leaves)
        if t:
            prev=frames[t-1];m=len(f.arcs)
            counts=np.bincount(prev.owner.astype(np.int64)*m+f.owner,minlength=len(prev.arcs)*m).reshape(-1,m)
            for v in set([prev.root,f.root]): counts[prev.owner[v],f.owner[v]]-=1
            A=[prev.arc_for_child(v).id for v in prev.leaves];B=[f.arc_for_child(v).id for v in f.leaves]
            score=counts[np.ix_(A,B)];a,b=linear_sum_assignment(-score)
            for i,j in zip(a,b):
                if score[i,j]>0:ids[j]=tracks[-1][i]
        for j in range(len(ids)):
            if ids[j] is None:ids[j]=next_id;next_id+=1
        tracks.append(ids)
    return tracks


def run(name):
    directory=DATA/name;out=RESULTS/name;out.mkdir(parents=True,exist_ok=True)
    protocol=json.loads((directory/'protocol.json').read_text())
    coords=np.load(directory/'coordinates.npz');x=coords['x'];y=coords['y']
    shape=protocol.get('shape_tzyx',protocol.get('shape_tyx'))
    z=coords['z'] if 'z' in coords else None
    frames=[Frame(t,directory/'trees',x,y,z) for t in range(shape[0])]
    records=[f.feature() for f in frames];tracks=tracked(frames,records)
    # Prespecified x direction for all three variants. Avoid fitting direction
    # to outputs or assigning physical time to static molecular z slices.
    extent=float(np.ptp(x));origin=float(x.min())
    n=int(np.prod(shape[1:]))
    max_leaves=max(len(f.leaves) for f in frames)
    gap_divisor=max(240,4*max_leaves)
    p=Parameters(canvas=extent,canvas_origin=origin,width_scale=.5*extent/n,
                 gap=extent/gap_divisor,extra_budget=extent/120,rho=.5)
    if any((len(f.leaves)-1)*p.gap>.5*extent for f in frames):
        raise ValueError('declared fixed gap lacks capacity; no adaptive smoothing is allowed')
    protocol.update(reference='fixed x axis, source physical coordinates',raster=RASTER,
        methods=['TMTM','RG-MTM-P']+[f'RG-MTM-R {c:g}' for c in CAPS],
        tmtm_focus=0,relaxation_gate_fraction=.02,relaxation_pruning=False,
        candidate_order_limit=4,secondary_global_optimum_claimed=False,
        motion_truth='computed feature-overlap matching; geometric proxy, not physical identities',
        original_342_frame_table_modified=False,
        gap_rule='extent/max(240,4*sequence_max_leaf_count), fixed across all frames and methods',
        scalar_normalization='one fixed sequence scalar range; NMLE in this normalized scalar',
        max_input_leaves=max_leaves)
    dump(out/'protocol.json',protocol);dump(out/'parameters.json',asdict(p))
    dump(out/'features.json',dict(frames=records,tracks=tracks))
    source_files=[Path(__file__),Path(sl.__file__),Path(rh.__file__),Path(filling.__file__),
        ROOT/'experiments/paper1_suite/prepare.py',ROOT/'experiments/volume3d/compact_tmtm.py',
        ROOT/'experiments/volume3d/paper_trees.py',ROOT/'src/rgmtm/reference_guided.py',
        ROOT/'src/rgmtm/error_budget.py',ROOT/'src/rgmtm/baselines/stmtm.py']
    dump(out/'source_manifest.json',{str(f.relative_to(ROOT)):sha256(f) for f in source_files})
    maps=directory/'maps';maps.mkdir(exist_ok=True)
    results=[];previews={m:[] for m in protocol['methods']};prev_rg={};fixed=None;fixed_layout=None;flip=None
    started=time.perf_counter()
    for t,(frame,feat) in enumerate(zip(frames,records)):
        q=feat['extrema'][:,0];w=p.width_scale*np.array(feat['support_counts']);tree=feat['hierarchy']
        cert=sl.certificate(tree,w,q,p,time_limit=2.)
        free=sl.free_bounds(w,q,p)
        h_low=max(0.,cert['lower']-free['upper']);h_hi=max(0.,cert['upper']-free['lower'])
        gate='active' if h_low>.02*extent else ('inactive' if h_hi<=.02*extent else 'undetermined')
        compact=CompactTMTM(frame)
        if fixed is None:decision={};layout=compact.layout();objective=None
        else:decision,layout,objective=compact.align(fixed,fixed_layout)
        fixed=compact;fixed_layout=layout
        native=compact.layout(decision,render=True)
        ranks=np.array([native['positions'][v] for v in frame.leaves])
        if flip is None:
            flip=bool(np.dot(ranks-ranks.mean(),q-q.mean())<0)
        column=native['values'][::-1] if flip else native['values']
        ids=native['sample_ids'][::-1] if flip else native['sample_ids']
        ranks=compact.length-1-ranks if flip else ranks
        baseline_x=origin+ranks/(compact.length-1)*extent
        np.save(maps/f'TMTM_{t:03d}.npy',column);np.save(maps/f'TMTM_ids_{t:03d}.npy',ids)
        true=frame.lca_values();top=float(np.max(abs(barrier_matrix(column,ranks)-true)))
        assert top<2e-6
        frame_rows=[dict(index=t,method='TMTM',NROE=nroe(baseline_x,q,extent),NMLE=top,
            anchors=ranks,positions=baseline_x,virtual_saddles=[v for v,_ in native['virtual_copies']],
            temporal_overlap_objective=objective,flip=flip)]
        source_struct=rh.node_tree(frame,list(frame.leaves))
        for cap,name_m in [(0.,'RG-MTM-P')]+[(c,f'RG-MTM-R {c:g}') for c in CAPS]:
            struct=source_struct;flattened=[];method_cert=cert
            if cap and gate=='active':
                flattened=[v for v,parent in rh.merge_nodes(struct) if abs(float(frame.values[v]-frame.values[parent]))<=cap+1e-12]
                for v in flattened:struct=rh.flatten(struct,v)
                method_tree=rh.to_tuple(struct)
                method_cert=sl.certificate(method_tree,w,q,p,time_limit=2.,candidate_orders=[cert['order']])
            else:method_tree=tree
            previous,previous_q,mask,preference=history(prev_rg.get(name_m),tracks[t-1] if t else [],tracks[t],q,
                                                       records[t-1]['extrema'][:,0] if t else None)
            baseline_order=np.argsort(ranks).tolist()
            row=sl.solve_candidates(feat['centers'],w,q,method_tree,p,method_cert,previous,previous_q,mask,
                extra_orders=[sl.preferred(method_tree,preference),baseline_order],maximum_orders=4)
            matrix,skeletons,error=render_sequence([frame],[list(frame.leaves)],[row],extent,RASTER,canvas_origin=origin)
            column=matrix[:,0];sk=skeletons[0];analytic=0.
            if flattened:column,analytic=filling.optimal_fill(column,list(sk.ordering),sk.anchors,frame,'join')
            anchors=np.asarray(sk.anchors)[[sk.ordering.index(v) for v in frame.leaves]]
            top=float(np.max(abs(barrier_matrix(column,anchors)-true)))
            if not flattened:assert top<2e-6
            else:assert abs(top-analytic)<2e-6
            pos=origin+anchors/(RASTER-1)*extent
            np.save(maps/f'{name_m.replace(" ","_")}_{t:03d}.npy',column)
            frame_rows.append(dict(index=t,method=name_m,NROE=nroe(pos,q,extent),NMLE=top,
                anchors=anchors,positions=pos,anchor_MAE=float(np.mean(abs(pos-q)))/extent,
                flattened_nodes=flattened,primary_certificate=method_cert,free_certificate=free,
                H_lower=h_low,H_upper=h_hi,gate=gate,layout=row,raster_errors=error[0],analytic_NMLE=analytic))
            prev_rg[name_m]=row
        for row in frame_rows:
            file=maps/f'{row["method"].replace(" ","_")}_{t:03d}.npy'
            col=np.load(file);row['array']=str(file.relative_to(ROOT));row['array_sha256']=sha256(file)
            previews[row['method']].append(col[np.rint(np.linspace(0,len(col)-1,2048)).astype(int)])
        results.extend(frame_rows)
        dump(out/'status.json',dict(status='running',completed_frames=t+1,requested_frames=len(frames)))
        dump(out/'frame_metrics.json',results)
        print(name,'layout',t,'leaves',len(q),'gate',gate,flush=True)
    summary=[]
    for method in protocol['methods']:
        rows=[r for r in results if r['method']==method]
        summary.append(dict(method=method,frames=len(rows),NROE_mean=float(np.mean([r['NROE'] for r in rows])),
            NMLE_mean=float(np.mean([r['NMLE'] for r in rows])),NMLE_max=max(r['NMLE'] for r in rows),
            exact_topology_frames=sum(r['NMLE']<=1e-6 for r in rows),
            relaxed_frames=sum(bool(r.get('flattened_nodes')) for r in rows)))
    dump(out/'metrics.json',summary)
    with (out/'comparison.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    np.savez_compressed(out/'display_maps.npz',**{k:np.column_stack(v) for k,v in previews.items()})
    dump(out/'status.json',dict(status='computed_pending_verification',frames=len(frames),seconds=time.perf_counter()-started))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset',choices=['nucleon','benzene-density','cylinder2d','square-cylinder3d','benzene-potential3d'])
    run(parser.parse_args().dataset)
