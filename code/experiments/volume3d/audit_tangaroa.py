"""Audit Tangaroa against TMTM's public workspaces, before TTK simplification.

Full-resolution source snapshots 0/100/200 are kept separate from the old
12-frame coarse split-tree pilot. The CPU DVR is a reference visualization,
not a claim of pixel-identical Inviwo rendering or a full TMTM reproduction.
"""
from pathlib import Path
from itertools import product
import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zlib

import numpy as np
from scipy.ndimage import map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.cm import ScalarMappable

from experiments.volume3d.prepare import ROOT,sha256,read_amira_vector
from experiments.volume3d.prepare_tangaroa_official import DATA

COMMIT='2c75a10ed2cd55177a25ff751e0c0a8261200717'
PREFIX='modules/mergetreemaps/data/'
INDICES=(0,100,200)
OUT=ROOT/'results/volume3d/tangaroa-input-audit-20261018'


def dump(path,value):
    Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def author_settings(repo,out):
    def get(path):
        return subprocess.check_output(['git','show',COMMIT+':'+path],cwd=repo)
    paths=[PREFIX+'workspaces/sequence_tangaroa.inv',PREFIX+'workspaces/sequence_tangaroa_volRendering.inv',
        PREFIX+'scripts/iterateTimestepsTangaroa.py','modules/tools/src/volumesequenceclampvaluerange.cpp',
        'modules/mergetreemaps/src/processors/topologicalsimplificationforsequence.cpp']
    content={p:get(p) for p in paths}
    main=ET.fromstring(content[paths[0]]);vis=ET.fromstring(content[paths[1]])
    def processor(root,identifier):return next(n for n in root.findall('.//Processor') if n.get('identifier')==identifier)
    def value(node,identifier,tag='value'):
        p=node.find('.//Property[@identifier="'+identifier+'"]/'+tag)
        return None if p is None else p.attrib
    clamp=processor(main,'VolumeSequenceClampValueRange2')
    assert value(clamp,'targetRange')=={'x':'0','y':'2'}
    assert value(clamp,'createMask')['content']=='1'
    assert float(value(clamp,'maskOutEps')['content'])==1e-6
    assert float(value(clamp,'maskOutNewValue')['content'])==1
    assert value(processor(main,'ContourTreesForSequence'),'treeType','selectedIdentifier')['content']=='join'
    connections={(n.get('src'),n.get('dst')) for n in main.findall('.//Connection')}
    expected=[('VolumeSequenceSource2.data','VolumeSequenceClampValueRange2.inport'),
        ('VolumeSequenceClampValueRange2.outport','VolumeToTriangulationForSequence.volumes'),
        ('VolumeToTriangulationForSequence.outport','TopologicalSimplificationForSequence.scalarsIn'),
        ('TopologicalSimplificationForSequence.scalarsOut','ContourTreesForSequence.scalars')]
    assert set(expected)<=connections
    ray=processor(vis,'VolumeRaycaster')
    points=sorted([[float(p.find('pos').get('content')),*[float(p.find('rgba').get(k)) for k in ['x','y','z','w']]]
        for p in ray.findall('.//Property[@identifier="transferFunction"]/TransferFunction/Points/Point')])
    camera=ray.find('.//Property[@identifier="camera"]/Camera')
    def vector(tag):return [float(camera.find(tag).get(k)) for k in ['x','y','z']]
    settings=dict(repository='https://github.com/Wiebke/TemporalMergeTreeMaps',commit=COMMIT,
        sources={p:hashlib.sha256(b).hexdigest() for p,b in content.items()},
        scalar='velocity magnitude',tree_type='join',near_zero_value=0.,near_zero_epsilon=1e-6,near_zero_replacement=1.,
        scalar_clip=[0.,2.],visualization_workspace_epsilon=1e-9,
        connected_scalar_pipeline=[list(pair) for pair in expected],
        saved_raw_range=[float(value(clamp,'dataRange')[k]) for k in ['x','y']],
        saved_main_absolute_simplification_threshold=float(value(processor(main,'TopologicalSimplificationForSequence'),'threshold')['content']),
        paper_persistence_percent=[.15,.5,2.,10.],nominal_absolute_thresholds=[.003,.01,.04,.2],
        threshold_note='paper percentages of the declared [0,2] range; saved workspace explicitly contains only threshold 0.2, not all four final run outputs',
        camera=dict(look_from=vector('lookFrom'),look_to=vector('lookTo'),up=vector('lookUp'),
            fov=float(camera.find('fov').get('content')),aspect=float(camera.find('aspectRatio').get('content'))),
        transfer_function_points=points,author_sampling_rate=float(value(ray,'samplingRate')['content']),
        missing_external_mesh='E:/Data/Tangaroa/tangaroa.stl; not included in the official Amira archive',
        model_note='main workspace mask epsilon 1e-6; standalone volume rendering workspace epsilon 1e-9. Audit reports whether this changes any source samples.')
    dump(out/'author_settings.json',settings);return settings


