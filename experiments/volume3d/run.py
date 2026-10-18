"""Separate 3-D extension; never writes the six-sequence main-paper records."""
from pathlib import Path
from dataclasses import asdict
from itertools import product
import argparse
import json
import platform
import sys
import time
import traceback

import numpy as np
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from experiments import era5 as ep
from experiments.volume3d.prepare import DATA,sha256
from rgmtm.baselines import space_filling as sfc
from rgmtm.reference_points import reference_points_from_frames
from rgmtm.reference_guided import render_sequence
import general_method as gm
import conflict_strategies as cs
import relax_hierarchy as rh
import theory
import filling
import evaluation as ev
import persistence
from certificate_core import order_tau,free_tau
from result_tables import position_metrics
from rgmtm.error_budget import leaf_orders

PROTOCOL=dict(version=1,scope='separate 3-D supplement; excluded from 342-frame main aggregates',
    max_leaves=6,nominal_raster=4096,maximum_raster=131072,
    smoothing_sigmas_voxels=[0.,.5,1.,1.5,2.,3.,4.],
    smoothing_selection='first sigma for which EVERY frame has <=6 leaves and binary branching; counts only, never layout/motion scores',
    tie_perturbation='fixed C-order ramp of amplitude 1e-10 of unsmoothed scalar range, shared by all methods',
    relaxation_caps=[0.,.02,.2,1.],conflict_threshold_fraction=.02,
    motion_lags=[1,2,4],motion_thresholds=[.01,.02,.05],
    persistence_fractions=[0.,.01,.02,.05,.1,.2],
    persistence_scope='hierarchy-only deletion diagnostic; no TTK scalar-field simplification and no rendered comparison after pruning',
    matching='shared maximum-intersection Hungarian matching, positive overlap; resets between windows',
    reference='one offline principal motion direction in physical 3-D coordinates, eight domain corners',
    native_curves='fixed xyz Skilling Hilbert / xyz bit-interleaved Morton; all processed samples, no refilling',
    evaluation='NROE temporal frame mean, NMLE measured full rendered barriers, full-3D and projected motion truths separately')


def synthetic(conflict=False):
    x=np.linspace(0,120,22);y=np.linspace(0,120,18);z=np.linspace(0,120,16)
    Z,Y,X=np.meshgrid(z,y,x,indexing='ij');points=np.stack([X,Y,Z],axis=-1)
    a=np.array([24.,25.,28.]);b=np.array([94.,90.,82.]);d=b-a
    along=np.clip(np.einsum('...i,i->...',points-a,d)/(d@d),0,1)
    ridge=.5*np.exp(-np.sum((points-a-along[...,None]*d)**2,axis=-1)/(2*10**2))
    def blob(center,amplitude):return amplitude*np.exp(-np.sum((points-center)**2,axis=-1)/(2*8**2))
    fields=[];truth=[]
    for f in np.linspace(0,1,24):
        c=(np.array([10.,25.,90.])+f*np.array([100.,0.,0.]) if conflict else
           np.array([112.,62.,22.])+f*np.array([-48.,-25.,57.]))
        truth.append(c)
        fields.append(blob(a,1.)+blob(b,.95)+ridge+blob(c,1.08))
    measure=float((x[1]-x[0])*(y[1]-y[0])*(z[1]-z[0]))
    return np.array(fields),points.reshape(-1,3),dict(dataset='synthetic-3D-interleaved' if conflict else 'synthetic-3D-motion',sample_measure=measure,
        break_before=[],indices=list(range(24)),window_labels=['controlled'],
        moving_blob_centers=truth,source='analytic 3-D Gaussian blobs with a ridge; motion along x to construct interleaving' if conflict else 'analytic 3-D Gaussian blobs with a ridge; every motion coordinate varies',
        shape_tzyx=[24,len(z),len(y),len(x)],exact_paper_input=False)


