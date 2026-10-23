"""Compose frozen Tangaroa display evidence for the manuscript; no experiment rerun."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

PAPER=Path(__file__).resolve().parents[1]
ROOT=PAPER.parents[2]
SOURCE=ROOT/'code/results/volume3d/tangaroa-paper-p10-full201/paper_style'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
samples=np.load(SOURCE/'display_samples.npz')
cache=np.load(SOURCE/'volume_cache.npz')
settings=ROOT/'code/results/volume3d/tangaroa-input-audit-20261018/author_settings.json'
tf=np.asarray(json.loads(settings.read_text())['transfer_function_points'])
cmap=LinearSegmentedColormap.from_list('tangaroa_shared',[(v[0],tuple(v[1:4])) for v in tf],N=2048)
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
    'font.size':12,'mathtext.fontset':'stix','pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(14,5.3))
panels=[('TMTM','(a) TMTM'),('RG-MTM-P','(b) RG-MTM-P'),
        ('RG-MTM-R 0.02',r'(c) RG-MTM-R, $\kappa=2\%$'),
        ('RG-MTM-R 0.2',r'(d) RG-MTM-R, $\kappa=20\%$')]
for j,(key,title) in enumerate(panels):
    row,col=divmod(j,2)
    ax=fig.add_axes([.065+col*.315,.55-row*.43,.28,.34])
    ax.imshow(samples[key],origin='lower',aspect='auto',extent=(-.5,200.5,0,1),
              cmap=cmap,vmin=0,vmax=2,interpolation='bilinear',interpolation_stage='data')
    ax.set_title(title,loc='left',fontsize=12,pad=6)
    ax.set_xticks([0,50,100,150,200]);ax.tick_params(length=2,pad=3,labelbottom=row==1)
    ax.set_yticks([0,.5,1]);ax.set_ylabel('linearization' if key=='TMTM' else 'reference domain')
    if row==1:ax.set_xlabel('time step')
    for spine in ax.spines.values():spine.set_linewidth(.7)
corners=cache['corners'];projected=cache['projected']
for image,index,y in zip(cache['images'],[0,100,200],[.655,.377,.10]):
    ax=fig.add_axes([.715,y,.245,.24])
    ax.imshow(image,origin='lower',extent=(-1,1,-1,1),aspect='auto')
    for a in range(8):
        for b in range(a+1,8):
            if np.count_nonzero(corners[a]!=corners[b])==1:
                ax.plot(projected[[a,b],0],projected[[a,b],1],c='.78',lw=.35)
    ax.set_xlim(-1,1);ax.set_ylim(-1,1);ax.set_xticks([]);ax.set_yticks([])
    ax.text(.025,.07,f'$t={index}$',transform=ax.transAxes,fontsize=12)
    for spine in ax.spines.values():spine.set_linewidth(.7)
fig.text(.715,.94,'(e) Source magnitude',fontsize=12)
cb=fig.colorbar(ScalarMappable(norm=Normalize(0,2),cmap=cmap),cax=fig.add_axes([.976,.34,.012,.33]),ticks=[0,1,2])
cb.ax.tick_params(length=2,labelsize=10)
out=PAPER/'figures/rgmtm_tangaroa_existing_evidence'
for ext in ['pdf','png','svg']:fig.savefig(out.with_suffix('.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
plt.close(fig)
record={'scope':'Display composition from frozen arrays; no extraction, layout, metric, or volume-rendering rerun',
    'sources':{str(p.relative_to(ROOT)):sha(p) for p in [SOURCE/'display_samples.npz',SOURCE/'volume_cache.npz',settings]},
    'generator':str(Path(__file__).relative_to(ROOT)),
    'outputs':{ext:sha(out.with_suffix('.'+ext)) for ext in ['pdf','png','svg']},
    'panels':[k for k,_ in panels],'volume_stage':'near-zero replacement and clipping, before TTK simplification',
    'persistence_percent':10,'reference_extent_shared_for_RG':True,'full_domain_for_each_method':True}
out.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n')
print(out.with_suffix('.pdf'))
