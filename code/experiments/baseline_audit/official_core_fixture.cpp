/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2020 Inviwo Foundation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************************/


// Verification harness: LandscapeInfo and greedy routines extracted verbatim from
// Wiebke/TemporalMergeTreeMaps commit 2c75a10ed2cd55177a25ff751e0c0a8261200717.
// Stub tree accessors supply identical real-data augmented trees, not Inviwo/TTK.
#include <algorithm>
#include <cmath>
#include <vector>
#include <iostream>
#include <cassert>
#define IVW_ASSERT(cond,msg) assert(cond);
namespace ttk { namespace ftm {
using idNode=size_t; using idSuperArc=size_t;
struct Node { std::vector<size_t> down; size_t getNumberOfDownSuperArcs(){return down.size();} size_t getDownSuperArcId(size_t i){return down[i];} };
struct Arc { size_t down; size_t getDownNodeId(){return down;} };
struct FTMTree_MT { std::vector<Node> nodes; std::vector<Arc> arcs; size_t root,N; Node* getNode(size_t i){return &nodes[i];} Arc* getSuperArc(size_t i){return &arcs[i];} size_t getNumberOfSuperArcs(){return arcs.size();} size_t getNumberOfVertices(){return N;} };
}}
namespace mtmutils {
using namespace ttk::ftm;
struct SubTreeInfo {size_t numArcs;std::vector<size_t> arcSizes,treeSizes;};
struct Overlap {std::vector<std::vector<size_t>> treeTreeCount;};
size_t findRoot(FTMTree_MT* t){return t->root;}
struct LandscapeInfo {

    LandscapeInfo() { limits = std::vector<size_t>(5, 0); }

    size_t getOuterLimMin() const { return limits[0]; };

    size_t getOuterLimMax() const { return limits[1]; };

    size_t getInnerLimMin() const { return limits[2]; };

    size_t getInnerLimMax() const { return limits[3]; };

    size_t getDownNodePos() const { return limits[4]; }

    void setLimits(size_t outerLimMin, size_t outerLimMax, size_t innerLimMin, size_t innerLimMax) {
        IVW_ASSERT(outerLimMin <= outerLimMax,
                   "Minimum is larger than Maximum for outer landscape limit");
        IVW_ASSERT(innerLimMin <= innerLimMax,
                   "Minimum is larger than Maximum for inner landscape limit")
        limits[0] = outerLimMin;
        limits[1] = outerLimMax;
        limits[2] = innerLimMin;
        limits[3] = innerLimMax;
    };

    void setDownNodePos(size_t downNodePos) {
        // downNode Position should be right between innerLimMin and innerLimMax
        IVW_ASSERT(getInnerLimMin() < downNodePos,
                   "Super Node Position is smaller than Minimum for inner landscape limit");
        IVW_ASSERT(getInnerLimMax() > downNodePos,
                   "Super Node Position is larger than Maximum for inner landscape limit")
        limits[4] = downNodePos;
    };

    size_t getSubTreeSize() const { return getOuterLimMax() - getOuterLimMin() + 1; }

    size_t getArcSize() const {
        // Each arc consists of two intervals [outerMin, innerMin], [innerMax, outerMax] and down
        // and the down node position, which can be expressed as an additional interval
        // [downNodePos, downNodePos]
        // The size of each interval [a,b] is b-a+1
        // size of [outerMin, innerMin] = innerMin - innerMin + 1
        size_t size = getInnerLimMin() - getOuterLimMin() + 1;
        // size of [innerMax, outerMax] = outerMax - innerMax + 1
        // size of [downNodePos, downNodePos] = downNodePos - downNodePos + 1 =1
        size += getOuterLimMax() - getInnerLimMax() + 1 + 1;
        return size;
    }

