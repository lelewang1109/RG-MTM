"""Streaming native TTK extraction and compact feature export, full source grid."""
from pathlib import Path
from dataclasses import dataclass
import argparse,json,subprocess,time
import numpy as np
from experiments.volume3d.prepare import ROOT,sha256
from experiments.volume3d.prepare_tangaroa_paper import OUT as DATA,save

TREES=DATA/'ttk_p10'
BINARY=ROOT/'tmp/volume3d/native-build/rgmtm_ttk_volume'
SHAPE=(120,180,300)
BOUNDS=np.array([-.35,.65,-.3,.3,-.5,-.3])
SPACING=(BOUNDS[1::2]-BOUNDS[::2])/(np.array(SHAPE[::-1])-1)
SAMPLE_MEASURE=float(np.prod(SPACING))


@dataclass
class Arc:
    id:int
    parent:int
    child:int
    regular_vertices:np.ndarray


class Frame:
    """Memory-mapped augmented join tree, without Python lists for 6.48M samples."""
    def __init__(self,index,directory=TREES):
        self.timestep=index;self.prefix=Path(directory)/f'frame_{index:03d}'
        self.metadata=json.loads(Path(str(self.prefix)+'.json').read_text());self.root=self.metadata['root']
        self.values=np.memmap(str(self.prefix)+'.values.f32',dtype='<f4',mode='r')
        self.owner=np.memmap(str(self.prefix)+'.owner.i32',dtype='<i4',mode='r')
        self.offsets=np.memmap(str(self.prefix)+'.offsets.i32',dtype='<i4',mode='r')
        self.regular=np.memmap(str(self.prefix)+'.regular.i32',dtype='<i4',mode='r')
        self.node_ids=np.fromfile(str(self.prefix)+'.nodes.i32',dtype='<i4')
        self.arc_rows=np.fromfile(str(self.prefix)+'.arcs.i32',dtype='<i4').reshape(-1,4)
        self.children={int(i):[] for i in self.node_ids};self.arcs={};self._arc_for_child={}
        for a,(up,down,start,count) in enumerate(self.arc_rows):
            self.children[int(up)].append(int(down))
            # Native order is high -> low for TMTM. Shared RG filling expects low -> high.
            arc=Arc(a,int(up),int(down),self.regular[start:start+count][::-1])
            self.arcs[a]=arc;self._arc_for_child[int(down)]=arc
        self.children={k:tuple(sorted(v)) for k,v in self.children.items()}
        self.leaves=tuple(sorted(k for k,v in self.children.items() if not v))
        self.domain_min=BOUNDS[::2];self.domain_max=BOUNDS[1::2]

    def parent(self,node):return None if node==self.root else self._arc_for_child[int(node)].parent
    def arc_for_child(self,node):return self._arc_for_child[int(node)]
    def leaf_feature_vertices(self,leaf):return np.r_[leaf,self.arc_for_child(leaf).regular_vertices]
    def lca(self,a,b):
        ancestors=set()
        while a is not None:ancestors.add(a);a=self.parent(a)
        while b not in ancestors:b=self.parent(b)
        return b
    def nonleaf_path_to_ancestor(self,leaf,ancestor):
        result=[];node=self.parent(leaf)
        while node is not None and node!=ancestor:
            arc=self.arc_for_child(node);result.append(arc);node=arc.parent
        if node!=ancestor:raise ValueError('requested node is not an ancestor')
        return result
    def hierarchy(self):
        rank={v:i for i,v in enumerate(self.leaves)}
        def visit(v):
            c=self.children[v]
            if not c:return rank[v]
            if len(c)==1:return visit(c[0])
            return tuple(visit(u) for u in c)
        return visit(self.root)
    def lca_values(self):
        return np.array([[self.values[self.lca(a,b)] for b in self.leaves] for a in self.leaves],float)


def coordinates(vertices):
    z,y,x=np.unravel_index(vertices,SHAPE)
    return np.c_[x,y,z]*SPACING+BOUNDS[::2]


