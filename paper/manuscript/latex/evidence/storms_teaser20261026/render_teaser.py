"""Figure-1 composition: geographic witnesses, event locator, P/R1/R2/R5."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from scipy.interpolate import RegularGridInterpolator
from netCDF4 import Dataset
import build_preview as b
import render_linked as linked

FRAMES=[33,34,35,37,42]
LABELS={33:['A','B'],34:['A'],35:['A'],37:['A','C'],42:['D','E','F']}
METHODS=['P','R1','R2','R5']


def source_fields(a):
    path=b.HERE/'teaser_source_fields.npz'
    if path.exists():
        data=np.load(path)
        if np.array_equal(data['frames'],FRAMES):return data
    with Dataset(b.SOURCE) as ds:
        fields=[]
        for t in FRAMES:
            i=int(a['source_indices'][t])
            fields.append(np.asarray(ds['msl'][i],float)/100-np.asarray(ds['msl'][i-96:i+96],float).mean(0)/100)
        np.savez_compressed(path,fields=fields,frames=FRAMES,lat=np.asarray(ds['latitude'][:]),lon=np.asarray(ds['longitude'][:]))
    return np.load(path)


def render_teaser(a,old,results,metrics):
    for name in ['Arial.ttf','Arial Bold.ttf']:
        font_manager.fontManager.addfont('/System/Library/Fonts/Supplemental/'+name)
    plt.rcParams.update({'font.family':'Arial','font.style':'normal','font.size':16,
        'axes.labelsize':16,'axes.titlesize':18,'xtick.labelsize':16,'ytick.labelsize':16,
        'text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black',
        'axes.edgecolor':'black','axes.linewidth':.8,'axes.spines.top':True,'axes.spines.right':True,
        'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
    fig=plt.figure(figsize=(18,11.5),facecolor='white')
    fig.text(.06,.967,'(a) Full December sequence',fontsize=22,weight='bold')
    fig.text(.94,.967,'R, κ = 20%',fontsize=18,ha='right')
    overview=fig.add_axes([.08,.880,.86,.060])
    validations={'full_sequence':b.map_image(overview,old['mapR'],old['tracks'],old['normR'],0,743,factor=3)}
    overview_crop_difference=float(np.max(abs(old['mapR'][:,30:47]-results['map_R5'][:,30:47])))
    assert overview_crop_difference<1e-6
    overview.add_patch(Rectangle((29.5,.10),17,.32,fill=False,edgecolor=b.ACCENT,lw=2.3,zorder=10))
    overview.annotate('Selected window: 2 Dec, 06–22h',xy=(38,.26),xytext=(205,.72),fontsize=16,
        arrowprops=dict(arrowstyle='->',color='black',lw=1.2),ha='left',va='center',
        bbox=dict(fc='white',ec='none',alpha=.94,pad=2))
    overview.set(xlim=(-.5,743.5),ylim=(0,1),yticks=[0,1],xticks=[0,168,336,504,743],
        xticklabels=['1 Dec','8 Dec','15 Dec','22 Dec','31 Dec'])
    overview.tick_params(length=3,pad=5)
    fig.text(.06,.815,'(b) Geographic snapshots inside the selected window',fontsize=22,weight='bold')
    src=source_fields(a)
    co=np.cos(np.deg2rad(52.5));radius=6371.
    extent=np.r_[radius*co*np.deg2rad([-30,40]),radius*np.sin(np.deg2rad([30,75]))/co]
    ratio=np.ptp(extent[:2])/np.ptp(extent[2:])
    geo=b.Era5Geo(dict(lon=(-30,40),lat=(30,75)),a['coords'])
    geo.factor=1.;geo.offx=geo.bx0;geo.offy=geo.by0
    X,Y=np.meshgrid(np.linspace(extent[0],extent[1],650),np.linspace(extent[2],extent[3],round(650/ratio)))
    pts=np.stack([np.rad2deg(np.arcsin(Y*co/radius)),np.rad2deg(X/radius/co)],-1)
    pts[...,0]=np.clip(pts[...,0],src['lat'].min(),src['lat'].max())
    pts[...,1]=np.clip(pts[...,1],src['lon'].min(),src['lon'].max())
    width=.152;gap=.030;height=width*18/11.5/ratio
    correspondence=[]
    for number,t in enumerate(FRAMES,1):
        ax=fig.add_axes([.06+(number-1)*(width+gap),.535,width,height])
        image=RegularGridInterpolator((src['lat'],src['lon']),src['fields'][number-1])(pts)
        ax.imshow(image,origin='lower',extent=extent,cmap=b.CM,norm=b.NORM,interpolation='bilinear')
        geo.coastlines(ax,b.CODE/'data/geo/ne_110m_coastline.geojson',lw=.65,color='#263238',alpha=1)
        xt=radius*co*np.deg2rad([-20,20]);yt=radius*np.sin(np.deg2rad([35,55,75]))/co
        ax.set(xlim=extent[:2],ylim=extent[2:],aspect='equal',xticks=xt,xticklabels=['20°W','20°E'],yticks=yt)
        ax.set_yticklabels(['35°N','55°N','75°N'] if number==1 else [])
        ax.tick_params(length=3,pad=5)
        date=str(results['dates'][t]);stamp=f"{int(date[8:10])} Dec {date[11:13]}:00"
        ax.set_title(f'{number}   {stamp}',fontsize=18,weight='bold',loc='left',pad=9)
        org=np.array([extent[0]+.73*np.ptp(extent[:2]),extent[2]+.12*np.ptp(extent[2:])])
        vec=results['direction']*650
        ax.annotate('',xy=org+vec,xytext=org,arrowprops=dict(arrowstyle='->',color='black',lw=1.5))
        ax.text(*(org+vec+[60,25]),'d',fontsize=18)
        if t in [34,35]:
            assert not np.any(results['tracks'][t]==linked.FEATURES['B']['track'])
            assert not np.any(results['tracks'][t]==linked.FEATURES['C']['track'])
            ax.text(.04,.96,'No B extremum',transform=ax.transAxes,fontsize=16,va='top',
                bbox=dict(fc='white',ec='none',alpha=.9,pad=2))
        for letter in LABELS[t]:
            j=linked.feature(results,t,letter);lon,lat=results['lonlat'][t,j]
            leaf=int(results['leaf'][t,j]);assert np.allclose(a['lonlat'][leaf],[lon,lat],atol=1e-12,rtol=0)
            projected=(a['coords'][leaf]@results['direction']-results['geometry'][0])/results['geometry'][1]
            assert abs(projected-results['qnorm'][t,j])<1e-12
            linked.mark(ax,*geo.xy(lon,lat),letter,offset=(8,18) if letter in ['A','D'] else (8,8),size=18)
            correspondence.append(dict(snapshot=number,frame=t,letter=letter,track=linked.FEATURES[letter]['track'],longitude=float(lon),latitude=float(lat)))
    # Validate the omitted 12h onset as well as the displayed 10h/11h gap.
    assert int(np.flatnonzero(np.any(results['tracks']==linked.FEATURES['C']['track'],axis=1))[0])==36
    for letter in ['A','B','C']:
        exists=np.array([np.any(results['tracks'][t]==linked.FEATURES[letter]['track']) for t in range(33,38)])
        expected={'A':[1,1,1,1,1],'B':[1,0,0,0,0],'C':[0,0,0,1,1]}[letter]
        assert np.array_equal(exists,np.asarray(expected,bool))
    fig.text(.06,.465,'(c) Threshold comparison in the selected window',fontsize=22,weight='bold')
    fig.text(.06,.435,'2 Dec, UTC     × geographic reference     ● mapped position     | displacement',fontsize=16)
    # Every annotation must have a matching object in a displayed snapshot.
    local_features={t:list(LABELS[t]) for t in FRAMES}
    assert set(local_features)==set(FRAMES)
    assert {(t,letter) for t,letters in local_features.items() for letter in letters}=={(r['frame'],r['letter']) for r in correspondence}
    for index,method in enumerate(METHODS):
        row,col=divmod(index,2)
        ax=fig.add_axes([.08+col*.465,.270-row*.180,.395,.120])
        ax.set_title('P · hierarchy preserved' if method=='P' else f'R, κ = {method[1:]}%',fontsize=18,weight='bold',loc='left',pad=8)
        validations[method]=b.map_image(ax,results['map_'+method],results['tracks'],results['norm_'+method],b.START,b.END,factor=13)
        ax.set(xlim=(29.5,46.5),ylim=(.1,.42),yticks=[.1,.25,.4],xticks=[33,37,42,46],xticklabels=['09h','13h','18h','22h'])
        ax.tick_params(length=3,pad=4,labelbottom=row==1)
        if col==0:ax.set_ylabel('Position / L')
        for t,letters in local_features.items():
            ax.axvline(t,color='black',alpha=.17,ls=':',lw=.8)
            for letter in letters:
                j=linked.feature(results,t,letter);q=results['qnorm'][t,j];u=results['norm_'+method][t,j];color=linked.FEATURES[letter]['color']
                assert .1<=q<=.42 and .1<=u<=.42
                ax.plot([t,t],[q,u],color=color,lw=2,zorder=5)
                ax.plot(t,q,'x',color=color,ms=7,mew=1.7,zorder=7)
                offset=(-12,-3) if letter in ['A','E'] else (9,6)
                if letter=='A' and t in [34,35]:offset=(4,11)
                if letter=='D':offset=(-10,8)
                linked.mark(ax,t,u,letter,offset=offset,size=17)
        validations[method]['source_snapshot_frames']=FRAMES
        validations[method]['annotation_frames']=list(local_features)
        validations[method]['annotation_features']=local_features
    cb=fig.colorbar(ScalarMappable(norm=b.NORM,cmap=b.CM),cax=fig.add_axes([.36,.027,.38,.013]),orientation='horizontal',ticks=[-35,0,35])
    cb.ax.tick_params(labelsize=16,length=3,pad=4)
    fig.text(.345,.034,'MSLP anomaly [hPa]',fontsize=16,ha='right',va='center')
    visible=[o for o in fig.findobj(Text) if o.get_visible() and o.get_text().strip()]
    assert min(o.get_fontsize() for o in visible)>=16
    assert all(o.get_fontfamily()==['Arial'] and o.get_fontstyle()=='normal' for o in visible)
    examples=[]
    for t,l1,l2,method in [(33,'A','B','R5'),(37,'A','C','R1'),(42,'E','F','R2')]:
        i,j=linked.feature(results,t,l1),linked.feature(results,t,l2)
        sign=np.sign(results['qnorm'][t,i]-results['qnorm'][t,j])
        assert np.sign(results['norm_P'][t,i]-results['norm_P'][t,j])==-sign
        assert np.sign(results['norm_'+method][t,i]-results['norm_'+method][t,j])==sign
        examples.append(dict(frame=t,pair=[l1,l2],P_reverses=True,restored_by=method))
    for ext in ['png','svg','pdf']:fig.savefig(b.HERE/f'Anatol_event_threshold_preview.{ext}',dpi=230)
    plt.close(fig)
    b.dump(b.HERE/'teaser_layout.json',dict(figure_inches=[18,11.5],font='Arial regular/bold',minimum_font_size_pt=16,
        source_frames=FRAMES,threshold_methods=METHODS,geographic_correspondence=correspondence,verified_examples=examples,
        annotation_frames=FRAMES,annotation_features=LABELS,only_displayed_snapshot_features_annotated=True,
        B_absent_frames_verified=[34,35],C_first_frame=36,
        scope='744-hour overview above; five genuine source snapshots from the selected window in one row; four matched local threshold maps below.',
        selection=dict(frame_edges=[29.5,46.5],position_bounds=[.1,.42],overview_method='saved full-month R20',local_methods=METHODS),
        overview_crop_vs_R5_max_scalar_difference=overview_crop_difference,
        continuity='A continuous at f33..f37; B absent at f34/f35; C first appears at f36 and is shown at f37. No physical B-C identity claim.',
        source_and_numerical_results_unchanged=True,full_eight_threshold_version='Anatol_all_thresholds_geographic.png'))
    b.dump(b.HERE/'teaser_display_validation.json',validations)
    print('Figure-1 layout written: full sequence / five snapshots / P, R1, R2, R5; Arial >=16pt',flush=True)


if __name__=='__main__':render_teaser(*b.prepare())
