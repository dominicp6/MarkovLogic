#ifndef PATHFINDER_H_OCT_23_2009
#define PATHFINDER_H_OCT_23_2009

#include <iostream>
using namespace std;
#include "array.h"
#include "hashstring.h"
#include "timer.h"
#include "util.h"
#include "uutil.h"
#include "atom.h"
#include "path.h"
#include "parser.h"

const int  TWO_PREDS_FREE_VAR = 2; //max free vars in a clause of len 2 or less
const int  TIME_STEP_SEC      = 24*3600;
const bool WRITE_RULES_PER_TIME_STEP = true;

typedef hash_map<int, Array<Atom*>*, HashInt, EqualInt> IntToAtomArrayMap;

class PathFinder
{
 private:
  StringToIntMap relNameToIdMap_;
  Array<string>  relIdToNameMap_;

  StringToIntMap constNameToIdMap_;
  Array<string>  constIdToNameMap_;
  AtomSet        atomSet_;

  int    maxLen_;
  int    maxFreeVar_;
  int    maxVar_;
  double secLimit_;
  string ldbFile_;
  string declFile_;
  string outFile_;

  double startSec_;
  int    prevTimeStep_;
  Array<PathSet*> pathSetByLen_;
  Array<PathSet*> dbPathSetByLen_;
  Timer timer_;

  int   numComs_;

 public:
  PathFinder(const int& maxLen, const int& maxFreeVar, const int& maxVar, const double& hrLimit, const string& ldbFile, 
             const string& declFile, const string outFile)
    : maxLen_(maxLen), maxFreeVar_(maxFreeVar), maxVar_(maxVar), secLimit_(hrLimit*3600), ldbFile_(ldbFile), declFile_(declFile),
      outFile_(outFile), numComs_(0)
  {
    readDeclFile(declFile_); //populate relNameToIdMap_ and relIdToNameMap_
  }

  ~PathFinder() 
  { 
    deleteAtomsInAtomSet(); 
    for (int i = 0; i < pathSetByLen_.size(); i++)
    {
      Array<Path*> tmpPaths(10000);
      PathSet* pathSet = pathSetByLen_[i];
      for (PathSet::iterator it = pathSet->begin(); it != pathSet->end(); it++)
        tmpPaths.append(*it);
      for (int j = 0; j < tmpPaths.size(); j++)
        deletePath(tmpPaths[j]);
      delete pathSet;
    }
  }

  void run()
  {
    pathSetByLen_.clear();
    pathSetByLen_.growToSize(maxLen_+1);
    for (int i = 0; i < pathSetByLen_.size(); i++)
      pathSetByLen_[i] = new PathSet;
    
    startSec_ = timer_.time();
    prevTimeStep_ = 0;

    ifstream in(ldbFile_.c_str());  Util::assertGoodInStream(in, ldbFile_);

    //for each community, find paths
    Array<string> db;
    int comCnt = 0;
    int dbId;
    Array<string> supComArr(100);
    //!START: Pathfinding in motifs
    double customStartSec = timer_.time();
    while (Parser::readCommunityDB(in, db, numComs_, dbId, supComArr))
    {
      double begSec = timer_.time();
      cout << "finding paths in COMMUNITY " << comCnt++ << "  #atoms " << db.size() << endl;
      //for (int i = 0; i < db.size(); i++)  cout << db[i] << endl; cout << endl;

      findPath(db, dbId, supComArr);

      cout << "COMMUNITY  " << comCnt-1 << " took "; timer_.printTime(cout, timer_.time()-begSec); cout << endl;
    }
    cout << "TIMER pathfinding in motifs took ";
    timer_.printTime(cout, timer_.time() - customStartSec);
    cout << endl;
    //!END: Pathfinding in motifs
    in.close();

    ofstream out(outFile_.c_str());   
    //writePaths(out);
    writePathsSortBySupport(out);
    out.close();
  }

