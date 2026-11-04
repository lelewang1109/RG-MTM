// Original RG-MTM adapter to the BSD-licensed TTK 0.9.9 base library.
// No resampling, scalar smoothing, persistence pair deletion on a tree, or
// numerical ramp: TTK modifies the scalar field and returns its SoS offsets.
#include <PersistenceDiagram.h>
#include <TopologicalSimplification.h>
#include <FTMTree.h>
#include <Triangulation.h>
#include <OrderDisambiguation.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

template<class T> void write(const std::string &path,const std::vector<T> &v) {
  std::ofstream f(path,std::ios::binary);
  if(!f)throw std::runtime_error("cannot write "+path);
  f.write(reinterpret_cast<const char*>(v.data()),v.size()*sizeof(T));
  if(!f)throw std::runtime_error("incomplete write "+path);
}

int main(int argc,char **argv) {
  try {
    if(argc!=9)throw std::runtime_error("usage: input.npy prefix nx ny nz absolute_threshold threads saddle_connectors_0_or_1");
    const int nx=std::stoi(argv[3]),ny=std::stoi(argv[4]),nz=std::stoi(argv[5]);
    const int n=nx*ny*nz,threads=std::stoi(argv[7]);const double threshold=std::stod(argv[6]);
    const bool connectors=std::stoi(argv[8]);const std::string prefix=argv[2];
    std::ifstream f(argv[1],std::ios::binary);char magic[8];f.read(magic,8);
    if(std::string(magic,6)!=std::string("\x93NUMPY",6)||magic[6]!=1)throw std::runtime_error("expected NumPy v1 little-endian f4 C-order array");
    uint16_t size;f.read(reinterpret_cast<char*>(&size),2);std::string header(size,' ');f.read(&header[0],size);
    if(header.find("'<f4'")==std::string::npos||header.find("False")==std::string::npos)throw std::runtime_error("expected C-order float32 NPY");
    std::vector<float> values(n),simplified(n);f.read(reinterpret_cast<char*>(values.data()),n*sizeof(float));
    if(!f)throw std::runtime_error("incomplete scalar volume");
    for(float v:values)if(!std::isfinite(v))throw std::runtime_error("nonfinite scalar");
    const auto start=std::chrono::steady_clock::now();
    ttk::Triangulation tri;tri.setInputGrid(0,0,0,1,1,1,nx,ny,nz); // topology only; physical geometry stays in Python
    std::vector<ttk::SimplexId> offsets(n),outOffsets(n);ttk::preconditionOrderArray(n,values.data(),offsets.data());
    std::vector<ttk::PersistencePair> pairs;
    {
      ttk::PersistenceDiagram pd;pd.setThreadNumber(threads);pd.setDebugLevel(1);pd.setComputeSaddleConnectors(connectors);
      pd.preconditionTriangulation(&tri);
      if(pd.execute(pairs,values.data(),offsets.data(),&tri)<0)throw std::runtime_error("TTK persistence diagram failed");
    }
    std::vector<ttk::SimplexId> authorized;
    std::ofstream diagram(prefix+".pairs.csv");diagram<<"birth,death,persistence,pair_type\n";
    for(const auto &p:pairs) {
      diagram<<p.birth<<','<<p.death<<','<<p.persistence<<','<<p.pairType<<'\n';
      if(p.persistence>=threshold){authorized.push_back(p.birth);authorized.push_back(p.death);}
    }
    if(authorized.empty())throw std::runtime_error("threshold keeps no pair; inspect the protocol");
    ttk::TopologicalSimplification simplification;simplification.setThreadNumber(threads);simplification.setDebugLevel(1);
    simplification.setAddPerturbation(false);simplification.preconditionTriangulation(&tri);
    if(simplification.execute(values.data(),simplified.data(),authorized.data(),offsets.data(),outOffsets.data(),authorized.size(),tri)<0)
      throw std::runtime_error("TTK scalar simplification failed");
    const auto simplifiedAt=std::chrono::steady_clock::now();
    ttk::ftm::FTMTree tree;tree.setThreadNumber(threads);tree.setDebugLevel(1);
    tree.setTreeType(0); // TTK TreeType::Join
    tree.setSegmentation(true);tree.setNormalizeIds(true);
    tree.setVertexScalars(simplified.data());tree.setVertexSoSoffsets(outOffsets.data());
    tree.preconditionTriangulation(&tri);tree.build<float>(&tri);
    auto *jt=tree.getJoinTree();
    std::vector<int32_t> nodes,arcs,regular,owner(n,-1),critical(n,-1);
    int leaves=0,nonbinary=0,root=-1;
    for(unsigned i=0;i<jt->getNumberOfNodes();++i){
      auto *node=jt->getNode(i);const int v=node->getVertexId();nodes.push_back(v);critical[v]=i;
      if(node->getNumberOfDownSuperArcs()==0)++leaves;
      if(node->getNumberOfDownSuperArcs()>2)++nonbinary;
      if(node->getNumberOfUpSuperArcs()==0)root=v;
    }
    for(unsigned a=0;a<jt->getNumberOfSuperArcs();++a){
      auto *arc=jt->getSuperArc(a);
      const int up=jt->getNode(arc->getUpNodeId())->getVertexId(),down=jt->getNode(arc->getDownNodeId())->getVertexId();
      std::vector<int32_t> region;
      for(int j=0;j<arc->getNumberOfRegularNodes();++j){const int v=arc->getRegularNodeId(j);if(critical[v]<0)region.push_back(v);}
      std::sort(region.begin(),region.end(),[&](int a,int b){return outOffsets[a]>outOffsets[b];});
      arcs.insert(arcs.end(),{up,down,static_cast<int32_t>(regular.size()),static_cast<int32_t>(region.size())});
      for(int v:region){if(owner[v]>=0)throw std::runtime_error("overlapping arc segmentation");owner[v]=a;}
      if(owner[down]>=0)throw std::runtime_error("duplicate critical point ownership");owner[down]=a;
      if(up==root)owner[root]=a;
      regular.insert(regular.end(),region.begin(),region.end());
    }
    if(root<0||std::find(owner.begin(),owner.end(),-1)!=owner.end()||regular.size()+nodes.size()!=static_cast<size_t>(n))
      throw std::runtime_error("augmented tree does not own every original sample exactly once");
    write(prefix+".values.f32",simplified);write(prefix+".offsets.i32",outOffsets);
    write(prefix+".nodes.i32",nodes);write(prefix+".arcs.i32",arcs);write(prefix+".regular.i32",regular);write(prefix+".owner.i32",owner);
    double maxChange=0;size_t changed=0;
    for(int i=0;i<n;++i){const double d=std::abs(double(values[i])-simplified[i]);maxChange=std::max(maxChange,d);changed+=d>0;}
    const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::ofstream meta(prefix+".json");
    meta<<"{\"ttk_version\":\"0.9.9\",\"tree_kind\":\"join\",\"samples\":"<<n<<",\"nodes\":"<<nodes.size()
      <<",\"arcs\":"<<arcs.size()/4<<",\"leaves\":"<<leaves<<",\"nonbinary_nodes\":"<<nonbinary<<",\"root\":"<<root
      <<",\"absolute_persistence_threshold\":"<<threshold<<",\"numerical_perturbation\":false,\"saddle_connectors\":"<<(connectors?"true":"false")
      <<",\"changed_samples\":"<<changed<<",\"maximum_scalar_change\":"<<maxChange<<",\"seconds\":"<<elapsed
      <<",\"simplification_and_pd_seconds\":"<<std::chrono::duration<double>(simplifiedAt-start).count()<<"}\n";
    std::cout<<"TTK original-grid scalar simplification + join tree: "<<nodes.size()<<" nodes, "<<leaves<<" leaves; "<<elapsed<<" s\n";
    return 0;
  } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
