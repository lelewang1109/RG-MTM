"""Paper-inspired presentation of frozen, independently verified Tangaroa results.

This module changes display only. RG parameters are not persistence thresholds.
Every scalar-map source is hash-checked against the numerical evidence.
"""
from copy import deepcopy
from itertools import product
from pathlib import Path
import argparse,hashlib,inspect,json,os
import numpy as np
from scipy.ndimage import map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.font_manager import FontProperties,findSystemFonts
from experiments.volume3d.run_paper import ROOT,OUT,DATA
from experiments.volume3d.prepare import sha256

BOUNDS=np.array([-.35,.65,-.3,.3,-.5,-.3])

def chinese_font():
    explicit=os.environ.get('RGMTM_CJK_FONT')
    if explicit:
        if not Path(explicit).is_file():raise FileNotFoundError(explicit)
        return FontProperties(fname=explicit)
    candidates=[Path('/System/Library/Fonts/Supplemental/Songti.ttc')]
    candidates += [Path(p) for p in sorted(findSystemFonts())
        if any(name in Path(p).name.lower() for name in ['notoserifcjk','notosanscjk','simsun','simhei','songti'])]
    return next((FontProperties(fname=p) for p in candidates if p.is_file()),None)


def read(p):return json.loads(Path(p).read_text())


def parallel_dvr(field,bounds,settings,width=800):
    """Orthographic display, author view orientation/TF, entire source domain.

    Parallel rays improve the legibility of the long thin domain in the paper's
    narrow panels. This is a declared presentation camera, not the saved camera.
    """
    camera=settings['camera'];height=round(width/camera['aspect']);aspect=width/height
    forward=np.array(camera['look_to'])-camera['look_from'];forward/=np.linalg.norm(forward)
    right=np.cross(forward,camera['up']);right/=np.linalg.norm(right);up=np.cross(right,forward)
    lo=bounds[::2];hi=bounds[1::2];span=hi-lo;center=(hi+lo)/2
    corners=np.array(list(product(*zip(lo,hi))));relative=corners-center
    half=max(np.max(abs(relative@right))/aspect,np.max(abs(relative@up)))/.96
    yy,xx=np.meshgrid((np.arange(height)+.5)*2/height-1,(np.arange(width)+.5)*2/width-1,indexing='ij')
    origins=(center-2*np.linalg.norm(span)*forward+xx[...,None]*half*aspect*right+yy[...,None]*half*up).reshape(-1,3)
    with np.errstate(divide='ignore',invalid='ignore'):
        t0=(lo-origins)/forward;t1=(hi-origins)/forward
    entry=np.maximum(np.minimum(t0,t1).max(1),0);exit=np.maximum(t0,t1).min(1)
    valid=np.flatnonzero(exit>entry);image=np.ones((len(origins),3),np.float32)
    points=np.asarray(settings['transfer_function_points']);positions=points[:,0]
    dimensions=np.array(field.shape[::-1],float)
    dt=1/(settings['author_sampling_rate']*np.linalg.norm(forward/span*(dimensions-1)))
    correction=150*np.linalg.norm(forward/span)*dt
    for start in range(0,len(valid),512):
        ix=valid[start:start+512];count=np.ceil((exit[ix]-entry[ix])/dt).astype(int)
        k=np.arange(count.max());t=entry[ix,None]+(k[None,:]+.5)*dt
        xyz=origins[ix,None,:]+t[...,None]*forward
        ijk=(xyz-lo)/span*(dimensions-1)
        sample=map_coordinates(field,np.moveaxis(ijk[...,::-1],-1,0),order=1,mode='nearest',prefilter=False)/2
        rgba=np.stack([np.interp(sample,positions,points[:,c]) for c in range(1,5)],axis=-1)
        opacity=1-np.maximum(1-rgba[...,3],0)**correction
        opacity[k[None,:]>=count[:,None]]=0
        trans=np.cumprod(np.concatenate([np.ones((len(ix),1)),1-opacity],axis=1),axis=1)
        rgb=np.sum(rgba[...,:3]*(opacity*trans[:,:-1])[...,None],axis=1)+trans[:,-1,None]
        image[ix]=np.clip(rgb,0,1)
    projected=np.c_[(relative@right)/(half*aspect),(relative@up)/half]
    return image.reshape(height,width,3),corners,projected


