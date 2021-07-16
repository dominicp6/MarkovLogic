#ifndef RWLEARNER_H_OCT_11_2009
#define RWLEARNER_H_OCT_11_2009

#include "hashint.h"
#include "timer.h"
#include "node.h"
#include "parser.h"

class RWLearner
{
private:
  Array<Type *> types_;
  Array<string> typeNames_; //look at types in this order
  Array<Predicate *> foPreds_;
  Array<Graph *> graphs_;
  Timer timer_;
  string outFile_;
  string unmergedOutFile_;
  string outSrcAndClustFile_;
  Array<ConstNodeTree *> constNodeTrees_;

public:
  RWLearner(const string &declFile, const string &dbFile, const string &typeFile, const int &numSamples, const int &maxLen,
            const double &delta, const double &eps, const double &timeThresh, const double &mergeTimeThresh, const double &jsThresh,
            const int &jsTopN, const string &outFile, const string &unmergedOutFile, const string &outSrcAndClustFile)
      : outFile_(outFile), unmergedOutFile_(unmergedOutFile), outSrcAndClustFile_(outSrcAndClustFile)
  {
    //! START: Initialise RWLearner

    double startSec = timer_.time();
    Parser parser;
    cout << "reading predicate declaration..." << endl;
    parser.readDeclFile(declFile, types_, foPreds_);
    parser.readTypeFile(typeFile, typeNames_);
    Util::assertt(checkTypes(), "error in types", -1);

    cout << "  TYPES" << endl;
    for (int i = 0; i < typeNames_.size(); i++)
      cout << typeNames_[i] << endl;
    cout << endl;

    cout << "creating graph from " << dbFile << endl;
    ConstNodeTree *constNodeTree;
    Graph *graph = parser.createGraph(dbFile, types_, foPreds_, constNodeTree);
    constNodeTrees_.append(constNodeTree);
    graph->setNumSamples(numSamples);
    graph->setMaxLen(maxLen);
    graph->setDelta(delta);
    graph->setEps(eps);
    graph->setTypeNames(typeNames_);
    graph->setTimeThresh(timeThresh);
    graph->setMergeTimeThresh(mergeTimeThresh);
    graph->setJSThresh(jsThresh);
    graph->setJSTopN(jsTopN);
    graphs_.append(graph);
    cout << "#ConstNodes = " << graph->numConstNodes() << endl;
    cout << "#PredNodes  = " << graph->numPredNodes() << endl;
    cout << "#Edges      = " << graph->numEdges() << endl;

    cout << "TIMER init RWLearner took ";
    timer_.printTime(cout, timer_.time() - startSec);
    cout << endl;

    //! END: Initialise RWLearner
  }

  void run()
  {

    double startSec = timer_.time();
    Array<Array<Community *> *> comsByGraph(graphs_.size());
    Array<Array<Community *> *> unmergedComsByGraph(graphs_.size());
    Array<Array<int> *> srcNodesByGraph(graphs_.size());
    
    //! START: Running Random Walks Over Each Node
    for (int i = 0; i < graphs_.size(); i++)
    {
      Array<Community *> *unmergedComs = NULL;
      Array<int> *srcNodes = NULL;
      Array<Community *> *coms = graphs_[i]->runRandomWalks(unmergedComs, srcNodes);
      comsByGraph.append(coms);
      unmergedComsByGraph.append(unmergedComs);
      srcNodesByGraph.append(srcNodes);
    }
    


    cout << endl;
    printCommunities(cout, comsByGraph);
    cout << endl;
    printCommunitySizes(cout, comsByGraph);
    writeCommunitiesAsDB(comsByGraph, outFile_);
    writeCommunitiesAsDB(unmergedComsByGraph, unmergedOutFile_);
    writeSrcAndClusts(comsByGraph, unmergedComsByGraph, srcNodesByGraph, outSrcAndClustFile_);

    for (int i = 0; i < comsByGraph.size(); ++i)
    {
      Array<Community *> *coms = comsByGraph[i];
      coms->deleteItemsAndClear();
      delete coms;
      coms = unmergedComsByGraph[i];
      coms->deleteItemsAndClear();
      delete coms;
    }
    srcNodesByGraph.deleteItemsAndClear();
    cout << "TIMER run RWLearner took ";
    timer_.printTime(cout, timer_.time() - startSec);
    cout << endl;
    //! END: Running Random Walks Over Each Node
  }

