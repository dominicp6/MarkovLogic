#ifndef COMCREATOR_H_OCT_23_2009
#define COMCREATOR_H_OCT_23_2009

#include <iostream>
#include <ctype.h>
#include <unistd.h>
#include <sys/time.h>
using namespace std;
#include "util.h"
#include "uuutil.h"
#include "timer.h"
#include "path.h"
#include "comgnder.h"

typedef hash_map<Path *, NodeIdsSet *, HashPath, EqualPath> PathToNodeIdsSetMap;
int compareInts(const void *a, const void *b) { return (*(int *)a - *(int *)b); }

class ComCreator
{
private:
  Array<string> ldbFiles_;
  Array<string> uldbFiles_;
  Array<string> srcClustsFiles_;
  string declFile_;
  int minSup_;
  string outFile_;
  string learnWtsExec_;
  char command_[10000];
  Timer timer_;
  double mergeSec_;
  double comGndSec_;

  StringToIntMap typeNameToIdMap_;
  Array<Array<int> *> relIdToTypeIdsMap_;
  Array<string> relIdToNameMap_;
  StringToIntMap relNameToIdMap_;
  StringToIntMap constNameToIdMap_;
  Array<string> constIdToNameMap_;
  StringToStringMap relNameToDeclMap_;

  Array<PathSet *> pathSetByLen_;
  bool mergePaths_;
  int subsumeCnt_;

public:
  ComCreator(const Array<string> &ldbFiles, const Array<string> &uldbFiles, const Array<string> &srcClustsFiles,
             const string &declFile, const int &minSup, const string &outFile, const string &learnWtsExec, const bool &mergePaths)
      : ldbFiles_(ldbFiles), uldbFiles_(uldbFiles), srcClustsFiles_(srcClustsFiles), declFile_(declFile), minSup_(minSup),
        outFile_(outFile), learnWtsExec_(learnWtsExec), mergeSec_(0.0), comGndSec_(0.0), mergePaths_(mergePaths), subsumeCnt_(0)
  {
    Util::assertt(ldbFiles_.size() == uldbFiles_.size(), "expect ldbFiles_.size() == uldbFiles_.size()", -1);
    Util::assertt(ldbFiles_.size() == srcClustsFiles_.size(), "expect ldbFiles_.size() == srcClustsFiles_.size()", -1);
    pathSetByLen_.growToSize(11, NULL);
    readDeclFile(declFile_);
  }

  ~ComCreator()
  {
    relIdToTypeIdsMap_.deleteItemsAndClear();
    for (int i = 0; i < pathSetByLen_.size(); i++)
      delete pathSetByLen_[i];
  }

  void createComs()
  {
    double begSec = timer_.time();
    mergeSec_ = 0.0;
    struct timeval tvA;
    struct timezone tzpA;
    gettimeofday(&tvA, &tzpA);

    Array<PathToNodeIdsSetMap> pathToNodeIdsSetArr;
    pathToNodeIdsSetArr.growToSize(ldbFiles_.size());

    //!START: Perform DFS on the lifted hypergraph
    double startSec = timer_.time();
    for (int i = 0; i < ldbFiles_.size(); i++)
    {
      cout << "Creating communities for " << i + 1 << " / " << ldbFiles_.size() << "  " << ldbFiles_[i] << endl;
      string ldbFile = ldbFiles_[i];
      string uldbFile = uldbFiles_[i];
      string srcClustsFile = srcClustsFiles_[i];
      createComs(ldbFile, uldbFile, srcClustsFile, i, pathToNodeIdsSetArr[i]);
    }
    cout << "TIMER DFS on lifted hypergraph took ";
    timer_.printTime(cout, timer_.time() - startSec);
    cout << endl;
    //!END: Perform DFS on the lifted hypergraph

    PathSet pathSet;
    //!START: Removing duplicate paths
    double customStartSec = timer_.time();
    getUniquePaths(pathSet, pathToNodeIdsSetArr);
    cout << "TIMER getting unique paths took ";
    timer_.printTime(cout, timer_.time() - customStartSec);
    cout << endl;
    //!END: Removing duplicate paths
    //!START: Accumulating support
    customStartSec = timer_.time();
    accumSupport(pathSet, pathToNodeIdsSetArr);
    cout << "TIMER accummulating support took ";
    timer_.printTime(cout, timer_.time() - customStartSec);
    cout << endl;
    //!END: Accumulating support
    //!START: Pruning paths
    customStartSec = timer_.time();
    prunePaths(pathSet);
    cout << "TIMER prunning paths took ";
    timer_.printTime(cout, timer_.time() - customStartSec);
    cout << endl;
    //!END: Pruning paths
    populatePathSetByLen(pathSet);
    if (mergePaths_)
    {
      writePathNumSupport(cout, "\nBEFORE MERGE");
      mergePaths();
    }

    writePaths();
    writePathSizes(cout);
    writePathNumSupport(cout, "FINAL PATHS");

    cleanUp(pathToNodeIdsSetArr);

    double secTaken = timer_.time() - begSec;
    cout << "TOTAL merge      took ";
    timer_.printTime(cout, mergeSec_);
    cout << endl;
    cout << "TOTAL nonMerge   took ";
    timer_.printTime(cout, secTaken);
    cout << endl;
    cout << "TOTAL comGnder   took ";
    timer_.printTime(cout, comGndSec_);
    cout << endl;
    struct timeval tvB;
    struct timezone tzpB;
    gettimeofday(&tvB, &tzpB);
    cout << "TOTAL wallClock  took ";
    timer_.printTime(cout, tvB.tv_sec - tvA.tv_sec);
    cout << endl;
    cout << "TOTAL CreateComs took ";
    timer_.printTime(cout, mergeSec_ + secTaken);
    cout << endl;
  }