def features(frame):
    centers=[];counts=[];boundary=[]
    for leaf in frame.leaves:
        ids=frame.leaf_feature_vertices(leaf);z,y,x=np.unravel_index(ids,SHAPE)
        centers.append(np.array([x.mean(),y.mean(),z.mean()])*SPACING+BOUNDS[::2]);counts.append(len(ids))
        boundary.append(bool(np.any((x==0)|(x==299)|(y==0)|(y==179)|(z==0)|(z==119))))
    return dict(index=frame.timestep,leaf_ids=list(frame.leaves),leaf_arcs=[frame.arc_for_child(v).id for v in frame.leaves],
        centers=np.array(centers).tolist(),extrema=coordinates(np.array(frame.leaves)).tolist(),
        support_counts=counts,volumes=(np.array(counts)*SAMPLE_MEASURE).tolist(),boundary=boundary,
        hierarchy=frame.hierarchy(),source_lca_values=frame.lca_values().tolist(),
        children={str(k):list(v) for k,v in frame.children.items()},root=frame.root,
        source_node_values={str(k):float(frame.values[k]) for k in frame.children})


def extract(indices=range(201),threads=6,wait_for_inputs=True):
    TREES.mkdir(parents=True,exist_ok=True)
    protocol=dict(ttk_source_version='0.9.9',ttk_source_archive_sha256=sha256(ROOT/'tmp/volume3d/ttk-0.9.9.tar.gz'),
        native_binary_sha256=sha256(BINARY),native_source_sha256=sha256(Path(__file__).with_name('native')/'main.cpp'),
        driver_source_sha256=sha256(__file__),absolute_persistence_threshold=.2,persistence_percent=10.,
        declared_scalar_range=[0.,2.],tree_kind='join',saddle_connectors=False,numerical_perturbation=False,
        grid_shape_xyz=[300,180,120],grid_adjacency='TTK implicit regular-grid triangulation, nonperiodic',
        vtk_or_inviwo_used=False,version_note='public author workflow reimplemented with pinned TTK legacy simplification; not a byte-identical author binary or unpublished scalar export')
    save(TREES/'protocol.json',protocol);records=[]
    suffixes=['.json','.pairs.csv','.nodes.i32','.arcs.i32','.regular.i32','.owner.i32','.values.f32','.offsets.i32']
    for index in indices:
        src=DATA/f'scalar_{index:03d}.npy';prefix=TREES/f'frame_{index:03d}';record_path=Path(str(prefix)+'.manifest.json')
        while not src.exists():
            if not wait_for_inputs:raise FileNotFoundError(src)
            time.sleep(2)
        valid=False
        if record_path.exists():
            old=json.loads(record_path.read_text())
            valid=(old['native_binary_sha256']==protocol['native_binary_sha256'] and old['input_sha256']==sha256(src)
                and all((TREES/name).exists() and sha256(TREES/name)==digest for name,digest in old['files'].items()))
        if not valid:
            with Path(str(prefix)+'.log').open('w') as log:
                subprocess.run([str(BINARY),str(src),str(prefix),'300','180','120','.2',str(threads),'0'],stdout=log,stderr=subprocess.STDOUT,check=True)
        frame=Frame(index);feature=features(frame);feature_path=Path(str(prefix)+'.features.json');save(feature_path,feature)
        record=dict(index=index,input_sha256=sha256(src),native_binary_sha256=protocol['native_binary_sha256'],
            files={prefix.name+s:sha256(Path(str(prefix)+s)) for s in suffixes},feature_sha256=sha256(feature_path),
            samples=frame.metadata['samples'],nodes=frame.metadata['nodes'],leaves=len(frame.leaves))
        save(record_path,record);records.append(record)
        save(TREES/'status.json',dict(status='running',complete_indices=[r['index'] for r in records]))
        print('TTK paper input',index,frame.metadata['nodes'],'nodes',len(frame.leaves),'leaves',flush=True)
    save(TREES/'manifest.json',dict(protocol=protocol,records=records))
    save(TREES/'status.json',dict(status='complete',complete_indices=[r['index'] for r in records]))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--threads',type=int,default=6)
    parser.add_argument('--indices',type=int,nargs='+');args=parser.parse_args();extract(range(201) if args.indices is None else args.indices,args.threads)
