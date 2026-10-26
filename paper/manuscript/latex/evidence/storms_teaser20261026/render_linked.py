"""Arial, large-type geographic correspondence for the Anatol event preview."""
from pathlib import Path
import csv, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from scipy.interpolate import RegularGridInterpolator
from netCDF4 import Dataset
import build_preview as b

FRAMES=[33,36,42,54,66,90]
# Letters refer to the same saved computational feature, never display order.
FEATURES={
    'A':dict(track=7,color='#0072B2'),
    'B':dict(track=5,color='#D55E00'),
    'C':dict(track=8,color='#009E73'),
    'D':dict(track=9,color='#CC79A7'),
    'E':dict(track=10,color='#A50F15'),
    'F':dict(track=0,color='#555555'),
}
SELECTED={33:['A','B'],36:['A','C'],42:['D','E','F'],54:['E'],66:['E'],90:['E']}


def raw(a):
    path=b.HERE/'geographic_snapshots.npz'
    if path.exists():
        saved=np.load(path)
        if np.array_equal(saved['frames'],FRAMES):return saved
    with Dataset(b.SOURCE) as ds:
        fields=[]
        for t in FRAMES:
            i=int(a['source_indices'][t])
            fields.append(np.asarray(ds['msl'][i],float)/100-np.asarray(ds['msl'][i-96:i+96],float).mean(0)/100)
        np.savez_compressed(path,frames=FRAMES,fields=fields,lat=np.asarray(ds['latitude'][:]),lon=np.asarray(ds['longitude'][:]))
    return np.load(path)


def feature(results,t,letter):
    j=np.flatnonzero(results['tracks'][t]==FEATURES[letter]['track'])
    assert len(j)==1,(t,letter)
    return int(j[0])


def mark(ax,x,y,letter,offset=(8,8),size=17):
    color=FEATURES[letter]['color']
    ax.plot(x,y,'o',ms=7,mec='white',mew=2,mfc=color,zorder=12)
    ax.annotate(letter,xy=(x,y),xytext=offset,textcoords='offset points',
        fontsize=size,fontweight='bold',color='black',ha='right' if offset[0]<0 else 'left',
        va='center',bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=.3),zorder=13)