  ostream& print(ostream& out) const
  {
    out << "--------- ATOMS ----------" << endl;
    for (AtomSet::iterator it = atomSet_.begin(); it != atomSet_.end(); it++)
    {
      printAtom(out, *(*it)); out << endl;
    }
    out << endl;

    out << "--------- ATOMS & LINKS ---------" << endl;
    for (AtomSet::iterator it = atomSet_.begin(); it != atomSet_.end(); it++)
    {
      printAtom(out, *(*it)); out << " -> ";
      Atom** linkToAtoms = (*it)->linkToAtoms();
      int numLinkToAtoms = (*it)->numLinkToAtoms();
      for (int i = 0; i < numLinkToAtoms; i++)
      {
        printAtom(out, *linkToAtoms[i]); out << "  ";
      }
      out << endl;
    }
    out << endl;

    out << "--------- REL NAME -> ID MAP ---------" << endl;
    for (StringToIntMap::const_iterator it = relNameToIdMap_.begin(); it != relNameToIdMap_.end(); it++)
      out << (*it).first << " -> " << (*it).second << endl;
    out << endl;

    out << "--------- REL ID -> NAME MAP ---------" << endl;
    for (int i = 0; i < relIdToNameMap_.size(); i++)
      out << i << " -> " << relIdToNameMap_[i] << endl;
    out << endl;

    out << "--------- CONST NAME -> ID MAP ---------" << endl;
    for (StringToIntMap::const_iterator it = constNameToIdMap_.begin(); it != constNameToIdMap_.end(); it++)
      out << (*it).first << " -> " << (*it).second << endl;
    out << endl;

    out << "--------- CONST ID -> NAME MAP ---------" << endl;
    for (int i = 0; i < constIdToNameMap_.size(); i++)
      out << i << " -> " << constIdToNameMap_[i] << endl;
    out << endl;

    return out;
  }

 private:
  void findPath(const Array<string>& db, const int& dbId, const Array<string>& supComArr)
  {
    dbPathSetByLen_.clear();
    dbPathSetByLen_.growToSize(maxLen_+1);
    for (int i = 0; i < dbPathSetByLen_.size(); i++)
      dbPathSetByLen_[i] = new PathSet;

    setAtomsAndConstIds(db);

    int numAtoms = (int) atomSet_.size();
    int atomCnt = 0;
    for (AtomSet::iterator it = atomSet_.begin(); it != atomSet_.end(); it++)
    {
      if (exceedTimeLimit()) { cout << "EXCEED TIME LIMIT 1" << endl; break; }
      writePathsPerTimeStep();

      cout << "  starting from atom " << ++atomCnt << "/" << numAtoms << "..."; cout.flush();
      double bsec = timer_.time();
      Atom* atom = (*it);

      Array<Atom*> linkToAtoms;
      linkToAtoms.append(atom);
      findPath(NULL, linkToAtoms);

      cout << "time taken for atom " << atomCnt-1 << " = "; Timer::printTime(cout, timer_.time()-bsec); cout << " , ";
      cout << "elapsed time = "; Timer::printTime(cout, timer_.time()-startSec_); cout << endl;
    }

    string dbIdStr = Util::intToString(dbId);

    for (int i = 0; i < dbPathSetByLen_.size(); i++)
    {
      PathSet& dbPathSet = *dbPathSetByLen_[i];
      PathSet& pathSet   = *pathSetByLen_[i];
      Array<Path*> paths( dbPathSet.size() );
      for (PathSet::iterator it = dbPathSet.begin(); it != dbPathSet.end(); it++)
        paths.append(*it);

      for (int j = 0; j < paths.size(); j++)
      {
        Path* path = paths[j];
        canonicalizePath(path);
        PathSet::iterator itt = pathSet.find(path);
        //if (itt == pathSet.end()) { pathSet.insert(path); path->addSupportIdStr(dbIdStr); }
        //else                      { (*itt)->addSupport(path->support()); (*itt)->addSupportIdStr(dbIdStr); deletePath(path); }
        if (itt == pathSet.end())   { pathSet.insert(path); path->addSupportIdStr(dbIdStr);  path->addSupportIdStr2(supComArr); }
        else                        {                      (*itt)->addSupportIdStr(dbIdStr); (*itt)->addSupportIdStr2(supComArr); deletePath(path); }
      }

      delete &dbPathSet;
    }

  }

