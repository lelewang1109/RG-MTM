"""Replace coarse temporal rasters only, retaining native figure layouts."""
from pathlib import Path
from zipfile import ZipFile
import sys,json,hashlib,posixpath,xml.etree.ElementTree as E
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import Normalize,SymLogNorm,LinearSegmentedColormap

R=Path(__file__).resolve().parents[1];C=R.parent/'code';B=R/'.build/temporal_display20261023';O=R/'evidence/temporal_display20261023'
sys.path.insert(0,str(R/'scripts'))
from temporal_display_renderer import render
from scene import Scene
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
stems=['Fig7','Fig10','Fig11','Supplement_Wildfires_Comparison','Supplement_Tangaroa_Comparison','Supplement_Cylinder_Comparison']
scenes={};pictures={};plans={s:[]for s in stems};reports={};sources={}
for stem in stems:
    with ZipFile(B/'before'/(stem+'.pptx'))as z:
        tree=E.fromstring(z.read('ppt/slides/slide1.xml'));sz=E.fromstring(z.read('ppt/presentation.xml')).find(f'{{{P}}}sldSz');rels={r.get('Id'):r.get('Target')for r in E.fromstring(z.read('ppt/slides/_rels/slide1.xml.rels'))}
        pics=[]
        for pic in tree.iter(f'{{{P}}}pic'):
            xf=pic.find(f'{{{P}}}spPr/{{{A}}}xfrm');off=xf.find(f'{{{A}}}off');ext=xf.find(f'{{{A}}}ext');rid=pic.find(f'.//{{{A}}}blip').get(f'{{{RR}}}embed');target=rels[rid];part=posixpath.normpath(target.lstrip('/')if target.startswith('/')else'ppt/slides/'+target)
            pics.append(dict(part=part,x=int(off.get('x'))/9525,y=int(off.get('y'))/9525,w=int(ext.get('cx'))/9525,h=int(ext.get('cy'))/9525))
    scenes[stem]=Scene(0,stem+' temporal display update');scenes[stem].d.update(width=int(sz.get('cx'))/9525,height=int(sz.get('cy'))/9525);pictures[stem]=pics

def source(p):sources[str(p)]=sha(p)
def add(case,method,G,tracks,anchors,cm,norm,selection,targets):
    for stem,index,local in targets:
        pic=pictures[stem][index];lo,hi=selection['window']if local else(0,G.shape[1]);r0,r1=0,len(G)
        if local:
            yy=[float(anchors[t,int(np.flatnonzero(tracks[t]==tr)[0])])for t in range(lo,hi)for tr in selection['tracks']if tr in tracks[t]]
            if method in ['P','R']:yy.extend(float(selection['qnorm'][t,int(np.flatnonzero(tracks[t]==tr)[0])])for t in range(lo,hi)for tr in selection['tracks']if tr in tracks[t])
            yl=max(0,min(yy)-.05);yh=min(1,max(yy)+.05);r0=int(np.floor(yl*(len(G)-1)));r1=int(np.ceil(yh*(len(G)-1)))+1
        factor=101 if local else(61 if case=='wildfire'else 17)
        out=B/'assets'/f'{stem}_{method}_{"local"if local else"full"}.png'
        report=render(G,tracks,anchors,cm,norm,out,factor,(lo,hi),(r0,r1),pic['w']/pic['h'])
        key=stem+'_'+method+('_local'if local else'_full');reports[key]=dict(dataset=case,saved_method=method,**report)
        scenes[stem].image(out,pic['x'],pic['y'],pic['w'],pic['h'],name=key)
        plans[stem].append(dict(**pic,image=str(out),report_key=key))
        print('Rendered',key,report['image_pixels'],'from',G.shape,flush=True)