  ///////////////////////////// CREATE COM WITH DFS //////////////////////////////////////////////
private:
  void createComs(const string &ldbFile, const string &uldbFile, const string &srcClustsFile, const int &domId, PathToNodeIdsSetMap &pathToNodeIdsSet)
  {
    ifstream ldbIn(ldbFile.c_str());
    Util::assertGoodInStream(ldbIn, ldbFile);
    ifstream uldbIn(uldbFile.c_str());
    Util::assertGoodInStream(uldbIn, uldbFile);
    ifstream clustIn(srcClustsFile.c_str());
    Util::assertGoodInStream(clustIn, srcClustsFile);

    //get the number of communities
    int numCom, numComDFS = 0, numComFail = 0;
    string buf, noop;
    getline(ldbIn, buf);
    Util::assertt(!buf.empty(), "expect non-empty" + ldbFile, -1);
    istringstream iss(buf);
    iss >> noop >> noop >> numCom;

    for (int i = 0; i < numCom; i++)
    {
      cout << "reading com " << i + 1 << " / " << numCom << "  ";
      string comIdStr = Util::intToString(domId) + "_" + Util::intToString(i);

      //read the input files
      Array<string> clustAtoms, gndAtoms;
      int srcId;
      Array<int> singleNodeIds, allNodeIds;
      Array<Array<int> *> clustIdToNodeIds;
      getAtoms(ldbIn, clustAtoms);
      getAtoms(uldbIn, gndAtoms);
      getSrcClusts(clustIn, srcId, singleNodeIds, clustIdToNodeIds, allNodeIds);
      //print(cout, clustAtoms, gndAtoms, srcId, singleNodeIds, clustIdToNodeIds, allNodeIds);

      //create the community
      Path *path = NULL;
      NodeIds *supNodeIds = NULL; //constIds of true gnding for community

      path = createComDFS(clustAtoms, gndAtoms, srcId, comIdStr, domId, singleNodeIds, clustIdToNodeIds, supNodeIds);
      if (path)
      {
        numComDFS++;
        storePath(path, pathToNodeIdsSet, supNodeIds);
      }
      else
        numComFail++;
      clustIdToNodeIds.deleteItemsAndClear();
    }
    ldbIn.close();
    uldbIn.close();
    clustIn.close();

    cout << "  #ComDFS   " << numComDFS << endl;
    cout << "  #ComFail  " << numComFail << endl;
    cout << "  #ComTotal " << numComDFS + numComFail << endl;
  }

  void getAtoms(ifstream &in, Array<string> &atoms)
  {
    string buf, noop;
    while (!Util::startsWith(buf, "#START_DB"))
      getline(in, buf);
    int numAtoms;
    istringstream iss(buf);
    iss >> noop >> noop >> noop >> noop >> noop >> numAtoms;
    for (int j = 0; j < numAtoms; j++)
    {
      getline(in, buf);
      atoms.append(Util::trim(buf));
    }
  }

  void getSrcClusts(ifstream &in, int &srcId, Array<int> &singleNodeIds, Array<Array<int> *> &clustIdToNodeIds, Array<int> &allNodeIds)
  {
    string buf, noop;
    while (!Util::startsWith(buf, "#START_DB"))
      getline(in, buf);
    int numSingles, numClusts, numNodes;
    istringstream iss(buf);
    iss >> noop >> noop >> noop >> numSingles >> noop >> numClusts >> noop >> numNodes;

    //get src id
    getline(in, buf);
    istringstream iss2(buf);
    iss2 >> noop >> srcId;

    //get single ids
    singleNodeIds.clear();
    singleNodeIds.growToSize(numSingles);
    for (int i = 0; i < numSingles; i++)
    {
      getline(in, buf);
      istringstream iss(buf);
      int nodeId;
      iss >> nodeId;
      singleNodeIds[i] = nodeId;
    }

    //get clustId to node ids
    clustIdToNodeIds.clear();
    clustIdToNodeIds.growToSize(numClusts);
    for (int i = 0; i < numClusts; i++)
    {
      getline(in, buf);
      buf += " -1";
      istringstream iss(buf);
      int clustId;
      iss >> noop >> clustId;
      Util::assertt(i == clustId, "expect i == clustId", -1);

      Array<int> *nodeIds = new Array<int>;
      clustIdToNodeIds[i] = nodeIds;
      int nodeId;
      while (true)
      {
        iss >> nodeId;
        if (nodeId < 0)
          break;
        nodeIds->append(nodeId);
      }
    }

    int nodeId;
    allNodeIds.clear();
    allNodeIds.growToSize(numNodes);
    getline(in, buf);
    istringstream iss3(buf);
    iss3 >> noop;
    for (int i = 0; i < numNodes; i++)
    {
      iss3 >> nodeId;
      allNodeIds[i] = nodeId;
    }
  }