def dump(path,obj):
    def encode(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        if isinstance(v,Path):return str(v)
        raise TypeError(type(v).__name__)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,default=encode,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def select_fields(raw,out):
    ramp=np.linspace(0,1,raw[0].size).reshape(raw.shape[1:])*float(np.ptp(raw))*1e-10
    audit=[]
    for sigma in PROTOCOL['smoothing_sigmas_voxels']:
        fields=np.array([gaussian_filter(f,sigma,mode='reflect') if sigma else f.copy() for f in raw])+ramp
        counts=[];nonbinary=[]
        for t,field in enumerate(fields):
            tree=ep.b1.build_augmented_merge_tree(field,'split')
            counts.append(sum(not n.child_arcs for n in tree.nodes.values()))
            if any(len(n.child_arcs)>2 for n in tree.nodes.values()):nonbinary.append(t)
        row=dict(sigma_voxels=sigma,leaves=counts,leaves_max=max(counts),nonbinary_frames=nonbinary,
            rmse=float(np.sqrt(np.mean((fields-raw)**2))),max_change=float(np.max(abs(fields-raw))),
            scalar_range=float(np.ptp(fields)))
        audit.append(row);dump(out/'preprocessing_audit.json',audit)
        print(f'sigma {sigma}: max leaves {max(counts)}, nonbinary {len(nonbinary)}',flush=True)
        if max(counts)<=PROTOCOL['max_leaves'] and not nonbinary:return fields,audit
    raise RuntimeError('No declared smoothing candidate meets the exact-layout capacity; see preprocessing_audit.json')


def render_reference(sc,rows,p,relaxed):
    length=PROTOCOL['nominal_raster'];attempts=[]
    while True:
        try:
            maps,sk,errors=render_sequence(sc['frames'],sc['ids'],rows,p.canvas,length,canvas_origin=p.canvas_origin)
            analytic=[]
            if relaxed:
                for t,(frame,skeleton) in enumerate(zip(sc['frames'],sk)):
                    maps[:,t],cost=filling.optimal_fill(maps[:,t],list(skeleton.ordering),skeleton.anchors,frame,'split')
                    analytic.append(cost)
            else:analytic=[0.]*len(rows)
            bad=[]
            if not relaxed:
                bad=[t for t,tr in enumerate(sc['trees']) if ep.signature(maps[:,t],'split')!=ep.signature(tr)]
            attempts.append(dict(length=length,topology_failed=bad))
            if bad:raise ValueError('topology capacity; increase resolution')
            anchors=[np.asarray(s.anchors)[[s.ordering.index(k) for k in ids]] for s,ids in zip(sk,sc['ids'])]
            positions=[a*p.canvas/(length-1)+p.canvas_origin for a in anchors]
            return dict(maps=maps,anchors=anchors,u=positions,rows=rows,analytic_cost=analytic,
                        raster_attempts=attempts,raster_errors=errors)
        except ValueError as e:
            if 'increase resolution' not in str(e) or length>=PROTOCOL['maximum_raster']:raise
            attempts.append(dict(length=length,error=str(e)));length*=2


def baseline(sc,method,p):
    params=ep.b2.LayoutParameters('uniform',float(p.width_scale*sc['areas'][0].sum()),.95,.5,
                                PROTOCOL['nominal_raster'],0,min_spacing_delta=.01,optimizer_tolerance=1e-11)
    run=ep.run_method(sc,method,p,canvas=p.canvas,length=PROTOCOL['nominal_raster'],stmtm_parameters=params)
    size=run['maps'].shape[0];gauge=run['gauge'];scale,shift=gauge['scale'],gauge['shift']
    if method=='TMTM':
        anchors=[np.rint((r['pixel_x']-shift)/scale*(size-1)/p.canvas).astype(int) for r in run['rows']]
    else:
        anchors=[np.array(d['anchors'])[[d['ordering'].index(k) for k in ids]] for d,ids in zip(run['records']['discrete'],sc['ids'])]
    if scale<0:anchors=[size-1-a for a in anchors]
    return dict(maps=run['maps'],anchors=anchors,u=[r['pixel_x'] for r in run['rows']],
                checks=run['checks'],seconds=run['compute_seconds'])


def measured_cost(sc,result,scalar_range):
    errors=[]
    for frame,ids,col,ranks in zip(sc['frames'],sc['ids'],result['maps'].T,result['anchors']):
        actual=sfc.merge_levels_on_line(col,ranks,'split')
        true=np.array([[frame.values[i] if i==j else frame.values[frame.lca(i,j)] for j in ids] for i in ids])
        errors.append(float(np.max(abs(actual-true))))
    return dict(mean=float(np.mean(errors))/scalar_range,max=max(errors)/scalar_range,per_frame=(np.array(errors)/scalar_range).tolist())


def motion(sc,ext,ref,U,lo,hi):
    extent=max(float(max(u.max() for u in U)-min(u.min() for u in U)),1e-12)
    result=[]
    for lag,eps,truth in product(PROTOCOL['motion_lags'],PROTOCOL['motion_thresholds'],['3d','projected']):
        W=ev.windows(sc,ext,U,extent,lag,eps,float(np.linalg.norm(hi-lo)),ref['qs'],.02*ref['extent'],
                     truth_mode=truth,axis_extent=ref['extent'])
        clear=int(W['clear'].sum()) if W else 0
        result.append(dict(lag=lag,epsilon=eps,truth=truth,pairs=len(W['clear']) if W else 0,clear=clear,
            reversal=float(W['rev'].sum()/clear) if clear else None,
            miss=float(W['miss'].sum()/clear) if clear else None,
            error=float((W['rev']|W['miss']).sum()/clear) if clear else None))
    return result


def run(dataset,out,input_path=None,include_stmtm=False):
    out.mkdir(parents=True,exist_ok=True)
    dump(out/'protocol.json',{**PROTOCOL,'include_stmtm_extension':include_stmtm,
        'baseline_scope':'TMTM primary published 3-D baseline; ST-MTM optional project extension, not original 3-D validation'})
    started=time.perf_counter()
    if dataset.startswith('synthetic'):raw,coords,metadata=synthetic(conflict=dataset=='synthetic-conflict')
    else:
        if dataset in ('tangaroa','ctc') and input_path is None:
            raise ValueError('--input is required for '+dataset)
        with np.load(input_path or DATA/'prepared_q_36.npz',allow_pickle=False) as source:
            raw=source['fields'];coords=source['coords'];metadata=json.loads(str(source['metadata']))
        metadata['prepared_input_sha256']=sha256(input_path or DATA/'prepared_q_36.npz')
        if raw.ndim!=4 or coords.shape!=(raw[0].size,3):raise ValueError('expected TZYX fields and XYZ coordinates')
    dump(out/'input_protocol.json',metadata)
    fields,audit=select_fields(raw,out)
    t0=time.perf_counter()
    sc=ep.scene_from_fields(fields,coords,metadata['sample_measure'],'split',max_leaves=PROTOCOL['max_leaves'],
                            break_before=metadata.get('break_before',[]))
    extraction_seconds=time.perf_counter()-t0
    # Baselines and our temporal objectives reset at identical boundaries. All
    # tracking IDs already reset; TMTM also needs independent optimization calls.
    breaks=[0]+list(metadata.get('break_before',[]))+[len(fields)]
    lo,hi=coords.min(0),coords.max(0)
    ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum')
    ref=gm.directional_reference(sc,ext,lo,hi)
    from pointcert import tau_pt
    P0,P1=gm.motion_pairs(sc,ext);corners=np.array(list(product(*zip(lo,hi))))
    axes=[]
    for label,direction in [('auto',np.array(ref['candidates']['direction']['a']))]+list(zip(['x','y','z'],np.eye(3))):
        extent=float(np.ptp(corners@direction));bounds=[]
        for e,h in zip(ext,sc['hier']):bounds.append(float(tau_pt(leaf_orders(h),e@direction).min())/extent)
        axes.append(dict(axis=label,direction=direction,capture=gm.capture_direction(direction,P0,P1) if len(P0) else 0.,
            width_free_bound_mean=float(np.mean(bounds)),width_free_bound_max=max(bounds),
            scope='direction sensitivity of projected-motion capture and width-free hierarchy certificate; no additional layout run'))
    dump(out/'reference_axes.json',axes)
    domain_measure=fields[0].size*metadata['sample_measure']
    p=gm.universal_parameters(ref['origin'],ref['extent'],domain_measure)
    scalar_range=float(np.ptp(fields));theta=.02*p.canvas
    H=[];certificates=[]
    for t,(q,w,h) in enumerate(zip(ref['qs'],sc['areas'],sc['hier'])):
        widths=p.width_scale*w;tf,exact=free_tau(widths,q,p)
        th=float(order_tau(leaf_orders(h),widths,q,p.canvas_origin,p.canvas,p.gap,p.rho).min())
        H.append(th-tf);certificates.append(dict(t=t,leaves=len(q),tau_hier=th,tau_free=tf,exact=exact,H=th-tf))
    dump(out/'certificates.json',certificates)
    methods={};durations={}
    for name in ['TMTM']+(['ST-MTM'] if include_stmtm else []):
        print('layout',name,flush=True);t0=time.perf_counter();parts=[]
        for start,end in zip(breaks[:-1],breaks[1:]):
            sub={key:(value[start:end] if key in ('fields','frames','trees','ids','centers','areas','hier','boundary','matches','tracks') else value)
                 for key,value in sc.items()}
            sub['matches']=[{}]+sub['matches'][1:]
            parts.append(baseline(sub,name,p))
        # The fixed requested length usually suffices. Keep one shared raster
        # per baseline; reject inconsistent refinement across disconnected runs.
        if len({v['maps'].shape[0] for v in parts})!=1:raise RuntimeError('baseline windows need a shared larger nominal raster')
        methods[name]=dict(maps=np.column_stack([v['maps'] for v in parts]),anchors=sum([v['anchors'] for v in parts],[]),u=sum([v['u'] for v in parts],[]),
                           checks=sum([v['checks'] for v in parts],[]))
        durations[name]=time.perf_counter()-t0
    for curve in ['Hilbert','Morton']:
        t0=time.perf_counter();matrix=sfc.linearize(fields,curve);inverse=sfc.inverse_order(fields.shape[1:],curve)
        anchors=[inverse[ids] for ids in sc['ids']]
        methods[curve]=dict(maps=matrix,anchors=anchors,u=[a*p.canvas/(len(inverse)-1) for a in anchors])
        durations[curve]=time.perf_counter()-t0
    rowsP=None
    for cap in PROTOCOL['relaxation_caps']:
        name='RG-MTM-P' if cap==0 else f'RG-MTM-R {cap:g}'
        print('layout',name,flush=True);t0=time.perf_counter();structs=[];logs=[]
        for t,(frame,ids,q,w) in enumerate(zip(sc['frames'],sc['ids'],ref['qs'],sc['areas'])):
            base=rh.node_tree(frame,ids)
            if cap>0 and H[t]>theta:
                st,steps,td=rh.relax_frame_threshold(frame,ids,p.width_scale*w,q,p,theta,certificates[t]['tau_free'],cap*scalar_range)
            else:st,steps=base,[]
            structs.append(st);logs.append(dict(t=t,steps=steps,legal_orders=rh.n_legal_orders(rh.to_tuple(st))))
        rows=rh.solve_sequence_structs(sc,ref['qs'],structs,p)
        rh.validate_relaxed(sc,rows,structs,p)
        result=render_reference(sc,rows,p,cap>0);result['relaxation']=logs
        methods[name]=result;durations[name]=time.perf_counter()-t0
        if not cap:rowsP=rows
    # Exact projection is a motion floor/control, not a filled scalar map.
    methods['Exact projection']=dict(u=ref['qs'])
    # Sign of an unoriented baseline is fixed by frame-zero agreement with q,
    # shared across all windows, never chosen from aggregate performance.
    for name,result in methods.items():
        if name.startswith('RG-') or name=='Exact projection':continue
        q=ref['qs'][0];u=result['u'][0]
        flip=np.dot(q-q.mean(),u-u.mean())<0
        if flip:
            result['maps']=result['maps'][::-1]
            result['anchors']=[len(result['maps'])-1-a for a in result['anchors']]
            result['u']=[-u for u in result['u']]
        result['orientation_flipped_at_first_frame']=bool(flip)
    pos=position_metrics({k:v['u'] for k,v in methods.items()},ref['qs'],sc['hier'],ref['extent'])
    metrics=[];frame_metrics=[]
    for name,result in methods.items():
        row=dict(method=name,NROE_mean=pos['methods'][name]['mean'],NROE_max=pos['methods'][name]['max'],
                 seconds=durations.get(name),anchor_MAE=None,anchor_max=None,NMLE_mean=None,NMLE_max=None,
                 topology_exact_frames=None)
        if 'maps' in result:
            cost=measured_cost(sc,result,scalar_range);row.update(NMLE_mean=cost['mean'],NMLE_max=cost['max'])
            exact=[]
            for t,tr in enumerate(sc['trees']):
                try:exact.append(ep.signature(result['maps'][:,t],'split')==ep.signature(tr))
                except ValueError:exact.append(False)
            row['topology_exact_frames']=sum(exact)
            if name in ('TMTM','ST-MTM','RG-MTM-P') and (not all(exact) or cost['max']>1e-7):
                raise AssertionError(f'{name}: expected exact scalar topology, measured {cost}')
            if name.startswith('RG-'):
                deviation=np.concatenate([abs(u-q) for u,q in zip(result['u'],ref['qs'])])/p.canvas
                row.update(anchor_MAE=float(deviation.mean()),anchor_max=float(deviation.max()))
                difference=max(abs(np.array(cost['per_frame'])*scalar_range-np.array(result['analytic_cost'])))
                row['filling_formula_error']=float(difference/scalar_range)
                if difference>max(1.,scalar_range)*1e-6:raise AssertionError('filled merge cost disagrees with analytic optimum')
                dump(out/(name.replace(' ','_')+'_layouts.json'),dict(rows=result['rows'],relaxation=result['relaxation'],
                     raster_attempts=result['raster_attempts'],raster_errors=result['raster_errors']))
            np.savez_compressed(out/(name.replace(' ','_')+'_map.npz'),map=result['maps'],
                                anchors=np.concatenate(result['anchors']),anchor_counts=np.array([len(a) for a in result['anchors']]))
            frame_metrics.extend(dict(method=name,t=t,NROE=nr,NMLE=nm,leaves=len(sc['ids'][t]),topology_exact=bool(exact[t]))
                                 for t,(nr,nm) in enumerate(zip(pos['methods'][name]['per_frame'],cost['per_frame'])))
        row['motion']=motion(sc,ext,ref,result['u'],lo,hi)
        metrics.append(row);dump(out/'metrics.json',metrics)
    # Separate persistence deletion audit: it does not generate simplified fields.
    pruned=[]
    for fraction in PROTOCOL['persistence_fractions']:
        counts=[];obstruction=[]
        for frame,ids,q in zip(sc['frames'],sc['ids'],ref['qs']):
            tree,_=persistence.pruned(frame,ids,fraction*scalar_range,-1.)
            retained=persistence.leaves(tree);rank={k:i for i,k in enumerate(retained)}
            compact=persistence.relabel(tree,rank)
            from pointcert import tau_pt
            obstruction.append(float(tau_pt(leaf_orders(compact),np.asarray(q)[retained]).min())/p.canvas)
            counts.append(len(retained))
        pruned.append(dict(persistence_fraction=fraction,retained_instances=sum(counts),mean_leaves=float(np.mean(counts)),
            removed_share=1-sum(counts)/sum(map(len,sc['ids'])),width_free_bound_mean=float(np.mean(obstruction)),
            scope=PROTOCOL['persistence_scope']))
    dump(out/'persistence_diagnostic.json',pruned);dump(out/'frame_metrics.json',frame_metrics)
    dump(out/'features.json',dict(ids=sc['ids'],tracks=sc['tracks'],boundary=sc['boundary'],tracking=sc['tracking'],
        extrema=ext,centers=sc['centers'],volumes=sc['areas'],references=ref['qs']))
    np.savez_compressed(out/'processed_fields.npz',fields=fields,raw=raw,coords=coords)
    source_files=[Path(__file__),Path(__file__).with_name('prepare.py'),ROOT/'experiments/era5.py',ROOT/'analysis/general_method.py',
        ROOT/'analysis/evaluation.py',ROOT/'analysis/relax_hierarchy.py',ROOT/'analysis/conflict_strategies.py',
        ROOT/'analysis/filling.py',ROOT/'analysis/theory.py',ROOT/'analysis/certificate_core.py',ROOT/'analysis/result_tables.py',
        ROOT/'analysis/persistence.py',ROOT/'analysis/pointcert.py',ROOT/'src/rgmtm/reference_points.py',
        ROOT/'src/rgmtm/baselines/space_filling.py',ROOT/'src/rgmtm/baselines/tmtm.py',ROOT/'src/rgmtm/baselines/stmtm.py',
        ROOT/'src/rgmtm/reference_guided.py',ROOT/'src/rgmtm/error_budget.py']
    if metadata.get('preparation_source'):
        preparer=ROOT/metadata['preparation_source']
        if sha256(preparer)!=metadata['preparation_sha256']:raise ValueError('prepared input source hash mismatch')
        source_files.append(preparer)
    elif dataset=='tangaroa':source_files.append(Path(__file__).with_name('prepare_tangaroa.py'))
    manifest=dict(dataset=dataset,frames=len(fields),shape_tzyx=list(fields.shape),leaves=[len(v) for v in sc['ids']],
        scalar_range=scalar_range,reference={k:v for k,v in ref.items() if k!='qs'},parameters=asdict(p),
        conflict_frames=int(np.sum(np.array(H)>theta)),extraction_seconds=extraction_seconds,
        seconds=time.perf_counter()-started,runtime=dict(python=sys.version,numpy=np.__version__,platform=platform.platform()),
        source_sha256={str(f.relative_to(ROOT)):sha256(f) for f in source_files},
        artifact_sha256={f.name:sha256(f) for f in sorted(out.iterdir()) if f.suffix in ('.json','.npz') and f.name not in ('manifest.json','status.json','render_manifest.json','verification.json')})
    dump(out/'manifest.json',manifest)
    from experiments.volume3d.report import build
    build(out)
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',choices=['synthetic','synthetic-conflict','cylinder','tangaroa','ctc'],default='synthetic')
    parser.add_argument('--include-stmtm',action='store_true',help='Optional project 3-D extension, excluded from the primary comparison by default')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args();out=args.out or ROOT/'results/volume3d'/args.dataset
    dump(out/'status.json',dict(status='running',dataset=args.dataset))
    try:
        manifest=run(args.dataset,out,args.input,args.include_stmtm)
        dump(out/'status.json',dict(status='complete',dataset=args.dataset,seconds=manifest['seconds']))
        print('Complete:',out,flush=True)
    except Exception as error:
        dump(out/'status.json',dict(status='failed',dataset=args.dataset,error=str(error),traceback=traceback.format_exc()))
        raise