  void findPath(Path*const& curPath, Array<Atom*>& links)
  {
    for (int i = 0; i < links.size(); i++)
    {
      if (exceedTimeLimit()) { cout << "EXCEEDED TIME LIMIT" << endl; break; }

      Atom* atom = links[i];
      Path* newPath = createNewPath(atom, curPath);
      storePath(newPath);
      Array<Atom*>* newLinks = getNewLinks(atom, curPath);

      if (newPath->numAtoms() < maxLen_) findPath(newPath, *newLinks);
      else                               delete newPath;
      delete newLinks;
    }
    delete curPath;
  }

  Array<Atom*>* getNewLinks(const Atom*const& atom, const Path*const& path)
  {
    AtomSet curAtomSet;
    getAtomsInPath(curAtomSet, path);

    Atom** candLinks = atom->linkToAtoms();
    int numCandLinks = atom->numLinkToAtoms();
    Array<Atom*>* newLinks = new Array<Atom*>( numCandLinks );
    for (int j = 0; j < numCandLinks; j++)
    {
      Atom* aatom = candLinks[j];
      if (curAtomSet.find(aatom) == curAtomSet.end())
        newLinks->append(aatom);
    }
    return newLinks;
  }

  void getAtomsInPath(AtomSet& curAtomSet, const Path* const& curPath)
  {
    if (curPath == NULL) return;
    Atom** curAtoms = curPath->atoms();
    int numCurAtoms = curPath->numAtoms();
    for (int i = 0; i < numCurAtoms; i++)
      curAtomSet.insert(curAtoms[i]);
    Util::assertt((int)curAtomSet.size() == numCurAtoms, "expect curAtomSet.size() == numCurAtoms", -1);
  }

  Path* createNewPath(Atom* const& newAtom, const Path* const& path)
  {
    int pathLen = (path == NULL) ? 0 : path->numAtoms();
    int newLen = pathLen+1;

    Atom** atoms = (path== NULL) ? NULL : path->atoms();
    int newAtomIdx = findInsertIdx(newAtom, atoms, 0, pathLen-1);

    Atom** newAtoms = new Atom*[newLen];
    for (int i = 0; i < newLen; i++)
    {
      if (i < newAtomIdx)       newAtoms[i] = atoms[i];
      else if (i == newAtomIdx) newAtoms[i] = newAtom;
      else                      newAtoms[i] = atoms[i-1];
    }

    Path* newPath = new Path(newAtoms, newLen);
    return newPath;
  }

  int findInsertIdx(const Atom* newAtom, Atom** const & atoms, const int& startIdx, const int& endIdx)
  {
    int numIdxs = endIdx - startIdx + 1;
    if (numIdxs == 0) return 0;
    if (numIdxs == 1)
    {
      if (newAtom > atoms[startIdx]) return startIdx + 1;
      if (newAtom < atoms[startIdx]) return startIdx;
      Util::assertt(newAtom != atoms[startIdx], "expect newAtom != atoms[startIdx]", -1);
    }
    else if (numIdxs == 2)
    {
      if (atoms[startIdx] < newAtom && newAtom < atoms[endIdx]) return endIdx;
      if (newAtom < atoms[startIdx]) return startIdx;
      if (newAtom > atoms[endIdx])   return endIdx+1;
      Util::assertt(newAtom != atoms[startIdx] && newAtom != atoms[endIdx], "expect newAtom != first/last atom id", -1);
    }
    else if (numIdxs > 2)
    {
      int midIdx = startIdx + numIdxs/2;
      Util::assertt(startIdx < midIdx && midIdx < endIdx, "", -1);
      if (atoms[midIdx] < newAtom && newAtom < atoms[midIdx+1]) return midIdx+1;

      if (newAtom < atoms[midIdx])        return findInsertIdx(newAtom, atoms, startIdx, midIdx-1);
      else if (newAtom > atoms[midIdx+1]) return findInsertIdx(newAtom, atoms, midIdx+1, endIdx);
      Util::assertt(newAtom!= atoms[midIdx] && newAtom != atoms[midIdx+1], "newAtomId != ids[midIdx] && newAtomId != ids[midIdx+1]", -1);
    }
    return -1;
  }

