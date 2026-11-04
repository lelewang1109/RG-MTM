"""Independent checks of all saved final maps, formulas, selection and ranks."""
from pathlib import Path
import json,csv,hashlib,importlib.util,sys
import numpy as np
from scipy.spatial.distance import pdist,squareform
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));spec=importlib.util.spec_from_file_location('formal_run',HERE/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
from experiments.volume3d.compact_tmtm import barrier_matrix

def tw(c,u,k):
 n=len(u)
 if not 0<k<n/2:return None
 D=squareform(pdist(c));H=squareform(pdist(np.array(u)[:,None]));penalty=0
 for i in range(n):
  js=np.array([j for j in range(n) if j!=i]);a=js[np.lexsort((js,D[i,js]))];b=js[np.lexsort((js,H[i,js]))];rank={j:k+1 for k,j in enumerate(a)};penalty+=sum(rank[j]-k for j in set(b[:k])-set(a[:k]))
 return 1-2*penalty/(n*k*(2*n-3*k-1))

def minima_count(v):
 v=np.asarray(v);v=v[np.r_[True,np.diff(v)!=0]]
 if len(v)==1:return 1
 return int(v[0]<v[1])+int(v[-1]<v[-2])+int(np.sum((v[1:-1]<v[:-2])&(v[1:-1]<v[2:])))

def main():
 O=r.O;records=[];frame_checks=[];core=r.read(O/'config/core_sha256.json')
 assert all(r.sha(r.W/k)==h for k,h in core.items())
 with r.threadpool_limits(limits=1):
  for name in r.PARAMS:
   root=O/'results'/name;warm=root/'preparation';F=np.load(warm/'fields.npy');xy=np.load(warm/'coordinates.npy');meta=r.read(warm/'protocol.json');cfg=r.PARAMS[name];d=r.load(name,F,xy,meta['sample_measure'],warm/'trees');sc=d['scene'];p=d['parameters'];audit=r.read(root/'input_audit.json');a=np.array(d['reference']['candidates']['direction']['a'])
   for q,e in zip(d['reference']['qs'],d['extrema']):np.testing.assert_allclose(q,np.sum(np.asarray(e)*a[None,:],axis=1),atol=1e-12,rtol=0)
   for q1,q2 in zip(audit['source_reference']['qs'],d['reference']['qs']):np.testing.assert_array_equal(q1,q2)
   selected=r.read(root/'selection.json');assert selected['rule_version']==3 and selected['epsilon']>0
   candidate=[x for x in selected['candidates'] if x['epsilon']>0 and x['success'] and x.get('NPE') is not None and x.get('SNS') is not None and x['topology_max']<=x['epsilon']+1e-12 and x['rendered_budget_violations']==0];assert candidate
   normalizers={key:(min(x[key] for x in candidate),max(x[key] for x in candidate)) for key in ['NPE','SNS']};scores=[]
   for x in candidate:
    values=[]
    for key in ['NPE','SNS']:
     lo,hi=normalizers[key];v=0. if hi-lo<=1e-12 else (x[key]-lo)/(hi-lo);np.testing.assert_allclose(v,x[key+'_norm'],atol=1e-12);values.append(v)
    score=.5*values[0]+.5*values[1];np.testing.assert_allclose(score,x['J'],atol=1e-12);scores.append((x,score))
   low=min(score for _,score in scores);near=[x for x,score in scores if score<=low+.01+1e-12];win=min(near,key=lambda x:(x['epsilon'],x['topology_max']));assert selected['epsilon']==win['epsilon']
   for label in ['Exact','Balanced']:
    dest=root/label;s=r.read(dest/'summary.json');assert s['success'],(name,label,s.get('error'));lay=r.read(dest/'layouts.json');M=np.load(dest/'map.npz')['map'];assert M.shape==(cfg['L'],cfg['T']) and np.isfinite(M).all();U=[np.array(z['pixel_x']) for z in lay];sns=[];trust=[];npe=[];td=0.;steps=0;maxerr=0.;unlabelled=0;repaired=0;maxpixerror=0.;native_parity=0
    for t,(fr,ids,c,q,u,row,tr,V) in enumerate(zip(sc['frames'],sc['ids'],sc['centers'],d['reference']['qs'],U,lay,sc['tracks'],d['merge_values'])):
     assert np.isfinite(u).all();pix=np.rint((u-p.canvas_origin)/p.canvas*(cfg['L']-1)).astype(int);assert len(set(pix))==len(pix) and pix.min()>=0 and pix.max()<cfg['L'];np.testing.assert_allclose(M[pix,t],fr.values[ids],atol=1e-8,rtol=0)
     matrix=barrier_matrix(M[:,t],pix);err=float(np.max(abs(matrix-V))/d['scalar_range']);maxerr=max(maxerr,err);assert err<=s['epsilon']+1e-12
     x,z,w=map(np.array,(row['x'],row['z'],row['w']));order=np.array(row['order']);assert np.all(z-w/2>=p.canvas_origin-1e-6) and np.all(z+w/2<=p.canvas_origin+p.canvas+1e-6);assert np.all(abs(x-z)<=p.rho*w/2+1e-6);assert np.all(np.diff(z[order])>=(w[order][:-1]+w[order][1:])/2+p.gap-1e-6)
     src=pdist(c);dst=pdist(u[:,None])
     if len(src) and src@src>0:
      scale=(src@dst)/(dst@dst) if dst@dst>0 else 0.;sns.append(float(np.sum((src-scale*dst)**2)/np.sum(src*src)))
     v=tw(c,u,cfg['k'])
     if v is not None:trust.append(v)
     npe.append(float(max(abs(u-q))/p.canvas))
     if t:
      old=dict(zip(sc['tracks'][t-1],U[t-1]));td+=sum(abs(x-old[k])/p.canvas for k,x in zip(tr,u) if k in old);steps+=sum(k in old for k in tr)
     diag=row.get('raster_error',{}).get('integer_rounding',{});repaired+=diag.get('repaired',False);maxpixerror=max(maxpixerror,diag.get('max_coordinate_rounding_error_pixels',0.));nmin=minima_count(M[:,t]);unlabelled+=nmin!=len(ids)
     if diag and not diag.get('repaired'):
      _,sk,_=r._native_renderer([fr],[ids],[row],p.canvas,cfg['L'],canvas_origin=p.canvas_origin);original=dict(zip(sk[0].ordering,sk[0].anchors));assert all(original[k]==px for k,px in zip(ids,pix));native_parity+=1
     frame_checks.append(dict(Dataset=name,Method=label,frame=t,leaf_labels=len(ids),display_profile_minima=nmin,labelled_topology_error=err,rounding_repaired=diag.get('repaired',False),rounding_error_pixels=diag.get('max_coordinate_rounding_error_pixels',0.)))
    np.testing.assert_allclose(np.mean(sns),s['SNS'],atol=1e-12);np.testing.assert_allclose(np.mean(npe),s['NPE'],atol=1e-12);np.testing.assert_allclose(td,s['TD'],atol=1e-10);np.testing.assert_allclose(maxerr,s['topology_max'],atol=1e-12);assert steps==s['matched_steps'];assert len(trust)==s['TW_valid_frames']
    if trust:np.testing.assert_allclose(np.mean(trust),s['TW'],atol=1e-12)
    else:assert s['TW'] is None
    assert s['t_total']>=s['t_preprocess']+s['t_topology']+s['t_features_reference']+s['method_seconds']-1e-6
    assert unlabelled==0,(name,label,'unexpected unlabelled profile minima',unlabelled)
    records.append(dict(Dataset=name,Method=label,all_metrics_independently_verified=True,finite_maps=True,all_leaf_anchors_preserved=True,source_reference_verified=True,topology_budget_verified=True,TW_valid_frames=len(trust),TD_matched_steps=steps,profile_minimum_count_mismatch_frames=unlabelled,integer_repaired_frames=repaired,max_rounding_error_pixels=maxpixerror,native_rounding_parity_checked_frames=native_parity))
   for mode in ['tmtm','base','temporal']:
    folder=root/'baseline_npe';s=r.read(folder/(mode+'.json'));assert s['success'],(name,mode,s.get('error'));U=r.read(folder/(mode+'_anchors.json'));value=np.mean([max(abs(np.array(u)-q))/p.canvas for u,q in zip(U,d['reference']['qs'])]);np.testing.assert_allclose(value,s['NPE'],atol=1e-12)
    for part in ['Eq2_certificates','Eq1_fallback_certificates']:
     f=folder/(mode+'_'+part+'.json')
     if f.exists():
      for z in r.read(f):
       c=z['certificate'];limit=c.get('complementarity_acceptance_limit',1e-7)
       if 'objective_scale' in c:np.testing.assert_allclose(limit,1e-7+1e-10*c['objective_scale'],atol=1e-15)
       assert c['primal_residual']<1e-7 and c['stationarity_residual']<1e-7 and c['complementarity_residual']<limit
   print('VERIFIED',name,flush=True)
 # Ranking audit is recomputed without calling the table generator's rank function.
 data=r.read(O/'assembled.json');rows=data['comparison'];lookup={(x['Dataset'],x['Method']):x for x in rows}
 for x in r.read_csv(O/'ranking_audit.csv'):
  metric=x['Metric'];group=x['Group'];ds=x['Dataset'];rr=[]
  for row in rows:
   if row['Dataset']!=ds:continue
   if group=='local_normalized_TD':
    if row['metrics_source']=='local' and row['TD_measured_local'] is not None:rr.append((row['Method'],row['TD_measured_local']))
   elif row[metric+'_rank_group']==group and row[metric] is not None:rr.append((row['Method'],row[metric]))
  digits=2 if metric=='TD' else 3 if metric in ['SNS','TW'] else 4;values=sorted({round(v,digits) for _,v in rr},reverse=metric=='TW');val=next(v for m,v in rr if m==x['Method']);assert values.index(round(val,digits))+1==int(x['Rank'])
  expected='best' if int(x['Rank'])==1 else 'second' if int(x['Rank'])==2 else 'normal';assert expected==x['Style']
 for f in (O/'tables').glob('*.tex'):
  text=f.read_text();assert '\\toprule' in text and '\\bottomrule' in text
  assert not any('|' in line for line in text.splitlines() if '\\begin{tabular}' in line)
 for ds in r.PARAMS:
  rr=[row for row in rows if row['Dataset']==ds];assert len(rr)==4
  for metric in ['SNS','TW','NPE']:
   assert len({row[metric+'_rank_group'] for row in rr})==1
  assert all(row['TD'] is not None and row['TD_rank_group'] in ['published_TD','local_normalized_TD'] for row in rr)
  for row in rr:
   if row['metrics_source']=='local':
    s=r.read(O/'results'/ds/row['Method'].replace('AnchorMTM ','')/'summary.json')
    for metric in ['TD','t_opt','t_total']:np.testing.assert_allclose(row[metric],s[metric],atol=1e-12)
 assert sum(x['Metric']=='TD' for x in r.read_csv(O/'ranking_audit.csv'))==16
 assert '\\rowcolor' not in (O/'tables/anchor_parameter_settings.tex').read_text()
 assert (O/'tables/quantitative_comparison.tex').read_text().count('$t_{\\rm opt}$')==2
 assert all(r.sha(r.W/k)==h for k,h in core.items())
 r.table(O/'independent_verification.csv',records);r.table(O/'profile_validation_per_frame.csv',frame_checks);r.dump(O/'verification.json',dict(all_passed=True,core_sources_unchanged=True,all_eight_anchor_runs_legal=True,all_twelve_baseline_NPE_computed=True,rankings_independently_verified=True,selection_replayed_without_test_metrics=True,records=records))

if __name__=='__main__':main()