  ~RWLearner()
  {
    types_.deleteItemsAndClear();
    for (int i = 0; i < foPreds_.size(); i++)
    {
      Predicate *foPred = foPreds_[i];
      const Array<Constant *> &argTypes = foPred->args();
      for (int j = 0; j < argTypes.size(); j++)
        delete argTypes[j];
    }
    foPreds_.deleteItemsAndClear();
    graphs_.deleteItemsAndClear();
    constNodeTrees_.deleteItemsAndClear();
  }

private:
  bool checkTypes()
  {
    StringSet sset;
    for (int i = 0; i < typeNames_.size(); i++)
      sset.insert(typeNames_[i]);
    if ((unsigned int)types_.size() != sset.size())
      return false;
    for (int i = 0; i < types_.size(); i++)
      if (sset.find(types_[i]->name()) == sset.end())
        return false;
    return true;
  }

  void printCommunities(ostream &out, const Array<Array<Community *> *> &comsByGraph) const
  {
    for (int i = 0; i < comsByGraph.size(); i++)
    {
      out << "GRAPH " << i << endl;
      Array<Community *> &coms = *(comsByGraph[i]);
      for (int j = 0; j < coms.size(); j++)
      {
        out << "COMMUNITY " << j << endl;
        out << *coms[j] << endl;
      }
    }
  }

  void printCommunitySizes(ostream &out, const Array<Array<Community *> *> &comsByGraph) const
  {
    Array<int> sizeToCnt;
    sizeToCnt.growToSize(1000, 0);
    for (int i = 0; i < comsByGraph.size(); i++)
    {
      Array<Community *> &coms = *(comsByGraph[i]);
      for (int j = 0; j < coms.size(); j++)
      {
        int sz = coms[j]->totalClusts();
        if (sz >= sizeToCnt.size())
          sizeToCnt.growToSize(sz + 1, 0);
        sizeToCnt[sz]++;
      }
    }
    for (int i = 0; i < sizeToCnt.size(); i++)
      if (sizeToCnt[i] > 0)
        out << "COM_SIZE " << i << " : " << sizeToCnt[i] << endl;
  }

  void writeCommunitiesAsDB(const Array<Array<Community *> *> &comsByGraph, const string &outFile) const
  {
    ofstream out(outFile.c_str());
    for (int i = 0; i < comsByGraph.size(); i++)
    {
      Array<Community *> &coms = *(comsByGraph[i]);

      out << "#START_GRAPH  #COMS " << coms.size() << endl
          << endl;
      for (int j = 0; j < coms.size(); j++)
      {
        ostringstream oss;
        int numAtoms = writeCommunityAsDB(oss, *coms[j]);
        out << "#START_DB  " << j << "  #COMS  1  #NUM_ATOMS " << numAtoms << endl;
        out << oss.str();
        out << "#END_DB" << endl
            << endl;
      }
      out << "#END_GRAPH" << endl;
    }
    out.close();
  }

  int writeCommunityAsDB(ostream &out, const Community &com) const
  {
    IntSet constIds;
    IntToStringMap constIdToNameMap;
    getConstIdsAndConstIdToNameMap(constIds, constIdToNameMap, com);

    Node **singleNodes = com.singleNodes();
    int numSingleNodes = com.numSingleNodes();
    NodeArr **clusts = com.clusts();
    int numClusts = com.numClusts();

    StringHashArray atomStrs;

    for (int i = 0; i < numSingleNodes; i++)
      createAtomStrs((ConstNode *)singleNodes[i], constIds, constIdToNameMap, atomStrs);

    for (int i = 0; i < numClusts; i++)
    {
      Node **nodes = clusts[i]->nodes();
      int numNodes = clusts[i]->size();
      for (int j = 0; j < numNodes; j++)
        createAtomStrs((ConstNode *)nodes[j], constIds, constIdToNameMap, atomStrs);
    }

    for (int i = 0; i < atomStrs.size(); i++)
      out << atomStrs[i] << endl;

    return atomStrs.size();
  }

  void writeSrcAndClusts(const Array<Array<Community *> *> &comsByGraph, const Array<Array<Community *> *> &unmergedComsByGraph,
                         const Array<Array<int> *> &srcNodesByGraph, const string &outFile) const
  {
    Util::assertt(comsByGraph.size() == unmergedComsByGraph.size(), "expect comsByGraph.size() == unmergedComsByGraph.size()", -1);
    Util::assertt(comsByGraph.size() == srcNodesByGraph.size(), "expect comsByGraph.size() == srcNodesByGraph.size()", -1);

    ofstream out(outFile.c_str());
    for (int i = 0; i < comsByGraph.size(); i++)
    {
      Array<Community *> &coms = *(comsByGraph[i]);
      Array<Community *> &unmergedComs = *(unmergedComsByGraph[i]);
      Array<int> &srcNodes = *(srcNodesByGraph[i]);

      Util::assertt(coms.size() == unmergedComs.size(), "expect coms.size() == unmergedComs.size()", -1);
      Util::assertt(coms.size() == srcNodes.size(), "expect coms.size() == srcNodes.size()", -1);

      out << "#START_GRAPH  #COMS " << coms.size() << endl
          << endl;
      for (int j = 0; j < coms.size(); j++)
      {
        int numClusts, numSingles, numNodes;
        ostringstream oss;
        writeSrcAndClusts(oss, *coms[j], *unmergedComs[j], srcNodes[j], numSingles, numClusts, numNodes);
        out << "#START_DB  " << j << "  #NUM_SINGLES " << numSingles << "  #NUM_CLUSTS " << numClusts << "  #NUM_NODES " << numNodes << endl;
        out << oss.str();
        out << "#END_DB" << endl
            << endl;
      }
      out << "#END_GRAPH" << endl;
    }
    out.close();
  }