def render_geographic(a,old,results,metrics):
    for name in ['Arial.ttf','Arial Bold.ttf']:
        font_manager.fontManager.addfont('/System/Library/Fonts/Supplemental/'+name)
    assert Path(font_manager.findfont(font_manager.FontProperties(family='Arial'),fallback_to_default=False)).name=='Arial.ttf'
    plt.rcParams.update({'font.family':'Arial','font.size':16,'font.style':'normal',
        'axes.titlesize':18,'axes.labelsize':16,'xtick.labelsize':16,'ytick.labelsize':16,
        'text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black',
        'axes.edgecolor':'black','axes.linewidth':.8,'axes.spines.top':True,'axes.spines.right':True,
        'svg.fonttype':'none','savefig.facecolor':'white','mathtext.fontset':'custom',
        'mathtext.rm':'Arial','mathtext.bf':'Arial:bold'})
    fig=plt.figure(figsize=(18,18),facecolor='white')
    fig.text(.06,.978,'(a) December context',fontsize=20,weight='bold')
    overview=fig.add_axes([.29,.956,.65,.032])
    validations={}
    validations['overview']=b.map_image(overview,old['mapR'],old['tracks'],old['normR'],0,743,factor=3)
    overview.add_patch(Rectangle((b.START-.5,0),b.END-b.START+1,1,fill=False,edgecolor=b.ACCENT,lw=2))
    overview.set(yticks=[],xticks=[0,336,743],xticklabels=['1 Dec','15 Dec','31 Dec'])
    overview.tick_params(length=3,pad=4)
    overview.annotate('Anatol',xy=(60,.5),xytext=(155,.65),fontsize=16,color='black',
        arrowprops=dict(arrowstyle='->',color='black',lw=1),va='center',
        bbox=dict(fc='white',ec='none',alpha=.9,pad=1))

    fig.text(.06,.911,'(b) Geographic locations and event evolution · E: Anatol-associated low',fontsize=20,weight='bold')
    source=raw(a)
    co=np.cos(np.deg2rad(52.5));radius=6371.
    extent=np.r_[radius*co*np.deg2rad([-30,40]),radius*np.sin(np.deg2rad([30,75]))/co]
    ratio=np.ptp(extent[:2])/np.ptp(extent[2:])
    geo=b.Era5Geo(dict(lon=(-30,40),lat=(30,75)),a['coords'])
    geo.factor=1.;geo.offx=geo.bx0;geo.offy=geo.by0
    X,Y=np.meshgrid(np.linspace(extent[0],extent[1],600),np.linspace(extent[2],extent[3],round(600/ratio)))
    points=np.stack([np.rad2deg(np.arcsin(Y*co/radius)),np.rad2deg(X/radius/co)],-1)
    points[...,0]=np.clip(points[...,0],source['lat'].min(),source['lat'].max())
    points[...,1]=np.clip(points[...,1],source['lon'].min(),source['lon'].max())
    gap=.017;width=(.88-5*gap)/6;height=width/ratio;bottom=.735
    records=[]
    for index,t in enumerate(FRAMES):
        ax=fig.add_axes([.06+index*(width+gap),bottom,width,height])
        image=RegularGridInterpolator((source['lat'],source['lon']),source['fields'][index])(points)
        ax.imshow(image,origin='lower',extent=extent,cmap=b.CM,norm=b.NORM,interpolation='bilinear')
        geo.coastlines(ax,b.CODE/'data/geo/ne_110m_coastline.geojson',lw=.65,color='#263238',alpha=1)
        xt=radius*co*np.deg2rad([-20,20]);yt=radius*np.sin(np.deg2rad([35,55,75]))/co
        ax.set(xlim=extent[:2],ylim=extent[2:],aspect='equal',xticks=xt,xticklabels=['20°W','20°E'],yticks=yt)
        ax.set_yticklabels(['35°N','55°N','75°N'] if index==0 else [])
        ax.tick_params(length=2,pad=4)
        # Direction is constant and uses the same geographic projection as the minima.
        org=np.array([extent[0]+.68*np.ptp(extent[:2]),extent[2]+.11*np.ptp(extent[2:])])
        vec=results['direction']*650
        ax.annotate('',xy=org+vec,xytext=org,arrowprops=dict(arrowstyle='->',color='black',lw=1.3))
        ax.text(*(org+vec+[65,10]),'d',fontsize=16)
        date=str(results['dates'][t]);stamp=f"{int(date[8:10])} Dec {date[11:13]}h"
        ax.set_title(f'{index+1}   {stamp}',loc='left',pad=8,fontsize=16,weight='bold')
        for letter in SELECTED[t]:
            j=feature(results,t,letter);lon,lat=results['lonlat'][t,j];x,y=geo.xy(lon,lat)
            leaf=int(results['leaf'][t,j])
            assert np.allclose(a['lonlat'][leaf],[lon,lat],atol=1e-12,rtol=0)
            projected=(a['coords'][leaf]@results['direction']-results['geometry'][0])/results['geometry'][1]
            assert abs(projected-results['qnorm'][t,j])<1e-12
            offset=(7,16) if letter in ['A','D'] else (7,8)
            mark(ax,x,y,letter,offset)
            record=dict(frame=t,date=str(results['dates'][t]),letter=letter,track=FEATURES[letter]['track'],
                longitude=float(lon),latitude=float(lat),reference=float(results['qnorm'][t,j]),
                P=float(results['norm_P'][t,j]),R5=float(results['norm_R5'][t,j]))
            records.append(record)
    fig.text(.06,.699,'P reverses A/B at 09h and E/F at 18h; R5 restores their geographic order along d.',fontsize=16)

    fig.text(.06,.669,'(c) Event map and the geographic features above',fontsize=20,weight='bold')
    fig.text(.94,.669,'R, κ = 5%',fontsize=18,ha='right')
    event=fig.add_axes([.08,.563,.86,.076])
    validations['event_R5']=b.map_image(event,results['map_R5'],results['tracks'],results['norm_R5'],b.START,b.END,factor=13)
    event.add_patch(Rectangle((29.5,.1),17,.32,fill=False,edgecolor=b.ACCENT,lw=2,zorder=9))
    for index,t in enumerate(FRAMES):
        event.axvline(t,ls=':',lw=1,color='black',alpha=.4)
        event.text(t,1.06,str(index+1),transform=event.get_xaxis_transform(),ha='center',fontsize=16)
        for letter in SELECTED[t]:
            j=feature(results,t,letter)
            event.plot(t,results['norm_R5'][t,j],'o',mfc=FEATURES[letter]['color'],mec='white',mew=.6,ms=5,zorder=10)
    j=feature(results,66,'E')
    event.annotate('E',xy=(66,results['norm_R5'][66,j]),xytext=(10,12),textcoords='offset points',fontsize=18,weight='bold',color='black',
        bbox=dict(fc='white',ec='none',pad=1,alpha=.9))
    event.set(yticks=[0,.5,1],xticks=[24,48,72,96],xticklabels=['2 Dec 00h','3 Dec 00h','4 Dec 00h','5 Dec 00h'],ylabel='Position / L')
    event.tick_params(length=3,pad=4)

    fig.text(.06,.510,'(d) Threshold comparison in the orange box · 2 Dec, 06–22h UTC',fontsize=20,weight='bold')
    fig.text(.06,.486,'Same letters and colours as the geographic maps.   × reference   ● output   | displacement',fontsize=16)
    witness=[33,36,37,41,42]
    local_features={33:['A','B'],36:['A','C'],37:['A','C'],41:['D','E','F'],42:['D','E','F']}
    for index,method in enumerate(b.METHODS):
        row,col=divmod(index,2);bottom=.382-row*.103
        ax=fig.add_axes([.08+col*.465,bottom,.395,.075])
        title='P' if method=='P' else f'R, κ = {method[1:]}%'
        ax.set_title(title,loc='left',fontsize=18,weight='bold',pad=8)
        # Crop the same full-window display reconstruction, rather than fitting
        # or interpolating an independent local map.
        validations[method]=b.map_image(ax,results['map_'+method],results['tracks'],results['norm_'+method],b.START,b.END,factor=13)
        ax.set(xlim=(29.5,46.5),ylim=(.1,.42),xticks=[33,36,42,46],xticklabels=['09h','12h','18h','22h'],yticks=[.1,.25,.4])
        if col==0:ax.set_ylabel('Position / L',fontsize=16)
        ax.tick_params(length=2,pad=4,labelbottom=row==3)
        for t in witness:
            ax.axvline(t,color='#555555',alpha=.2,ls=':',lw=.8)
            for letter in local_features[t]:
                j=feature(results,t,letter);q=results['qnorm'][t,j];u=results['norm_'+method][t,j];color=FEATURES[letter]['color']
                assert .1<=q<=.42 and .1<=u<=.42
                ax.plot([t,t],[q,u],color=color,lw=1.8,zorder=5)
                ax.plot(t,q,'x',color=color,ms=7 if t in SELECTED else 5,mew=1.7,zorder=7)
                offset=(-11,-4) if letter in ['A','E'] else (8,5)
                if letter=='D':offset=(-9,7)
                if t in SELECTED:
                    mark(ax,t,u,letter,offset=offset,size=16)
                else:
                    ax.plot(t,u,'o',ms=5,mfc=color,mec='white',mew=1,zorder=12)
        validations[method]['geographic_link']=dict(source_snapshots=[33,36,42],position_bounds=[.1,.42],time_bounds=[29.5,46.5],
            feature_letters={k:v['track'] for k,v in FEATURES.items()},scalar_range_unchanged=True)
    cb=fig.colorbar(ScalarMappable(norm=b.NORM,cmap=b.CM),cax=fig.add_axes([.36,.023,.38,.012]),orientation='horizontal',ticks=[-35,0,35])
    cb.ax.tick_params(labelsize=16,length=3,pad=4)
    fig.text(.345,.029,'MSLP anomaly [hPa]',fontsize=16,ha='right',va='center')

    # Check actual visible text objects, not just rcParams defaults.
    text_objects=[o for o in fig.findobj(Text) if o.get_visible() and o.get_text().strip()]
    assert min(o.get_fontsize() for o in text_objects)>=16
    assert all(o.get_fontfamily()==['Arial'] and o.get_fontstyle()=='normal' for o in text_objects)
    reversals=[]
    for t,l1,l2 in [(33,'A','B'),(42,'E','F')]:
        i,j=feature(results,t,l1),feature(results,t,l2)
        reference_sign=np.sign(results['qnorm'][t,i]-results['qnorm'][t,j])
        assert np.sign(results['norm_P'][t,i]-results['norm_P'][t,j])==-reference_sign
        assert np.sign(results['norm_R5'][t,i]-results['norm_R5'][t,j])==reference_sign
        reversals.append(dict(frame=t,pair=[l1,l2],P_reverses_reference=True,R5_restores_reference=True))
    style=dict(font='Arial regular/bold',minimum_font_size_pt=min(o.get_fontsize() for o in text_objects),
        visible_text_objects=len(text_objects),source_frames=FRAMES,feature_correspondence=records,
        source_fields_unchanged=True,scalar_limits_hPa=[-35,35],numerical_results_recomputed=False,
        source_coordinates_and_reference_projection_independently_verified=True,
        order_reversals_verified=reversals,
        full_event_background='R5, explicitly labelled; the eight local panels compare all saved P/R settings',
        reason_for_layout='One shared full-event locator replaces eight repeated full maps, allowing readable geographic labels and threshold panels.')
    for ext in ['png','svg']:fig.savefig(b.HERE/f'Anatol_event_threshold_preview.{ext}',dpi=220)
    plt.close(fig)
    b.dump(b.HERE/'geographic_correspondence.json',style)
    b.dump(b.HERE/'display_validation.json',validations)
    with (b.HERE/'geographic_correspondence.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    print('Updated geographic preview; Arial minimum 16 pt',flush=True)


if __name__=='__main__':render_geographic(*b.prepare())
