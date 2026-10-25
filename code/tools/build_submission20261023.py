"""Build/check the 2026-10-23 nine-input submission from unchanged saved evidence.

Annual PM2.5 is a verified full-year replacement. Other saved experiments and
frozen publication2027 manifests are not rewritten.
"""
from pathlib import Path
import argparse, csv, hashlib, io, json, math, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'analysis'))
from dataset_suite import PAPER_DATASETS
from provenance import verify_saved_file, historical_source_bytes
OUT = ROOT/'results/submission20261023'
PAPER = ROOT.parent/'paper/manuscript/latex'
EVIDENCE = PAPER/'evidence/submission20261023'
NAMES = dict(era5='Storms', wildfire='Wildfires', olr='OLR', pm25='PM2.5', ring='Ring')
METHODS = {'TMTM':'TMTM', 'ST-MTM':'ST-MTM', 'A':'RG-MTM-P', 'R 20%':'RG-MTM-R20'}
FILES = {}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def frozen_authoring_sha():
    """Preserve the frozen manifest through an explicitly recorded path-only fix."""
    ledger = json.loads((ROOT/'provenance/github_portability_20261023.json').read_text())
    assert hashlib.sha256(historical_source_bytes(ROOT, 'tools/build_submission20261023.py')).hexdigest() == ledger['after_sha256'], 'Unregistered builder change'
    original = ledger['before_source'].encode('utf-8')
    assert hashlib.sha256(original).hexdigest() == ledger['before_sha256']
    return ledger['before_sha256']

def load(name):
    p = ROOT/name; FILES[name] = sha(p)
    return json.loads(p.read_text())
def sources(obj):
    # Numerical source hashes stay historical; exact reverse edits are verified.
    if isinstance(obj, dict) and isinstance(obj.get('source_sha256'),dict):
        for name,h in obj.get('source_sha256', {}).items(): verify_saved_file(ROOT, name, h)

def motion(row):
    n = row.get('clear', row.get('clear_events'))
    e = round(row['error']*n)
    assert abs(row['error']*n-e)<1e-8
    return dict(errors=e, clear=n, error_fraction=row['error'])
def getmotion(rows, truth):
    r = [x for x in rows if x['lag']==2 and x['epsilon']==.02 and x['truth']==truth]
    assert len(r)==1, (truth,len(r))
    return motion(r[0])