  Path *createComDFS(const Array<string> &clustAtoms, const Array<string> &gndAtoms, const int &srcId, const string &comIdStr, const int &domId,
                     const Array<int> &singleNodeIds, const Array<Array<int> *> &clustIdToNodeIds, NodeIds *&supNodeIds)
  {
    cout << "createComDFS..." << endl;
    Graph *graph = new Graph(clustAtoms, gndAtoms, srcId, singleNodeIds, clustIdToNodeIds);
    //cout << *graph << endl;
    Array<GndEdge *> gndEdges;
    Array<GndNode *> gndNodes;
    bool ok = graph->extractCom(gndEdges, gndNodes);
    if (!ok)
    {
      cout << "  createComDFS failed! " << endl;
      delete graph;
      return false;
    }
    //cout << "--------------- LITERALS -------------------" << endl;
    //for (int j = 0; j < gndEdges.size(); j++) cout << *gndEdges[j] << endl;

    Array<string> atomStrs(gndEdges.size());
    for (int j = 0; j < gndEdges.size(); j++)
      atomStrs.append(gndEdges[j]->atomStr());
    Path *path = createPath(atomStrs);
    if (path == NULL)
      return NULL;

    //get the ids of the GndNodes
    Array<int> gndNodeIds(gndNodes.size());
    for (int i = 0; i < gndNodes.size(); i++)
      gndNodeIds.append(gndNodes[i]->getNodeIds());
    qsort((int *)gndNodeIds.getItems(), gndNodeIds.size(), sizeof(int), compareInts);
    supNodeIds = new NodeIds(gndNodeIds, srcId, comIdStr, domId);

    delete graph;
    return path;
  }

  void storePath(Path *&path, PathToNodeIdsSetMap &pathToNodeIdsSet, NodeIds *const &supNodeIds)
  {
    NodeIdsSet *nodeIdsSet;
    PathToNodeIdsSetMap::iterator it = pathToNodeIdsSet.find(path);
    if (it == pathToNodeIdsSet.end())
    {
      nodeIdsSet = new NodeIdsSet;
      pathToNodeIdsSet[path] = nodeIdsSet;
    }
    else
    {
      nodeIdsSet = (*it).second;
      delete path;
      path = (*it).first;
    }

    pair<NodeIdsSet::iterator, bool> pr = nodeIdsSet->insert(supNodeIds);

    if (pr.second)
    { /*path->incrSupport(); path->addSupportIdStr(supNodeIds->comIdStr());*/
    }
    else
      delete supNodeIds;
  }

  void prunePaths(PathSet &pathSet)
  {
    cout << endl
         << "pruning paths..." << endl;
    Array<Path *> toBeRem(pathSet.size());
    for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
    {
      Path *path = (*it);
      if (path->support() < minSup_)
        toBeRem.append(path);
    }

    for (int i = 0; i < toBeRem.size(); i++)
      pathSet.erase(toBeRem[i]);

    cout << "TOTAL_PATHS        " << toBeRem.size() + pathSet.size() << endl;
    cout << "NUM_PATHS_PRUNED   " << toBeRem.size() << endl;
    cout << "NUM_PATHS_RETAINED " << pathSet.size() << endl;
  }

  void getUniquePaths(PathSet &pathSet, const Array<PathToNodeIdsSetMap> &pathToNodeIdsSetArr)
  {
    cout << "getting unique coms...";
    for (int i = 0; i < pathToNodeIdsSetArr.size(); i++)
    {
      PathToNodeIdsSetMap &pathToNodeIdsSet = pathToNodeIdsSetArr[i];
      for (PathToNodeIdsSetMap::iterator it = pathToNodeIdsSet.begin(); it != pathToNodeIdsSet.end(); it++)
        pathSet.insert((*it).first);
    }
    cout << "#unique coms " << pathSet.size() << endl;
  }