def write_report(out,result,settings,render):
    base='https://github.com/Wiebke/TemporalMergeTreeMaps/blob/'+COMMIT+'/'
    lines=['# Tangaroa 输入复核与旧实验更正（2026-10-18）','',
        '**核对结论：官方原始数据来源有充分一致性证据；此前 12 帧试跑的实际标量处理和树类型与作者公开工作空间不一致，不能作为论文图 15 的同输入复现或方法优劣证据。**','',
        '复核第一篇论文表 1、图 15，以及作者固定提交的工作空间、预处理器 C++ 和简化器源码。'
        '作者未公开其最终 Magnitude/*.dat 导出文件及校验和，因此不声称与这些未取得文件逐字节相同。','',
        '| 项目 | 论文／作者公开工作空间 | 此前官方 12 帧试跑 |','|---|---|---|',
        '| 原始来源 | FAU Tangaroa，300×180×120×201 三分量速度 | 相同官方来源，仅使用前 12 帧 |',
        '| 标量 | 速度模长 | 速度模长 |',
        '| 近零处理 | 主工作空间将 abs(v)<1e-6 替换为 1 | 未替换 |',
        '| 数值截断 | 真正修改标量到 [0,2]，并设置 data/value range | 未截断 |',
        '| 树 | join tree（跟踪低值分支） | split tree（高值分支） |',
        '| 空间网格 | 作者 Tangaroa 主处理链没有降采样或高斯平滑 | 抗混叠后降为 30×18×12，再 sigma=1 平滑 |',
        '| 时间 | 全部 201 帧；图 15(b) 为编号 0、100、200 | 编号 0–11，对应物理时间 0.00–0.11 |',
        '| 拓扑简化 | TTK 修改标量场；0.15%、0.5%、2%、10% 持久性阈值 | 复杂度驱动平滑；仅另做树上删叶诊断 |',
        '| 三维图 | 体渲染，带非单调透明度传递函数 | 处理后数值最高 5% 的散点图 |','',
        '图 15 的四个持久性百分比与 RG 层次放松资格参数不是同一个量。按声明的 [0,2] 范围，'
        '四个名义绝对阈值为 0.003、0.01、0.04、0.2；公开主工作空间明确保存的是 0.2，'
        '不据此假定已取得全部四个最终简化输出。论文最强简化下仍有 50–186 个 supernodes，'
        '也不能与旧试跑每帧至多 6 叶的规模混为一谈。','',
        '## 本次实际完成的原分辨率核对','',
        '从官方 Amira 压缩包选取图 15(b) 的三个指定成员，逐一校验成员长度、CRC32、SHA256、'
        'Amira 空间头和轴序，在完整源网格计算 float32 速度模长，再按公开主工作空间作近零替换和截断。'
        '处理结果保存在本地 data/real/Tangaroa-FAU/paper_protocol_speed_index_*.npz。'
        '**这些是 TTK 简化前输入，不是已完成的合并树地图。**','',
        '| 论文帧号 | 官方文件 | 原始速度模长范围 | 替换为 1 的样本数 | >2 截断数 | 两工作空间 epsilon 导致的不同样本数 |',
        '|---:|---|---:|---:|---:|---:|']
    for r in result['records']:
        lines.append(f"| {r['paper_index']} | {r['filename']} | {r['speed_range_float32']} | {r['masked_samples_main']} | {r['clipped_high_samples']} | {r['mask_workspace_difference_samples']} |")
    lines+=['',f"第 0 帧速度模长最大值为 {result['records'][0]['speed_range_float32'][1]}，"
        f"与作者工作空间保存的原始最大值 {settings['saved_raw_range'][1]} 完全一致。"
        '这是标量通道和版本的一项强一致性证据，不能代替未公开导出文件的 SHA256。',
        '物理范围直接读取源头：x=[-0.35,0.65]、y=[-0.3,0.3]、z=[-0.5,-0.3]；'
        '内存轴序 Z,Y,X,component，x 连续。三个成员均为 120×180×300×3，未裁剪空间域、未平滑、未降采样。','',
        '## 体渲染检查','']
    if render:lines+=['![原分辨率三帧输入体渲染核对](original_resolution_volume_audit.png)','']
    lines+=['使用作者独立体渲染工作空间的相机、传递函数节点和采样率 8；用 CPU 三线性采样、'
        '前向透明度合成产生输入检查图。作者体渲染工作空间的近零 epsilon 为 1e-9，主地图工作空间为 1e-6，'
        '差异样本数已在上表实际检查。绘图沿用主地图预处理结果。',
        'CPU 参考渲染没有重现原 Blinn–Phong 光照。官方速度压缩包也不含作者路径中的 tangaroa.stl 船体网格，'
        '本图明确省略船体，不用拟造网格补齐。透明度步长修正采用归一化纹理距离约定，'
        '尚未核对作者编译版本的着色器。因此不能声称像素级复现，外观相似也不能替代输入校验。','',
        '## 对旧结论的处理','',
        '旧 tangaroa-official 目录的数组和指标保留为可追溯的粗网格 split-tree 试跑；'
        '其 NROE 0.287%→0、三维运动错误 14/14→2/14 等数字，**停止用于支持论文 Tangaroa 同输入比较**。'
        '旧源插值核验只证明代码忠实实现了旧协议，不能证明旧协议符合作者流程。'
        'ECNR VTM 备份同样不能替代论文速度模长输入。已同步更正结果索引、旧报告和写作说明。','',
        '尚未完成全部 201 帧的同设置 TTK 简化、join-tree 提取与完整 RG-MTM 布局，也未得到作者最终标量导出校验和。'
        '因此当前结论是“已纠正输入协议并完成指定三帧的原分辨率标量核对”，不能写为“论文图 15 或全序列实验已复现”。','',
        '## 证据与复核入口','',
        '- [逐帧源文件、处理计数与哈希](input_audit.json)',
        '- [作者参数与源码哈希](author_settings.json)',
        '- [生成文件校验和](artifact_hashes.json)',
        f'- [作者 Tangaroa 主工作空间]({base+PREFIX}workspaces/sequence_tangaroa.inv)',
        f'- [作者体渲染工作空间]({base+PREFIX}workspaces/sequence_tangaroa_volRendering.inv)',
        f'- [实际修改标量的预处理器]({base}modules/tools/src/volumesequenceclampvaluerange.cpp)',
        '- [FAU 官方数据页](https://www.vc.tf.fau.de/publications/datasets/)',
        '- [旧粗网格试跑报告](../tangaroa-official/REPORT.md)','']
    (out/'REPORT.md').write_text('\n'.join(lines))