  void storePath(const Path* const& path)
  {
    Path* copyPath = path->copy();
    int pathLen = copyPath->numAtoms();

    int numFreeVar, numVar;
    countVar(numFreeVar, numVar, copyPath);
    int maxxFreeVar = (pathLen > 2) ? maxFreeVar_ : TWO_PREDS_FREE_VAR;

    if (numFreeVar > maxxFreeVar || numVar > maxVar_) deletePath(copyPath);
    else
    {
      PathSet& dbPathSet = *dbPathSetByLen_[pathLen];
      pair<PathSet::iterator,bool> pr = dbPathSet.insert(copyPath);
      if (pr.second) { /*copyPath->setSupport(numComs_);*/ } //CO: support is the number of unique supCom
      else           { deletePath(copyPath); }
    }
  }

  void countVar(int& numFreeVar, int& numVar, const Path* const& path)
  {
    Atom** atoms = path->atoms();
    int numAtoms = path->numAtoms();
    IntToIntMap idToCntMap;
    for (int i = 0; i < numAtoms; i++)
    {
      Atom* atom = atoms[i];
      for (int j = 0; j < atom->numConstIds(); j++)
      {
        int constId = atom->constId(j);
        if (idToCntMap.find(constId) == idToCntMap.end())  idToCntMap[constId] = 1;
        else                                               idToCntMap[constId]++;
      }
    }

    numFreeVar = 0;
    numVar = 0;
    for (IntToIntMap::iterator it=idToCntMap.begin(); it!=idToCntMap.end(); it++)
    {
      if ((*it).second <= 1) numFreeVar++;
      numVar++;
    }
  }

  void canonicalizePath(Path* const& path)
  {
    Atom** atoms = path->atoms();
    int numAtoms = path->numAtoms();

    Array<int>* constIdToNumAppearMap = Path::getConstIdToNumAppearMap(atoms, numAtoms);
    Path::sortAtoms(atoms, 0, numAtoms-1, *constIdToNumAppearMap);
    delete constIdToNumAppearMap;

    renumVars(atoms, numAtoms);

    constIdToNumAppearMap = Path::getConstIdToNumAppearMap(atoms, numAtoms);
    Path::sortAtoms(atoms, 0, numAtoms-1, *constIdToNumAppearMap);
    delete constIdToNumAppearMap;

    path->computeHashCode();
  }

  void renumVars(Atom** const& atoms, const int& numAtoms)
  {
    IntToIntMap oldToNewMap;
    for (int i = 0; i < numAtoms; i++)
    {
      Atom* atom = atoms[i];
      int numConstIds = atom->numConstIds();
      for (int j = 0; j < numConstIds; j++)
      {
        int oldId = atom->constId(j);
        IntToIntMap::iterator it = oldToNewMap.find(oldId);
        int newId;
        if (it == oldToNewMap.end()) { newId = oldToNewMap.size(); oldToNewMap[oldId] = newId; }
        else                           newId = (*it).second;
        atom->setConstId(j, newId);
      }
    }
  }

  void deletePath(Path* const& path) { path->deleteAtoms(); delete path; }

  void deleteAtomsInAtomSet()
  {
    Array<Atom*> tmpAtoms(atomSet_.size());
    for (AtomSet::iterator it = atomSet_.begin(); it != atomSet_.end(); it++)
      tmpAtoms.append(*it);
    tmpAtoms.deleteItemsAndClear();
  }

 private:
  void setAtomsAndConstIds(const Array<string>& atomStrs)
  {
    constNameToIdMap_.clear();
    constIdToNameMap_.clear();
    deleteAtomsInAtomSet();
    atomSet_.clear();
   
    IntToAtomArrayMap constIdToAtomsMap;

    for (int i = 0; i < atomStrs.size(); i++)
    {
      string relName;
      Array<string> constNames;
      UUtil::readRelArgs(atomStrs[i], relName, constNames);

      int relId = getRelId(relName);
      Array<int> constIds( constNames.size() );
      getConstIds(constIds, constNames);

      Atom* atom = new Atom(relId, constIds);
      pair<AtomSet::iterator,bool> pr = atomSet_.insert(atom);
      if (!pr.second) { delete atom; continue; }

      //map constId to atoms
      IntHashArray uniqConstIds;
      for (int i = 0; i < constIds.size(); i++)
        uniqConstIds.append(constIds[i]);

      for (int i = 0; i < uniqConstIds.size(); i++)
      {
        int constId = uniqConstIds[i];
        IntToAtomArrayMap::iterator it = constIdToAtomsMap.find(constId);
        Array<Atom*>* atoms;
        if (it == constIdToAtomsMap.end()) { atoms = new Array<Atom*>; constIdToAtomsMap[constId] = atoms; }
        else                                 atoms = (*it).second;
        atoms->append(atom);
      }
    }
    Util::assertt((int)constNameToIdMap_.size() == constIdToNameMap_.size(), "expect both const maps same size", -1);

    linkToAtomToAtoms(constIdToAtomsMap);

    IntToAtomArrayMap::iterator it = constIdToAtomsMap.begin();
    for(; it != constIdToAtomsMap.end(); it++) delete (*it).second;
  }