  //accumulate support across domains
  void accumSupport(PathSet &pathSet, const Array<PathToNodeIdsSetMap> &pathToNodeIdsSetArr)
  {
    double begSec = timer_.time();
    struct timeval tvA;
    struct timezone tzpA;
    gettimeofday(&tvA, &tzpA);
    //removePaths(pathSet, pathToNodeIdsSetArr);

    cout << endl
         << "accumulating support..." << endl;
    //store the paths by their lengths
    Array<PathSet *> pathSetByLen;
    populatePathSetByLen(pathSetByLen, pathSet);
    Array<Path *> sortedPaths;
    getSortedPaths(sortedPaths, pathSetByLen); //sorted longest to shortest

    int numPathsIncrSup = 0;
    for (int p = 0; p < sortedPaths.size(); p++)
    {
      Path *path = sortedPaths[p];
      Array<NodeIdsSet> nodeIdsSetByDom;
      nodeIdsSetByDom.growToSize(pathToNodeIdsSetArr.size());
      //cout << "=====Path:  "; printPath(cout, path); cout << endl << endl;

      //accumulate support within domain
      int begSup = 0, endSup = 0;
      for (int i = 0; i < pathToNodeIdsSetArr.size(); i++) //for each domain
      {
        NodeIdsSet &accumNodeIdsSet = nodeIdsSetByDom[i];
        PathToNodeIdsSetMap &pathToNodeIdsSet = pathToNodeIdsSetArr[i];

        //add path's unaccumulated nodeIds to accumNodeIdsSet
        PathToNodeIdsSetMap::const_iterator it = pathToNodeIdsSet.find((Path *)path);
        if (it != pathToNodeIdsSet.end())
        {
          NodeIdsSet *curNodeIdsSet = (*it).second;
          if (curNodeIdsSet)
          {
            for (NodeIdsSet::iterator itt = curNodeIdsSet->begin(); itt != curNodeIdsSet->end(); itt++)
              accumNodeIdsSet.insert(*itt);
          }
        }

        begSup += accumNodeIdsSet.size();
        accumSupportWithinDomain(accumNodeIdsSet, path, pathToNodeIdsSet, pathSetByLen);
        endSup += accumNodeIdsSet.size();
      }
      cout << "accum path " << p << " / " << sortedPaths.size() << " : ";
      if (endSup > begSup)
      {
        cout << "support incr:  " << begSup << " -> " << endSup << endl;
        numPathsIncrSup++;
      }
      else
        cout << endl;

      //accumulate support across domain
      for (int i = 0; i < nodeIdsSetByDom.size(); i++)
      {
        NodeIdsSet &nodeIdsSet = nodeIdsSetByDom[i];
        for (NodeIdsSet::iterator it = nodeIdsSet.begin(); it != nodeIdsSet.end(); it++)
        {
          NodeIds *nodeIds = (*it);
          path->incrSupport();
          path->addSupportIdStr(nodeIds->comIdStr());
        }
      }
    }
    cout << "#path incr support: " << numPathsIncrSup << " / " << pathSet.size() << endl;
    pathSetByLen.deleteItemsAndClear();

    struct timeval tvB;
    struct timezone tzpB;
    gettimeofday(&tvB, &tzpB);
    cout << "accumSupport took wallclock time  ";
    timer_.printTime(cout, tvB.tv_sec - tvA.tv_sec);
    cout << endl;
    cout << "accumSupport took system    time  ";
    timer_.printTime(cout, timer_.time() - begSec);
    cout << endl;
  }

  void removePaths(PathSet &pathSet, const Array<PathToNodeIdsSetMap> &pathToNodeIdsSetArr)
  {
    Array<Path *> remPaths;
    for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
    {
      Path *path = *it;
      int numSup = 0;
      for (int i = 0; i < pathToNodeIdsSetArr.size(); i++)
      {
        PathToNodeIdsSetMap &pathToNodeIdsSet = pathToNodeIdsSetArr[i];
        NodeIdsSet *nodeIdsSet = pathToNodeIdsSet[path];
        if (nodeIdsSet)
          numSup += nodeIdsSet->size();
      }
      if (numSup <= 1)
        remPaths.append(path);
    }

    for (int i = 0; i < remPaths.size(); i++)
      pathSet.erase(remPaths[i]);
    cout << "#Paths (with support 1) removed: " << remPaths.size() << endl;
    cout << "#Paths remaining:                " << pathSet.size() << endl;
  }

  //if pathJ subsumes pathI, add pathJ's support to pathI if no conflicts
  void accumSupportWithinDomain(NodeIdsSet &accumNodeIdsSet, const Path *const &path, const PathToNodeIdsSetMap &pathToNodeIdsSet, const Array<PathSet *> &pathSetByLen)
  {
    //try to accumulate nodeIds of larger paths that subsumes path
    int pathLen = path->numAtoms();
    for (int i = pathSetByLen.size() - 1; i > pathLen; i--)
    {
      if (pathSetByLen[i] == NULL)
        continue;
      PathSet &pathSet = *pathSetByLen[i];
      for (PathSet::iterator itp = pathSet.begin(); itp != pathSet.end(); itp++) //for each larger path
      {
        Path *largerPath = (*itp);
        if (subsumes(largerPath, (Path *)path, false))
        {
          //try adding largerPath's support to path
          PathToNodeIdsSetMap::const_iterator it = pathToNodeIdsSet.find(largerPath);
          if (it != pathToNodeIdsSet.end())
          {
            NodeIdsSet *largerNodeIdsSet = (*it).second;
            if (largerNodeIdsSet)
            {
              for (NodeIdsSet::iterator itl = largerNodeIdsSet->begin(); itl != largerNodeIdsSet->end(); itl++)
              {
                NodeIds &largerNodeIds = *(*itl);
                if (!conflicts(largerNodeIds, accumNodeIdsSet))
                  accumNodeIdsSet.insert(&largerNodeIds);
              }
            }
          }
        }
      }
    }
  }

  bool conflicts(NodeIds &nodeIdsA, const NodeIdsSet &nodeIdsSet)
  {
    if (nodeIdsSet.empty() == 0)
      return false;
    int numIds = INT_MAX;
    for (NodeIdsSet::const_iterator it = nodeIdsSet.begin(); it != nodeIdsSet.end(); it++)
    {
      NodeIds &nodeIdsB = *(*it);
      if (nodeIdsB.ids().size() < numIds)
        numIds = nodeIdsB.ids().size();
    }

    for (NodeIdsSet::const_iterator it = nodeIdsSet.begin(); it != nodeIdsSet.end(); it++)
      if (conflicts(nodeIdsA, *(*it), numIds - 1))
        return true;
    return false;
  }