def reference_dvr(field,bounds,settings,width=800):
    """Perspective front-to-back alpha compositing on the original grid.

    Uses exported camera and TF nodes. No scalar smoothing/downsampling.
    Unlit reference: the original Blinn-Phong lighting and external STL are
    deliberately not imitated with invented geometry or fitted parameters.
    """
    camera=settings['camera'];height=round(width/camera['aspect']);aspect=width/height
    eye=np.asarray(camera['look_from']);target=np.asarray(camera['look_to']);up=np.asarray(camera['up'])
    forward=target-eye;forward/=np.linalg.norm(forward)
    right=np.cross(forward,up);right/=np.linalg.norm(right);up=np.cross(right,forward)
    half=np.tan(np.deg2rad(camera['fov'])/2)
    yy,xx=np.meshgrid((np.arange(height)+.5)*2/height-1,(np.arange(width)+.5)*2/width-1,indexing='ij')
    rays=forward+xx[...,None]*half*aspect*right+yy[...,None]*half*up
    rays/=np.linalg.norm(rays,axis=-1,keepdims=True);rays=rays.reshape(-1,3)
    lo=bounds[::2];hi=bounds[1::2];span=hi-lo
    t0=(lo-eye)/rays;t1=(hi-eye)/rays
    entry=np.maximum(np.minimum(t0,t1).max(1),0);exit=np.maximum(t0,t1).min(1)
    valid=np.flatnonzero(exit>entry);image=np.ones((len(rays),3),np.float32)
    points=np.asarray(settings['transfer_function_points']);positions=points[:,0]
    dimensions=np.array(field.shape[::-1],float)
    # Normalized texture-distance alpha correction; 8 samples per source voxel
    # along the ray, matching the author's declared sampling rate.
    sampling=settings['author_sampling_rate']
    for start in range(0,len(valid),512):
        ix=valid[start:start+512];direction=rays[ix]
        rate=np.linalg.norm(direction/span*(dimensions-1),axis=1)
        dt=1/(sampling*rate);count=np.ceil((exit[ix]-entry[ix])/dt).astype(int)
        k=np.arange(count.max());t=entry[ix,None]+(k[None,:]+.5)*dt[:,None]
        xyz=eye+t[...,None]*direction[:,None,:]
        ijk=(xyz-lo)/span*(dimensions-1)
        sample=map_coordinates(field,np.moveaxis(ijk[...,::-1],-1,0),order=1,mode='nearest',prefilter=False)/2
        rgba=np.stack([np.interp(sample,positions,points[:,c]) for c in range(1,5)],axis=-1)
        correction=150*np.linalg.norm(direction/span,axis=1)*dt
        opacity=1-np.maximum(1-rgba[...,3],0)**correction[:,None]
        opacity[k[None,:]>=count[:,None]]=0
        trans=np.cumprod(np.concatenate([np.ones((len(ix),1)),1-opacity],axis=1),axis=1)
        rgb=np.sum(rgba[...,:3]*(opacity*trans[:,:-1])[...,None],axis=1)+trans[:,-1,None]
        image[ix]=np.clip(rgb,0,1)
    corners=np.array(list(product(*zip(lo,hi))));relative=corners-eye
    depth=relative@forward
    projected=np.c_[(relative@right)/(depth*half*aspect),(relative@up)/(depth*half)]
    return image.reshape(height,width,3),corners,projected


