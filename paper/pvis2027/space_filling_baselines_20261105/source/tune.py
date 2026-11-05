"""Choose one orientation per curve/dataset using chronological validation only."""
from evaluate import *
O=O/'tuned'
def aggregate(rows):
 result={}
 for key in ['SNS','TW','NPE']:
  v=[r[key] for r in rows if r[key] is not None];result[key]=float(np.mean(v)) if v else None;result[key+'_valid_frames']=len(v)
 return result
def candidates(shape,method):
 grid=np.arange(np.prod(shape)).reshape(shape);out=[];seen={}
 for rot in range(4):
  for mirror in [False,True]:
   transformed=np.rot90(grid,rot)
   if mirror:transformed=np.fliplr(transformed)
   order=transformed.ravel()[sample_order(transformed.shape,method)]
   for reverse in [False,True]:
    ordered=order[::-1] if reverse else order
    inverse=np.empty(len(ordered),int);inverse[ordered]=np.arange(len(ordered));h=hashlib.sha256(inverse.tobytes()).hexdigest()
    name=f'rot{rot*90}_mirror{int(mirror)}_reverse{int(reverse)}'
    out.append(dict(candidate=name,rotation_degrees=rot*90,mirror=mirror,reverse=reverse,duplicate_of=seen.get(h),inverse=inverse,permutation_sha256=h))
    seen.setdefault(h,name)
 return out
def measure(frame,inverse,par,L,k,t):
 ii,c,q=frame;ranks=inverse[ii];pixels=np.rint(ranks*(L-1)/(len(inverse)-1)).astype(int);u=par['canvas_origin']+pixels*par['canvas']/(L-1);d=pdist(c)
 return dict(frame=t,features=len(ii),SNS=scale_normalized_stress(squareform(d),u) if len(d) and np.dot(d,d)>0 else None,TW=trustworthiness(c,u,k) if 0<k<len(ii)/2 else None,NPE=float(np.max(abs(u-q))/par['canvas']),coincident_display_anchors=len(ii)-len(set(pixels)))
def main():
 O.mkdir(parents=True,exist_ok=True)
 protocol=dict(validation='first chronological25%, ceil(T/4)',objective='J=.5*NPE_norm+.5*SNS_norm; minmax across all legal distinct orientations per method/dataset; constant term0',tie='absolute J difference<=1e-12: prefer earlier canonical enumeration',candidates='4 array rotations x2 left-right mirrors x2 traversal directions; duplicate permutations identified',mapping='same full-grid rank and original-L quantization as canonical experiment; no scaling or translation fitting',test='freeze before evaluating full and last75%; earlier results already observed, exploratory validation not new blind test',missing='do not fill missing raw SNS/TW; if validation has no SNS values, mark selector unavailable instead of silently zeroing it',scope='change curve orientations only, no core algorithm/QP/data/reference changes')
 (O/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');summaries=[];all_candidates=[]
 for ds,k in K.items():
  root=E/'results'/ds;prep=root/'preparation';audit=json.loads((root/'input_audit.json').read_text());par=audit['parameters'];qs=audit['source_reference']['qs'];xy=np.load(prep/'coordinates.npy');F=np.load(prep/'fields.npy',mmap_mode='r');n=len(F);nv=int(np.ceil(n/4));L=196 if ds=='Ring' else 4096
  def frame(t):
   f=Frame(t,prep/'trees',xy);ii=np.array(f.leaves);return ii,np.array([f.leaf_centroid(int(i)) for i in ii]),np.array(qs[t])
  validation=[frame(t) for t in range(nv)]
  for method in ['Hilbert','Morton']:
   cand=candidates(F.shape[1:],method);unique=[c for c in cand if c['duplicate_of'] is None];measured=[]
   for c in unique:
    v=aggregate([measure(fr,c['inverse'],par,L,k,t) for t,fr in enumerate(validation)]);assert v['SNS'] is not None,'No validation SNS samples; J selector unavailable'
    measured.append({key:value for key,value in c.items() if key!='inverse'}|v)
   for metric in ['NPE','SNS']:
    lo=min(r[metric] for r in measured);hi=max(r[metric] for r in measured)
    for r in measured:r[metric+'_norm']=(r[metric]-lo)/(hi-lo) if hi-lo>1e-12 else 0
   for r in measured:r['J']=.5*r['NPE_norm']+.5*r['SNS_norm']
   minimum=min(r['J'] for r in measured);selected=next(r for r in measured if r['J']<=minimum+1e-12);chosen=next(c for c in unique if c['candidate']==selected['candidate']);dest=O/ds/method;dest.mkdir(parents=True,exist_ok=True)
   selection=dict(Dataset=ds,Method=method,validation_frames=list(range(nv)),assessment_frames=list(range(nv,n)),selected=selected,nominal_candidate_count=len(cand),distinct_candidate_count=len(unique),aliases=[{k:v for k,v in c.items() if k!='inverse'} for c in cand]);(dest/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
   # The selection has now been frozen on disk before accessing held-out frames.
   rr=[measure(fr,chosen['inverse'],par,L,k,t) for t,fr in enumerate(validation)]
   for t in range(nv,n):rr.append(measure(frame(t),chosen['inverse'],par,L,k,t))
   save(dest/'per_frame.csv',rr)
   for r in measured:all_candidates.append(dict(Dataset=ds,Method=method,selected=r['candidate']==selected['candidate'],**r))
   sm=dict(Dataset=ds,Method=method+' tuned',candidate=chosen['candidate'],frames=n,validation_frames=nv,assessment_frames=n-nv,TW_k=k,L=L,coincident_anchor_frames=sum(r['coincident_display_anchors']>0 for r in rr),**aggregate(rr))
   sm.update({'assessment_'+key:val for key,val in aggregate(rr[nv:]).items()});summaries.append(sm);print(ds,method,chosen['candidate'],{key:sm[key] for key in ['SNS','TW','NPE']},flush=True)
 save(O/'validation_candidates.csv',all_candidates);save(O/'metrics.csv',summaries)
if __name__=='__main__':main()