def fit_author_camera(original):
    """Keep the author's closer-view orientation/FOV; fit all eight corners."""
    forward=np.array(original['look_to'])-original['look_from'];forward/=np.linalg.norm(forward)
    right=np.cross(forward,original['up']);right/=np.linalg.norm(right);up=np.cross(right,forward)
    corners=np.array(list(product(*zip(BOUNDS[::2],BOUNDS[1::2]))));target=(BOUNDS[::2]+BOUNDS[1::2])/2
    relative=corners-target;half=np.tan(np.deg2rad(original['fov'])/2)
    # All projected corners fit inside 96% of the viewport; no volume crop.
    distance=max(np.max(abs(relative@right)/(.96*half*original['aspect'])-relative@forward),
                 np.max(abs(relative@up)/(.96*half)-relative@forward))
    camera={**original,'look_from':(target-distance*forward).tolist(),'look_to':target.tolist()}
    return camera,original


def build(directory=OUT,language='auto'):
    out=Path(directory);dest=out/'paper_style';dest.mkdir(exist_ok=True)
    verification=read(out/'verification.json');assert verification['status']=='passed'
    assert verification['manifest_sha256']==sha256(out/'manifest.json')
    numerical=read(out/'manifest.json')
    for name,digest in numerical['numerical_evidence_sha256'].items():assert sha256(out/name)==digest,name
    rows=read(out/'frame_metrics.json');lookup={(r['method'],r['index']):r for r in rows}
    indices=numerical['indices'];assert indices==list(range(201))
    settings_path=ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json'
    settings=read(settings_path);tf=np.array(settings['transfer_function_points'])
    cmap=LinearSegmentedColormap.from_list('author purple-white-orange',[(v[0],tuple(v[1:4])) for v in tf],N=2048)
    camera_path=Path(__file__).with_name('inputs')/'tangaroa_closer_camera.json'
    camera_record=read(camera_path)
    camera,original_camera=fit_author_camera(camera_record['camera']);volume_settings=deepcopy(settings);volume_settings['camera']=camera
    font=chinese_font() if language!='en' else None
    if language=='zh' and font is None:raise ValueError('Chinese font unavailable: set RGMTM_CJK_FONT or use --language en')
    chinese=language=='zh' or (language=='auto' and font is not None)
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
        'font.size':12,'mathtext.fontset':'stix','svg.fonttype':'path','axes.linewidth':1.1})
    consumed={};generated=[];sampling={};maps={}
    def save(fig,name):
        for ext in ['png','svg','pdf']:
            path=dest/f'{name}.{ext}';fig.savefig(path,dpi=240,facecolor='white');generated.append(path)
        plt.close(fig)
    methods=['RG-MTM-P','RG-MTM-R 0.02','RG-MTM-R 0.2','RG-MTM-R 1','TMTM']
    # Display at fixed normalized coordinates, using actual saved samples.
    # The cropped TMTM view uses the author's exact endpoint exclusions/stride.
    zoom=[]
    for name in methods:
        columns=[];details=[]
        for index in indices:
            row=lookup[name,index];path=ROOT/row['full_array'];digest=sha256(path)
            assert digest==row['full_array_sha256'],path
            consumed[row['full_array']]=digest
            array=np.load(path,mmap_mode='r');grid=np.linspace(0,len(array)-1,4096)
            columns.append(np.interp(grid,np.arange(len(array)),array).astype(np.float32))
            if name=='TMTM':
                first=2592000;stop=len(array)-2592000;stride=317
                selected=array[first:stop:stride];assert len(selected)==4089
                zoom.append(np.array(selected));details.append(dict(index=index,start=first,stop=stop,stride=stride,rows=len(selected)))
        maps[name]=np.array(columns).T;sampling[name]=details or dict(rows=4096,coordinate='uniform normalized full saved domain',interpolation='linear')
        print('Display samples checked:',name,flush=True)
    zoom=np.array(zoom).T
    np.savez_compressed(dest/'display_samples.npz',**maps,TMTM_middle20=zoom)
    generated.append(dest/'display_samples.npz')
    # Cache is bound to source/settings/code hashes, so rerendering typography is cheap.
    volume_key=dict(sources={f'scalar_{i:03d}.npy':sha256(DATA/f'scalar_{i:03d}.npy') for i in [0,100,200]},
        settings=volume_settings,projection='orthographic full-domain display',
        renderer_sha256=hashlib.sha256(inspect.getsource(parallel_dvr).encode()).hexdigest(),width=800)
    cache=dest/'volume_cache.npz';cache_meta=dest/'volume_cache.json'
    cache_ok=cache.exists() and cache_meta.exists() and read(cache_meta).get('inputs')==volume_key and read(cache_meta).get('sha256')==sha256(cache)
    if not cache_ok:
        images=[]
        for index in [0,100,200]:
            print('Rendering original-grid volume:',index,flush=True)
            scalar_path=DATA/f'scalar_{index:03d}.npy';metadata=read(DATA/f'scalar_{index:03d}.json')
            field=np.load(scalar_path,mmap_mode='r');assert field.shape==(120,180,300)
            # The independently verified preparation metadata binds the scalar array.
            assert metadata['scalar_sha256']==sha256(scalar_path)
            img,corners,projected=parallel_dvr(field,BOUNDS,volume_settings,width=800);images.append(img)
        np.savez_compressed(cache,images=images,corners=corners,projected=projected)
        cache_meta.write_text(json.dumps(dict(inputs=volume_key,sha256=sha256(cache)),indent=2)+'\n')
    generated.extend([cache,cache_meta]);cached=np.load(cache);images=cached['images'];corners=cached['corners'];projected=cached['projected']
    # Rounded pixel height slightly changes aspect; retain a 3% safety margin.
    for p in projected:assert np.max(np.abs(p))<=.97,'volume viewport crops the domain'
    translations={
        '(b) 三维体渲染':'(b) Volume rendering',
        '(a) 固定持久性简化下的 RG-MTM 时间图':'(a) RG-MTM at fixed persistence',
        'Tangaroa · 300 × 180 × 120 · 201 帧；持久性简化统一为 10%（绝对阈值 0.2）':'Tangaroa: 300 x 180 x 120, 201 frames; persistence 10% (absolute 0.2)',
        'κ 表示层次放松资格参数，与论文图 15 的四档持久性阈值不同。纵轴为全序列固定参考轴，四图使用同一完整视窗。':'Kappa denotes relaxation eligibility, not persistence. All RG panels use the same full reference domain.',
        '(a) TMTM 视窗对照与 RG-MTM':'(a) TMTM display windows and RG-MTM',
        'Tangaroa · 同一批 201 帧、同一 TTK 简化标量与 join tree；持久性 10%':'Tangaroa: same 201 frames, TTK-simplified scalars and join trees; persistence 10%',
        'TMTM 右上图仅显示中间 20% 的线性化空间；RG 两图保持同一完整物理参考视窗。放大显示不改变输入或评价。':'Upper right: middle 20% of TMTM linearization. RG uses its full reference domain. Display zoom does not change evaluation.'}
    def ctext(fig,x,y,text,size=12,**kwargs):
        if chinese:fig.text(x,y,text,fontproperties=font,fontsize=size,**kwargs)
        else:fig.text(x,y,translations[text],fontsize=size,**kwargs)
    def map_panel(fig,rect,array,title,ylabel='reference space',bottom=False,extent=(0,1)):
        ax=fig.add_axes(rect)
        ax.imshow(array,origin='lower',aspect='auto',extent=(-.5,200.5,*extent),vmin=0,vmax=2,cmap=cmap,
            interpolation='bilinear',interpolation_stage='data',resample=True)
        ax.set_xlim(-.5,200.5);ax.set_ylim(*extent);ax.set_yticks([]);ax.set_xticks([0,50,100,150]);ax.tick_params(length=3,pad=3,labelbottom=bottom)
        for s in ax.spines.values():s.set_visible(True)
        ax.text(.035,.92,title,transform=ax.transAxes,ha='left',va='top',fontsize=12.5,
            bbox=dict(facecolor='white',edgecolor='none',alpha=.78,pad=2))
        ax.set_ylabel(ylabel,labelpad=9,fontsize=12)
        # Arrows lie just outside the rectangular scalar-image frame.
        ax.annotate('',xy=(1.005,-.045),xytext=(-.002,-.045),xycoords='axes fraction',
            arrowprops=dict(arrowstyle='-|>',lw=.85,color='black'),annotation_clip=False)
        ax.annotate('',xy=(-.028,1.02),xytext=(-.028,-.005),xycoords='axes fraction',
            arrowprops=dict(arrowstyle='-|>',lw=.85,color='black'),annotation_clip=False)
        if bottom:ax.text(1.005,-.18,'$t$',transform=ax.transAxes,ha='right',fontsize=15)
        return ax
    def volume_panels(fig):
        height=.25*16/(camera['aspect']*5.7)
        for img,index,y in zip(images,[0,100,200],[.675,.42,.165]):
            ax=fig.add_axes([.688,y,.25,height]);ax.imshow(img,origin='lower',extent=(-1,1,-1,1),aspect='auto')
            for a in range(8):
                for b in range(a+1,8):
                    if np.count_nonzero(corners[a]!=corners[b])==1:
                        ax.plot(projected[[a,b],0],projected[[a,b],1],c='.8',lw=.35)
            ax.set_xlim(-1,1);ax.set_ylim(-1,1);ax.set_xticks([]);ax.set_yticks([])
            for spine in ax.spines.values():spine.set_visible(True)
            ax.text(.025,.045,f'$t={index}$',transform=ax.transAxes,fontsize=12,bbox=dict(facecolor='white',edgecolor='none',alpha=.75,pad=.5))
        cb=fig.colorbar(ScalarMappable(norm=Normalize(0,2),cmap=cmap),cax=fig.add_axes([.956,.34,.012,.38]),ticks=[0,2])
        cb.ax.tick_params(length=3,labelsize=12)
        ctext(fig,.812,.065,'(b) 三维体渲染',16,ha='center')
    rects=[[.05,.565,.285,.32],[.377,.565,.285,.32],[.05,.165,.285,.32],[.377,.165,.285,.32]]
    fig=plt.figure(figsize=(16,5.7))
    labels=['RG-MTM-P','RG-MTM-R, $\\kappa=2\\%$','RG-MTM-R, $\\kappa=20\\%$','RG-MTM-R, $\\kappa=100\\%$']
    for j,(name,label) in enumerate(zip(methods[:4],labels)):map_panel(fig,rects[j],maps[name],label,bottom=j>=2)
    volume_panels(fig)
    ctext(fig,.356,.065,'(a) 固定持久性简化下的 RG-MTM 时间图',16,ha='center')
    ctext(fig,.05,.955,'Tangaroa · 300 × 180 × 120 · 201 帧；持久性简化统一为 10%（绝对阈值 0.2）',13)
    ctext(fig,.05,.015,'κ 表示层次放松资格参数，与论文图 15 的四档持久性阈值不同。纵轴为全序列固定参考轴，四图使用同一完整视窗。',10)
    save(fig,'rgmtm_paper_style')
    fig=plt.figure(figsize=(16,5.7))
    panels=[(maps['TMTM'],'TMTM: full domain','linearized space',(0,1)),
        (zoom,'TMTM: middle 20%','linearized space',(.4,.6)),
        (maps['RG-MTM-P'],'RG-MTM-P','reference space',(0,1)),
        (maps['RG-MTM-R 0.2'],'RG-MTM-R, $\\kappa=20\\%$','reference space',(0,1))]
    for j,(array,label,ylabel,extent) in enumerate(panels):map_panel(fig,rects[j],array,label,ylabel,j>=2,extent)
    volume_panels(fig)
    ctext(fig,.356,.065,'(a) TMTM 视窗对照与 RG-MTM',16,ha='center')
    ctext(fig,.05,.955,'Tangaroa · 同一批 201 帧、同一 TTK 简化标量与 join tree；持久性 10%',13)
    ctext(fig,.05,.015,'TMTM 右上图仅显示中间 20% 的线性化空间；RG 两图保持同一完整物理参考视窗。放大显示不改变输入或评价。',10)
    save(fig,'tmtm_rgmtm_paper_style')
    notes='''# 论文风格的 Tangaroa 三维实验图

完整数值结果及独立核验见[实验报告](../REPORT.md)。本目录只改变图形展示，不修改数值实验。

- [RG-MTM 四面板与三维体渲染](rgmtm_paper_style.png)：左侧 2×2 为 P、R κ=2%／20%／100%，右侧为官方序列第 0／100／200 帧。
- [TMTM 视窗对照与 RG-MTM](tmtm_rgmtm_paper_style.png)：显示 TMTM 全域及作者工作空间采用的中间 20% 视窗，下面是 RG-P 和 R κ=20%。
- 每图提供 PNG、矢量 SVG 和 PDF。图中文字、坐标轴及标尺为矢量，标量图和 DVR 为图像。

## 与论文图 15 的对应关系

沿用四面板时间图、三张横向体渲染、白底黑框、箭头坐标轴，以及作者紫—白—橙传递函数和 [0,2] 共用标尺。
没有叠加极值散点，没有对数值场另做平滑、时间重排或删帧。显示插值为线性／双线性，颜色映射范围固定。

论文的四个面板比较持久性阈值 0.15%／0.5%／2%／10%；本次方法图全部固定在 10%，比较 RG-P 与三档 RG-R。
**κ 不能标成持久性阈值，资格参数也不是输出 NMLE 的硬上界。** 未运行的另外三档持久性结果不作为已有实验展示。

TMTM 的作者工作空间每端排除 2,592,000 个样本（各 40%），对剩余空间每隔 317 个样本取一个，得到 4089 行。
右上放大图落实相同显示窗口。RG 纵轴是固定三维参考投影的域比例，采用完整域；不能把同样的 40% 裁切强加到不同物理语义的纵轴上。
这些显示取样可能漏掉窄于显示像素的叶支持；所有指标与独立核验始终使用完整保存数组。

右侧展示 **TTK 简化前、按作者近零替换和 [0,2] 截断后的原分辨率速度模长**，对应作者独立体渲染工作空间的标量阶段。
布局使用其 TTK 简化后标量；[简化后布局输入体渲染](../actual_3d_inputs.png) 单独保留以便核对。
沿用作者 `sequence_tangaroa_volRendering_closer.inv` 中的观察方向、上方向、宽高比以及已核对的传递函数。
为接近参考图的窄幅框图并清楚展示完整计算域，组合图采用正交投影，按八个角点适配视窗；原始透视相机与本图显示设置保存在清单中，没有裁掉三维输入。
使用 CPU 三线性采样、前向透明度合成；省略未公开的船体 STL 和原工作空间的光照，因此不声称与原图像素一致。

## 证据边界

数据为官方 300×180×120×201 全序列；全部标量值经过独立重算。作者未公开最终 Magnitude 导出及原二进制环境。
本组 10% 简化后节点数为 36–186，论文表 1 为 50–186；差异尚未定位，不能称为作者最终派生树的精确复现。
正式方法主比较采用 TMTM 与 RG-MTM，不强行加入第二篇没有原文三维案例的 ST-MTM。

复现命令（项目根目录）：

```sh
PYTHONPATH=src:. python -m experiments.volume3d.paper_style
```

相机元数据随代码提供，不依赖临时目录。`--language auto` 在有中文字体时使用中文，否则使用英文；
也可指定 `--language en`，或设置 `RGMTM_CJK_FONT` 指向本机中文字体后使用 `--language zh`。

`visual_manifest.json` 绑定绘图源码、全部读取的地图、三维标量、相机来源、数值清单及生成文件的 SHA256。
'''
    (dest/'README.md').write_text(notes);generated.append(dest/'README.md')
    manifest=dict(presentation_only=True,source_sha256=sha256(__file__),numerical_manifest_sha256=sha256(out/'manifest.json'),
        verification_sha256=sha256(out/'verification.json'),frame_metrics_sha256=sha256(out/'frame_metrics.json'),
        author_settings_sha256=sha256(settings_path),camera_workspace_sha256=camera_record['source_sha256'],camera_config_sha256=sha256(camera_path),
        language='zh' if chinese else 'en',
        original_closer_camera=original_camera,orientation_camera=camera,projection='orthographic',camera_fit='center domain; author view orientation/up/aspect; parallel rays; fit all eight corners inside 96% viewport',
        volume_stage='original grid, author near-zero replacement and [0,2] clip; before TTK simplification',
        volume_inputs=volume_key['sources'],map_inputs_sha256=consumed,sampling=sampling,
        map_display_interpolation='bilinear scalar display, no extrema overlay; no scientific field or metric changes',
        files={p.name:sha256(p) for p in generated})
    (dest/'visual_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print('Figures completed:',dest,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=OUT)
    p.add_argument('--language',choices=['auto','zh','en'],default='auto');a=p.parse_args();build(a.out,a.language)
