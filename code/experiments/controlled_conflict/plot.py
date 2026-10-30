"""Plot N4 using saved records only; scientific vector figures plus PNG previews."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
CODE = Path(__file__).resolve().parents[2]
RES = CODE / 'results/controlled_conflict20261030'
FIG = CODE.parent / 'paper/pvis2027/figures'
BLUE, ORANGE, GREEN, GREY = '#0072B2', '#D55E00', '#009E73', '#707A82'
plt.rcParams.update({'font.family':'Arial', 'font.size':7, 'axes.titlesize':7,
    'axes.labelsize':7, 'xtick.labelsize':6, 'ytick.labelsize':6, 'pdf.fonttype':42,
    'axes.spines.top':False, 'axes.spines.right':False, 'axes.linewidth':.6,
    'legend.frameon':False, 'legend.fontsize':5.8})


def save(fig, stem):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(FIG / f'{stem}.{ext}', dpi=240, bbox_inches='tight', pad_inches=.025)
    plt.close(fig)


def decorate(ax):
    ax.grid(color='#E4E8EB', lw=.45); ax.set_axisbelow(True)


def main():
    rows = json.loads((RES / 'overlap.json').read_text())
    budgets = json.loads((RES / 'budget.json').read_text())
    point = [r for r in rows if r['width']==0]
    wide = [r for r in rows if r['width']==.06]
    x = np.array([r['overlap'] for r in wide])*100
    fig, axes = plt.subplots(1, 2, figsize=(3.45, 1.62))
    fig.subplots_adjust(left=.13, right=.99, bottom=.24, top=.83, wspace=.39)
    ax = axes[0]
    ax.plot(x, [r['exact_tau']*100 for r in wide], color=BLUE, lw=1.1, label='Interval optimum')
    ax.plot(x, [r['nu']*100 for r in point], '--', color=ORANGE, lw=1., label=r'Point bound $\nu^*$')
    ax.plot(x[::4], [r['width_lower']*100 for r in wide][::4], 'o', mfc='white', mec=BLUE, mew=.6, ms=2.8, label='Width bound')
    ax.set(xlabel='Signed overlap d (%)', ylabel='Displacement (%)', title='(a) Increasing conflict', xlim=(-12,30), ylim=(-.5,18))
    ax.set_xticks([-10,0,10,20,30]); ax.set_yticks([0,5,10,15]); ax.axvline(0, color=GREY, lw=.5, ls=':')
    ax.legend(loc='upper left', handlelength=1.4, borderaxespad=.3, labelspacing=.2)
    decorate(ax)
    ax = axes[1]
    b = [r for r in budgets if r['inner_level']==.4]
    ax.step([r['epsilon']*100 for r in b], [r['tau']*100 for r in b], where='post', color=BLUE, lw=1.2)
    ax.plot([0, 29.5, 30,45], [14,14,0,0], 'o', color=BLUE, ms=2.8)
    ax.axvline(30, color=GREY, lw=.6, ls=':')
    ax.text(27, 8.2, r'$2\varepsilon=h$', ha='right', fontsize=6)
    ax.text(3, 3.5, 'd = 24%, h = 60%', fontsize=5.8, color=GREY)
    ax.set(xlabel=r'Merge budget $\varepsilon$ (%)', title='(b) Releasing the conflict', xlim=(0,45), ylim=(-.5,18))
    ax.set_xticks([0,15,30,45]); ax.set_yticks([0,5,10,15]); decorate(ax)
    save(fig, 'fig_controlled_conflict')

    fig, axes = plt.subplots(1,3,figsize=(7.,2.25))
    fig.subplots_adjust(left=.06,right=.99,bottom=.21,top=.85,wspace=.35)
    ax=axes[0]
    for x0, pair, col in [(.28,[.14,.42],BLUE),(.74,[.6,.88],ORANGE)]:
        ax.plot([x0,x0],[.82,.6],color=col,lw=1)
        ax.plot([pair[0],pair[0],pair[1],pair[1]],[.4,.6,.6,.4],color=col,lw=1)
    ax.plot([.28,.28,.74,.74],[.82,.95,.95,.82], color=GREY,lw=1)
    ax.text(.51,.97,'1',ha='center',fontsize=6); ax.text(.28,.65,'0.4',ha='center',fontsize=6)
    ax.text(.74,.65,'0.4',ha='center',fontsize=6)
    for xi, lab in zip([.14,.42,.6,.88],['A','B','C','D']): ax.text(xi,.35,lab,ha='center',fontsize=6)
    for y,d in [(.19,-.10),(.04,.12),(-.11,.24)]:
        ax.plot([.2,.5],[y+.035]*2,color=BLUE,lw=2)
        ax.plot([.5-d,.8-d],[y]*2,color=ORANGE,lw=2)
        ax.text(1.15,y+.01,f'd={d*100:.0f}%',fontsize=5.5,ha='right')
    ax.text(.2,-.24,'Blue: {A,B}; orange: {C,D}',fontsize=6)
    ax.set(xlim=(0,1.17),ylim=(-.3,1.05),title='(a) Fixed tree; moving reference hulls');ax.axis('off')
    ax=axes[1]
    for width,col in [(.03,GREEN),(.06,BLUE),(.09,ORANGE)]:
        r=[r for r in rows if r['width']==width]
        ax.plot(x,[v['hierarchy_excess']*100 for v in r],color=col,lw=1,label=f'W = {width*100:.0f}%')
    ax.set(xlabel='Signed overlap d (%)',ylabel=r'Hierarchy excess $H_{\rm hier}$ (%)',title='(b) Beyond free interval packing',xlim=(-12,30))
    ax.legend(loc='upper left');decorate(ax)
    ax=axes[2]
    for inner,col,ls in [(.8,GREEN,'-'),(.6,BLUE,'--'),(.4,ORANGE,'-.'),(.2,GREY,':')]:
        b=[r for r in budgets if r['inner_level']==inner]
        ax.step([r['epsilon']*100 for r in b],[r['tau']*100 for r in b],where='post',color=col,ls=ls,lw=1.2,label=f'h = {(1-inner)*100:.0f}%')
    ax.set(xlabel=r'Merge budget $\varepsilon$ (%)',ylabel='Displacement (%)',title='(c) Different parent gaps',xlim=(0,45),ylim=(-.5,19))
    ax.legend(loc='upper right',ncol=2,fontsize=5.8,columnspacing=.6,handlelength=1.3);decorate(ax)
    save(fig, 'fig_controlled_conflict_supp')


if __name__=='__main__':main()