  void writeSrcAndClusts(ostream &out, const Community &com, const Community &unmergedCom, const int &srcNode,
                         int &numSingleNodes, int &numClusts, int &numNodes) const
  {
    Node **singleNodes = com.singleNodes();
    numSingleNodes = com.numSingleNodes();
    NodeArr **clusts = com.clusts();
    numClusts = com.numClusts();

    out << "SRC " << srcNode << endl;

    for (int i = 0; i < numSingleNodes; i++)
      out << Util::intToString(((ConstNode *)singleNodes[i])->constant()->id()) << endl;

    for (int i = 0; i < numClusts; i++)
    {
      out << "CLUST " + Util::intToString(i) << "  ";
      Node **nodes = clusts[i]->nodes();
      int numNodes = clusts[i]->size();
      for (int j = 0; j < numNodes; j++)
        out << Util::intToString(((ConstNode *)nodes[j])->constant()->id()) << " ";
      out << endl;
    }

    singleNodes = unmergedCom.singleNodes();
    numNodes = unmergedCom.numSingleNodes();
    out << "NODES  ";
    for (int i = 0; i < numNodes; i++)
      out << Util::intToString(((ConstNode *)singleNodes[i])->constant()->id()) << " ";
    out << endl;
  }

  void getConstIdsAndConstIdToNameMap(IntSet &constIds, IntToStringMap &constIdToNameMap, const Community &com) const
  {
    Node **singleNodes = com.singleNodes();
    int numSingleNodes = com.numSingleNodes();
    NodeArr **clusts = com.clusts();
    int numClusts = com.numClusts();
    int totalNodes = com.totalNodes();

    for (int i = 0; i < numSingleNodes; i++)
    {
      ConstNode *constNode = (ConstNode *)singleNodes[i];
      int id = constNode->constant()->id();
      constIds.insert(id);
      //constIdToNameMap[id] = constNode->constant()->name();
      constIdToNameMap[id] = "NODE_" + Util::intToString(id);
    }

    for (int i = 0; i < numClusts; i++)
    {
      Node **nodes = clusts[i]->nodes();
      int numNodes = clusts[i]->size();
      for (int j = 0; j < numNodes; j++)
      {
        ConstNode *constNode = (ConstNode *)nodes[j];
        int id = constNode->constant()->id();
        constIds.insert(id);
        constIdToNameMap[id] = "CLUST_" + Util::intToString(i);
      }
    }
    Util::assertt((int)constIds.size() == totalNodes, "expect #unique constIds == #nodes in com", -1);
  }

  void createAtomStrs(const ConstNode *const &constNode, const IntSet &constIds, IntToStringMap &constIdToNameMap,
                      StringHashArray &atomStrs) const
  {
    const Array<PredNode *> &atoms = constNode->predNodes();
    for (int i = 0; i < atoms.size(); i++)
    {
      string atomStr = createAtomStr(atoms[i], constIds, constIdToNameMap);
      if (!atomStr.empty())
        atomStrs.append(atomStr);
    }
  }

  string createAtomStr(const PredNode *const &atom, const IntSet &constIds, IntToStringMap &constIdToNameMap) const
  {
    const Array<Constant *> &args = atom->args();
    if (!argsInSet(args, constIds))
      return "";
    return createAtomStr(atom, constIdToNameMap);
  }

  bool argsInSet(const Array<Constant *> &args, const IntSet &constIds) const
  {
    for (int i = 0; i < args.size(); i++)
      if (constIds.find(args[i]->id()) == constIds.end())
        return false;
    return true;
  }

  string createAtomStr(const PredNode *const &atom, IntToStringMap &constIdToNameMap) const
  {
    string predName = atom->predicate()->name();
    string retAtomStr = predName + "(";

    const Array<Constant *> &args = atom->args();
    for (int i = 0; i < args.size(); i++)
    {
      int id = args[i]->id();
      string name = constIdToNameMap[id];
      retAtomStr += name + ((i < args.size() - 1) ? "," : ")");
    }
    return retAtomStr;
  }
};

#endif
