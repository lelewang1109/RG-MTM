"""RG-MTM on original-resolution Tangaroa, author scalar protocol and TTK join trees.

Default scope: all 201 consecutive frames, persistence 10% of declared [0,2].
Large source/render arrays stay in the ignored raw-data directory. Reports bind
their hashes and retain numerical feature evidence and display-only previews.
"""
from dataclasses import asdict
from itertools import combinations,product
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from experiments.volume3d.prepare import sha256
from experiments.volume3d.prepare_tangaroa_paper import OUT as DATA,save
from experiments.volume3d.paper_trees import Frame,features,TREES,SHAPE,BOUNDS,SAMPLE_MEASURE
from experiments.volume3d.compact_tmtm import CompactTMTM,barrier_matrix
from experiments.volume3d import scalable_layout as sl
from rgmtm.error_budget import Parameters
from rgmtm.reference_guided import render_sequence
import relax_hierarchy as rh
import filling

OUT=ROOT/'results/volume3d/tangaroa-paper-p10-full201'
CAPS=[.02,.2,1.]
RASTER=131072


def dump(path,obj):
    def convert(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        raise TypeError(type(v).__name__)
    temp=Path(str(path)+'.tmp');temp.write_text(json.dumps(obj,default=convert,indent=2,ensure_ascii=False,allow_nan=False)+'\n');temp.replace(path)


def overlap(previous,current):
    na,nb=len(previous.arcs),len(current.arcs)
    codes=previous.owner.astype(np.int64)*nb+current.owner
    counts=np.bincount(codes,minlength=na*nb).reshape(na,nb)
    for v in set([previous.root,current.root]):counts[previous.owner[v],current.owner[v]]-=1
    A=[previous.arc_for_child(v).id for v in previous.leaves];B=[current.arc_for_child(v).id for v in current.leaves]
    return counts[np.ix_(A,B)]


def load_features(indices,out):
    records=[];tracks=[];next_id=0;previous=None;steps=[]
    for index in indices:
        path=TREES/f'frame_{index:03d}.features.json'
        while not path.exists():time.sleep(2)
        feature=json.loads(path.read_text());frame=Frame(index)
        current_tracks=[None]*len(frame.leaves);pairs=[]
        if previous is not None:
            score=overlap(previous,frame);a,b=linear_sum_assignment(-score)
            for i,j in zip(a,b):
                if score[i,j]>0:current_tracks[j]=tracks[-1][i];pairs.append([int(i),int(j),int(score[i,j])])
        for j in range(len(current_tracks)):
            if current_tracks[j] is None:current_tracks[j]=next_id;next_id+=1
        records.append(feature);tracks.append(current_tracks);steps.append(pairs);previous=frame
    result=dict(indices=list(indices),frames=records,tracks=tracks,matches=steps,
        matching='maximum original-voxel leaf-arc intersection, Hungarian, positive overlap only; computed proxy, not physical identity ground truth')
    dump(out/'features.json',result);return records,tracks,steps


def reference(records,tracks,steps):
    ext=[np.array(r['extrema']) for r in records];changes=[]
    for t,pairs in enumerate(steps[1:],1):
        changes.extend(ext[t][j]-ext[t-1][i] for i,j,_ in pairs)
    changes=np.array(changes).reshape(-1,3);S=changes.T@changes;eig,V=np.linalg.eigh(S);total=float(eig.sum())
    a=V[:,-1] if total>1e-20 else np.array([1.,0.,0.])
    signed=float(np.sum(changes@a))
    if signed<0 or (abs(signed)<1e-12 and a[np.argmax(abs(a))]<0):a=-a
    corners=np.array(list(product(*zip(BOUNDS[::2],BOUNDS[1::2]))));projected=corners@a
    return dict(direction=a,origin=float(projected.min()),extent=float(np.ptp(projected)),
        capture=float(a@S@a/total) if total else 0.,eigenvalues=eig,matched_steps=len(changes),
        qs=[e@a for e in ext],domain_diagonal=float(np.linalg.norm(BOUNDS[1::2]-BOUNDS[::2])),
        scope='one offline physical-coordinate direction for the whole requested sequence, all eight domain corners')


def history(previous,previous_tracks,tracks,q,previous_q):
    if previous is None:return None,None,np.zeros(len(q),bool),q.copy()
    lookup={k:i for i,k in enumerate(previous_tracks)};x=np.zeros(len(q));oldq=np.zeros(len(q));mask=np.zeros(len(q),bool)
    preference=q.copy()
    for i,k in enumerate(tracks):
        if k in lookup:
            j=lookup[k];mask[i]=True;x[i]=previous['x'][j];oldq[i]=previous_q[j];preference[i]=x[i]
    return x,oldq,mask,preference


def nroe(u,q,extent):
    ordered=np.asarray(q)[np.argsort(u,kind='stable')]
    return max(0.,float(np.max(np.maximum.accumulate(ordered)[:-1]-ordered[1:]))/2)/extent if len(q)>1 else 0.


def tmtm_decisions(indices,out,focus=100):
    """Author workspace focus=100; propagate both forward and backward."""
    if focus not in indices:focus=indices[0]
    k=indices.index(focus);initial=CompactTMTM(Frame(focus));initial_layout=initial.layout()
    result={focus:dict(decisions={},temporal_overlap_objective=None)}
    for sequence in [indices[k+1:],list(reversed(indices[:k]))]:
        previous=initial;layout=initial_layout
        for index in sequence:
            current=CompactTMTM(Frame(index));decision,next_layout,objective=current.align(previous,layout)
            result[index]=dict(decisions={str(v):bool(d) for v,d in decision.items()},temporal_overlap_objective=objective)
            previous=current;layout=next_layout
    dump(out/'tmtm_orders.json',dict(focus_source_index=focus,frames={str(k):v for k,v in result.items()}))
    return result


def render(frame,row,p,relaxed):
    matrix,sk,error=render_sequence([frame],[list(frame.leaves)],[row],p.canvas,RASTER,canvas_origin=p.canvas_origin)
    values=matrix[:,0];analytic=0.
    if relaxed:values,analytic=filling.optimal_fill(values,list(sk[0].ordering),sk[0].anchors,frame,'join')
    anchors=np.asarray(sk[0].anchors)[[sk[0].ordering.index(v) for v in frame.leaves]]
    return values,anchors,error[0],analytic


def motion(records,tracks,qs,U,ref):
    extent=max(1e-12,max(float(np.max(u)) for u in U)-min(float(np.min(u)) for u in U));out=[]
    ext=[np.array(r['extrema']) for r in records]
    for lag,eps,truth in product([1,2,4],[.01,.02,.05],['3d','projected']):
        pairs=clear=rev=miss=interior_clear=0
        for t in range(len(U)-lag):
            A={v:i for i,v in enumerate(tracks[t])};B={v:i for i,v in enumerate(tracks[t+lag])}
            for a,b in combinations(sorted(A.keys()&B.keys()),2):
                i,j,ii,jj=A[a],A[b],B[a],B[b];pairs+=1
                real=(np.linalg.norm(ext[t+lag][ii]-ext[t+lag][jj])-np.linalg.norm(ext[t][i]-ext[t][j]) if truth=='3d' else
                    abs(qs[t+lag][ii]-qs[t+lag][jj])-abs(qs[t][i]-qs[t][j]))
                threshold=eps*(ref['domain_diagonal'] if truth=='3d' else ref['extent'])
                if abs(real)<=threshold:continue
                clear+=1;interior_clear+=not any([records[t]['boundary'][i],records[t]['boundary'][j],records[t+lag]['boundary'][ii],records[t+lag]['boundary'][jj]])
                mapped=abs(U[t+lag][ii]-U[t+lag][jj])-abs(U[t][i]-U[t][j])
                if abs(mapped)<=eps*extent:miss+=1
                elif np.sign(mapped)!=np.sign(real):rev+=1
        out.append(dict(lag=lag,epsilon=eps,truth=truth,pairs=pairs,clear=clear,interior_clear=int(interior_clear),
            reversal=rev/clear if clear else None,miss=miss/clear if clear else None,error=(rev+miss)/clear if clear else None))
    return out


def run(out=OUT,indices=range(201)):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);indices=list(indices)
    if indices!=list(range(indices[0],indices[-1]+1)):raise ValueError('this run requires consecutive source indices')
    source_files=[Path(__file__),Path(sl.__file__),Path(__file__).with_name('compact_tmtm.py'),Path(__file__).with_name('paper_trees.py'),
        ROOT/'src/rgmtm/reference_guided.py',ROOT/'src/rgmtm/error_budget.py',ROOT/'src/rgmtm/baselines/stmtm.py',ROOT/'analysis/filling.py',ROOT/'analysis/relax_hierarchy.py']
    source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in source_files}
    protocol=dict(requested_indices=indices,requested_frames=len(indices),original_grid_xyz=[300,180,120],
        preprocessing='official velocity magnitude, abs(v)<1e-6 -> 1, clip [0,2], TTK 0.9.9 legacy scalar simplification at absolute 0.2',
        persistence_percent=10.,declared_scalar_range=[0.,2.],spatial_smoothing=False,spatial_resampling=False,tree_kind='join',
        leaf_limit=None,reference='offline principal matched-extremum displacement, fixed over sequence in physical 3-D coordinates',
        source_sha256=source_hashes,relaxation_eligibility_fractions=CAPS,conflict_fraction=.02,
        optional_relaxation_pruning=False,relaxation_note='all eligible merges flattened; optional strongest-first pruning disabled for the large-tree run',
        candidate_qp_order_limit=4,secondary_global_optimum_claimed=False,primary_milp_seconds_limit=2.,
        primary_certificate='continuous Pareto DP where arity <=10; otherwise interval-workload bound or time-limited MILP with both bounds retained',
        motion_lags=[1,2,4],motion_thresholds=[.01,.02,.05],render_raster=RASTER,preview_rows=4096,
        tmtm_nonbinary_extension='m-way saddles use m-2 disclosed virtual separator copies in 1-D output, with original scalar values; source volume unchanged',
        tmtm_nonbinary_child_optimization='original top-down normal/reversed choice; for genuine nonbinary saddles the whole child list is reversed',
        tmtm_focus_source_index=100 if 100 in indices else indices[0],
        main_342_frame_results_modified=False)
    dump(out/'protocol.json',protocol);dump(out/'status.json',dict(status='waiting_for_original_grid_trees',requested_frames=len(indices)))
    records,tracks,steps=load_features(indices,out);ref=reference(records,tracks,steps);dump(out/'reference.json',ref)
    p=Parameters(canvas=ref['extent'],canvas_origin=ref['origin'],width_scale=.5*ref['extent']/(np.prod(SHAPE)*SAMPLE_MEASURE),
        gap=ref['extent']/240,extra_budget=ref['extent']/120,rho=.5)
    dump(out/'parameters.json',asdict(p));names=['TMTM','RG-MTM-P']+[f'RG-MTM-R {cap:g}' for cap in CAPS]
    preview={name:[] for name in names};positions={name:[] for name in names};per_frame=[];certificates=[]
    large=DATA/('maps_'+out.name);large.mkdir(parents=True,exist_ok=True)
    baseline_orders=tmtm_decisions(indices,out)
    previous_rg={};flip=None;started=time.time()
    for t,index in enumerate(indices):
        frame=Frame(index);feature=records[t];q=np.asarray(ref['qs'][t]);w=p.width_scale*np.array(feature['volumes']);tree=feature['hierarchy']
        cert=sl.certificate(tree,w,q,p,time_limit=2.)
        free=sl.free_bounds(w,q,p)
        if not free['exact_to_tolerance']:
            trial=sl.milp_certificate(tuple(range(len(q))),w,q,p,time_limit=2.)
            trial['lower']=max(trial['lower'],free['lower']);trial['upper']=min(trial['upper'],free['upper'])
            free={**trial,'absolute_gap':max(0.,trial['upper']-trial['lower'])}
        Hlo=cert['lower']-free['upper'];Hhi=cert['upper']-free['lower'];theta=.02*p.canvas
        gate='active' if Hlo>theta+1e-9*p.canvas else ('inactive' if Hhi<=theta+1e-9*p.canvas else 'undetermined')
        certificates.append(dict(index=index,hierarchy=cert,free=free,H_lower=Hlo,H_upper=Hhi,gate=gate))
        compact=CompactTMTM(frame)
        saved=baseline_orders[index];decisions={int(v):d for v,d in saved['decisions'].items()};objective=saved['temporal_overlap_objective']
        native=compact.layout(decisions,render=True);native_ranks=np.array([native['positions'][v] for v in frame.leaves])
        raw_u=p.canvas_origin+native_ranks/(compact.length-1)*p.canvas
        if flip is None:flip=bool(np.dot(raw_u-raw_u.mean(),q-q.mean())<0)
        col=native['values'][::-1] if flip else native['values']
        ranks=compact.length-1-native_ranks if flip else native_ranks
        u=p.canvas_origin+ranks/(compact.length-1)*p.canvas
        true=frame.lca_values();top=float(np.max(abs(barrier_matrix(col,ranks)-true)))
        if top>2e-6:raise AssertionError('native TMTM failed measured join-tree barrier check')
        native_path=large/f'TMTM_{index:03d}.npy';np.save(native_path,col)
        sample_ids=native['sample_ids'][::-1] if flip else native['sample_ids']
        sample_path=large/f'TMTM_ids_{index:03d}.npy';np.save(sample_path,sample_ids)
        preview['TMTM'].append(col[np.rint(np.linspace(0,len(col)-1,4096)).astype(int)])
        positions['TMTM'].append(u)
        frame_metrics=[dict(index=index,method='TMTM',NROE=nroe(u,q,p.canvas),NMLE=top/2.,
            anchor_MAE=float(np.mean(abs(u-q)))/p.canvas,virtual_saddle_copies=compact.virtual_count,
            full_array=str(native_path.relative_to(ROOT)),full_array_sha256=sha256(native_path),
            sample_ids_array=str(sample_path.relative_to(ROOT)),sample_ids_sha256=sha256(sample_path),
            virtual_saddles=[int(v) for v,_ in native['virtual_copies']],
            raster=len(col),anchors=ranks.tolist(),temporal_overlap_objective=objective,
            decisions={str(k):bool(v) for k,v in decisions.items()},source_samples_exactly_once=True,
            orientation_flipped_at_frame_zero=flip)]
        source_struct=rh.node_tree(frame,list(frame.leaves))
        for cap,name in [(0.,'RG-MTM-P')]+[(cap,f'RG-MTM-R {cap:g}') for cap in CAPS]:
            struct=source_struct;flattened=[];method_cert=cert
            if cap and gate=='active':
                nodes=rh.merge_nodes(source_struct)
                flattened=[v for v,parent in nodes if abs(float(frame.values[v]-frame.values[parent]))<=cap*2.+1e-12]
                for v in flattened:struct=rh.flatten(struct,v)
                method_tree=rh.to_tuple(struct)
                method_cert=sl.certificate(method_tree,w,q,p,time_limit=2.,candidate_orders=[cert['order']])
            else:method_tree=tree
            prev=previous_rg.get(name)
            previous,previous_q,mask,preference=history(prev,tracks[t-1] if t else [],tracks[t],q,ref['qs'][t-1] if t else None)
            rank={v:i for i,v in enumerate(frame.leaves)}
            tmtm_order=[rank[v] for v in sorted(frame.leaves,key=lambda v:native['positions'][v],reverse=flip)]
            row=sl.solve_candidates(feature['centers'],w,q,method_tree,p,method_cert,previous,previous_q,mask,
                extra_orders=[sl.preferred(method_tree,preference),tmtm_order],maximum_orders=4)
            column,anchors,error,analytic=render(frame,row,p,bool(flattened))
            measured=float(np.max(abs(barrier_matrix(column,anchors)-true)))
            if not flattened and measured>2e-6:raise AssertionError('RG-P/shared unrelaxed map failed measured topology')
            if flattened and abs(measured-analytic)>1e-5:raise AssertionError('optimal filling analytic versus measured cost mismatch')
            path=large/f"{name.replace(' ','_')}_{index:03d}.npy";np.save(path,column)
            preview[name].append(column[np.rint(np.linspace(0,len(column)-1,4096)).astype(int)])
            positions[name].append(anchors*p.canvas/(RASTER-1)+p.canvas_origin)
            frame_metrics.append(dict(index=index,method=name,NROE=nroe(positions[name][-1],q,p.canvas),NMLE=measured/2.,
                anchor_MAE=float(np.mean(abs(positions[name][-1]-q)))/p.canvas,anchor_max=float(np.max(abs(positions[name][-1]-q)))/p.canvas,
                raster=RASTER,anchors=anchors.tolist(),full_array=str(path.relative_to(ROOT)),full_array_sha256=sha256(path),
                flattened_nodes=flattened,primary_certificate=method_cert,layout=row,raster_errors=error,
                measured_topology_absolute=measured,analytic_topology_absolute=analytic,gate=gate))
            previous_rg[name]=row
        per_frame.extend(frame_metrics)
        dump(out/'frame_metrics.json',per_frame);dump(out/'certificates.json',certificates)
        dump(out/'status.json',dict(status='running_layout',completed_frames=t+1,requested_frames=len(indices),last_index=index,elapsed_layout_seconds=time.time()-started))
        print('completed paper RG-MTM frame',index,'leaves',len(q),'gate',gate,'H bracket',Hlo/p.canvas,Hhi/p.canvas,flush=True)
    metrics=[]
    for name in names:
        rows=[r for r in per_frame if r['method']==name]
        metrics.append(dict(method=name,frames=len(rows),NROE_mean=float(np.mean([r['NROE'] for r in rows])),
            NROE_max=max(r['NROE'] for r in rows),NMLE_mean=float(np.mean([r['NMLE'] for r in rows])),NMLE_max=max(r['NMLE'] for r in rows),
            anchor_MAE=float(np.mean([r['anchor_MAE'] for r in rows])),
            exact_topology_frames=sum(r['NMLE']<=1e-6 for r in rows),relaxed_frames=sum(bool(r.get('flattened_nodes')) for r in rows),
            motion=motion(records,tracks,ref['qs'],positions[name],ref)))
    metrics.append(dict(method='Exact projection',frames=len(indices),NROE_mean=0.,motion=motion(records,tracks,ref['qs'],ref['qs'],ref)))
    dump(out/'metrics.json',metrics);dump(out/'positions.json',positions)
    np.savez_compressed(out/'display_maps.npz',**{name:np.column_stack(columns) for name,columns in preview.items()})
    manifest=dict(status='completed_computation',indices=indices,source_sha256=source_hashes,
        original_shape_tzyx=[len(indices),*SHAPE],source_preparation_protocol_sha256=sha256(DATA/'input_protocol.json'),
        tree_protocol_sha256=sha256(TREES/'protocol.json'),
        input_trees=[dict(index=i,manifest_sha256=sha256(TREES/f'frame_{i:03d}.manifest.json')) for i in indices],
        numerical_evidence_sha256={name:sha256(out/name) for name in ['protocol.json','features.json','reference.json','parameters.json','frame_metrics.json','certificates.json','metrics.json','positions.json','display_maps.npz','tmtm_orders.json']})
    dump(out/'manifest.json',manifest);dump(out/'status.json',dict(status='completed_computation_pending_independent_verification',frames=len(indices),elapsed_layout_seconds=time.time()-started))
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--indices',type=int,nargs='+');args=parser.parse_args();run(args.out,range(201) if args.indices is None else args.indices)