  bool conflicts(const NodeIds &nodeIdsA, const NodeIds &nodeIdsB, const int &maxSameIds)
  {
    const IntHashArray &idsA = nodeIdsA.ids();
    const IntHashArray &idsB = nodeIdsB.ids();
    if (idsA.lastItem() < idsB[0] || idsB.lastItem() < idsA[0])
      return false;
    int numSame = 0;
    for (int i = 0; i < idsA.size(); i++)
      if (idsB.contains(idsA[i]))
      {
        if (++numSame > maxSameIds)
          return true;
      }
    return false;
  }

  void getSortedPaths(Array<Path *> &sortedPaths, const Array<PathSet *> &pathSetByLen)
  {
    //sort paths longest to shortest
    for (int i = pathSetByLen.size() - 1; i >= 1; i--)
    {
      if (pathSetByLen[i] == NULL)
        continue;
      PathSet &pathSet = *pathSetByLen[i];
      for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
        sortedPaths.append(*it);
    }
    sortedPaths.compress();
  }

  void populatePathSetByLen(PathSet &pathSet)
  {
    for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
    {
      Path *path = (*it);
      PathSet *pathSet = getPathSetByLen(path->numAtoms());
      pathSet->insert(path);
    }
  }

  void populatePathSetByLen(Array<PathSet *> &pathSetByLen, const PathSet &pathSet)
  {
    pathSetByLen.clear();
    pathSetByLen.growToSize(11, NULL);
    for (PathSet::const_iterator it = pathSet.begin(); it != pathSet.end(); it++)
    {
      Path *path = (*it);
      PathSet *ppathSet = getPathSetByLen(path->numAtoms(), pathSetByLen);
      ppathSet->insert(path);
    }
  }

  PathSet *getPathSetByLen(const int &len, Array<PathSet *> &pathSetByLen)
  {
    if (pathSetByLen.size() <= len)
      pathSetByLen.growToSize(len + 1, NULL);
    if (pathSetByLen[len] == NULL)
      pathSetByLen[len] = new PathSet;
    return pathSetByLen[len];
  }

  PathSet *getPathSetByLen(const int &len)
  {
    if (pathSetByLen_.size() <= len)
      pathSetByLen_.growToSize(len + 1, NULL);
    if (pathSetByLen_[len] == NULL)
      pathSetByLen_[len] = new PathSet;
    return pathSetByLen_[len];
  }

  void writePaths()
  {
    ofstream out(outFile_.c_str());
    Util::assertGoodOutStream(out, outFile_);

    Array<Array<Path *> *> pathsBySup;
    pathsBySup.growToSize(1000, NULL);
    int numPaths = 0;

    for (int len = 1; len < pathSetByLen_.size(); len++)
    {
      if (pathSetByLen_[len] == NULL)
        continue;
      PathSet &pathSet = *pathSetByLen_[len];

      for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
      {
        numPaths++;
        Path *path = *it;
        int sup = path->support();

        if (pathsBySup.size() <= sup)
          pathsBySup.growToSize(sup + 1, NULL);
        Array<Path *> *&paths = pathsBySup[sup];
        if (paths == NULL)
          paths = new Array<Path *>(10);
        paths->append(path);
      }
    }

    out << "#START_GRAPH  #COMS " << numPaths << endl
        << endl;

    int cnt = 0;
    for (int sup = pathsBySup.size() - 1; sup >= 1; sup--)
    {
      if (pathsBySup[sup] == NULL)
        continue;

      Array<Path *> &paths = *pathsBySup[sup];
      for (int i = 0; i < paths.size(); i++)
      {
        Path *path = paths[i];
        Atom **atoms = path->atoms();
        int numAtoms = path->numAtoms();
        int support = path->support();
        StringHashArray *supIds = path->supportIdStrs();

        out << "#START_DB  " << cnt++ << "  #COMS  " << support << "  #ATOMS  " << numAtoms << "  SUP_COM ";
        for (int j = 0; j < supIds->size(); j++)
          out << " " << (*supIds)[j];
        out << endl;

        for (int j = 0; j < numAtoms; j++)
        {
          printAtom(out, atoms[j]);
          out << endl;
        }
        out << "#END_DB" << endl
            << endl;

        //StringHashArray& supportIdStrs = *path->supportIdStrs();
        //for (int i = 0; i < supportIdStrs.size(); i++)
        //  out << supportIdStrs[i] << "  ";
        //out << endl << endl;
      }
    }

    out << "#END_GRAPH" << endl;
    out.close();
  }

  void writePathSizes(ostream &out)
  {
    out << endl;
    for (int len = 1; len < pathSetByLen_.size(); len++)
    {
      if (pathSetByLen_[len] == NULL)
        continue;
      if (pathSetByLen_[len]->size() > 0)
        out << "COM_SIZE " << len << " : " << pathSetByLen_[len]->size() << endl;
    }
    out << endl;
  }