    void computeLimitRoot(const size_t arcSize, const size_t treeSize) {
        // For all cases: If we add number of elements to an index, we have to subtract 1 to get
        // steps. The root arc resembles the entire tree and thus fills all of the landscape
        limits[0] = 0;
        limits[1] = treeSize - 1;
        // Iteration starts at the root node and switches sides for each subsequent node in the
        // arc If the number of nodes is uneven, there will be one more node on the root side
        // as that is where we started
        size_t arcSizeWithoutDownNode = arcSize - 1;
        limits[2] = limits[0] + ((arcSizeWithoutDownNode + 1) / 2 - 1);
        limits[3] = limits[1] - (arcSizeWithoutDownNode / 2 - 1);
    }

    void computeLimit(size_t lastAssigned, const size_t arcSize, const size_t treeSize) {
        // For all cases: If we add number of elements to an index, we have to subtract 1 to get
        // steps
        // !! Changed code to accomodate multiple variables
        // Previously, additional variables const LandscapeInfo& parentLimits, const bool first,
        // We assume a binary tree, i.e. at most 2 down arcs at each inner node, a node can only
        // be first or second limits can be computed from the inner limits of the parent arc,
        // for the first arc, the minimum outer limit depends on the minimum inner limit and the
        // tree size for that arc
        // for the second, the minimum outer limits depends on the maximum outer limit of the
        // first arc - to compute it independently, we instead compute the maximum outer limit
        // in terms of the maximum inner limit of the parent, then the minimum outer limit
        // depends on the tree size for that arc
        /*if (first) {
            limits[0] = parentLimits.getInnerLimMin() + 1;
            limits[1] = limits[0] + (treeSize - 1);
        } else {
            limits[1] = parentLimits.getInnerLimMax() - 1;
            limits[0] = limits[1] - (treeSize - 1);
        }*/
        limits[0] = lastAssigned + 1;
        limits[1] = limits[0] + (treeSize - 1);
        size_t arcSizeWithoutDownNode = arcSize - 1;
        // Independently of the order, each arc starts being traversed at the maximum (to fit
        // with overall starting at the minimum for the root ), thus in case of an uneven arc
        // size, one more node will be placed on the minimum side
        limits[2] = limits[0] + (arcSizeWithoutDownNode / 2 - 1);
        limits[3] = limits[1] - ((arcSizeWithoutDownNode + 1) / 2 - 1);
    }

    std::vector<size_t> limits;

    size_t static overlapInterval(size_t minA, size_t maxA, size_t minB, size_t maxB) {
        // Cases for overlap of interval A [minA, maxA] with interval B [minB, maxB]
        // one is fully before the other -> no overlap
        // A ----xxxxx------ [4,8]
        // B ---------xxxxxx [9,15]
        // -> oS = max(4,9) = 9, oE = min(8,15) = 8, return max(0, 8-9+1) = 0
        // one is partially within the other -> overlap = intersection
        // A ----xxxxx------ [4,8]
        // B -----xxx------- [5,7]
        // -> oS = max(4,5) = 5, oE = min(8,7) = 7, return max(0, 7-5+1) = 3
        // one is partially within the other -> overlap = intersection
        // A ----xxxxx------ [4,8]
        // B --xxxxxx------- [2,7]
        // -> oS = max(4,2) = 4, oE = min(8,7) = 7, return max(0, 7-4+1) = 4
        int overlapStart = static_cast<int>(std::max(minA, minB));
        int overlapEnd = static_cast<int>(std::min(maxA, maxB));
        return std::max(0, overlapEnd - overlapStart + 1);
    }

    size_t static overLapCountTrees(const LandscapeInfo& first, const LandscapeInfo& second) {
        // essentially computation of overlap of two intervals [minA, maxA], [minB, maxB]
        return overlapInterval(first.getOuterLimMin(), first.getOuterLimMax(),
                               second.getOuterLimMin(), second.getOuterLimMax());
    };

    float static overLapFractionTrees(const LandscapeInfo& first, const LandscapeInfo& second) {
        size_t overlap = LandscapeInfo::overLapCountTrees(first, second);
        size_t sizeFirst = first.getSubTreeSize();
        size_t sizeSecond = second.getSubTreeSize();
        // Normalize by union (sum of sizes - overlap, overlap would be counted twice otherwise)
        return overlap / static_cast<float>(sizeFirst + sizeSecond - overlap);
    };

