from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
O=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'Times New Roman','font.size':9,'svg.fonttype':'none','mathtext.fontset':'stix'})
fig,ax=plt.subplots(figsize=(3.35,3.05));fig.subplots_adjust(left=.04,right=.96,top=.98,bottom=.03);ax.set(xlim=(-.08,1.08),ylim=(-.1,1.12));ax.axis('off')
def fmt(k):
 return '$'+k[0]+'_'+k[1:].translate(str.maketrans('₀₁₂₃','0123'))+'$' if len(k)>1 else '$'+k+'$'
nodes={'R':(.50,1.05),'r₂':(.50,.97),'r₁':(.50,.89),'S₀':(.50,.81),'u₂':(.50,.66),'u₁':(.50,.58),'S₁':(.50,.50),'a₃':(.13,.66),'a₂':(.13,.58),'a₁':(.13,.50),'A':(.13,.42),'d₃':(.87,.66),'d₂':(.87,.58),'d₁':(.87,.50),'D':(.87,.42),'c₁':(.38,.38),'C':(.38,.30),'b₁':(.62,.38),'B':(.62,.30)}
chains=[['R','r₂','r₁','S₀'],['S₀','a₃','a₂','a₁','A'],['S₀','u₂','u₁','S₁'],['S₀','d₃','d₂','d₁','D'],['S₁','c₁','C'],['S₁','b₁','B']];colors={k:('#0068d8' if k.startswith('a') or k=='A' else '#ef7d00' if k.startswith('b') or k=='B' else '#00a45c' if k.startswith('c') or k=='C' else '#ae29bb' if k.startswith('d') or k=='D' else '#929da3') for k in nodes}
for chain in chains:
 for a,b in zip(chain,chain[1:]):
  x,y=nodes[a];xx,yy=nodes[b];ax.plot([x,x,xx,xx],[y,(y+yy)/2,(y+yy)/2,yy],color='#27313a',lw=.6,zorder=1)
order=['R','r₂','a₃','a₁','A','a₂','S₀','u₂','c₁','C','S₁','u₁','b₁','B','d₃','d₁','D','d₂','r₁'];positions={k:i/18 for i,k in enumerate(order)}
for k,(x,y) in nodes.items():
 ax.plot(x,y,'D' if k in ['R','S₀','S₁','A','B','C','D'] else 'o',ms=4,mfc=colors[k],mec='#26313a',mew=.45,zorder=3);ax.text(x+.025,y,fmt(k),va='center',color=colors[k])
 # Diagram mapping connectors, retained as illustration rather than a physical projection.
 ax.annotate('',(positions[k],.10),(x,y-.012),arrowprops=dict(arrowstyle='->',lw=.25,color=colors[k],alpha=.45),zorder=0)
ax.plot([-.025,1.025],[.10,.10],color='#222222',lw=.7)
for i,k in enumerate(order):
 x=positions[k];ax.plot(x,.10,'D' if k in ['R','S₀','S₁','A','B','C','D'] else 'o',ms=3.5,mfc=colors[k],mec='#26313a',mew=.4);ax.text(x,.035 if i%2==0 else -.055,fmt(k),ha='center',va='center',color=colors[k])
ax.text(.02,1.105,'Merge tree',ha='left');ax.text(.02,.18,'1D layout',ha='left')
for ext in ['pdf','png','svg']:fig.savefig(O/f'anchor_node_mapping.{ext}',dpi=600,bbox_inches='tight',pad_inches=.02)
