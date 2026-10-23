"""Array-based TMTM Algorithm 1 and temporal overlap objective on full volumes.

Spatial overlap is counted on original source samples, using augmented arc
owners and subtree incidence matrices. No 6.48M-element Python sets are made.
For a genuine m-way saddle, the 1-D output needs m-1 separator samples: the
original scalar sample plus m-2 explicitly recorded virtual copies at the SAME
scalar level. Input volumes are unchanged. This is a documented nonbinary
extension of the paper's binary Algorithm 1, not an undisclosed scalar edit.
"""
import numpy as np


class CompactTMTM:
    def __init__(self,frame):
        self.frame=frame;self.children={k:[frame.arc_for_child(v).id for v in children] for k,children in frame.children.items()}
        self.down={a:arc.child for a,arc in frame.arcs.items()};self.up={a:arc.parent for a,arc in frame.arcs.items()}
        self.regular={a:arc.regular_vertices[::-1] for a,arc in frame.arcs.items()}
        self.sizes={};self.desc=np.eye(len(frame.arcs),dtype=np.int64)
        def size_node(v):
            children=self.children[v]
            return max(1,len(children)-1)+sum(size_arc(a) for a in children)
        def size_arc(a):
            n=len(self.regular[a])+size_node(self.down[a]);self.sizes[a]=n
            for child in self.children[self.down[a]]:self.desc[a]+=self.desc[child]
            return n
        self.length=size_node(frame.root)
        self.virtual_count=self.length-len(frame.values)
        root_arcs=self.children[frame.root]
        self.objective_arcs=[a for a in frame.arcs if not(len(root_arcs)==1 and a==root_arcs[0])]

    def layout(self,decisions=None,render=False):
        decisions=decisions or {};intervals=np.empty((len(self.sizes),2),int);positions={}
        output=np.full(self.length,np.nan,np.float32) if render else None
        sample_ids=np.full(self.length,-1,np.int32) if render else None
        assigned=np.zeros(len(self.frame.values),bool) if render else None
        copies=[]
        def place(vertex,position,virtual=False):
            if not virtual:
                positions[vertex]=position
                if render:
                    if assigned[vertex]:raise AssertionError('original TMTM sample assigned twice')
                    assigned[vertex]=True
            else:copies.append((vertex,position))
            if render:output[position]=self.frame.values[vertex];sample_ids[position]=vertex
        def arc(a,left,right):
            intervals[a]=(left,right);ids=self.regular[a];n=len(ids)
            if render and n:
                odd=np.arange(1,n,2);even=np.arange(0,n,2)
                output[left+odd//2]=self.frame.values[ids[odd]]
                output[right-even//2]=self.frame.values[ids[even]]
                sample_ids[left+odd//2]=ids[odd];sample_ids[right-even//2]=ids[even]
                if assigned[ids].any():raise AssertionError('overlapping TMTM arc samples')
                assigned[ids]=True
            node(self.down[a],left+n//2,right-(n+1)//2)
        def node(v,left,right):
            children=self.children[v]
            if decisions.get(v,False):children=children[::-1]
            if not children:place(v,left);assert left==right;return
            if len(children)==1:
                place(v,left);arc(children[0],left+1,right);return
            cursor=left
            for k,a in enumerate(children):
                end=cursor+self.sizes[a]-1;arc(a,cursor,end);cursor=end+1
                if k<len(children)-1:place(v,cursor,virtual=k>0);cursor+=1
            assert cursor==right+1
        node(self.frame.root,0,self.length-1)
        root_arcs=self.children[self.frame.root]
        if len(root_arcs)==1:intervals[root_arcs[0]]=(0,self.length-1)
        if render:
            assert assigned.all() and np.isfinite(output).all() and len(copies)==self.virtual_count
        return dict(intervals=intervals,positions=positions,values=output,sample_ids=sample_ids,virtual_copies=copies)

    def overlap(self,other):
        n=len(other.sizes)
        codes=self.frame.owner.astype(np.int64)*n+other.frame.owner
        counts=np.bincount(codes,minlength=len(self.sizes)*n).reshape(len(self.sizes),n)
        # Roots are not regular samples of any proper child subtree. The native
        # segmentation gives each one an arbitrary incident owner; exclude it.
        for vertex in set([self.frame.root,other.frame.root]):
            counts[self.frame.owner[vertex],other.frame.owner[vertex]]-=1
        return self.desc@counts@other.desc.T

    def align(self,fixed,fixed_layout):
        nd=fixed.overlap(self);decisions={};fa=np.array(fixed.objective_arcs,int)
        fixed_intervals=fixed_layout['intervals'][fa]
        def local(layout,children):
            target=[a for a in children if a in self.objective_arcs]
            if not target or not len(fa):return 0.
            intervals=layout['intervals'][target]
            overlap=np.maximum(0,np.minimum(fixed_intervals[:,None,1],intervals[None,:,1])-np.maximum(fixed_intervals[:,None,0],intervals[None,:,0])+1)
            return float(np.sum((nd[np.ix_(fa,target)]-overlap)**2))
        def visit(v):
            children=self.children[v]
            if len(children)>=2:
                decisions[v]=False;normal=local(self.layout(decisions),children)
                decisions[v]=True;reverse=local(self.layout(decisions),children)
                decisions[v]=reverse<normal
            chosen=children[::-1] if decisions.get(v,False) else children
            for a in chosen:visit(self.down[a])
        visit(self.frame.root)
        layout=self.layout(decisions)
        ta=np.array(self.objective_arcs,int)
        A=fixed_layout['intervals'][fa];B=layout['intervals'][ta]
        overlap=np.maximum(0,np.minimum(A[:,None,1],B[None,:,1])-np.maximum(A[:,None,0],B[None,:,0])+1)
        objective=float(np.sum((nd[np.ix_(fa,ta)]-overlap)**2))
        return decisions,layout,objective


def barrier_matrix(values,anchors):
    """Independent actual max on every inter-anchor span, linear in map length."""
    anchors=np.asarray(anchors,int);order=np.argsort(anchors,kind='stable');r=anchors[order]
    adjacent=np.array([np.max(values[a:b+1]) for a,b in zip(r[:-1],r[1:])])
    result=np.diag(np.asarray(values)[anchors]).astype(float)
    for a in range(len(order)-1):
        v=np.maximum.accumulate(adjacent[a:]);result[order[a],order[a+1:]]=v;result[order[a+1:],order[a]]=v
    return result