def calculate():
    assert tuple(PAPER_DATASETS)==('era5','wildfire','olr','pm25','ring')
    perf=load('results/final_performance.json'); fill=load('results/filling.json'); ev=load('results/eval_projection.json')
    native=load('results/native_merge_errors.json')
    # Annual replacement is isolated from the frozen January aggregate.
    annual='pm25_2000'
    FILES['tools/submission_annual_tables.py']=sha(ROOT/'tools/submission_annual_tables.py')
    load('data/public_scalar/pm25_2000_20000101_20001231.json')
    annualrep=load('results/pm25_2000/replicate_pm25_2000.json')
    perf['pm25']=load('results/pm25_2000/final_performance.json')[annual]
    fill['pm25']=load('results/pm25_2000/filling.json')[annual]
    ev['pm25']=load('results/pm25_2000/eval_projection.json')[annual]
    native['pm25']=load('results/pm25_2000/native_merge_errors.json')[annual]
    validation=load('results/pm25_2000/validation.json');assert validation['status']=='passed'
    for n,h in validation['source_sha256'].items():assert sha(ROOT/n)==h,n
    rows=[]; sensitivity=[]; frontier={}; counts={} 
    grids=[49,64,49,49,14]; fields=['Mean sea-level pressure',r'$\log(1+\mathrm{FRP})$','Outgoing longwave radiation',r'PM$_{2.5}$ concentration','Synthetic ring intensity']
    kinds=['join','split','join','split','split']
    for i,key in enumerate(PAPER_DATASETS):
        rep=annualrep if key=='pm25' else load(f'results/replicate_{key}.json'); sources(rep); sources(perf[key]); sources(native[key])
        cert=rep['certificate']; L=cert['axis']; counts[key]=cert['frames']
        front=load('results/pm25_2000/attainable_pm25_2000.json') if key=='pm25' else load(f'results/attainable_{key}.json'); sources(front)
        f20=next(x for x in front['ours'] if x['cap']==.2)
        frontier[key]=dict(frames=cert['frames'], on_frontier_R20=f20['frames_pareto_optimal'], conflict_frames=cert['conflict_frames'])
        d=dict(key=key,name=NAMES[key],dimension=2,population='synthetic temporal sequence' if key=='ring' else 'physical temporal sequence',
               frames_or_sections=cert['frames'],grid=[grids[i]]*2,leaves=cert['leaves'],tree=kinds[i],scalar_field=fields[i],reference_extent=L,methods={})
        for original,m in METHODS.items():
            rr=next(x for x in ev[key]['proxy'] if x['method']==original and x['k']==2 and x['eps']==.02)
            nm=next(x for x in fill[key] if x['cap']==.2) if original=='R 20%' else None
            d['methods'][m]=dict(NROE=100*perf[key]['methods'][original]['mean'],NMLE_mean=100*nm['mean_opt_share'] if nm else 0.,
                                  NMLE_max=100*nm['D_opt_share'] if nm else 0.,motion={**motion(rr),'truth_dimension':2})
            if original in ('A','R 20%'):
                t=rep['tradeoff']['0.0' if original=='A' else '0.2']
                d['methods'][m].update(E_pool=100*t['ref_err_mean']/L,E_inf=100*t['ref_err_max']/L)
        for cap,t in rep['tradeoff'].items():
            f=next(x for x in fill[key] if x['cap']==float(cap))
            pm='A' if float(cap)==0 else ('R 20%' if float(cap)==.2 else ('R inf' if math.isinf(float(cap)) else None))
            sensitivity.append(dict(dataset=d['name'],cap=float(cap) if not math.isinf(float(cap)) else 'inf',
                E_pool=100*t['ref_err_mean']/L,E_inf=100*t['ref_err_max']/L,NMLE_mean=100*f['mean_opt_share'],NMLE_max=100*f['D_opt_share']))
        rows.append(d)
    configs=[('Tangaroa','tangaroa','results/volume3d/tangaroa-paper-p10-full201',3,[300,180,120],'join','Velocity magnitude',201),
             ('Cylinder','square-cylinder3d','results/paper1_suite/square-cylinder3d',3,[135,64,48],'split','Q criterion',102),
             ('Nucleon','nucleon','results/paper1_suite/nucleon',2,[64,64],'split','Nucleon scalar',1),
             ('Benzene','benzene-potential-reconstructed2d','results/paper1_suite/benzene-potential-reconstructed2d',2,[61,61],'join','Reconstructed electrostatic potential',21)]
    for name,key,folder,dim,grid,tree,field,nframes in configs:
        metrics=load(folder+'/metrics.json'); frames=load(folder+'/frame_metrics.json'); params=load(folder+'/parameters.json')
        protocol=load(folder+'/protocol.json'); sources(protocol)
        features=load(folder+'/features.json'); feature_frames=features if isinstance(features,list) else features['frames']
        source_manifest=ROOT/(folder+'/source_manifest.json')
        if source_manifest.exists():
            for n,h in load(folder+'/source_manifest.json').items(): verify_saved_file(ROOT,n,h)
        nleaves=[len(f['leaf_ids']) for f in feature_frames]
        L=params['canvas']; assert len(nleaves)==nframes
        static=name in ['Nucleon','Benzene']
        d=dict(key=key,name=name,dimension=dim,population='static section' if static else 'physical temporal sequence',frames_or_sections=nframes,
               grid=grid,leaves=[min(nleaves),max(nleaves)],tree=tree,scalar_field=field,reference_extent=L,methods={'ST-MTM':None},protocol=folder+'/protocol.json')
        cylinder_motion=load(folder+'/motion.json') if name=='Cylinder' else None
        for m in metrics:
            original=m['method']; standard={'TMTM':'TMTM','RG-MTM-P':'RG-MTM-P','RG-MTM-R 0.2':'RG-MTM-R20'}.get(original)
            if 'NMLE_mean' not in m: continue
            z=dict(NROE=100*m['NROE_mean'],NMLE_mean=100*m['NMLE_mean'],NMLE_max=100*m['NMLE_max'])
            selected=[f for f in frames if f['method']==original]; assert len(selected)==nframes
            assert np.isclose(np.mean([f['NROE'] for f in selected]),m['NROE_mean'],atol=1e-12)
            assert np.isclose(np.mean([f['NMLE'] for f in selected]),m['NMLE_mean'],atol=1e-12)
            if original!='TMTM':
                errors=[]
                for f in selected:
                    q=np.asarray(f['layout']['reference']); x=np.asarray(f['layout']['x'])
                    assert len(q)==len(x)==nleaves[f['index']]
                    errors.extend(np.abs(x-q).tolist())
                z.update(E_pool=100*sum(errors)/(L*len(errors)),E_inf=100*max(errors)/L,anchor_instances=len(errors))
                cap=0 if original=='RG-MTM-P' else float(original.split()[-1])
                sensitivity.append(dict(dataset=name,cap=cap,**z))
            if not static:
                eventrows=[r for r in cylinder_motion if r['method']==original] if cylinder_motion else m['motion']
                z['motion']={**getmotion(eventrows,'spatial' if cylinder_motion else '3d'),'truth_dimension':3}
                z['projected_motion']={**getmotion(eventrows,'projected'),'truth_dimension':1}
            if standard:d['methods'][standard]=z
        rows.append(d)
    assert sum(counts.values())==614
    summary=dict(scope='Nine-input submission with independently verified full-year 2000 PM2.5 replacement; other saved experiments unchanged',
        metric_units='NROE, NMLE, E_pool and E_inf are percentages; motion is errors over its own clear-event set',
        datasets=rows,sensitivity=sensitivity,planar_frontier=frontier,
        population=dict(primary_datasets=9,planar_temporal_sequences=5,planar_temporal_frames=614,
            temporal_sequences=7,all_temporal_frames=917,static_datasets=2,static_sections=22,
            exhaustive_planar_frontier_R20_on=sum(x['on_frontier_R20'] for x in frontier.values()),independent_mirror_control_frames=64),
        excluded_current_member=dict(key='gaussians',grid=[64,64],frames=64,reason='Editorial removal from current submission; original evidence retained as legacy'),
        safeguards=['Tangaroa and Cylinder source inputs remain 3-D.',
            'No cross-dataset motion-rate pooling. Static inputs have no motion score; ST-MTM not run on four additions.',
            '2-D optional hierarchy pruning and volume no-pruning are disclosed; kappa is eligibility, not a guaranteed NMLE cap.',
            'Benzene is reconstructed electrostatic potential and 21 static z sections, not physical time.',
            '241x241 mirror control and generic Gaussian primitives remain active.'])
    # Independently match the earlier read-only calculation, including exact source bytes.
    audit=json.loads((ROOT.parent/'docs/实验调整依据/去除Gaussian与统一指标_只读核算.json').read_text())
    for n,h in audit['source_sha256'].items():
        # Keep the historical audit unchanged, but verify this checkout's bytes.
        # A successful local check must not accidentally read another worktree.
        recorded = Path(n)
        if recorded.is_absolute():
            prefix, marker, relative = n.partition('/RG-MTM/code/')
            if not marker:
                raise ValueError(f'Unknown historical source root: {n}')
            recorded = Path(relative)
        current = ROOT / recorded
        assert current.resolve().is_relative_to(ROOT), n
        assert sha(current)==h, n
    for d in rows:
        if d['name']=='PM2.5':continue # annual values checked against isolated saved arrays, not January audit
        a=next(x for x in audit['datasets'] if x['name']==d['name'])
        for m,z in d['methods'].items():
            if z is None: assert a['methods'][m] is None;continue
            for metric in ['NROE','NMLE_mean','NMLE_max','E_pool','E_inf']:
                if metric in z:assert math.isclose(z[metric],a['methods'][m][metric],rel_tol=1e-10,abs_tol=1e-10),(d['name'],m,metric,z[metric],a['methods'][m][metric])
            if 'motion' in z:assert z['motion']['errors']==a['methods'][m]['motion']['errors'] and z['motion']['clear']==a['methods'][m]['motion']['clear']
    return summary