    size_t static overLapCountArcs(const LandscapeInfo& first, const LandscapeInfo& second) {
        // Each arc consists of two intervals [outerMin, innerMin], [innerMax, outerMax]
        // and the down node position, which can be expressed as an additional interval
        // [downNodePos, downNodePos]
        // So for the overlap we need to compute 3*3 interval intersections
        size_t overlap = 0;
        // overlap for intervals first.mins and second.mins
        overlap += overlapInterval(first.getOuterLimMin(), first.getInnerLimMin(),
                                   second.getOuterLimMin(), second.getInnerLimMin());
        // overlap for intervals first.mins and second.maxs
        overlap += overlapInterval(first.getOuterLimMin(), first.getInnerLimMin(),
                                   second.getInnerLimMax(), second.getOuterLimMax());
        // overlap for intervals first.mins and second.downNode
        overlap += overlapInterval(first.getOuterLimMin(), first.getInnerLimMin(),
                                   second.getDownNodePos(), second.getDownNodePos());
        // overlap for intervals first.maxs and second.mins
        overlap += overlapInterval(first.getInnerLimMax(), first.getOuterLimMax(),
                                   second.getOuterLimMin(), second.getInnerLimMin());
        // overlap for intervals first.maxs and second.maxs
        overlap += overlapInterval(first.getInnerLimMax(), first.getOuterLimMax(),
                                   second.getInnerLimMax(), second.getOuterLimMax());
        // overlap for intervals first.mins and second.downNode
        overlap += overlapInterval(first.getInnerLimMax(), first.getOuterLimMax(),
                                   second.getDownNodePos(), second.getDownNodePos());
        // overlap for intervals first.downNode and second.mins
        overlap += overlapInterval(first.getDownNodePos(), first.getDownNodePos(),
                                   second.getOuterLimMin(), second.getInnerLimMin());
        // overlap for intervals first.downNode and second.maxs
        overlap += overlapInterval(first.getDownNodePos(), first.getDownNodePos(),
                                   second.getInnerLimMax(), second.getOuterLimMax());
        // overlap for intervals first.downNode and second.downNode
        overlap += overlapInterval(first.getDownNodePos(), first.getDownNodePos(),
                                   second.getDownNodePos(), second.getDownNodePos());

        return overlap;
    }