  void writePathNumSupport(ostream &out, const string &output)
  {
    out << output << endl;
    Array<int> sizeToCnt;
    sizeToCnt.growToSize(1000, 0);
    for (int len = 1; len < pathSetByLen_.size(); len++)
    {
      PathSet *pathSet = pathSetByLen_[len];
      if (pathSet == NULL)
        continue;

      for (PathSet::iterator it = pathSet->begin(); it != pathSet->end(); it++)
      {
        Path *path = (*it);
        int support = path->support();
        if (support >= sizeToCnt.size())
          sizeToCnt.growToSize(support + 1, 0);
        sizeToCnt[support]++;
      }
    }
    out << endl;
    for (int i = 0; i < sizeToCnt.size(); i++)
      if (sizeToCnt[i] > 0)
        out << "support->#com " << i << " : " << sizeToCnt[i] << endl;
    out << endl;
  }

  void print(ostream &out, const Array<string> &clustAtoms, const Array<string> &gndAtoms, const int &srcId, const Array<int> &singleNodeIds,
             const Array<Array<int> *> &clustIdToNodeIds, const Array<int> &allNodeIds)
  {
    out << "CLUST ATOMS" << endl;
    for (int i = 0; i < clustAtoms.size(); i++)
      out << clustAtoms[i] << endl;
    out << endl;

    out << "GND ATOMS" << endl;
    for (int i = 0; i < gndAtoms.size(); i++)
      out << gndAtoms[i] << endl;
    out << endl;

    out << "SRC ID  " << srcId << endl
        << endl;

    out << "SINGLE NODES";
    for (int i = 0; i < singleNodeIds.size(); i++)
      out << "  " << singleNodeIds[i];
    out << endl;

    out << "CLUST NODES" << endl;
    for (int i = 0; i < clustIdToNodeIds.size(); i++)
    {
      Array<int> &nodeIds = *clustIdToNodeIds[i];
      out << i << ":";
      for (int j = 0; j < nodeIds.size(); j++)
        out << " " << nodeIds[j];
      out << endl;
    }

    out << "ALL NODES" << endl;
    for (int i = 0; i < allNodeIds.size(); i++)
      out << allNodeIds[i] << " ";
    out << endl;
  }

  void printAtom(ostream &out, Atom *const &atom)
  {
    string relName = relIdToNameMap_[atom->relId()];
    out << relName << "(";
    int *constIds = atom->constIds();
    int numConstIds = atom->numConstIds();
    for (int k = 0; k < numConstIds; k++)
      out << "V" << constIds[k] << ((k < numConstIds - 1) ? "," : ")");
  }

  void cleanUp(Array<PathToNodeIdsSetMap> &pathToNodeIdsSetArr)
  {
    Array<Path *> delPaths(pathToNodeIdsSetArr.size());
    for (int i = 0; i < pathToNodeIdsSetArr.size(); i++)
    {
      PathToNodeIdsSetMap &pathToNodeIdsSet = pathToNodeIdsSetArr[i];
      for (PathToNodeIdsSetMap::iterator it = pathToNodeIdsSet.begin(); it != pathToNodeIdsSet.end(); it++)
      {
        delPaths.append((*it).first);
        NodeIdsSet *nodeIdsSet = (*it).second;
        Array<NodeIds *> delNodeIds(nodeIdsSet->size());
        for (NodeIdsSet::iterator itt = nodeIdsSet->begin(); itt != nodeIdsSet->end(); itt++)
          delNodeIds.append(*itt);
        delNodeIds.deleteItemsAndClear();
        delete nodeIdsSet;
      }
    }
    delPaths.deleteItemsAndClear();
  }

  ///////////////////////////// MERGE ////////////////////////////////////////////////////
private:
  void mergePaths()
  {
    double begSec = timer_.time();
    cout << endl
         << "merging paths..." << endl;

    int totalPaths = 0;
    int totalSub = 0;
    for (int i = 1; i < pathSetByLen_.size(); i++)
    {
      if (pathSetByLen_[i] == NULL)
        continue;
      Array<Path *> subsumedPaths(20);
      PathSet &pathSetI = *pathSetByLen_[i];
      for (PathSet::iterator it = pathSetI.begin(); it != pathSetI.end(); it++)
      {
        Path *pathI = (*it);
        bool isSubsumed = false;

        for (int j = pathSetByLen_.size() - 1; j > i; j--)
        {
          if (pathSetByLen_[j] == NULL)
            continue;
          PathSet &pathSetJ = *pathSetByLen_[j];
          for (PathSet::iterator it2 = pathSetJ.begin(); it2 != pathSetJ.end(); it2++)
            if (subsumes(*it2, pathI, true))
            {
              isSubsumed = true;
              break;
            }
          if (isSubsumed)
            break;
        }

        if (isSubsumed)
          subsumedPaths.append(pathI);
      }

      int initSize = pathSetI.size();
      totalPaths += pathSetI.size();
      totalSub += subsumedPaths.size();
      cout << "#SUBSUMED_PATHS_LEN_" << i << " : " << subsumedPaths.size() << " / " << pathSetI.size() << endl;
      for (int j = 0; j < subsumedPaths.size(); j++)
        pathSetI.erase(subsumedPaths[j]);

      Util::assertt((int)pathSetI.size() == initSize - subsumedPaths.size(), "wrong pathSetI size", -1);
    }

    cout << "SUBSUMED: " << totalSub << " / " << totalPaths << endl;
    cout << "merge paths took ";
    timer_.printTime(cout, timer_.time() - begSec);
    cout << endl;
  }