for case,main,supp,methods in [('wildfire','Fig7','Supplement_Wildfires_Comparison',['TMTM','ST-MTM','P','R']),('tangaroa','Fig10','Supplement_Tangaroa_Comparison',['TMTM','P','R'])]:
    fp=C/f'results/real_case_studies/evidence/{case}.npz';ep=fp.with_name(case+'_event.json');source(fp);source(ep);a=np.load(fp);selection=json.loads(ep.read_text())['selection'];selection['qnorm']=a['qnorm'];tracks=a['track']
    if case=='wildfire':cm=colormaps['YlOrBr'].copy();cm.set_under('#8196A6');norm=Normalize(0,float(a['field'].max()))
    else:
        settings=C/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json';source(settings);tf=json.loads(settings.read_text())['transfer_function_points'];cm=LinearSegmentedColormap.from_list('existing-tangaroa',[(v[0],tuple(v[1:4]))for v in tf],N=2048);norm=Normalize(0,2)
    for i,method in enumerate(methods):
        targets=[(supp,2*i,False),(supp,2*i+1,True)]
        if method in ['P','R']:
            first=8 if case=='wildfire'else 0;row=0 if method=='P'else 1
            targets += [(main,first+row*2,False),(main,first+row*2+1,True)]
        add(case,method,a['map'+method],tracks,a['norm'+method],cm,norm,selection,targets)
    a.close()

case='cylinder';result=C/'results/paper1_suite/square-cylinder3d';data=R.parent/'data/real/paper1_suite/square-cylinder3d'
for name in ['frame_metrics.json','features.json','protocol.json','display_metadata.json']:source(result/name)
rows=json.loads((result/'frame_metrics.json').read_text());features=json.loads((result/'features.json').read_text());protocol=json.loads((result/'protocol.json').read_text());metadata=json.loads((result/'display_metadata.json').read_text());T=len(features['tracks']);maxn=max(map(len,features['tracks']));tracks=np.array([np.pad(x,(0,maxn-len(x)),constant_values=-1)for x in features['tracks']]);cm=colormaps['coolwarm'];norm=SymLogNorm(linthresh=.02,vmin=metadata['vmin'],vmax=metadata['vmax'])
for mi,(method,label)in enumerate([('TMTM','TMTM'),('RG-MTM-P','P'),('RG-MTM-R 0.02','R2'),('RG-MTM-R 0.2','R')]):
    rr=sorted([r for r in rows if r['method']==method],key=lambda r:r['index']);assert len(rr)==102
    columns=[]
    for row in rr:
        p=data/'maps'/Path(row['array']).name;assert sha(p)==row['array_sha256'];source(p);columns.append(np.load(p))
    G=np.column_stack(columns).astype(np.float64);del columns;G*=-protocol['scalar_scale']
    anchors=np.array([np.pad(np.array(r['anchors'])/(len(G)-1),(0,maxn-len(r['anchors'])),constant_values=np.nan)for r in rr]);targets=[('Supplement_Cylinder_Comparison',mi,False)]
    if label in ['P','R']:targets.append(('Fig11',0 if label=='P'else 1,False))
    add(case,label,G,tracks,anchors,cm,norm,{},targets);del G

for stem,scene in scenes.items():
    scene.d['notes']=json.dumps(dict(scope='Replacement scientific rasters only',display='Intermediate time columns are conservative display interpolation, not additional observations or computed layouts. Original saved frame profiles remain exact before pixel antialiasing. Native reference traces, axes, annotations, source views and quantitative tables retain their coordinates.',provenance='evidence/temporal_display20261023/provenance.json'))
    (B/'scenes'/(stem+'_layers.json')).write_text(json.dumps(scene.d,indent=2)+'\n')
(B/'plans.json').write_text(json.dumps(plans,indent=2)+'\n')
record=dict(source_sha256=sources,display_reports=reports,figures=stems,scientific_arrays_modified=False,scientific_metrics_recomputed=False,actual_wildfire_cell_polygons_modified=False,limitation='Broad scalar bands and genuine order changes remain visible. No claim of new measurements between frames.')
(O/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
print('Completed temporal display layers for six existing figures.',flush=True)