def table(cols,header,rows,caption,label,note,wide=False):
    env='table*' if wide else 'table'
    return '\n'.join([rf'\begin{{{env}}}[t]',rf'\caption{{{caption}}}\label{{{label}}}',r'\centering\footnotesize\setlength{\tabcolsep}{4pt}',
        rf'\begin{{tabular}}{{{cols}}}\toprule',header+r'\\\midrule',*[' & '.join(row)+r'\\' for row in rows],
        r'\bottomrule\end{tabular}',r'\par\smallskip{\footnotesize\raggedright '+note+r'\par}',rf'\end{{{env}}}',''])
def outputs(summary):
    data=summary['datasets']; result={}
    def name(d):return r'PM$_{2.5}$' if d['name']=='PM2.5' else d['name']
    def pct(x):return f'{x:.4f}' if 0<x<.01 else f'{x:.3f}'
    rows=[]
    for d in data:
        grid='$'+'\\times'.join(map(str,d['grid']))+'$'
        count=str(d['frames_or_sections'])+(' sections' if d['name']=='Benzene' else (' slice' if d['name']=='Nucleon' else ' frames'))
        leaf='--'.join(map(str,d['leaves'])) if d['leaves'][0]!=d['leaves'][1] else str(d['leaves'][0])
        rows.append([name(d),f"{d['dimension']}-D",d['scalar_field'],grid,count,leaf,d['tree'].capitalize()])
    result['tables/datasets_main.tex']=table('lllrlll',r'Data & Input & Scalar field & Processed grid & Samples & Leaves & Tree',rows,
        'All nine inputs evaluated with the shared error definitions. Source dimension describes the input, not the two-dimensional map output.', 'tab:datasets_main',
        r'Storms, Wildfires, OLR and PM$_{2.5}$ are observed fields; Ring is synthetic. Tangaroa and Cylinder are volumetric simulations. Cylinder Q is computed on the original $192\times64\times48$ velocity grid before the $135\times64\times48$ crop. Nucleon is one author-provided static planar slice; Benzene is a reconstructed point-charge potential evaluated on 21 static sections. Seven temporal sequences contain 917 frames; static sections and the independent mirror control are separate populations.',True)
    # User-selected old-draft table layout: one common block for all nine inputs.
    # Templates contain headings/notes only; every numeric cell is regenerated.
    def styled_table(stem, rows):
        template=ROOT/'tools/submission_templates'/(stem+'.tex')
        FILES[str(template.relative_to(ROOT))]=sha(template)
        return template.read_text().replace('%%ROWS%%','\n'.join(' & '.join(row)+r'\\' for row in rows))
    rows=[]
    for d in data:
        m=d['methods']; r=m['RG-MTM-R20']; event=m['RG-MTM-P'].get('motion')
        precision=4 if d['name'] in ['Nucleon','Benzene'] else 2
        row=[d['name'],str(event['clear']) if event else '--']
        for k in ['TMTM','ST-MTM','RG-MTM-P','RG-MTM-R20']:
            v=m[k]
            row += [f"{v['NROE']:.{precision}f}" if v else 'n/r',
                    f"{v['motion']['error_fraction']:.3f}" if v and v.get('motion') else '--']
        row += [f"{r[k]:.{precision}f}" for k in ['NMLE_mean','NMLE_max']]
        rows.append(row)
    result['tables/comparison_revision.tex']=styled_table('comparison_revision',rows)
    rows=[[d['name'],*[f"{d['methods'][m][k]:.2f}" for m in ['RG-MTM-P','RG-MTM-R20'] for k in ['E_pool','E_inf']]] for d in data]
    result['tables/achieved_reference_main.tex']=styled_table('achieved_reference_main',rows)
    # A detailed settings table belongs to the supplement, retaining its historical label.
    rows=[]
    for d in data:
        if d['name'] not in ['Tangaroa','Cylinder']:continue
        for m in ['TMTM','RG-MTM-P']:
            z=d['methods'][m]; e=z['motion'];p=z['projected_motion']
            rows.append([d['name'],m,pct(z['NROE']),pct(z.get('E_pool',float('nan'))) if 'E_pool'in z else 'n/a',pct(z['NMLE_mean']),pct(z['NMLE_max']),f"{e['errors']}/{e['clear']}",f"{p['errors']}/{p['clear']}"])
        for z in summary['sensitivity']:
            if z['dataset']!=d['name'] or z['cap']==0:continue
            # Motion is obtained from exact stored method records without pooling.
            folder=d['protocol'].rsplit('/',1)[0]; ms=load(folder+'/metrics.json'); original=f"RG-MTM-R {z['cap']:g}"
            mm=next(x for x in ms if x['method']==original)
            motionrows=[x for x in load(folder+'/motion.json') if x['method']==original] if d['name']=='Cylinder' else mm['motion']
            e=getmotion(motionrows,'spatial' if d['name']=='Cylinder' else '3d');p=getmotion(motionrows,'projected')
            rows.append([d['name'],rf'R, $\kappa={100*z["cap"]:g}\%$',pct(z['NROE']),pct(z['E_pool']),pct(z['NMLE_mean']),pct(z['NMLE_max']),f"{e['errors']}/{e['clear']}",f"{p['errors']}/{p['clear']}"])
        folder=d['protocol'].rsplit('/',1)[0]
        if d['name']=='Tangaroa':
            mm=next(x for x in load(folder+'/metrics.json') if x['method']=='Exact projection')
            e=getmotion(mm['motion'],'3d');p=getmotion(mm['motion'],'projected')
        else:
            projection=[x for x in load(folder+'/motion.json') if x['method']=='Exact x projection']
            e=getmotion(projection,'spatial');p=getmotion(projection,'projected')
        rows.append([d['name'],'Exact projection','0','0','n/a','n/a',f"{e['errors']}/{e['clear']}",f"{p['errors']}/{p['clear']}"])
    result['tables/volume3d_settings_supp.tex']=table('llrrrrll',r'Data & Method & NROE & $E_{\rm pool}$ & NMLE mean & NMLE max & Spatial motion & Projected motion',rows,
        'Detailed volumetric settings under the same shared metric definitions (percent and errors/clear events).','tab:volume',
        r'The main paper common result tables include these inputs; this supplementary table expands only the parameter and projection checks. $E_{\rm pool}$ uses continuous, pooled anchors. Spatial and projected motion have their own denominators and cannot be subtracted as a causal decomposition. Optional strongest-first hierarchy pruning is disabled for these larger inputs; $\kappa$ is not a measured scalar cap. ST-MTM is not run.',False)
    detail=result['tables/volume3d_settings_supp.tex']
    detail=detail.replace(r'\begin{tabular}',r'\resizebox{\linewidth}{!}{\begin{tabular}',1).replace(r'\bottomrule\end{tabular}',r'\bottomrule\end{tabular}}',1)
    result['tables/volume3d_settings_supp.tex']=detail
    # Existing supplement diagnostics are filtered selections, never rewritten raw evidence.
    # This historical snapshot excludes tables from later experiments.
    frozen_outputs=json.loads((OUT/'manifest.json').read_text())['generated_sha256']
    for p in sorted((PAPER/'tables').glob('*.tex')):
        rel='tables/'+p.name
        if rel not in frozen_outputs: continue
        if rel in result: continue
        s=p.read_text();s='\n'.join(line for line in s.splitlines() if not line.startswith(('Gaussian &','Gaussians &')))+'\n'
        s=s.replace('Six sequences, 342 frames.','Five planar temporal sequences, 278 frames.').replace('six-dataset suite','five-dataset planar suite')
        s=s.replace(' Gaussian has no clear events, so its rates are undefined.','').replace('Gaussian has only unchanged labels and is not used to assess motion classification. ','')
        # Carry a standalone legacy table only as a compatibility source; current supplement uses the common-definition table.
        if p.name=='volume3d_main.tex':continue
        result[rel]=s
    for filename in ['final_performance.json','eval_projection.json','filling.json','pointcert.json','native_merge_errors.json']:
        original=load('results/'+filename)
        if filename in ['final_performance.json','eval_projection.json','filling.json','pointcert.json','native_merge_errors.json']:
            original['pm25']=load('results/pm25_2000/'+filename)['pm25_2000']
        result['selected_evidence/'+filename]=json.dumps({k:original[k] for k in PAPER_DATASETS},indent=2)+'\n'
    claims=dict(frames=614,active_planar_datasets=list(PAPER_DATASETS),frontier=summary['planar_frontier'],
                R20_on_frontier=summary['population']['exhaustive_planar_frontier_R20_on'],conflict_frames_total=sum(x['conflict_frames'] for x in summary['planar_frontier'].values()),primary_datasets=9,temporal_frames=917,static_sections=22)
    result['claims.json']=json.dumps(claims,indent=2)+'\n'
    result['unified_metrics.json']=json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    f=io.StringIO();w=csv.writer(f,lineterminator="\n");w.writerow(['dataset','dimension','population','samples','method','NROE_pct','NMLE_mean_pct','NMLE_max_pct','E_pool_pct','E_inf_pct','motion_errors','motion_clear','motion_rate'])
    for d in data:
        for m,z in d['methods'].items():
            if z is None:w.writerow([d['name'],d['dimension'],d['population'],d['frames_or_sections'],m,'n/r','n/r','n/r','n/r','n/r','n/r','n/r','n/r']);continue
            e=z.get('motion',{})
            w.writerow([d['name'],d['dimension'],d['population'],d['frames_or_sections'],m,*[z.get(k,'n/a') for k in ['NROE','NMLE_mean','NMLE_max','E_pool','E_inf']],e.get('errors','n/a'),e.get('clear','n/a'),e.get('error_fraction','n/a')])
    result['unified_metrics.csv']=f.getvalue()
    from submission_annual_tables import apply
    return apply(result,load)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    summary=calculate(); result=outputs(summary)
    # Manifest records inputs, selected population, and byte-exact generated outputs.
    manifest=dict(scope=summary['scope'],population=summary['population'],source_sha256=FILES,
        generated_sha256={n:hashlib.sha256(s.encode()).hexdigest() for n,s in result.items()},
        authoring_script='tools/build_submission20261023.py',authoring_script_sha256=frozen_authoring_sha(),
        historical_manifest='results/publication2027/manifest.json',historical_manifest_sha256=sha(ROOT/'results/publication2027/manifest.json'))
    result['manifest.json']=json.dumps(manifest,indent=2,ensure_ascii=False)+'\n'
    for rel,s in result.items():
        paths=[OUT/rel]
        if rel.startswith('tables/'):paths.append(PAPER/rel)
        elif rel in ['unified_metrics.json','unified_metrics.csv','manifest.json','claims.json'] or rel.startswith('selected_evidence/'):paths.append(EVIDENCE/rel)
        for path in paths:
            if a.check:
                assert path.is_file() and path.read_text()==s, f'Current submission output differs: {path}'
            else:
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s)
    report=dict(status='passed',population=summary['population'],source_files=len(FILES),
        checks=['Original source hashes validated through exact reversible source ledger','Saved-frame aggregation matches saved sequence metrics',
                'Same-definition continuous displacement independently recomputed from layouts','Unchanged inputs match historical audit; annual PM2.5 matches independent saved-array checks',
                'All selected outputs match current bytes'],numerical_rerun='annual PM2.5 only')
    if not a.check:
        (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