  bool subsumes(Path *const &path0, Path *const &path1, const bool &enforceDiffVar)
  {
    //cout << "--------- " << ++subsumeCnt_ << " ------------------" << endl;
    //cout << "Path0:  "; printPath(cout,path0); cout << endl;
    //cout << "Path1:  "; printPath(cout,path1); cout << endl;
    //cout << endl << endl;

    if (path0->getNumRel() < path1->getNumRel())
    { /*cout << "RETURN FALSE -- #rel" << endl;*/
      return false;
    }

    int maxRelId = relIdToNameMap_.size() - 1;
    Array<int> &relIdToCntMap0 = *path0->getRelIdToCntMap(maxRelId);
    Array<int> &relIdToCntMap1 = *path1->getRelIdToCntMap(maxRelId);
    Util::assertt(relIdToCntMap0.size() == relIdToCntMap1.size(), "expect relIdToCntMaps same size", -1);
    for (int i = 0; i < relIdToCntMap1.size(); i++)
      if (relIdToCntMap0[i] < relIdToCntMap1[i])
      { /*cout << "RETURN FALSE -- relCnt" << endl;*/
        return false;
      }

    int maxTypeId = typeNameToIdMap_.size() - 1;
    Array<IntHashArray> &typeIdToConstsMap0 = *path0->getTypeIdToConstsMap(maxTypeId, relIdToTypeIdsMap_);
    Array<IntHashArray> &typeIdToConstsMap1 = *path1->getTypeIdToConstsMap(maxTypeId, relIdToTypeIdsMap_);
    for (int i = 0; i < typeIdToConstsMap1.size(); i++)
      if (typeIdToConstsMap0[i].size() < typeIdToConstsMap1[i].size())
      { /*cout << "RETURN FALSE -- constCnt" << endl;*/
        return false;
      }

    double asec = timer_.time();
    ComGnder comGnder(path1, path0, relIdToNameMap_.size() - 1, enforceDiffVar, &relIdToNameMap_);
    double tsec = timer_.time() - asec;
    comGndSec_ += tsec;
    bool htg = comGnder.hasTrueGnding();
    //cout << endl << ((htg)?"true  ":"false  ")  << subsumeCnt_ << ": #timeSec " << tsec << "  : "; timer_.printTime(cout, tsec); cout << endl;
    return htg;
  }

  ///////////////////////////// QUICK CHECK TRUE GNDINGS //////////////////////////////////////////////
private:
  Path *createPath(Array<string> &atomStrs)
  {
    Atom **atoms = getAtoms(atomStrs);
    int numAtoms = atomStrs.size();
    Path *path = new Path(atoms, numAtoms);

    Array<int> *constIdToNumAppearMap = Path::getConstIdToNumAppearMap(atoms, numAtoms);
    Path::sortAtoms(atoms, 0, numAtoms - 1, *constIdToNumAppearMap);
    delete constIdToNumAppearMap;

    renumVars(atoms, numAtoms);

    constIdToNumAppearMap = Path::getConstIdToNumAppearMap(atoms, numAtoms);
    Path::sortAtoms(atoms, 0, numAtoms - 1, *constIdToNumAppearMap);
    delete constIdToNumAppearMap;

    path->computeHashCode();
    return path;
  }

  void renumVars(Atom **const &atoms, const int &numAtoms)
  {
    IntToIntMap oldToNewMap;
    for (int i = 0; i < numAtoms; i++)
    {
      Atom *atom = atoms[i];
      int numConstIds = atom->numConstIds();
      for (int j = 0; j < numConstIds; j++)
      {
        int oldId = atom->constId(j);
        IntToIntMap::iterator it = oldToNewMap.find(oldId);
        int newId;
        if (it == oldToNewMap.end())
        {
          newId = oldToNewMap.size();
          oldToNewMap[oldId] = newId;
        }
        else
          newId = (*it).second;
        atom->setConstId(j, newId);
      }
    }
  }

  Atom **getAtoms(const Array<string> &atomStrs)
  {
    Atom **atoms = new Atom *[atomStrs.size()];
    int atomCnt = 0;
    constNameToIdMap_.clear();
    constIdToNameMap_.clear();
    for (int i = 0; i < atomStrs.size(); i++)
    {
      string relName;
      Array<string> constNames;
      UUUtil::readRelArgs(atomStrs[i], relName, constNames);

      int relId = getRelId(relName);
      Array<int> constIds(constNames.size());
      getConstIds(constIds, constNames);

      atoms[atomCnt++] = new Atom(relId, constIds);
    }
    Util::assertt((int)constNameToIdMap_.size() == constIdToNameMap_.size(), "expect both const maps same size", -1);
    return atoms;
  }

  void getConstIds(Array<int> &constIds, const Array<string> &constNames)
  {
    for (int i = 0; i < constNames.size(); i++)
      constIds.append(getConstId(constNames[i]));
  }

  int getConstId(const string &constName)
  {
    StringToIntMap::iterator it = constNameToIdMap_.find(constName);
    if (it == constNameToIdMap_.end())
    {
      int constId = (int)constNameToIdMap_.size();
      constNameToIdMap_[constName] = constId;
      constIdToNameMap_.append(constName);
      Util::assertt(constIdToNameMap_.size() == constId + 1, "wrong array size2", -1);
      return constId;
    }
    return (*it).second;
  }