def audit(out,repo,render=True):
    out.mkdir(parents=True,exist_ok=True);settings=author_settings(repo,out)
    inventory=json.loads((DATA/'archive_inventory.json').read_text())
    members={r['name']:r for r in inventory['members']}
    assert sum(name.endswith('.am') for name in members)==201
    records=[];images=[];bounds=None
    for index in INDICES:
        name=f'tangaroa-{index*.01:.2f}.am';path=DATA/name
        item=members[name];payload=path.read_bytes()
        assert len(payload)==item['size'] and zlib.crc32(payload)==item['crc32']
        velocity,bounds=read_amira_vector(path);assert velocity.shape==(120,180,300,3)
        np.testing.assert_allclose(bounds,[-.35,.65,-.3,.3,-.5,-.3],rtol=0,atol=1e-12)
        # VectorMagnitude and exported scalar volumes use float32. Arithmetic
        # is not claimed bit-identical to the author's original GPU shader.
        speed=np.linalg.norm(velocity,axis=-1).astype(np.float32);del velocity
        mask_main=np.abs(speed)<settings['near_zero_epsilon']
        mask_vis=np.abs(speed)<settings['visualization_workspace_epsilon']
        corrected=np.clip(np.where(mask_main,1.,speed),0.,2.).astype(np.float32)
        target=DATA/f'paper_protocol_speed_index_{index:03d}.npz'
        np.savez_compressed(target,field=corrected,bounds_xyz=bounds,index=index,source_time=index*.01,
            tree_kind='join',ttk_simplification_applied=False,spatial_smoothing_applied=False,spatial_resampling_applied=False)
        row=dict(paper_index=index,source_time=index*.01,filename=name,source_sha256=sha256(path),source_crc32=item['crc32'],
            source_shape_zyxc=list((*corrected.shape,3)),scalar_shape_zyx=list(corrected.shape),bounds_xyz=bounds.tolist(),
            speed_range_float32=[float(speed.min()),float(speed.max())],corrected_range=[float(corrected.min()),float(corrected.max())],
            masked_samples_main=int(mask_main.sum()),masked_samples_rendering=int(mask_vis.sum()),
            mask_workspace_difference_samples=int(np.count_nonzero(mask_main!=mask_vis)),clipped_high_samples=int((speed>2).sum()),
            corrected_input_sha256=sha256(target),corrected_field_sha256=hashlib.sha256(corrected.tobytes()).hexdigest())
        records.append(row);print('audited original-resolution frame',index,row,flush=True)
        if render:
            image,corners,projected=reference_dvr(corrected,bounds,settings);images.append(image)
            np.save(out/f'reference_dvr_{index:03d}.npy',image)
    result=dict(status='passed_input_audit',author_settings_sha256=sha256(out/'author_settings.json'),
        source_archive_members=201,checked_indices=list(INDICES),records=records,
        source_identity_scope='public official source, matching dimensions, times, physical bounds and recorded float32 maximum; author original exported scalar files/checksums are not published, so no byte-identical identity claim',
        corrected_input_scope='author public main-workspace scalar preprocessing before TTK; not TTK-simplified fields or a complete 201-frame layout',
        ttk_simplification_applied=False,complete_201_frame_rgmtm_reproduction=False,
        rendering=dict(mode='unlit CPU front-to-back direct volume rendering',camera_and_transfer_function='author standalone volume-rendering workspace',
            sampling_rate=settings['author_sampling_rate'],spatial_resampling=False,spatial_smoothing=False,
            original_blinn_phong_lighting_reproduced=False,external_vessel_stl_included=False),
        audit_source_sha256=sha256(Path(__file__)))
    dump(out/'input_audit.json',result)
    if render:
        fig,axes=plt.subplots(3,1,figsize=(10,13),layout='constrained')
        for ax,image,index in zip(axes,images,INDICES):
            ax.imshow(image,origin='lower',extent=(-1,1,-1,1),aspect=1/settings['camera']['aspect'])
            for i,a in enumerate(corners):
                for j in range(i+1,len(corners)):
                    if np.count_nonzero(a!=corners[j])==1:ax.plot(projected[[i,j],0],projected[[i,j],1],c='.45',lw=.5,alpha=.65)
            ax.set_xlim(-1,1);ax.set_ylim(-1,1);ax.axis('off');ax.set_title(f'Paper frame {index}  |  source time {index*.01:.2f}',loc='left',fontsize=11)
        tf=np.asarray(settings['transfer_function_points'])
        cmap=LinearSegmentedColormap.from_list('author_tangaroa',[(p,tuple(rgb)) for p,*rgb in tf[:,:4]],N=1024)
        fig.colorbar(ScalarMappable(norm=Normalize(0,2),cmap=cmap),ax=axes,shrink=.55,pad=.02,label='Velocity magnitude after author mask and clip')
        fig.suptitle('Original 300 x 180 x 120 scalar volumes | author transfer function and camera\nCPU input audit: no smoothing, no downsampling; vessel STL and original lighting omitted',fontsize=11)
        fig.savefig(out/'original_resolution_volume_audit.png',dpi=160,bbox_inches='tight')
        fig.savefig(out/'original_resolution_volume_audit.svg',bbox_inches='tight');plt.close(fig)
    write_report(out,result,settings,render)
    dump(out/'artifact_hashes.json',{p.name:sha256(p) for p in out.iterdir() if p.suffix in ['.json','.png','.svg','.npy','.md'] and p.name!='artifact_hashes.json'})
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--author-repo',type=Path,default=ROOT/'tmp/volume3d/TMTM-reference')
    parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args();audit(args.out,args.author_repo,not args.no_render)
