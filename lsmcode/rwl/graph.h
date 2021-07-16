#ifndef GRAPH_H_OCT_11_2009
#define GRAPH_H_OCT_11_2009

#include <cfloat>
#include <cmath>
#include "array.h"
#include "timer.h"
#include "hashstring.h"
#include "hashint.h"
#include "node.h"
#include "nodecluster.h"
#include "community.h"

const bool MERGE_NODES = true; 
const bool MERGE_NODES_BY_JS = true; //if true merge by JS divergence, otherwise by hit times

typedef hash_map<string, Array<ConstNode *> *, HashString, EqualString> StringToConstNodesMap;
typedef hash_map<string, Array<PredNode *> *, HashString, EqualString> StringToPredNodesMap;

class Graph
{
private:
  Timer timer_;
  StringToConstNodesMap typeToConstNodesMap_; //maps type name to constant nodes
  StringToPredNodesMap predToPredNodesMap_;   //maps predicate name to predicate nodes
  int numSamples_;
  int maxLen_;
  double delta_;
  double eps_;
  int numConstNodes_;
  int numPredNodes_;
  int numNodes_;
  double timeThresh_;
  double mergeTimeThresh_;
  double jsThresh_;
  int jsTopN_;
  Array<string> typeNames_;

public:
  Graph() : numSamples_(-1), maxLen_(-1), delta_(-1.0), eps_(-1.0),
            numConstNodes_(-1), numPredNodes_(-1), numNodes_(-1),
            timeThresh_(-1.0), mergeTimeThresh_(-1.0), jsThresh_(-1.0) {}
  ~Graph()
  {
    StringToConstNodesMap::iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      Array<ConstNode *> *arr = (*it).second;
      arr->deleteItemsAndClear();
      delete arr;
    }
    StringToPredNodesMap::iterator it2;
    for (it2 = predToPredNodesMap_.begin(); it2 != predToPredNodesMap_.end(); it2++)
    {
      Array<PredNode *> *arr = (*it2).second;
      arr->deleteItemsAndClear();
      delete arr;
    }
  }

  StringToConstNodesMap &typeToConstNodesMap() { return typeToConstNodesMap_; }
  StringToPredNodesMap &predToPredNodesMap() { return predToPredNodesMap_; }

  int numSamples() const { return numSamples_; }
  void setNumSamples(const int &s) { numSamples_ = s; }
  int maxLen() const { return maxLen_; }
  void setMaxLen(const int &l) { maxLen_ = l; }
  double delta() const { return delta_; }
  void setDelta(const double &delta) { delta_ = delta; }
  double eps() const { return eps_; }
  void setEps(const double &eps) { eps_ = eps; }
  double timeThresh() const { return timeThresh_; }
  void setTimeThresh(const double &p) { timeThresh_ = p; }
  double mergeTimeThresh() const { return mergeTimeThresh_; }
  void setMergeTimeThresh(const double &p) { mergeTimeThresh_ = p; }
  double jsThresh() const { return jsThresh_; }
  void setJSThresh(const double &p) { jsThresh_ = p; }
  void setJSTopN(const int &n) { jsTopN_ = n; }

  const Array<string> &typeNames() const { return typeNames_; }
  void setTypeNames(const Array<string> &names)
  {
    typeNames_.clear();
    typeNames_.append(names);
  }

  void compress()
  {
    StringToConstNodesMap::iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      Array<ConstNode *> &constNodes = *((*it).second);
      constNodes.compress();
      for (int i = 0; i < constNodes.size(); i++)
      {
        ConstNode *constNode = constNodes[i];
        constNode->compressOutLinks();
        constNode->compressPredNodes();
      }
    }

    StringToPredNodesMap::iterator it2;
    for (it2 = predToPredNodesMap_.begin(); it2 != predToPredNodesMap_.end(); it2++)
    {
      Array<PredNode *> &predNodes = *((*it2).second);
      predNodes.compress();
      for (int i = 0; i < predNodes.size(); i++)
      {
        PredNode *predNode = predNodes[i];
        predNode->compressOutLinks();
      }
    }
  }

  void setNumNodesAndLinkProbsAndAssignNodeIds()
  {
    numConstNodes_ = numConstNodes();
    numPredNodes_ = numPredNodes();
    numNodes_ = numConstNodes_;

    int cnt = 0;

    StringToPredNodesMap::iterator it2;
    for (it2 = predToPredNodesMap_.begin(); it2 != predToPredNodesMap_.end(); it2++)
    {
      Array<PredNode *> &predNodes = *((*it2).second);
      for (int i = 0; i < predNodes.size(); ++i)
        predNodes[i]->setId(cnt++);
    }

    StringToConstNodesMap::iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      Array<ConstNode *> &constNodes = *((*it).second);
      for (int i = 0; i < constNodes.size(); ++i)
      {
        constNodes[i]->setId(cnt++);
        constNodes[i]->setOutLinkProbs();
      }
    }
  }

  int numConstNodes() const
  {
    int n = 0;
    StringToConstNodesMap::const_iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
      n += (*it).second->size();
    return n;
  }

  int numPredNodes() const
  {
    int n = 0;
    StringToPredNodesMap::const_iterator it;
    for (it = predToPredNodesMap_.begin(); it != predToPredNodesMap_.end(); it++)
      n += (*it).second->size();
    return n;
  }

  int numEdges() const
  {
    int numEdges = 0;
    StringToConstNodesMap::const_iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      Array<ConstNode *> &constNodeArr = *((*it).second);
      for (int i = 0; i < constNodeArr.size(); i++)
        numEdges += constNodeArr[i]->numOutLinks();
    }
    numEdges /= 2;
    return numEdges;
  }

  ostream &print(ostream &out) const
  {
    StringHashArray uniqConstNodes;
    StringToConstNodesMap::const_iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      string typeName = (*it).first;
      Array<ConstNode *> &constNodeArr = *((*it).second);
      for (int i = 0; i < constNodeArr.size(); i++)
      {
        string constName = constNodeArr[i]->constant()->name();
        uniqConstNodes.append(constName);
        out << typeName << ": " << constName << endl;
      }
    }

    StringHashArray uniqPredNodes;
    StringToPredNodesMap::const_iterator it2;
    for (it2 = predToPredNodesMap_.begin(); it2 != predToPredNodesMap_.end(); it2++)
    {
      Array<PredNode *> &predNodeArr = *((*it2).second);
      for (int i = 0; i < predNodeArr.size(); i++)
      {
        string strRep = predNodeArr[i]->strRep();
        uniqPredNodes.append(strRep);
        out << "PRED: " << strRep << endl;
      }
    }

    //print the graph
    int numEdges = 0;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      Array<ConstNode *> &constNodeArr = *((*it).second);
      for (int i = 0; i < constNodeArr.size(); i++)
      {
        ConstNode *node = constNodeArr[i];
        string strRep = node->strRep();
        out << "CONST: " << strRep << " -> " << endl;
        const Array<OutLink *> &outLinks = node->outLinks();
        numEdges += outLinks.size();
        for (int j = 0; j < outLinks.size(); j++)
        {
          out << "    " << outLinks[j]->toNode()->strRep() << endl;
        }
        for (int j = 0; j < outLinks.size(); j++)
        {
          Node *node = outLinks[j]->toNode();
          out << "  " << node->strRep() << " -> " << endl;
          const Array<OutLink *> &outLinks2 = node->outLinks();
          for (int k = 0; k < outLinks2.size(); k++)
          {
            Node *node = outLinks2[k]->toNode();
            out << "    " << node->strRep() << endl;
          }
        }
      }
    }

    out << "#ConstNodes " << numConstNodes() << ", #uniqConstNodes " << uniqConstNodes.size() << endl;
    out << "#PredNodes " << numPredNodes() << ", #uniqPredNodes " << uniqPredNodes.size() << endl;
    out << "#Edges " << numEdges << endl;
    return out;
  }

  void printTypes(ostream &out)
  {
    StringToConstNodesMap::iterator it;
    for (it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
      out << (*it).first << endl;
  }

  Array<Community *> *runRandomWalks(Array<Community *> *&unmergedComs, Array<int> *&srcNodes)
  {
    Util::assertt(typeNames_.size() == (int)typeToConstNodesMap_.size(), "wrong num of types", -1);
    double begSec = timer_.time();

    //if too few samples, change number of samples and find corresponding eps
    adjustNumSamplesAndEps();

    //to compute the ave num of clusts and nodes per community
    double totalClusts = 0.0, totalNodes = 0.0;
    double totalClusts2 = 0.0, totalNodes2 = 0.0;

    Array<Community *> *coms = new Array<Community *>;
    CommunitySet *comSet = new CommunitySet();
    unmergedComs = new Array<Community *>;
    srcNodes = new Array<int>;

    //for each constant node, run random walks starting from it
    int nodeCnt = 0;
    for (StringToConstNodesMap::iterator it = typeToConstNodesMap_.begin(); it != typeToConstNodesMap_.end(); it++)
    {
      cout << "random walk for type " << (*it).first << endl;
      string typeName = (*it).first;

      //CO
      //string tt = "bib"; //bib person title author
      //if (typeName.compare(tt) != 0) continue;

      Array<ConstNode *> &nodes = *((*it).second);

      for (int i = 0; i < nodes.size(); i++)
      {
        double begSec = timer_.time();
        cout << ++nodeCnt << "/" << numConstNodes_ << ": running walks for " << nodes[i]->strRep() << "..." << endl;

        Community *unmergedCom = NULL;
        Community *com = runRandomWalks(nodes[i], unmergedCom);

        //! Dom
        cout << *com << endl;

        pair<CommunitySet::iterator, bool> pr = comSet->insert(com);
        if (pr.second)
        {
          coms->append(com);
          unmergedComs->append(unmergedCom);
          srcNodes->append(nodes[i]->constant()->id());
          updateTotalClustsNodes(totalClusts, totalClusts2, totalNodes, totalNodes2, com);
        }
        else
        {
          delete com;
          delete unmergedCom;
        }

        cout << "  took ";
        timer_.printTime(cout, timer_.time() - begSec);
        cout << endl;
      }
    }

    cout << "#communities " << coms->size() << endl;
    printAveClustsNodes(cout, totalClusts, totalClusts2, totalNodes, totalNodes2, coms->size());
    cout << "runRandomWalks() took ";
    timer_.printTime(cout, timer_.time() - begSec);
    cout << endl;

    delete comSet;
    coms->compress();
    return coms;
  }

private:
  Community *runRandomWalks(Node *const &node, Community *&unmergedCom)
  {
    NodeSet nodeSet; //data structure to record the nodes that are hit
    Array<int> samplePath(maxLen_);
    for (int samp = 0; samp < numSamples_; samp++)
    {
      samplePath.clear();
      runRandomWalk(node, node->id(), samp, 0, nodeSet, samplePath);
    }
    Community *com = getNearestNodes(nodeSet, unmergedCom);
    return com;
  }

  void runRandomWalk(Node *const &node, const int &startNodeId, const int &sampleId, const int &len, NodeSet &nodeSet, Array<int> &samplePath)
  {
    if (len > maxLen_)
      return;

    if (node->startNodeId() != startNodeId) //if node is hit for the first time
    {
      Util::assertt(node->startNodeId() < startNodeId, "expect node->startNodeId < startNodeId", -1);
      node->setNumHits(1);
      node->setStartNodeId(startNodeId);
      node->setSampleId(sampleId);
      node->setAccHitTime(len);
      if (node->nodeType() == Node::CONSTANT)
      {
        nodeSet.insert(node);
        if (MERGE_NODES_BY_JS)
          node->addSamplePath(samplePath);
      }
    }
    else if (node->sampleId() != sampleId) //if node is hit for the first time in this sample
    {
      //node->startNodeId() == startNodeId
      Util::assertt(node->sampleId() < sampleId, "expect node->sampleId < sampleId", -1);
      Util::assertt(node->numHits() > 0, "expect numHits() > 0, " + Util::intToString(node->numHits()), -1);
      node->incrNumHits();
      node->setSampleId(sampleId);
      node->addAccHitTime(len);
      if (node->nodeType() == Node::CONSTANT && MERGE_NODES_BY_JS)
        node->addSamplePath(samplePath);
    }
    else //node has been hit before in this sample
    {
      //node->startNodeId() == startNodeId
      //node->sampledId() == sampleId
    }

    OutLink *outlink = node->randomOutLink();
    if (outlink == NULL)
      return;
    Node *nextNode = outlink->toNode();
    samplePath.append(outlink->relId());
    runRandomWalk(nextNode, startNodeId, sampleId, len + 1, nodeSet, samplePath);
  }

private:
  double minNumSamples() const { return 0.5 + log(2 * numNodes_ / delta_) / (2 * eps_ * eps_); }
  double epsilon() const { return sqrt(log(2 * numNodes_ / delta_) / (2 * numSamples_)); }
  void adjustNumSamplesAndEps()
  {
    double minNumSamp = minNumSamples();
    //if (minNumSamp > numSamples_) //CO: use the values specified for experiments
    if (false)
    {
      double prevEps = epsilon();
      double prevNumSamples = numSamples_;
      numSamples_ = (int)(minNumSamp + 0.5);
      eps_ = epsilon();
      cout << "change #samples from " << prevNumSamples << " to " << numSamples_ << endl;
      cout << "change eps from " << prevEps << " to " << eps_ << endl;
      cout << "delta " << delta_ << endl;
      cout << "epsilon * maxLen " << eps_ * maxLen_ << endl;
    }
    else
    {
      cout << "#samples " << numSamples_ << endl;
      cout << "epsilon " << epsilon() << endl;
      cout << "delta " << delta_ << endl;
      cout << "epsilon * maxLen " << epsilon() * maxLen_ << endl;
    }
  }

  void updateTotalClustsNodes(double &totalClusts, double &totalClusts2, double &totalNodes, double &totalNodes2, Community *const com)
  {
    totalClusts += com->totalClusts();
    totalClusts2 += com->totalClusts() * com->totalClusts();
    totalNodes += com->totalNodes();
    totalNodes2 += com->totalNodes() * com->totalNodes();
  }

  void printAveClustsNodes(ostream &out, double &totalClusts, double &totalClusts2, double &totalNodes, double &totalNodes2, const int &comsSize)
  {
    double aveClusts = totalClusts / comsSize;
    double aveClusts2 = totalClusts2 / comsSize;
    double aveNodes = totalNodes / comsSize;
    double aveNodes2 = totalNodes2 / comsSize;
    out << "ave #clusts per com  " << aveClusts << " , stdev  " << sqrt(aveClusts2 - (aveClusts * aveClusts)) << endl;
    out << "ave #nodes  per com  " << aveNodes << " , stdev  " << sqrt(aveNodes2 - (aveNodes * aveNodes)) << endl;
  }

  Node **sortNodeSet(const NodeSet &nodeSet)
  {
    Node **nodeArr = new Node *[nodeSet.size()];
    int idx = 0;
    for (NodeSet::const_iterator it = nodeSet.begin(); it != nodeSet.end(); it++)
    {
      Node *node = *it;
      node->computeHitTime(numSamples_, maxLen_);
      nodeArr[idx++] = node;
    }
    qsort(nodeArr, nodeSet.size(), sizeof(Node *), compareNodeHitTime);

    /*//CO
    for (unsigned int i = 0; i < nodeSet.size(); i++)
    {
      Node* node = nodeArr[i];
      cout << "  " << i << ": " << node->strRep() << " " << node->hitTime() << endl;
      //cout << "--------- SamplePaths:" << endl; node->printSamplePathSet(cout); cout << "----------------------" << endl;
    }
    //*/

    return nodeArr;
  }

  Community *getNearestNodes(const NodeSet &nodeSet, Community *&unmergedCom)
  {
    Node **nodes = sortNodeSet(nodeSet);
    int numNodes = nodeSet.size();

    Array<Node *> topNodes;
    for (int i = 0; i < numNodes; i++)
    {
      if (nodes[i]->hitTime() > timeThresh_)
        break;
      topNodes.append(nodes[i]);
    }
    delete[] nodes;

    Node **topNodes2 = new Node *[topNodes.size()];
    for (int i = 0; i < topNodes.size(); i++)
      topNodes2[i] = topNodes[i];

    cout << "  selected nearest " << topNodes.size() << " out of " << numNodes << endl;

    //CO
    /*cout << "-------- TOP_NODES -------" << endl;
    for (int i = 0; i < topNodes.size(); i++)
      cout << "  " << i << " " << topNodes2[i]->id() << ": " << topNodes2[i]->strRep() << " " << topNodes2[i]->hitTime() << endl;
    //*/

    Community *com;
    if (MERGE_NODES)
    {
      com = mergeNodes(topNodes2, topNodes.size());
      unmergedCom = new Community(topNodes2, topNodes.size(), NULL, 0);
    }
    else
    {
      com = new Community(topNodes2, topNodes.size(), NULL, 0);
      unmergedCom = NULL;
    }

    delete[] topNodes2;
    return com;
  }

  Community *mergeNodes(Node **const &nodes, const int &numNodes)
  {
    Array<Array<Node *> > typeIdToNodesMap;
    typeIdToNodesMap.growToSize(typeToConstNodesMap_.size());
    for (int i = 0; i < numNodes; i++)
    {
      Node *node = nodes[i];
      typeIdToNodesMap[((ConstNode *)node)->typeId()].append(node);
    }

    //merge nodes for each type
    Array<Node *> singleNodes;
    Array<NodeArr *> clusts;
    for (int t = 0; t < typeIdToNodesMap.size(); t++)
    {
      Array<Node *> &nodes = typeIdToNodesMap[t];
      if (nodes.size() > 0)
        mergeNodesHelper(singleNodes, clusts, nodes);
    }

    //create community
    Node **singleNodesCopy = new Node *[singleNodes.size()];
    for (int i = 0; i < singleNodes.size(); i++)
      singleNodesCopy[i] = singleNodes[i];

    NodeArr **clustsCopy = new NodeArr *[clusts.size()];
    for (int i = 0; i < clusts.size(); i++)
      clustsCopy[i] = clusts[i];

    Community *com = new Community(singleNodesCopy, singleNodes.size(), clustsCopy, clusts.size());
    delete[] singleNodesCopy;

    for (int i = 0; i < numNodes; i++)
      nodes[i]->deleteSamplePathSet();

    cout << "  merge " << numNodes << " -> " << singleNodes.size() + clusts.size() << endl;

    return com;
  }

  void mergeNodesHelper(Array<Node *> &singleNodes, Array<NodeArr *> &clusts, const Array<Node *> &nodes)
  {
    Array<Node *> simNodes(20);

    int startIdx;
    if (nodes[0]->hitTime() != 0.0)
    {
      simNodes.append(nodes[0]);
      startIdx = 1;
    }
    else
    {
      singleNodes.append(nodes[0]);
      if (nodes.size() == 1)
        return;
      simNodes.append(nodes[1]);
      startIdx = 2;
    }

    //! Dom
    int num_distance_symmetric_clusters = 0;

    for (int i = startIdx; i < nodes.size() + 1; i++)
    {
      if (i == nodes.size() || fabs(nodes[i]->hitTime() - nodes[i - 1]->hitTime()) > mergeTimeThresh_)
      {
        if (simNodes.size() > 1)
        {
          if (MERGE_NODES_BY_JS)
            mergeNodesByJSDiv(simNodes, singleNodes, clusts);
          else
            mergeNodesByHitTimes(simNodes, singleNodes, clusts);
        }
        else
        {
          cout << "Sngl nd" << endl;
          singleNodes.append(simNodes[0]);
        }
        simNodes.clear();
        //! Dom
        num_distance_symmetric_clusters += 1;
      }
      if (i < nodes.size())
        simNodes.append(nodes[i]);
    }

    //! Dom
    cout << "Num dist sym clusters: " << num_distance_symmetric_clusters << endl;
  }

  void mergeNodesByJSDiv(const Array<Node *> &nodes, Array<Node *> &retSingleNodes, Array<NodeArr *> &retClusts)
  {
    Array<NodeCluster *> clusts(nodes.size());
    for (int i = 0; i < nodes.size(); i++)
      clusts.append(new NodeCluster(nodes[i], jsTopN_));

    cout << "DistSymClust Size: " << clusts.size() << endl;


    bool mergeOccurred = true;
    while (mergeOccurred)
    {
      mergeOccurred = false;
      pair<int, int> bestPair(-1, -1);
      double smallestDiv = DBL_MAX;
      for (int i = 0; i < clusts.size(); i++)
        for (int j = i + 1; j < clusts.size(); j++)
        {
          double div = clusts[i]->jsDiv(*clusts[j]);
          if (div < smallestDiv && div < jsThresh_)
          {
            smallestDiv = div;
            bestPair.first = i;
            bestPair.second = j;
          }
          // if (div > jsThresh_)
          // {
          //   cout << "Exceeded threshold!" << endl;
          // }
        }

      if (smallestDiv < DBL_MAX)
      {
        mergeOccurred = true;
        int i = bestPair.first;
        int j = bestPair.second;
        NodeCluster *clusti = clusts[i];
        NodeCluster *clustj = clusts[j];
        clusti->merge(*clustj);
        clusts.removeItemFastDisorder(j);
        delete clustj;
        //cout << "  SMALLEST_DIV " << smallestDiv << " , i, j = " << i << " , " << j << endl;
      }
    }

    //int numSingle = 0, numClust = 0;
    //for (int i = 0; i < clusts.size(); i++)
    //  if (nodes.size()==1) numSingle++;
    //  else                 numClust++;
    //cout << "#nodes " << nodes.size() << " , #single " << numSingle << " , #clust " << numClust << endl;

    for (int i = 0; i < clusts.size(); i++)
    {
      const Array<Node *> &nodes = clusts[i]->nodes();
      if (nodes.size() == 1)
      {
        retSingleNodes.append(nodes[0]);
      }
      else
      {
        Node **nodes2 = new Node *[nodes.size()];
        for (int i = 0; i < nodes.size(); i++)
          nodes2[i] = nodes[i];
        NodeArr *nodeArr = new NodeArr(nodes2, nodes.size());
        retClusts.append(nodeArr);
      }
    }

    clusts.deleteItemsAndClear();
  }

  void mergeNodesByHitTimes(const Array<Node *> &nodes, Array<Node *> &retSingleNodes, Array<NodeArr *> &retClusts)
  {
    Array<Node *> clust(20);
    clust.append(nodes[0]);
    double aveHitTime = nodes[0]->hitTime();

    for (int i = 1; i < nodes.size() + 1; i++)
    {
      if (i == nodes.size() || fabs(nodes[i]->hitTime() - aveHitTime) > mergeTimeThresh_)
      {
        if (clust.size() > 1)
        {
          Node **nodes = new Node *[clust.size()];
          for (int j = 0; j < clust.size(); j++)
            nodes[j] = clust[j];
          NodeArr *nodeArr = new NodeArr(nodes, clust.size());
          retClusts.append(nodeArr);
        }
        else
        {
          retSingleNodes.append(clust[0]);
        }
        clust.clear();
        aveHitTime = 0;
      }

      if (i < nodes.size())
      {
        clust.append(nodes[i]);
        double totalTime = aveHitTime * (clust.size() - 1) + nodes[i]->hitTime();
        aveHitTime = totalTime / clust.size();
      }
    }
  }
};

inline ostream &operator<<(ostream &out, const Graph &g) { return g.print(out); }

#endif