    float static overLapFractionArcs(const LandscapeInfo& first, const LandscapeInfo& second) {
        size_t overlap = LandscapeInfo::overLapCountArcs(first, second);
        size_t sizeFirst = first.getArcSize();
        size_t sizeSecond = second.getArcSize();
        // Normalize by union (sum of sizes - overlap, overlap would be counted twice otherwise)
        return overlap / static_cast<float>(sizeFirst + sizeSecond - overlap);
    }
};
float objectiveForSeveralArcs(const SubTreeInfo& infoFromPrev,
                              const std::vector<LandscapeInfo>& landscapeFromPrev,
                              const Overlap& overlapND, const bool useCounts,
                              const std::vector<ttk::ftm::idSuperArc>& superArcIds,
                              const std::vector<LandscapeInfo>& landscapes) {
    float objective = 0.0f;
    for (size_t superArcIdPrev = 0; superArcIdPrev < infoFromPrev.numArcs; superArcIdPrev++) {
        auto& landscapeFromPrevCurr = landscapeFromPrev[superArcIdPrev];
        for (size_t i = 0; i < superArcIds.size(); i++) {
            float objectiveCurrent = 0.0f;
            const auto& superArcId = superArcIds[i];
            const auto& landscape = landscapes[i];
            if (useCounts) {
                objectiveCurrent =
                    static_cast<float>(overlapND.treeTreeCount[superArcIdPrev][superArcId]) -
                    LandscapeInfo::overLapCountTrees(landscapeFromPrevCurr, landscape);
            } else {
                size_t superArcPrevSize = landscapeFromPrevCurr.getSubTreeSize();
                size_t arcSize = landscape.getSubTreeSize();
                float objectiveNDCurrent =
                    static_cast<float>(overlapND.treeTreeCount[superArcIdPrev][superArcId]);
                objectiveCurrent =
                    objectiveNDCurrent / (superArcPrevSize + arcSize - objectiveNDCurrent) -
                    LandscapeInfo::overLapFractionTrees(landscapeFromPrevCurr, landscape);
            }
            objective += objectiveCurrent * objectiveCurrent;
        }
    }
    return objective;
}

float decideGreedy(ttk::ftm::FTMTree_MT* tree, const SubTreeInfo& infoFromPrev,
                   const std::vector<LandscapeInfo>& landscapeFromPrev, const SubTreeInfo& info,
                   const Overlap& overlapND, const ttk::ftm::idSuperArc& superArcId,
                   const bool useCounts, const bool chooseWorse, std::vector<int>& decisions,
                   std::vector<LandscapeInfo>& landscapes) {

    auto& thisArcInfo = landscapes[superArcId];
    auto superArc = tree->getSuperArc(superArcId);
    auto nodeId = superArc->getDownNodeId();
    auto nextNode = tree->getNode(nodeId);
    auto numDown = nextNode->getNumberOfDownSuperArcs();

    std::vector<ttk::ftm::idSuperArc> superArcIds;
    for (ttk::ftm::idSuperArc i = 0; i < numDown; ++i) {
        auto superArcId = nextNode->getDownSuperArcId(i);
        superArcIds.push_back(superArcId);
    }
    // Sort here since MiniZinc will do this internally too
    std::sort(superArcIds.begin(), superArcIds.end());

    // Leaf
    if (superArcIds.size() == 0) {
        thisArcInfo.setDownNodePos(thisArcInfo.getInnerLimMin() + 1);
        return 0.0f;
    }

    // Try out the two ordering options
    std::vector<LandscapeInfo> landscapesDecisionTrue(superArcIds.size());
    std::vector<LandscapeInfo> landscapesDecisionFalse(superArcIds.size());
    std::vector<ttk::ftm::idSuperArc> superArcIdsReverse(superArcIds.size());
    std::reverse_copy(superArcIds.begin(), superArcIds.end(), superArcIdsReverse.begin());

    size_t lastAssigned = thisArcInfo.getInnerLimMin();
    size_t lastAssignedRev = thisArcInfo.getInnerLimMin();

    // If decision is false: Order by Id, if it is true, order inversly by id
    for (size_t i = 0; i < superArcIds.size(); i++) {
        // True -> superarcs in reverse order
        const auto& superArcIdCurrRev = superArcIdsReverse[i];
        LandscapeInfo& landscapeCurrTrue = landscapesDecisionTrue[i];
        landscapeCurrTrue.computeLimit(lastAssigned, info.arcSizes[superArcIdCurrRev],
                                       info.treeSizes[superArcIdCurrRev]);
        lastAssigned = landscapeCurrTrue.getOuterLimMax();
        // False -> superarcs in order
        const auto& superArcIdCurr = superArcIds[i];
        LandscapeInfo& landscapeCurrFalse = landscapesDecisionFalse[i];
        landscapeCurrFalse.computeLimit(lastAssignedRev, info.arcSizes[superArcIdCurr],
                                        info.treeSizes[superArcIdCurr]);
        lastAssignedRev = landscapeCurrFalse.getOuterLimMax();
        // Reserve space for downNode of current arc
        if (i == 0) {
            lastAssigned++;
            lastAssignedRev++;
        }
    }

    float objTrue = objectiveForSeveralArcs(infoFromPrev, landscapeFromPrev, overlapND, useCounts,
                                            superArcIdsReverse, landscapesDecisionTrue);

    float objFalse = objectiveForSeveralArcs(infoFromPrev, landscapeFromPrev, overlapND, useCounts,
                                             superArcIds, landscapesDecisionFalse);
    int decision = objTrue < objFalse;

	// Choose opposite
    if (chooseWorse) decision = !decision;
    decisions[superArcId] = decision;

    if (decision) {
        for (size_t i = 0; i < superArcIds.size(); i++) {
            const auto& superArcIdCurrRev = superArcIdsReverse[i];
            landscapes[superArcIdCurrRev] = landscapesDecisionTrue[i];
        }
    } else {
        for (size_t i = 0; i < superArcIds.size(); i++) {
            const auto& superArcIdCurr = superArcIds[i];
            landscapes[superArcIdCurr] = landscapesDecisionFalse[i];
        }
    }

    // Set downnode after the first child (we reserved this space earlier)
    thisArcInfo.setDownNodePos((decision ? landscapesDecisionTrue[0].getOuterLimMax() + 1
                                         : landscapesDecisionFalse[0].getOuterLimMax() + 1));

    float objectiveChildren = 0.0;
    for (size_t i = 0; i < superArcIds.size(); i++) {
        objectiveChildren +=
            decideGreedy(tree, infoFromPrev, landscapeFromPrev, info, overlapND, superArcIds[i],
                         useCounts, chooseWorse, decisions, landscapes);
    }

    return (decision ? objTrue : objFalse) + objectiveChildren;
}

float decideGreedyTree(ttk::ftm::FTMTree_MT* tree, const SubTreeInfo& infoFromPrev,
                       const std::vector<LandscapeInfo>& landscapeFromPrev, const SubTreeInfo& info,
                       const Overlap& overlapND, const bool useCounts, const bool chooseWorse,
                       std::vector<int>& decisions, std::vector<LandscapeInfo>& landscapes) {

    auto numArcs = tree->getNumberOfSuperArcs();
    landscapes = std::vector<LandscapeInfo>(numArcs);

    auto roodId = findRoot(tree);
    auto root = tree->getNode(roodId);
    auto rootNumDown = root->getNumberOfDownSuperArcs();
    auto rootSuperArcId = root->getDownSuperArcId(0);

    if (rootNumDown > 1) return pow(tree->getNumberOfSuperArcs() * tree->getNumberOfVertices(), 2);

    auto& rootArcInfo = landscapes[rootSuperArcId];
    rootArcInfo.computeLimitRoot(info.arcSizes[rootSuperArcId], info.treeSizes[rootSuperArcId]);

    // The overlap with the root is equal to the subtree size for each arc
    // This is true for ND and 1D, obj value will thus be 0
    // float objRoot = ...

    return decideGreedy(tree, infoFromPrev, landscapeFromPrev, info, overlapND, rootSuperArcId,
                        useCounts, chooseWorse, decisions, landscapes);
}

}
int main(){using namespace mtmutils;size_t pairs;std::cin>>pairs;
for(size_t pair=0;pair<pairs;pair++){
 size_t prevArcs,arcs,nodes,root,N;std::cin>>prevArcs>>arcs>>nodes>>root>>N;
 SubTreeInfo prev{prevArcs},curr{arcs};std::vector<LandscapeInfo> prevland(prevArcs);
 for(auto &l:prevland){std::cin>>l.limits[0]>>l.limits[1];}
 ttk::ftm::FTMTree_MT tree;tree.root=root;tree.N=N;tree.nodes.resize(nodes);tree.arcs.resize(arcs);
 for(auto &n:tree.nodes){size_t count;std::cin>>count;n.down.resize(count);for(auto &i:n.down)std::cin>>i;}
 curr.arcSizes.resize(arcs);curr.treeSizes.resize(arcs);
 for(size_t i=0;i<arcs;i++)std::cin>>tree.arcs[i].down>>curr.arcSizes[i]>>curr.treeSizes[i];
 Overlap o;o.treeTreeCount.resize(prevArcs,std::vector<size_t>(arcs));for(auto& row:o.treeTreeCount)for(auto& v:row)std::cin>>v;
 std::vector<int> decisions(arcs,0);std::vector<LandscapeInfo> layouts;float objective=decideGreedyTree(&tree,prev,prevland,curr,o,true,false,decisions,layouts);
 std::cout<<pair<<' '<<objective;
 for(size_t i=0;i<arcs;i++)std::cout<<' '<<decisions[i]<<' '<<layouts[i].getOuterLimMin()<<' '<<layouts[i].getOuterLimMax()<<' '<<layouts[i].getDownNodePos();std::cout<<'\n';
}}