  void readDeclFile(const string& declFile)
  {
    ifstream in(declFile.c_str());  Util::assertGoodInStream(in, declFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;
      Util::assertt(isalpha(buf.at(0)), "expect predicate declaration to start with alpha", buf, -1);

      string relName; Array<string> curTypeNames;
      UUtil::readRelArgs(buf, relName, curTypeNames);

      StringToIntMap::iterator it = relNameToIdMap_.find(relName);
      if (it == relNameToIdMap_.end())
      {
        int relId = (int) relNameToIdMap_.size();
        relNameToIdMap_[relName] = relId;
        relIdToNameMap_.append(relName);  Util::assertt(relIdToNameMap_.size() == relId+1, "wrong array size", -1);      
      }     
    }
    in.close();
    Util::assertt((int)relNameToIdMap_.size() == relIdToNameMap_.size(),   "expect both rel maps same size",   -1);
  }

  void printAtom(ostream& out, const Atom& atom) const
  {
    string relName = relIdToNameMap_[atom.relId()];
    out << relName << "(";
    int* constIds = atom.constIds();
    int numConstIds = atom.numConstIds();
    for (int j = 0; j < numConstIds; j++)
    {
      string constName = constIdToNameMap_[constIds[j]];
      out << constName << ((j < numConstIds-1)?",":")");
    }
  }

  int getRelId(const string& relName)
  {
    StringToIntMap::iterator it = relNameToIdMap_.find(relName);
    Util::assertt(it != relNameToIdMap_.end(), "relName not found", relName, -1);
    return (*it).second;
  }

  void getConstIds(Array<int>& constIds, const Array<string>& constNames)
  {
    for (int i = 0; i < constNames.size(); i++)
      constIds.append( getConstId(constNames[i]) );
  }

  int getConstId(const string& constName)
  {
    StringToIntMap::iterator it = constNameToIdMap_.find(constName);
    if (it == constNameToIdMap_.end())
    {
      int constId = (int) constNameToIdMap_.size();
      constNameToIdMap_[constName] = constId;
      constIdToNameMap_.append(constName);  Util::assertt(constIdToNameMap_.size() == constId+1, "wrong array size2", -1);
      return constId;
    }
    return (*it).second;
  }

  void linkToAtomToAtoms(const IntToAtomArrayMap& constIdToAtomsMap)
  {
    for (AtomSet::iterator it = atomSet_.begin(); it != atomSet_.end(); it++)
    {
      Atom* atom = (*it);
      AtomSet aset;
      int* constIds = atom->constIds();
      int numConstIds = atom->numConstIds();
      for (int i = 0; i < numConstIds; i++)
      {
        IntToAtomArrayMap::const_iterator itt = constIdToAtomsMap.find( constIds[i] );  Util::assertt(itt != constIdToAtomsMap.end(), "expect constId to exist", -1);
        Array<Atom*>& atomArr = *( (*itt).second );
        for (int j = 0; j < atomArr.size(); j++)
        {
          Atom* aatom = atomArr[j];
          if (aatom != atom) aset.insert(aatom);
        }
      }

      int idx = 0;
      Atom** linkToAtoms = new Atom*[aset.size()];
      for (AtomSet::iterator it2 = aset.begin(); it2 != aset.end(); it2++)
        linkToAtoms[idx++] = (*it2);
      atom->setLinkToAtoms(linkToAtoms);
      atom->setNumLinkToAtoms(aset.size());
    }
  }