  int getRelId(const string &relName)
  {
    StringToIntMap::iterator it = relNameToIdMap_.find(relName);
    Util::assertt(it != relNameToIdMap_.end(), "relName not found", relName, -1);
    return (*it).second;
  }

  ////////////////////////////// RUN ALCHEMY TO CHECK TRUE GNDING ////////////////////
private:
  string createDBFile(const Path *const &path)
  {
    string dbFile = "/scratch/" + outFile_ + "_TMP.db";
    ofstream out(dbFile.c_str());
    Util::assertGoodOutStream(out, dbFile);
    for (int i = 0; i < path->numAtoms(); i++)
    {
      printAtom(out, path->atom(i));
      out << endl;
    }
    out.close();
    return dbFile;
  }

  string createMLNFile(Path *const &path, Path *const &pathDecl, const bool &enforceVarDiff)
  {
    string mlnFile = "/scratch/" + outFile_ + "_TMP.mln";
    ofstream out(mlnFile.c_str());
    Util::assertGoodOutStream(out, mlnFile);

    //write out the predicate declaration
    Array<int> &relIdToCntMap = *pathDecl->getRelIdToCntMap(relNameToIdMap_.size() - 1);
    IntSet uniqRelIds;
    for (int i = 0; i < relIdToCntMap.size(); i++)
    {
      if (relIdToCntMap[i] <= 0)
        continue;
      int relId = i;
      pair<IntSet::iterator, bool> pr = uniqRelIds.insert(relId);
      if (pr.second)
      {
        string relName = relIdToNameMap_[relId];
        out << relNameToDeclMap_[relName] << endl;
      }
    }
    out << endl;

    //write out the formula
    for (int i = 0; i < path->numAtoms(); i++)
    {
      out << "!";
      printAtom2(out, path->atom(i));
      if (i < path->numAtoms() - 1)
        out << " v ";
    }

    if (enforceVarDiff)
    {
      Array<IntHashArray> &typeIdToConstsMap = *path->getTypeIdToConstsMap(typeNameToIdMap_.size() - 1, relIdToTypeIdsMap_);
      for (int t = 0; t < typeIdToConstsMap.size(); t++)
      {
        IntHashArray &constIds = typeIdToConstsMap[t];
        for (int a = 0; a < constIds.size(); a++)
          for (int b = a + 1; b < constIds.size(); b++)
            out << " v v" << constIds[a] << " = "
                << "v" << constIds[b];
      }
      out << endl;
    }

    out.close();
    return mlnFile;
  }

  void printAtom2(ostream &out, Atom *const &atom)
  {
    string relName = relIdToNameMap_[atom->relId()];
    out << relName << "(";
    int *constIds = atom->constIds();
    int numConstIds = atom->numConstIds();
    for (int k = 0; k < numConstIds; k++)
      out << "v" << constIds[k] << ((k < numConstIds - 1) ? "," : ")");
  }

  void printPath(ostream &out, Path *const &path)
  {
    Atom **atoms = path->atoms();
    int numAtoms = path->numAtoms();
    for (int i = 0; i < numAtoms; i++)
    {
      printAtom(out, atoms[i]);
      out << "  ";
    }
    out << endl;
  }

  //////////////////////////////// MISC //////////////////////////////////////
private:
  void readDeclFile(const string &declFile)
  {
    ifstream in(declFile.c_str());
    Util::assertGoodInStream(in, declFile);
    string buf;
    while (getline(in, buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//") == 0)
        continue;
      Util::assertt(isalpha(buf.at(0)), "expect predicate declaration to start with alpha", buf, -1);

      string relName;
      Array<string> curTypeNames;
      UUUtil::readRelArgs(buf, relName, curTypeNames);

      StringToIntMap::iterator it = relNameToIdMap_.find(relName);
      if (it == relNameToIdMap_.end())
      {
        int relId = (int)relNameToIdMap_.size();
        relNameToIdMap_[relName] = relId;
        relIdToNameMap_.append(relName);
        Util::assertt(relIdToNameMap_.size() == relId + 1, "wrong array size", -1);
        relNameToDeclMap_[relName] = buf;

        Array<int> *typeIds = new Array<int>(curTypeNames.size());
        for (int t = 0; t < curTypeNames.size(); t++)
        {
          string typeName = curTypeNames[t];
          StringToIntMap::iterator it = typeNameToIdMap_.find(typeName);
          int typeId;
          if (it == typeNameToIdMap_.end())
          {
            typeId = typeNameToIdMap_.size();
            typeNameToIdMap_[typeName] = typeId;
          }
          else
            typeId = (*it).second;
          typeIds->append(typeId);
        }
        relIdToTypeIdsMap_.append(typeIds);
      }
    }
    in.close();
    Util::assertt((int)relNameToIdMap_.size() == relIdToNameMap_.size(), "expect both rel maps to be of same size", -1);
    Util::assertt((int)relIdToTypeIdsMap_.size() == relIdToNameMap_.size(), "expect both rel maps to be of same size", -1);
  }
};

#endif