 private:
  bool exceedTimeLimit()
  {
    if (secLimit_ <= 0.0) return false;
    double elapsedSec = timer_.time() - startSec_;
    return (elapsedSec > secLimit_);
  }

  void writePathsPerTimeStep()
  {
    if (!WRITE_RULES_PER_TIME_STEP) return;
    int timeStep = int( (timer_.time() - startSec_) / TIME_STEP_SEC );
    if (timeStep > prevTimeStep_)
    {
      prevTimeStep_ = timeStep;
      string outFile = outFile_ + "_" + Util::intToString(prevTimeStep_);
      ofstream out(outFile.c_str());
      writePaths(out);
      out.close();
    }
  }

  void writePaths(ostream& out)
  {
    for (int len = 2; len < pathSetByLen_.size(); len++)
      if (pathSetByLen_[len]->size() > 0)
        out << "//LEN " << len << "  #PATHS " << pathSetByLen_[len]->size() << endl;
    out << endl;

    out << "//INDEX  LEN  SUP  RULE" << endl;
    int pathIdx = 0;
    for (int len = 2; len < pathSetByLen_.size(); len++)
    {
      PathSet& pathSet = *pathSetByLen_[len];
      for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
      {
        //change the path's support to the number of com in which it is found
        (*it)->setSupport( (*it)->supportIdStrs2()->size() );

        out << pathIdx++ << " " << len << " "; writePath(out, (*it)); out << endl;
        StringHashArray& dbIdStrs = *(*it)->supportIdStrs();
        out << "    DB_IDS ";
        for (int j = 0; j < dbIdStrs.size(); j++)
          out << " " << dbIdStrs[j];
        out << endl;
      }
    }
    out << endl;
  }

  void writePathsSortBySupport(ostream& out)
  {
    int numPaths = 0;
    for (int len = 2; len < pathSetByLen_.size(); len++)
      numPaths += pathSetByLen_[len]->size();

    Array<Path*> paths(numPaths);
    for (int len = 2; len < pathSetByLen_.size(); len++)
    {
      PathSet& pathSet = *pathSetByLen_[len];
      for (PathSet::iterator it = pathSet.begin(); it != pathSet.end(); it++)
      {
        //change the path's support to the number of com in which it is found
        (*it)->setSupport( (*it)->supportIdStrs2()->size() );
        paths.append(*it);
      }
    }

    qsort((Path**) paths.getItems(), paths.size(), sizeof(Path*), comparePathsBySupport);

    for (int len = 2; len < pathSetByLen_.size(); len++)
      if (pathSetByLen_[len]->size() > 0)
        out << "//LEN " << len << "  #PATHS " << pathSetByLen_[len]->size() << endl;
    out << endl;

    out << "//INDEX  LEN  SUP  RULE" << endl;
    for (int i = 0; i < paths.size(); i++)
    {
      out << i << " " << paths[i]->numAtoms() << " "; writePath(out, paths[i]); out << endl;
      StringHashArray& dbIdStrs = *paths[i]->supportIdStrs();
      out << "    DB_IDS ";
      for (int j = 0; j < dbIdStrs.size(); j++)
        out << " " << dbIdStrs[j];
      out << endl;

      /*
      StringHashArray& dbIdStrs2 = *paths[i]->supportIdStrs2();
      out << "    DB_IDS2 ";
      for (int j = 0; j < dbIdStrs2.size(); j++)
        out << " " << dbIdStrs2[j];
      out << endl;
      */
    }
    out << endl;
  }

  void writePath(ostream& out, const Path* const& path)
  {
    Atom** atoms = path->atoms();
    int numAtoms = path->numAtoms();
    int support = path->support();
    out << support << " ";
    for (int i = 0; i < numAtoms; i++)
    {
      writeAtom(out, atoms[i]); out << " ";
    }
  }

  void writeAtom(ostream& out, const Atom* const& atom)
  {
    int relId = atom->relId();
    string relName = relIdToNameMap_[relId];
    out << relName << "(";

    int* constIds = atom->constIds();
    int numConstIds = atom->numConstIds();
    for (int j = 0; j < numConstIds; j++)
      out << Util::intToString(constIds[j]) << ((j < numConstIds-1)?",":")");
  }

};

inline ostream& operator <<(ostream& out, const PathFinder& p) { return p.print(out); }

#endif
