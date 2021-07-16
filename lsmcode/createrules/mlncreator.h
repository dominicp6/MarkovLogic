#ifndef MLNCREATOR_H_OCT_23_2009
#define MLNCREATOR_H_OCT_23_2009

#include <iostream>
using namespace std;
#include <sstream>
#include <unistd.h>
#include <sys/time.h>
#include <cstring>
#include <string> //MYEDIT
#include <cfloat>
#include "array.h"
#include "arraysaccessor.h"
#include "hashstring.h"
#include "timer.h"
#include "util.h"
#include "uutil.h"
#include "clause.h"

const bool   WRITE_UNIT_CLAUSES_TO_MLN = true;
const string CONV_THRESH = "-gConvThresh 1e-6";
const string TMP_MLN     = "tmp_mln_xxx.mln";
const string TMP_OUT_MLN = "tmp_out_mln_xxx.mln";
const string TMP_DB      = "tmp_db_xxx.db";
const string TMP_LOG     = "tmp_log_xxx.log";
const int    MAX_LEN_TRIVIAL = 2;
const double BAD_SCORE   = -1000000.0;

typedef hash_map<int, Array<Array<Array<string>*>*>*, HashInt, EqualInt> IntToStringArrayArrayArrayMap;


class MLNCreator
{
 private:
  Array<string> dbFiles_;
  Array<double> numAtomsInDBs_; //all atoms (true/false/unknown) in each DB
  double        totalNumAtoms_; //all atoms across DBs
  Array<string> predDecls_;
  string        learnWtsExec_;
  string        tmpDir_;
  double        fractAtoms_;
  double        lenPenalty_;
  double        quickLenPenalty_;
  int           numFlips_;
  int           maxLen_;
  int           minAtoms_;
  int           maxAtoms_;
  int           numQuickPruneDBs_;
  char*         command_;
  string        outMLN_;
  int           seed_; 


  StringToIntMap    relNameToIdMap_;
  Array<string>     relIdToNameMap_;
  Array<ClauseSet*> candsByLen_;
  Array<Clause*>    cands_;
  StringToStringArrayMap relToTypesMap_;
  IntToStringArrayArrayArrayMap  dbIdToUnmergedDBsMap_; //maps DB id in comb.ldb to [domainId][unmerged dbId]

  Array<string> unitClausesStr_;
  double        unitScore_;

  Array<ClauseSet*> trivialClausesByLen_; //clauses that are always true/false
  IntSet symBinRelIds_;
  string trivialBinFile_;
  string symBinRelFile_;

  bool cfAllSub_;
  bool cora_;
  bool noQuickPrune_;

  double secLimit_;
  string filePrefix_;

  //T is a trivial clause if it is always true/false
  //We can disregard clause C v T. If T is always true, then C v T == T, and we need only consider T.
  //If T is always false, then C v T == C, and we need only consider C. 

 public:
 MLNCreator(const string& candFile, const int& minSup, const string& dbFiles, const string& combLDBFile, const string& unmergeLDBFiles,
            const string& declFile, const string& learnWtsExec, const string& tmpDir, const double& fractAtoms, const double& lenPenalty, 
            const double& quickLenPenalty, const int& numFlips, const int& maxLen, const int& minAtoms, const int& maxAtoms, 
            const int& numQuickPruneDBs, const string& outMLN, const int& seed, const string& trivialBinFile, const string& symBinRelFile, 
            const bool& cfAllSub, const bool& cora, const bool& noQuickPrune, const double& secLimit)
    : learnWtsExec_(learnWtsExec), tmpDir_(tmpDir), fractAtoms_(fractAtoms), lenPenalty_(lenPenalty), quickLenPenalty_(quickLenPenalty), numFlips_(numFlips), 
      maxLen_(maxLen), minAtoms_(minAtoms), maxAtoms_(maxAtoms), numQuickPruneDBs_(numQuickPruneDBs), outMLN_(outMLN), seed_(seed), unitScore_(1.0), 
      trivialBinFile_(trivialBinFile), symBinRelFile_(symBinRelFile), cfAllSub_(cfAllSub), cora_(cora), noQuickPrune_(noQuickPrune), secLimit_(secLimit), filePrefix_("")
  {
    //string::size_type s = outMLN_.rfind("/");
    //if (s == string::npos) filePrefix_ = outMLN_;
    //else                   filePrefix_ = Util::substr(outMLN_,s+1,outMLN_.length());
    //string::size_type d =  filePrefix_.rfind(".");
    //if (d != string::npos) filePrefix_ = Util::substr(filePrefix_,0,d);
    filePrefix_ = outMLN_;
    for (unsigned int i = 0; i < filePrefix_.length(); i++)
      if (filePrefix_[i] == '/' || filePrefix_[i] == '.') filePrefix_[i] = '_';

    readDeclFile(declFile); //set relNameToIdMap_, relIdToNameMap_, predDecls_, unitClausesStr_;
    Util::getStrings(dbFiles_, dbFiles);
    candsByLen_.growToSize(maxLen_+1, NULL);
    getCands(candFile, minSup);
    if (tmpDir_.at(tmpDir_.length()-1) != '/') tmpDir_.append("/");
    command_ = new char[2000 + dbFiles.length()];
    srandom(seed_);
    getNumAtomsInDBs(dbFiles); //also set totalNumAtoms_;
    createRelToTypesMap(declFile);
    createUnitClausesStr();
    createTrivialClausesByLen();

    if (!noQuickPrune_) createDBIdToUnmergedDBsMap(combLDBFile, unmergeLDBFiles);
  }

  ~MLNCreator()
  {
    delete [] command_;
    for (int i = 0; i < candsByLen_.size(); i++)
    {
      ClauseSet* cset = candsByLen_[i];
      if (cset == NULL) continue;
      Array<Clause*> tmpArr( cset->size() );
      for (ClauseSet::iterator it = cset->begin(); it != cset->end(); it++)
        tmpArr.append(*it);
      tmpArr.deleteItemsAndClear();
      delete cset;
    }
    cands_.deleteItemsAndClear();

    for (StringToStringArrayMap::iterator it = relToTypesMap_.begin(); it != relToTypesMap_.end(); it++)
      delete (*it).second;

    for (int i = 0; i < trivialClausesByLen_.size(); i++)
    {
      ClauseSet* cset = trivialClausesByLen_[i];
      Array<Clause*> tmpArr( cset->size() );
      for (ClauseSet::iterator it = cset->begin(); it != cset->end(); it++)
        tmpArr.append(*it);
      tmpArr.deleteItemsAndClear();
      delete cset;
    }

    IntToStringArrayArrayArrayMap::iterator it = dbIdToUnmergedDBsMap_.begin();
    for (; it != dbIdToUnmergedDBsMap_.end(); it++)
    {
      Array<Array<Array<string>*>*>* dbsByDom = (*it).second;
      for (int i = 0; i < dbsByDom->size(); i++)
      {
        Array<Array<string>*>* dbs = (*dbsByDom)[i];
        if (dbs != NULL) 
        { 
          //dbs->deleteItemsAndClear(); 
          delete dbs; 
        }
      }
      delete dbsByDom;
    }
  }

  void run()
  {
    if (noQuickPrune_) { runWithoutQuickPrune(); return; }
    //!START: MLN structure learning run
    struct timeval tvA; struct timezone tzpA;
    gettimeofday(&tvA,&tzpA);

    string chosenDBFiles; int numDBs; double fractAtoms;
    getTrainingDBs(chosenDBFiles, numDBs, fractAtoms);

    removePathsWithTrivialUnitClauses();
    createTrivialBinaryClauses();
    removeRedundantPathsWithSymBinRels();

    Array<Clause*> clauses(100000);
    quickPrune(clauses, tvA, tzpA);

    //Array<Clause*> clauses(100000);
    //createClausesFromFile(clauses, "/homes/gws/koks/lhl-expt/imdb3.qkclauses");  

    string mlnFile, outMLNFile, logFile;
    getFileNames(mlnFile, outMLNFile, logFile);
    int    numPruned  = 0;
    int    clauseCnt  = 0;

    unitScore_ = runLearnWts(mlnFile, NULL, outMLNFile, chosenDBFiles, fractAtoms, logFile, numDBs, true);

    for (int i = 0; i < clauses.size(); i++) //for each candidate clause
    {
      Clause* clause = clauses[i];
      clauseCnt++;

      cout << endl << "  TRY_PRUNE " << clauseCnt << " / " << clauses.size() << " : " << clauseStrRep(clause) << endl;
      struct timeval tv; struct timezone tzp;
      gettimeofday(&tv,&tzp);

      evalClause(clause, numPruned, mlnFile, outMLNFile, logFile, chosenDBFiles, numDBs, fractAtoms, false);

      struct timeval tv2; struct timezone tzp2;
      gettimeofday(&tv2,&tzp2);

      cout << "PRUNE_CLAUSE " << clauseCnt << " took "; Timer::printTime(cout, tv2.tv_sec-tv.tv_sec); cout << endl;
      cout << "ELAPSED TIME = "; Timer::printTime(cout, tv2.tv_sec-tvA.tv_sec); cout << endl;
    }

    unlink(mlnFile.c_str()); unlink(outMLNFile.c_str()); unlink(logFile.c_str());

    struct timeval tvB; struct timezone tzpB;
    gettimeofday(&tvB,&tzpB);
    cout << "TIMER RUN took "; Timer::printTime(cout, tvB.tv_sec-tvA.tv_sec); cout << endl;
    //!END: MLN structure learning run

    cout << "NUM_PRUNED    " << numPruned             << " / " << clauseCnt << endl;
    cout << "NUM_REMAINING " << (clauseCnt-numPruned) << " / " << clauseCnt << endl;
    cout << endl;

    writeRules();
  }

  void runWithoutQuickPrune()
  {
    struct timeval tvA; struct timezone tzpA;
    gettimeofday(&tvA,&tzpA);

    removePathsWithTrivialUnitClauses();
    createTrivialBinaryClauses();
    removeRedundantPathsWithSymBinRels();

    string chosenDBFiles; int numDBs; double fractAtoms;
    getTrainingDBs(chosenDBFiles, numDBs, fractAtoms);

    string mlnFile, outMLNFile, logFile;
    getFileNames(mlnFile, outMLNFile, logFile);
    int    numPruned  = 0;
    int    clauseCnt  = 0;

    unitScore_ = runLearnWts(mlnFile, NULL, outMLNFile, chosenDBFiles, fractAtoms, logFile, numDBs, true);

    for (int i = 0; i < cands_.size(); i++) //for each candidate path
    {
      cout << endl << i+1 << "/" << cands_.size() << " CAND_PATH " << clauseStrRep(cands_[i]) << endl;

      Array<Clause*> clauses;
      createFlipClauses(clauses, cands_[i]);

      if (cora_) checkCora(clauses);

      for (int j = 0; j < clauses.size(); j++)
      {
        Clause* clause = clauses[j];
        clauseCnt++;

        cout << endl << "  TRY_PRUNE " << clauseCnt << " : " << clauseStrRep(clause) << endl;
        struct timeval tv; struct timezone tzp;
        gettimeofday(&tv,&tzp);

        evalClause(clause, numPruned, mlnFile, outMLNFile, logFile, chosenDBFiles, numDBs, fractAtoms, true);

        struct timeval tv2; struct timezone tzp2;
        gettimeofday(&tv2,&tzp2);
        
        cout << "PRUNE_CLAUSE " << clauseCnt << " took "; Timer::printTime(cout, tv2.tv_sec-tv.tv_sec); cout << endl;
        cout << "ELAPSED TIME = "; Timer::printTime(cout, tv2.tv_sec-tvA.tv_sec); cout << endl;
      }
    }

    unlink(mlnFile.c_str()); unlink(outMLNFile.c_str()); unlink(logFile.c_str());

    struct timeval tvB; struct timezone tzpB;
    gettimeofday(&tvB,&tzpB);
    cout << "RUN took "; Timer::printTime(cout, tvB.tv_sec-tvA.tv_sec); cout << endl;

    cout << "NUM_PRUNED    " << numPruned             << " / " << clauseCnt << endl;
    cout << "NUM_REMAINING " << (clauseCnt-numPruned) << " / " << clauseCnt << endl;
    cout << endl;

    writeRules();
  }

 private:
  void quickPrune(Array<Clause*>& keptClauses, struct timeval& tvA, struct timezone& tzpA)
  {
    struct timeval tvA2; struct timezone tzpA2;
    gettimeofday(&tvA2,&tzpA2);

    string mlnFile, outMLNFile, logFile;
    getFileNames(mlnFile, outMLNFile, logFile);
    int    numPruned  = 0;
    int    clauseCnt  = 0;

    for (int i = 0; i < cands_.size(); i++) //for each candidate path
    {
      cout << endl << i+1 << "/" << cands_.size() << " CAND_PATH " << clauseStrRep(cands_[i]) << endl;
      Clause* cand = cands_[i];

      StringSet candPredNames;
      getPredNames(cand, candPredNames);

      Array<string> dbFiles;
      int numAtoms = createTrainingDBs(cand->dbIds(), cand->numDBIds(), dbFiles, candPredNames);
      cout << "  NUM_QUICK_SAMPLED_ATOMS " << numAtoms << endl;

      if (numAtoms < minAtoms_) 
      { 
        cout << "QUICK_PRUNE: CAND TOO FEW ATOMS: " << clauseStrRep(cand) << endl; 
        int numCreatedClauses = numFlipClauses(cand->numPreds()); 
        numPruned += numCreatedClauses;
        clauseCnt += numCreatedClauses;
        continue;
      }

      Array<Clause*> clauses;
      createFlipClauses(clauses, cands_[i]);

      if (cora_) checkCora(clauses);

      for (int j = 0; j < clauses.size(); j++)
      {
        Clause* clause = clauses[j];
        clauseCnt++;
        
        cout << endl << "  QUICK_PRUNE " << clauseCnt << " : " << clauseStrRep(clause) << endl;
        struct timeval tv; struct timezone tzp;
        gettimeofday(&tv,&tzp);

        bool isTrivial;
        bool keep = quickEvalClause(clause, mlnFile, outMLNFile, logFile, dbFiles, isTrivial);

        if (keep) { cout << "QUICK_KEEP: "  << clauseStrRep(clause) << endl; keptClauses.append(clause); }
        else
        {
          if (isTrivial)  cout << "QUICK_PRUNE_TRIVIAL: " << clauseStrRep(clause) << endl;
          else            cout << "QUICK_PRUNE: "         << clauseStrRep(clause) << endl;
          numPruned++; delete clause;
        }

        struct timeval tv2; struct timezone tzp2;
        gettimeofday(&tv2,&tzp2);

        cout << "QUICKPRUNE_CLAUSE " << clauseCnt << " took "; Timer::printTime(cout, tv2.tv_sec-tv.tv_sec); cout << endl;
        cout << "ELAPSED TIME = "; Timer::printTime(cout, tv2.tv_sec-tvA.tv_sec); cout << endl;
      }

      for (int i = 0; i < dbFiles.size(); i++)
        unlink(dbFiles[i].c_str());
    }

    unlink(mlnFile.c_str()); unlink(outMLNFile.c_str()); unlink(logFile.c_str());

    struct timeval tvB; struct timezone tzpB;
    gettimeofday(&tvB,&tzpB);
    cout << "QUICKPRUNE took "; Timer::printTime(cout, tvB.tv_sec-tvA2.tv_sec); cout << endl;

    cout << "QUICK_PRUNED    " << numPruned             << " / " << clauseCnt << endl;
    cout << "QUICK_REMAINING " << (clauseCnt-numPruned) << " / " << clauseCnt << endl;
    cout << endl;
  }


 private:
  void getPredNames(const Clause* const& clause, StringSet& predNames)
  {
    Pred** preds = clause->preds();
    int numPreds = clause->numPreds();    
    for (int i = 0; i < numPreds; i++)
    {
      int relId = preds[i]->relId();
      string predName = relIdToNameMap_[relId];
      predNames.insert(predName);
    }
  }

  void removePathsWithTrivialUnitClauses()
  {
    ClauseSet& unitClauseSet = *trivialClausesByLen_[1];
    if (unitClauseSet.empty()) return;

    Array<Clause*> candsCopy(cands_);
    cands_.clear();

    int numPathsRem = 0, numClausesRem = 0;
    for (int i = 0; i < candsCopy.size(); i++) //for each candidate path
    {
      if (candsCopy[i]->numPreds() <= 1) { delete candsCopy[i]; continue; } //unit clauses added by default, so ignore
      Clause* cand     = candsCopy[i];
      Pred**  preds    = cand->preds();
      int     numPreds = cand->numPreds();

      //check for trivial unit clauses
      bool isTrivial = false;
      for (int j = 0; j < numPreds; j++)
      {
        Clause* unitClause = createUnitClause( new Pred(*preds[j]) );
        if (unitClauseSet.find(unitClause) != unitClauseSet.end()) isTrivial = true;
        delete unitClause;
        if (isTrivial) break;
      }

      if (!isTrivial) cands_.append(cand);
      else
      {
        numPathsRem++;
        numClausesRem += numFlipClauses(numPreds);
        cout << "TRIVIAL_PRUNE_PATH: " << clauseStrRep(cand) << endl;
        delete cand;
      }
    }

    cout << "#TRIVIAL_PATHS_PRUNED " << numPathsRem << "  #TRIVIAL_CLAUSES_PRUNED " << numClausesRem << endl;
    cout << "#CAND_PATH_REMAINING  " << cands_.size() << endl;
  }

  void removeRedundantPathsWithSymBinRels()
  {
    if (symBinRelIds_.empty()) return;

    Array<Clause*> candsCopy(cands_);
    cands_.clear();

    int numPathsRem = 0, numClausesRem = 0;
    for (int i = 0; i < candsCopy.size(); i++) //for each candidate path
    {
      if (candsCopy[i]->numPreds() <= 1) { delete candsCopy[i]; continue; } //unit clauses added by default, so ignore
      Clause* cand     = candsCopy[i];
      Pred**  preds    = cand->preds();
      int     numPreds = cand->numPreds();

      bool isRedundant = false;
      if (!areTwoSymPreds(cand)) // if not "R(x,y)  R(y,x)"
      {
        //check if clause contains symmetric binary predicate R(1,0)
        for (int j = 0; j < numPreds; j++)
        {
          Pred* pred = preds[j];
          int relId = pred->relId();
          if (symBinRelIds_.find(relId) == symBinRelIds_.end()) continue;
          Util::assertt(pred->numVarIds() == 2, "expect binary predicate", -1);
          if (pred->varId(0) > pred->varId(1)) { isRedundant = true; break; }
        }
      }
      
      if (!isRedundant) cands_.append(cand);
      else
      {
        numPathsRem++;
        numClausesRem += numFlipClauses(numPreds);
        cout << "REDUND_PRUNE_PATH: " << clauseStrRep(cand) << endl;
        delete cand;
      }
    }

    cout << "#REDUND_PATHS_PRUNED " << numPathsRem << "  #REDUND_CLAUSES_PRUNED " << numClausesRem << endl;
    cout << "#CAND_PATH_REMAINING " << cands_.size() << endl;
  }

  //returns true if R(x,y) v R(y,x), ignoring signs
  bool areTwoSymPreds(const Clause* const& clause)
  {
    Pred**  preds    = clause->preds();
    int     numPreds = clause->numPreds();
    return (numPreds == 2 && preds[0]->relId() == preds[1]->relId() && preds[0]->numVarIds() == 2 && preds[0]->varId(0) != preds[0]->varId(1) && 
            preds[0]->varId(0) == preds[1]->varId(1) && preds[0]->varId(1) == preds[1]->varId(0));
  }

  int numFlipClauses(const int& numPreds)
  {
    int numRem = 1;
    int numFlips = (numPreds >= numFlips_) ? numFlips_ : numPreds;
    for (int r = 1; r <= numFlips; r++)
      numRem += Util::choose(numPreds,r);
    return numRem;
  }

  Clause* createUnitClause(Pred* const& pred)
  {
    Pred** preds = new Pred*[1];
    preds[0] = pred;
    normalizeVar(preds, 1);
    return new Clause(preds, 1);
  }

  void evalClause(Clause* const& clause, int& numPruned, const string& mlnFile, const string& outMLNFile, const string& logFile,
                  const string& dbFiles, const int& numDBs, const double& fractAtoms, const bool& evalTrivial)
  {
    if (evalTrivial) //if check whether clause contains trivial subclauses
    {
      for (int len = 2; len <= MAX_LEN_TRIVIAL && len < clause->numPreds(); len++)
        if (hasTrivialSubClause(clause,len)) { cout << "PRUNE: TRIVIAL: " << clauseStrRep(clause) << endl; numPruned++; delete clause; return; }
    }

    double newScore = runLearnWts(mlnFile, clause, outMLNFile, dbFiles, fractAtoms, logFile, numDBs, false);
    double diffScore = newScore - unitScore_ - clause->numPreds() * lenPenalty_;
    clause->setScore(diffScore);

    cout << "diffScore = " << newScore << " - " << unitScore_ << " - " << clause->numPreds()*lenPenalty_ << " = " << diffScore << endl;

    if (diffScore > 0.0) //if better than unit clauses
    {
      bool better = betterThanSubClauses(clause, mlnFile, outMLNFile, dbFiles, fractAtoms, logFile, numDBs);
      int numPreds = clause->numPreds();
      if (better) { candsByLen_[numPreds]->insert( clause ); cout<<"KEPT: "<<clauseStrRep(clause)<<endl; if (numPreds > 2) checkTrivial(clause); }
      else        { cout << "PRUNE: " << clauseStrRep(clause) << endl;  numPruned++; delete clause; }
    }
    else { cout <<"PRUNE: " << clauseStrRep(clause) << endl; numPruned++; delete clause; }
  }

  bool quickEvalClause(Clause* const& clause, const string& mlnFile, const string& outMLNFile, const string& logFile, const Array<string>& dbFiles, bool& isTrivial)
  {
    isTrivial = false;
    for (int len = 2; len <= MAX_LEN_TRIVIAL && len < clause->numPreds(); len++) //check whether clause contains trivial subclauses
      if (hasTrivialSubClause(clause, len)) { isTrivial = true; return false; }

    int numDBs = dbFiles.size();
    string dbFilesStr = dbFiles[0];
    for (int i = 1; i< dbFiles.size(); i++)
      dbFilesStr += "," + dbFiles[i];

    double unitScore = runLearnWts(mlnFile, NULL,   outMLNFile, dbFilesStr, 1.0, logFile, numDBs, false);
    double newScore  = runLearnWts(mlnFile, clause, outMLNFile, dbFilesStr, 1.0, logFile, numDBs, false);
    double diffScore = newScore - unitScore - clause->numPreds() * quickLenPenalty_;
    cout << "diffscore = " << newScore << " - " << unitScore << " - " << clause->numPreds()*quickLenPenalty_ << " = " << diffScore << endl;
    return (diffScore > 0.0);
  }

  bool hasTrivialSubClause(const Clause* const& clause, const int& len)
  {
    ClauseSet& cset = *trivialClausesByLen_[len];
    if (cset.empty()) return false;

    bool isTrivial = false;
    Array<Clause*> subClauses;
    createSubClauses(subClauses, clause, len);
    for (int i = 0; i < subClauses.size(); i++)
      if (cset.find( subClauses[i] ) != cset.end()) { isTrivial = true; break; }
    subClauses.deleteItemsAndClear();
    return isTrivial;
  }

  bool betterThanSubClauses(const Clause* const& clause, const string& mlnFile, const string& outMLNFile, const string& dbFiles,
                            const double& fractAtoms, const string& logFile, const int& numDBs)
  {
    Array<Clause*> subClauses;
    createSubClauses(subClauses, clause);

    Array<Clause*> foundSubClauses(10);

    for (int i = 0; i < subClauses.size(); i++)
    {
      Clause* subClause = subClauses[i];  Util::assertt(subClause->numPreds() < clause->numPreds(), "expect subClause to be shorter", -1);
      switchSymBinPredVarIds(subClause);
      cout << "  comparing against subClause: " << clauseStrRep(subClause) << " , ";

      ClauseSet* clauseSet = candsByLen_[ subClause->numPreds() ];

      Clause* foundSubClause = NULL;
      if (clauseSet)
      {
        ClauseSet::iterator it = clauseSet->find(subClause);
        if (it != clauseSet->end()) foundSubClause = (*it);
      }

      //ignore subclause since it is not created
      if (foundSubClause == NULL) { cout << "ignored because doesn't exist" << endl; continue; }

      double subScore  = foundSubClause->score();  Util::assertt(subScore != DBL_MAX, "expect subClause score to have been computed", -1);
      double score     = clause->score();
      double diffScore = score - subScore;
      cout << "score = " << score << " , subScore = " << subScore << " , diffScore = " <<  diffScore << endl;

      if (diffScore <= 0.0)
      {
        cout << "LESS_THAN_SUB: " << clauseStrRep(clause) << " diffScore = " << diffScore << " <= 0 ; subClause: " << clauseStrRep(subClause) << endl;
        subClauses.deleteItemsAndClear();
        return false;
      }

      foundSubClauses.append(foundSubClause);
    }

    if (cfAllSub_ && !foundSubClauses.empty())
    {
      double allSubScore = runLearnWts(mlnFile, foundSubClauses, outMLNFile, dbFiles, fractAtoms, logFile, numDBs, false);
      allSubScore = allSubScore - unitScore_ - totalNumPreds(foundSubClauses) * lenPenalty_;
      double diffScore = clause->score() - allSubScore;
      cout << "  comparing against all sub-clauses: score = " << clause->score() << " , allSubScore = " << allSubScore << " , diffScore = "  << diffScore << endl;
      if (diffScore <= 0.0)
      {
        cout << "LESS_THAN_ALL_SUB: " << clauseStrRep(clause) << " diffScore = " << clause->score() << " - " << allSubScore 
             << " = " << diffScore << " <= 0" << endl;
        subClauses.deleteItemsAndClear();
        return false;
      }
    }

    subClauses.deleteItemsAndClear();
    return true;
  }

  int totalNumPreds(const Array<Clause*>& clauses)
  {
    int numPreds = 0;
    for (int i = 0; i < clauses.size(); i++)
      numPreds += clauses[i]->numPreds();
    return numPreds;
  }

  bool switchSymBinPredVarIds(Clause* const& clause)
  {
    //switch the var ids of symmetric binary predicate R(1,0) to R(0,1)    
    if (areTwoSymPreds(clause)) return false;
    if (symBinRelIds_.empty()) return false;

    bool sswitch = false;
    int numPreds = clause->numPreds();
    Pred** preds = clause->preds();
    for (int i = 0; i < numPreds; i++)
    {
      Pred* pred = preds[i];
      int relId = pred->relId();
      if (symBinRelIds_.find(relId) == symBinRelIds_.end()) continue;
      Util::assertt(pred->numVarIds() == 2, "expect binary predicate", -1);
      if (pred->varId(0) > pred->varId(1)) {  int tmpId = pred->varId(0); pred->setVarId(0, pred->varId(1)); pred->setVarId(1, tmpId); sswitch = true; }
    }    
    return sswitch;
  }

  void checkTrivial(const Clause* const& clause)
  {
    if (clause->numPreds() > MAX_LEN_TRIVIAL) return;
    if (clause->numPreds() <= 2)              return;
    addTrivialClause(clause);
  }

  void createTrivialBinaryClauses()
  {
    if (!trivialBinFile_.empty())  { createTrivialBinaryClauseFromFile(); readSymBinRelFromFile(); return; }

    //C = !P v Q always true
    //  When P false,         C true
    //  When P true,  Q true, C true
    //  D = !P v !Q
    //    When P false,         D true
    //    When P true,  Q true, D false
    //    Thus D = !P, so any clause R v !P v !Q can be shortened to R v !P

    //C = !P v Q always false
    //  no grounding for which P false, i.e., P always true
    //  When P true, Q false, D = false;
    //  D = !P v !Q
    //    When P true, Q false, D is always true; !P v !Q is trivial

    //if both !P v Q and P v !Q always true, i.e., P<=>Q
    //  !P v !Q = !P = !Q
    //  P v Q = P = Q

    if (MAX_LEN_TRIVIAL < 2) return;
    cout << "creating trivial binary clauses..." << endl;
    struct timeval tvA; struct timezone tzpA;
    gettimeofday(&tvA,&tzpA);

    for (int i = 0; i < cands_.size(); i++)
    {
      Clause* cand = cands_[i];
      int numPreds = cand->numPreds();
      if (numPreds < 2) continue;
      if (numPreds > 2) break;

      cout << "  CAND_TRIVIAL_PATH " << clauseStrRep(cand) << endl;

      Array<Clause*> clauses;
      createAllFlipClauses(clauses, cand);  Util::assertt(clauses.size()==4, "expect 4 clauses", -1);

      Clause* NotP_v_Q_Clause = NULL, * P_v_NotQ_Clause = NULL, * P_v_Q_Clause = NULL, * NotP_v_NotQ_Clause = NULL;
      for (int j = 0; j < clauses.size(); j++)
      {
        Clause* clause = clauses[j];
        bool P = clause->pred(0)->sign();
        bool Q = clause->pred(1)->sign();
        if      (P == false && Q == true)   NotP_v_Q_Clause    = clause;
        else if (P == true  && Q == false)  P_v_NotQ_Clause    = clause;
        else if (P == true  && Q == true)   P_v_Q_Clause       = clause;
        else if (P == false && Q == false)  NotP_v_NotQ_Clause = clause;
      }
      Util::assertt(NotP_v_Q_Clause != NULL && P_v_NotQ_Clause != NULL && P_v_Q_Clause != NULL && NotP_v_NotQ_Clause != NULL, "expect non-null bin clauses", -1);

      int NotPvQ = addTrivialClause(NotP_v_Q_Clause);
      int PvNotQ = addTrivialClause(P_v_NotQ_Clause);

      if (NotPvQ == 1 && PvNotQ == 1)
      {
        addTrivialClauseDirectly(P_v_Q_Clause);
        addTrivialClauseDirectly(NotP_v_NotQ_Clause);

        Pred* pred0     = cand->pred(0);
        Pred* pred1     = cand->pred(1);
        int   numVarIds = pred0->numVarIds();
        int   relId0    = pred0->relId();
        int   relId1    = pred1->relId();
        //if both preds are the same binary relation, and each pred have different args, and their args are symmetric 
        if (relId0 == relId1 && numVarIds == 2 && pred0->varId(0) != pred0->varId(1) && 
            pred0->varId(0) == pred1->varId(1) && pred0->varId(1) == pred1->varId(0))
          symBinRelIds_.insert(relId0);
      }
      else if ( NotPvQ == 0 || NotPvQ == 1 || PvNotQ == 0 || PvNotQ == 1 )
      {
        addTrivialClause(P_v_Q_Clause);
        addTrivialClauseDirectly(NotP_v_NotQ_Clause);
      }
      else
      {
        addTrivialClause(P_v_Q_Clause);
        addTrivialClause(NotP_v_NotQ_Clause);
      }
     
      clauses.deleteItemsAndClear();     
    }

    struct timeval tvB; struct timezone tzpB;
    gettimeofday(&tvB,&tzpB);
    cout << "creating trivial binary clauses took "; Timer::printTime(cout, tvB.tv_sec-tvA.tv_sec); cout << endl;
  }

  void createClausesFromFile(Array<Clause*>& clauses, const string& inFile)
  {
    ifstream in(inFile.c_str());  Util::assertGoodInStream(in, inFile);
    string buf;
    int clauseCnt = 0;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;
      if (buf.find("QUICK_KEEP: ") != 0) continue;

      string::size_type sp = buf.find(" ");
      string clauseStr = Util::substr(buf,sp+1,buf.length());
      clauseStr = Util::trim(clauseStr);
      Clause* clause = createClauseFromString(clauseStr);      
      cout << clauseCnt++ << "  CREATED KEPT CLAUSE: " << clauseStrRep(clause) <<  endl;
      clauses.append(clause);
    }
    in.close();
  }

  void createTrivialBinaryClauseFromFile()
  {
    Util::assertt(!trivialBinFile_.empty(), "expect trivialBinFile", -1);
    ifstream in(trivialBinFile_.c_str());  Util::assertGoodInStream(in, trivialBinFile_);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;
      Clause* clause = createClauseFromString(buf);
      addTrivialClauseDirectly(clause);
      cout << "READ TRIVIAL CLAUSE: " << clauseStrRep(clause) <<  endl;
      delete clause;
    }
    in.close();
  }

  void readSymBinRelFromFile()
  {
    Util::assertt(!symBinRelFile_.empty(), "expect symBinRelFile", -1);
    ifstream in(symBinRelFile_.c_str());  Util::assertGoodInStream(in, symBinRelFile_);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;
      cout << "READ SYM_BIN_REL: " << buf << endl;
      StringToIntMap::iterator it = relNameToIdMap_.find(buf);  Util::assertt(it != relNameToIdMap_.end(), "bad relName " + buf, -1);
      int relId = (*it).second;
      symBinRelIds_.insert(relId);
    }
    in.close();
  }

  Clause* createClauseFromString(string clauseStr)
  {
    for (unsigned int i = 1; i < clauseStr.length()-1; i++)
    {
      if (clauseStr.at(i-1) == ' ' && clauseStr.at(i) == 'v' && clauseStr.at(i+1) == ' ')
        clauseStr.at(i) = ' ';
    }

    Array<string> tokens(10);
    Util::tokenize(clauseStr, tokens, " ");

    //remove the 'v' from args, e.g. "v0"
    for (int i = 0; i < tokens.size(); i++)
    {
      string pred = Util::trim(tokens[i]);
      string rel; Array<string> args;
      UUtil::readRelArgs(pred, rel, args);
      for (int j = 0; j < args.size(); j++)
        if (args[j].at(0) == 'v') 
          args[j] = args[j].substr(1,args[j].length()-1);
      pred = rel + "(" + args[0];
      for (int j = 1; j < args.size(); j++)
        pred += "," + args[j];
      pred += ")";
      tokens[i] = pred;
    }


    Array<bool> signs(tokens.size());
    for (int i = 0; i < tokens.size(); i++)
    {
      string pred = Util::trim(tokens[i]);
      if (pred.at(0) == '!') { signs.append(false); pred = pred.substr(1, pred.length()-1); }
      else                     signs.append(true);
      tokens[i] = pred;
    }

    int numPreds = tokens.size();
    Pred** preds = new Pred*[numPreds];
    for (int i = 0; i < tokens.size(); i++)
    {
      preds[i] = createPred(tokens[i]);
      if (signs[i]) preds[i]->setSign(true);
      else          preds[i]->setSign(false);
    }
    Clause* clause = new Clause(preds, numPreds);
    return clause;
  }

  int addTrivialClause(const Clause* const& clause)
  {
    if (clause->numPreds() > MAX_LEN_TRIVIAL) return 2;
    int numPreds = clause->numPreds();
    int total, numTrue;
    getTotalAndNumTrueGndings(clause, total, numTrue);
    if (numTrue != 0 && numTrue != total)  return 2;

    int retInt = (numTrue == 0) ? 0 : 1;

    Clause* copy = new Clause(*clause);
    canonicalize(copy);
    pair<ClauseSet::iterator,bool> pr = trivialClausesByLen_[numPreds]->insert(copy);
    if (!pr.second) delete copy;
    else            cout << "CREATED_TRIVIAL_CLAUSE: " << clauseStrRep(copy) << endl;
    return retInt;
  }

  bool addTrivialClauseDirectly(const Clause* const& clause)
  {
    if (clause->numPreds() > MAX_LEN_TRIVIAL) return false;
    int numPreds = clause->numPreds();
    Clause* copy = new Clause(*clause);
    canonicalize(copy);
    pair<ClauseSet::iterator,bool> pr = trivialClausesByLen_[numPreds]->insert(copy);
    if (!pr.second) { delete copy; return false; }
    cout << "CREATED_TRIVIAL_CLAUSE: " << clauseStrRep(copy) << endl;
    return true;
  }

  void getTrainingDBs(string& retDBFiles, int& retNumDBs, double& retFractAtoms)
  {
    retDBFiles     = "";
    retNumDBs      = 0;
    retFractAtoms  = 0.0;

    if (fractAtoms_ > 0.0) //if sample atoms
    {
      if (dbFiles_.size() > 1) //if multiple DBs
      {
        //sample databases
        Array<int> dbIdxs;
        for (int i = 0; i < dbFiles_.size(); i++) dbIdxs.append(i);

        double numAtomsSelected = 0.0;
        while (!dbIdxs.empty() && numAtomsSelected < fractAtoms_ * totalNumAtoms_)
        {
          int pos = random() % dbIdxs.size();
          int dbIdx = dbIdxs[pos];
          dbIdxs.removeItemFastDisorder(pos);

          retDBFiles += ((retDBFiles.empty())?"":",") + dbFiles_[dbIdx];
          cout << "sampled DB: " << dbFiles_[dbIdx] << endl;
          numAtomsSelected += numAtomsInDBs_[dbIdx];
          retNumDBs++;
        }
        retFractAtoms  = -1.0;
      }
      else
      { //sampling atoms but only one DB, so sample atoms in DB
        retDBFiles     = dbFiles_[0];
        retNumDBs      = 1;
        retFractAtoms  = fractAtoms_;
      }
    }
    else
    {  //not sampling atoms
      retNumDBs  = dbFiles_.size();
      retDBFiles = commaDelimitedDBFiles();
      retFractAtoms  = -1.0;
    }
  }

  int createTrainingDBs(int*const& dbIds, const int& numDBIds, Array<string>& retDBFiles, const StringSet& reqPredNames)
  {
    srandom(seed_);

    Array< Array<Array<string>*> > selectedDBsByDom;
    selectedDBsByDom.growToSize(dbFiles_.size());
    int numSelAtoms = selectDBs(selectedDBsByDom, dbIds, numDBIds, reqPredNames);      

    if (numSelAtoms < minAtoms_) 
    {
      for (int i = 0; i < selectedDBsByDom.size(); i++)      
        selectedDBsByDom[i].deleteItemsAndClear();
      return numSelAtoms;
    }
    
    //create DB file
    int numAtoms = 0;
    for (int d = 0; d < selectedDBsByDom.size(); d++)
    {
      Array<Array<string>*>& dbs = selectedDBsByDom[d];
      if (dbs.empty()) continue;

      string newDBFile = tmpDir_ + "D" + Util::intToString(d) + filePrefix_ + TMP_DB;
      retDBFiles.append(newDBFile);     
      ofstream out(newDBFile.c_str());  

      //Util::assertGoodOutStream(out, newDBFile);
      if (out.fail())
      {
        cout << "ERROR: failed to create " << newDBFile << endl;
        for (int i = 0; i < selectedDBsByDom.size(); i++)      
          if (!selectedDBsByDom[i].empty()) selectedDBsByDom[i].deleteItemsAndClear();
        return -1;
      }


      StringSet uniqAtoms;

      for (int i = 0; i < dbs.size(); i++)
      {
        Array<string>& db = *dbs[i];
        for (int j = 0; j < db.size(); j++)       
        {
          pair<StringSet::iterator,bool> pr = uniqAtoms.insert(db[j]);
          if (pr.second) out << db[j] << endl;
        }
        out << endl;
        if (numAtoms+(int)uniqAtoms.size() >= maxAtoms_) break;
      }

      numAtoms += uniqAtoms.size();        

      //prevent Alchemy from complaining that types have no constants
      int idx = 0;
      for (int i = 0; i < predDecls_.size(); i++)
      {
        string rel; Array<string> args;
        UUtil::readRelArgs(predDecls_[i], rel, args);
        out << rel << "(Z" << d << "_" << idx++;
        for (int j = 1; j < args.size(); j++)
          out << ",Z" << d << "_" << idx++;
        out << ")" << endl;
      }

      out.close();
      if (numAtoms >= maxAtoms_) break;
    }


    for (int i = 0; i < selectedDBsByDom.size(); i++)      
      selectedDBsByDom[i].deleteItemsAndClear();

    //exit(-1);

    return numAtoms;
  }

  int selectDBs(Array< Array<Array<string>*> >& selDBsByDom, int*const& dbIds, const int& numDBIds, const StringSet& reqPredNames)
  {
    Array< Array<Array<string>*> > udbsByDom;
    udbsByDom.growToSize( dbFiles_.size() );

    for (int i = 0; i < numDBIds; i++)
    {      
      Array<Array<Array<string>*>*>& dbsByDom = *dbIdToUnmergedDBsMap_[ dbIds[i] ];
      for (int d = 0; d < dbsByDom.size(); d++)
      {
        if (dbsByDom[d] == NULL || dbsByDom[d]->empty()) continue;
        Array<Array<string>*>& dbs = *dbsByDom[d];
        for (int j = 0; j < dbs.size(); j++)
          udbsByDom[d].append(dbs[j]);
      }
    }

    Array<int> domIds; for (int i = 0; i < udbsByDom.size(); i++) domIds.append(i);

    StringSet uniqAtoms;
    while ((int) uniqAtoms.size() < maxAtoms_ && !domIds.empty())
    {
      int domIdx = random() % domIds.size(); 
      int domId  = domIds[domIdx];
      Array<Array<string>*>& udbs = udbsByDom[domId];
      if (udbs.empty()) domIds.removeItemFastDisorder(domIdx);
      else
      {
        int udbIdx = random() % udbs.size();
        Array<string>* udb = udbs[udbIdx];
        udbs.removeItemFastDisorder(udbIdx);

        StringSet uniqPredNames;
        Array<string>* tmpudb = new Array<string>(udb->size());
        for (int i = 0; i < udb->size(); i++)
        {
          string rel; Array<string> args;
          UUtil::readRelArgs((*udb)[i], rel, args);

          string atom = rel + "(D" + Util::intToString(domId) + args[0];
          for (int j = 1; j < args.size(); j++)
            atom += ",D" + Util::intToString(domId) + args[j];
          atom += ")";

          uniqPredNames.insert(rel);
          tmpudb->append(atom);
        }

        //check whether DB supports clause
        bool hasAllPredNames;
        if (uniqPredNames.size() < reqPredNames.size()) hasAllPredNames = false;
        else
        {
          hasAllPredNames = true;
          for (StringSet::const_iterator it = reqPredNames.begin(); it != reqPredNames.end(); it++)
          {
            string predName = (*it);
            if (uniqPredNames.find(predName) == uniqPredNames.end())  { hasAllPredNames = false; break; }
          }
        }

        if (hasAllPredNames)
        {
          selDBsByDom[domId].append(tmpudb);
          for (int i = 0; i < tmpudb->size(); i++)
            uniqAtoms.insert((*tmpudb)[i]);         
        }
        else
          delete tmpudb;       


        if (udbs.empty()) domIds.removeItemFastDisorder(domIdx);
      }
    }

    return (int) uniqAtoms.size();
  }

  double runLearnWts(const string& mlnFile, const Clause* const& clause, const string& outMLNFile, const string& dbFiles,
                     const double& fractAtoms, const string& logFile, const int& numDB, const bool& print)
  {
    Array<Clause*> clauses(1);
    clauses.append((Clause*)clause);
    return runLearnWts(mlnFile, clauses, outMLNFile, dbFiles, fractAtoms, logFile, numDB, print);
  }

  double runLearnWts(const string& mlnFile, const Array<Clause*>& clauses, const string& outMLNFile, const string& dbFiles,
                     const double& fractAtoms, const string& logFile, const int& numDB, const bool& print)
  {
    bool ok = createMLNFile(mlnFile, clauses);
    if (!ok) return BAD_SCORE;
    createCommand(command_, mlnFile, outMLNFile, dbFiles, fractAtoms, logFile, numDB, print);
    system(command_);
    double loglike = readScore(logFile);
    return loglike;
  }

  void createCommand(char* const& command, const string& mlnFile, const string& outMLNFile, const string& dbFiles,
                     const double& fractAtoms, const string& logFile, const int& numDBs, const int& print)
  {
    bool sampleAtoms = (0.0 < fractAtoms && fractAtoms < 1.0);
    sprintf(command,"%s -g -i %s -o %s -t %s %s%s%s %s %s %s > %s",
            learnWtsExec_.c_str(), mlnFile.c_str(), outMLNFile.c_str(), dbFiles.c_str(),
            (sampleAtoms?" -sampleAtoms":""), (sampleAtoms?" -fractAtoms ":""), (sampleAtoms?(Util::doubleToString(fractAtoms).c_str()):""),
            ((numDBs>1)?"-multipleDatabases":""), CONV_THRESH.c_str(), ((secLimit_>0)?("-secLimit " + Util::doubleToString(secLimit_)).c_str():""), logFile.c_str());

    if (cora_)
      sprintf(command,"%s -g -i %s -o %s -t %s %s%s%s %s %s %s %s > %s",
              learnWtsExec_.c_str(), mlnFile.c_str(), outMLNFile.c_str(), dbFiles.c_str(),
              (sampleAtoms?" -sampleAtoms":""), (sampleAtoms?" -fractAtoms ":""), (sampleAtoms?(Util::doubleToString(fractAtoms).c_str()):""),
              ((numDBs>1)?"-multipleDatabases":""), CONV_THRESH.c_str(), "-ne SameBib,SameTitle,SameAuthor,SameVenue", 
              ((secLimit_>0)?("-secLimit "+Util::doubleToString(secLimit_)).c_str():""),
              logFile.c_str());

    if (print) cout << "command: " << command << endl;
  }

  double readScore(const string& logFile)
  {
    ifstream in(logFile.c_str());
    if (in.fail()) { cout << "ERROR: failed to open " << logFile << endl; return BAD_SCORE; }

    string buf;
    while (getline(in,buf))
    {
      if (buf.find("pseudo-log-likelihood = ") == 0)
      {
        string noop; double score;
        istringstream iss(buf); iss >> noop >> noop >> score;
        return score;
      }
    }

    cout << "ERROR: FAILED TO READ SCORE!" << endl;

    in.close();

    return BAD_SCORE;
  }

  string commaDelimitedDBFiles()
  {
    string dbFilesStr = dbFiles_[0];
    for (int i = 1; i < dbFiles_.size(); i++)
      dbFilesStr += "," + dbFiles_[i];
    return dbFilesStr;
  }

  void writeRules()
  {
    Array<Clause*> cands;
    getSortedCands(cands);
    ofstream out(outMLN_.c_str());  Util::assertGoodOutStream(out, outMLN_);

    for (int i = 0; i < predDecls_.size(); i++)
      out << predDecls_[i] << endl;
    out << endl;

    for (int i = 0; i < cands.size(); i++)
      out << clauseStrRep(cands[i]) << endl;

    if (WRITE_UNIT_CLAUSES_TO_MLN)
    {
      out << endl;
      for (int i = 0; i < unitClausesStr_.size(); i++)
        out << unitClausesStr_[i] << endl;
    }

    out.close();

    cout << "CANDIDATES:" << endl;
    for (int i = 0; i < cands.size(); i++)
      cout << cands[i]->score() << "  " << clauseStrRep(cands[i]) << endl;
    cout << endl;
  }

  void getSortedCands(Array<Clause*>& cands)
  {
    int numCands = 0;
    for (int i = 1; i < candsByLen_.size(); i++)
      if (candsByLen_[i] != NULL) numCands += candsByLen_[i]->size();

    cands.clear();
    cands.growToSize(numCands);
    int idx = 0;

    for (int i = 1; i < candsByLen_.size(); i++)
    {
      if (candsByLen_[i] == NULL) continue;
      ClauseSet* cset = candsByLen_[i];
      for (ClauseSet::iterator it = cset->begin(); it != cset->end(); it++)
        cands[idx++] = *it;
    }
    Util::assertt(idx == numCands, "expect idx == numCands", -1);

    qsort((Clause**)cands.getItems(), cands.size(), sizeof(Clause*), compareClausesByScore);
  }


 private:
  void readDeclFile(const string& declFile)
  {
    ifstream in(declFile.c_str());  Util::assertGoodInStream(in, declFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;
      Util::assertt(isalpha(buf.at(0)), "expect predicate declaration to start with alpha", buf, -1);

      predDecls_.append(buf);

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

  void createRelToTypesMap(const string& declFile)
  {
    relToTypesMap_.clear();
    ifstream in(declFile.c_str());  Util::assertGoodInStream(in, declFile);
    string buf;
    while(getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || Util::startsWith(buf, "//")) continue;

      string relStr;
      Array<string>* typeStrs = new Array<string>;
      UUtil::readRelArgs(buf, relStr, *typeStrs);

      cout << "Declared relation: " << relStr << "(" << (*typeStrs)[0];
      for (int i = 1; i < typeStrs->size(); i++) cout << "," << (*typeStrs)[i];
      cout << ")" << endl;

      if (relToTypesMap_.find(relStr) == relToTypesMap_.end()) relToTypesMap_[relStr] = typeStrs;
      else { Util::exit("ERROR: duplicate declaration of " + relStr, -1); }
    }
    in.close();
  }

  void createUnitClausesStr()
  {
    StringHashArray unitClauses;

    //for each relation
    for (StringToStringArrayMap::iterator it = relToTypesMap_.begin(); it != relToTypesMap_.end(); it++)
    {
      string rel = (*it).first;
      Array<string>& types = *( (*it).second );

      StringToIntMap typeToNumAppear;
      bool haveRepeatedTypes = false;
      for (int t = 0; t < types.size(); t++)
      {
        string type = types[t];
        if (typeToNumAppear.find(type) == typeToNumAppear.end()) typeToNumAppear[type] = 0;
        typeToNumAppear[type]++;
        if (typeToNumAppear[type] > 1)  haveRepeatedTypes = true;
      }

      if (!haveRepeatedTypes) continue;

      StringToIntMap typeToStartVar;
      int startVar = 0;
      for (StringToIntMap::iterator it = typeToNumAppear.begin(); it != typeToNumAppear.end(); it++)
      {
        string type = (*it).first;
        int numAppear = (*it).second;
        typeToStartVar[type] = startVar;
        startVar += numAppear;
      }
      assert(typeToStartVar.size() == typeToNumAppear.size());

      ArraysAccessor<int> acc;
      for (int t = 0; t < types.size(); t++)
      {
        string type      = types[t];
        int    numAppear = typeToNumAppear[type];
        int    startVar  = typeToStartVar[type];
        Array<int>* vars = new Array<int>;
        for (int i = 0; i < numAppear; i++) vars->append(startVar+i);
        acc.appendArray(vars);
      }

      StringToStringMap typeToVarNameMap;
      createTypeToVarNameMap(typeToVarNameMap, types);
      Array<int> vars;
      while(acc.getNextCombination(vars))
      {
        assert(vars.size() == types.size());
        IntToIntMap oldToNewVars;
        int cnt = 0;
        for (int t = 0; t < vars.size(); t++)
        {
          if (oldToNewVars.find(vars[t]) == oldToNewVars.end())
            oldToNewVars[vars[t]] = cnt++;
          vars[t] = oldToNewVars[vars[t]];
        }

        Array<string> strVars(vars.size());
        for (int t = 0; t < types.size(); t++)
          strVars.append(typeToVarNameMap[types[t]] + Util::intToString(vars[t]));

        bool haveRepeat = false;
        for (int a = 0; a < strVars.size(); a++)
          for (int b = a+1; b < strVars.size(); b++)
            if (strVars[a].compare(strVars[b])==0) { haveRepeat = true; break; }

        if (haveRepeat)
        {
          string unitClause = rel + "(" + strVars[0];
          for (int v = 1; v < strVars.size(); v++)
            unitClause += "," + strVars[v];
          unitClause += ")";
          unitClauses.append(unitClause);
        }
      }
      acc.deleteArraysAndClear();
    }//for each relation


    for (int i = 0; i < unitClauses.size(); i++)
      unitClausesStr_.append(unitClauses[i]);

    //for each relation
    for (StringToStringArrayMap::iterator it = relToTypesMap_.begin(); it != relToTypesMap_.end(); it++)
    {
      string rel = (*it).first;
      Array<string>& types = *( (*it).second );
      string unitClause = rel + "(v0";
      for (int v =  1; v < types.size(); v++)
        unitClause += ",v" + Util::intToString(v);
      unitClause += ")";
      unitClausesStr_.append(unitClause);
    }

    for (int i = 0; i < unitClausesStr_.size(); i++)
      cout << "UNIT_CLAUSE: " << unitClausesStr_[i] << endl;
  }

  void createTrivialClausesByLen()
  {
    trivialClausesByLen_.growToSize(maxLen_+1,NULL);
    for (int i = 0; i < trivialClausesByLen_.size(); i++)
      trivialClausesByLen_[i] = new ClauseSet;

    if (MAX_LEN_TRIVIAL <= 0) return;

    Array<Clause*> unitClauses(unitClausesStr_.size());
    for (int i = 0; i < unitClausesStr_.size(); i++)
    {
      Pred* pred = createPred2(unitClausesStr_[i]);
      pred->setSign(true);
      Clause* clause = createUnitClause(pred);
      unitClauses.append(clause);
    }

    cout << endl << "creating trivial unit clauses" << endl;
    pair<ClauseSet::iterator,bool> pr;
    for (int i = 0; i < unitClauses.size(); i++)
    {
      Clause* clause = unitClauses[i];
      int total, numTrue;
      getTotalAndNumTrueGndings(clause, total, numTrue);
      if (numTrue != 0 && numTrue != total) { delete clause; continue; }

      Clause* copy = new Clause(*clause);
      copy->pred(0)->setSign(false);
      copy->setHashCode();
      pr = trivialClausesByLen_[1]->insert(clause);  Util::assertt(pr.second, "trivial unit clause is a duplicate", -1);
      pr = trivialClausesByLen_[1]->insert(copy);    Util::assertt(pr.second, "trivial unit clause is a duplicate", -1);
      cout << "CREATED_TRIVIAL_UNIT_CLAUSE " << clauseStrRep(clause) << endl;
      cout << "CREATED_TRIVIAL_UNIT_CLAUSE " << clauseStrRep(copy)   << endl;
    }

    cout << "#TRIVIAL_UNIT_CLAUSES " << trivialClausesByLen_[1]->size() << endl;
  }

  void createDBIdToUnmergedDBsMap(const string& dbFile, const string& unmergeDBFiles)
  {
    Array<string> unmergeArr;
    Util::getStrings(unmergeArr, unmergeDBFiles);

    Array< Array<Array<string>*>* > allDBs(unmergeArr.size());
    for (int i = 0; i < unmergeArr.size(); i++)
    {
      string unmergeDbFile = unmergeArr[i];
      Array<Array<string>*>* dbs = createDBs(unmergeDbFile);
      allDBs.append(dbs);
    }

    Array<IntSet> allSelectedDBs;
    allSelectedDBs.growToSize(allDBs.size());

    ifstream in(dbFile.c_str());  Util::assertGoodInStream(in, dbFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || Util::startsWith(buf,"//")) continue;

      if (Util::startsWith(buf, "#START_DB"))
      {
        istringstream iss(buf); string noop; int dbId;
        iss >> noop >> dbId;

        string::size_type a = buf.find("SUP_COM");  Util::assertt(a != string::npos, "expect SUP_COM", -1);
        string::size_type b = buf.find(" ",a);      Util::assertt(b != string::npos, "expect whitespace", -1);
        string dbStrIds = Util::trim(buf.substr(b));
        Array<string> tokens(100);
        Util::tokenize(dbStrIds, tokens, " ");
        for (int j = 0; j < tokens.size(); j++)
        {
          string dbStrId = tokens[j];
          Array<string> toks(2);
          Util::tokenize(dbStrId, toks, "_");  Util::assertt(toks.size() == 2, "expect two tokens", -1);
          int unmergeDBsId = atoi( toks[0].c_str() ); //domain id
          int unmergeDBId  = atoi( toks[1].c_str() ); //id of DB within domain

          Array<Array<Array<string>*>*>* dbsByDom;

          IntToStringArrayArrayArrayMap::iterator it = dbIdToUnmergedDBsMap_.find(dbId);
          if (it == dbIdToUnmergedDBsMap_.end())
          {
            dbsByDom = new Array<Array<Array<string>*>*>;
            dbsByDom->growToSize( dbFiles_.size(), NULL );
            dbIdToUnmergedDBsMap_[dbId] = dbsByDom;
          }
          else { dbsByDom = (*it).second; }

          Array<string>* db = (*allDBs[ unmergeDBsId ])[ unmergeDBId ];

          Array<Array<string>*>*& dbs = (*dbsByDom)[unmergeDBsId];
          if (dbs == NULL) dbs = new Array<Array<string>*>;
          dbs->append(db);

          allSelectedDBs[unmergeDBsId].insert(unmergeDBId);
        }
      }
    }
    in.close();

    for (int i = 0; i < allDBs.size(); i++)
    {
      Array<Array<string>*>& dbs = *allDBs[i];
      IntSet& selectedDBIds = allSelectedDBs[i];
      for (int j = 0; j < dbs.size(); j++)
        if (selectedDBIds.find(j) == selectedDBIds.end()) delete dbs[j];
    }
    allDBs.deleteItemsAndClear();
  }

  Array<Array<string>*>* createDBs(const string& unmergeDBFile)
  {
    Array<Array<string>*>* dbs = NULL;

    ifstream in(unmergeDBFile.c_str());  Util::assertGoodInStream(in, unmergeDBFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || Util::startsWith(buf, "//")) continue;
      if (Util::startsWith(buf,"#START_GRAPH"))
      {
        istringstream iss(buf);
        string noop; int numDBs;
        iss >> noop >> noop >> numDBs;
        dbs = new Array<Array<string>*>(numDBs);
      }
      else if (Util::startsWith(buf, "#START_DB"))
      {
        Array<string>* db = new Array<string>;
        dbs->append(db);

        istringstream iss(buf);
        string noop; int dbId, numSupCom;
        iss >> noop >> dbId >> noop >> numSupCom;  Util::assertt(dbId+1 == dbs->size() && numSupCom == 1, "unexpected dbId or numSupCom " + Util::intToString(dbId) + " " + Util::intToString(numSupCom), -1);
        buf = Util::getLineAndTrim(in);
        while (!Util::startsWith(buf,"#END_DB")) { db->append(buf); buf = Util::getLineAndTrim(in); }
      }

    }
    in.close();
    Util::assertt(dbs != NULL, "expect dbs to be non-null", -1);
    return dbs;
  }

  void getTotalAndNumTrueGndings(const Clause* const& clause, int& total, int& numTrue)
  {
    string dbFiles    = commaDelimitedDBFiles();
    string mlnFile, outMLNFile, logFile;
    getFileNames(mlnFile, outMLNFile, logFile);

    createMLNFileNoUnitClauses(mlnFile, clause);

    sprintf(command_, "%s -g -i %s -o %s -t %s -multipleDatabases %s %s > %s",
            learnWtsExec_.c_str(), mlnFile.c_str(), outMLNFile.c_str(), dbFiles.c_str(), CONV_THRESH.c_str(), "-countGndings2", logFile.c_str());
    //cout << "command: " << command_ << endl;
    system(command_);

    total = -1;
    numTrue = -1;
    ifstream in(logFile.c_str());  Util::assertGoodInStream(in, logFile);
    string buf;
    while(getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;
      if (buf.find("numTrueClauseGndings") == 0)
      {
        istringstream iss(buf);
        string tmp; double dTotal, dNumTrue;
        iss >> tmp >> tmp >> tmp >> dNumTrue >> tmp >> dTotal;
        total = (int) dTotal;
        numTrue = (int) dNumTrue;
        break;
      }
    }
    Util::assertt(total >= 0 && numTrue >= 0, "failed to get clause #gndings " + clauseStrRep(clause), -1);
    in.close();

    unlink(mlnFile.c_str()); unlink(outMLNFile.c_str()); unlink(logFile.c_str());
  }

  void createTypeToVarNameMap(StringToStringMap& typeToVarNameMap, const Array<string>& types)
  {
    StringSet varNames;
    for (int t = 0; t != types.size(); t++)
    {
      string type = types[t];
      if (typeToVarNameMap.find(type) != typeToVarNameMap.end()) continue;

      bool assignedVarName = false;
      for (unsigned int i = 0; i < type.length()-1; i++)
      {
        string varName = type.substr(0,i+1);
        pair<StringSet::iterator,bool> pr = varNames.insert(varName);
        //if unique varName
        if (pr.second) { typeToVarNameMap[type] = varName; assignedVarName = true; break; }
      }

      if (assignedVarName) continue;

      int cnt = 1;
      while (true)
      {
        string varName = "";
        for (int i = 0; i < cnt; i++)
          varName += type[0];
        pair<StringSet::iterator,bool> pr = varNames.insert(varName);
        //if unique varName
        if (pr.second)  { typeToVarNameMap[type] = varName; break; }
        cnt++;
      }
    }
  }

  void getCands(const string& candFile, const int& minSup)
  {
    ifstream in(candFile.c_str());  Util::assertGoodInStream(in, candFile);
    string buf;
    int totalNumPaths  = 0;
    int numChosenPaths = 0;

    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;

      if (Util::startsWith(buf, "//LEN"))
      {
        istringstream iss(buf);
        string noop; int len; int numClauses;
        iss >> noop >> len >> noop >> numClauses;
        if (numClauses > 0) candsByLen_[len] = new ClauseSet;
      }
      else if (Util::startsWith(buf, "//")) continue;
      else
      {
        totalNumPaths++;

        //idx len sup path
        string pathStr = buf;
        string supDBIdStr = Util::getLineAndTrim(in); Util::assertt(supDBIdStr.find("DB_IDS") == 0, "expect to see DB_IDS", -1);

        Array<string> tokens(maxLen_+3);
        Util::tokenize(pathStr, tokens, " ");
        int len = atoi(tokens[1].c_str());
        int sup = atoi(tokens[2].c_str());
        if (sup >= minSup && len > 1)
        {
          //create clause
          numChosenPaths++;
          int idx = 0;
          int numPreds = tokens.size()-3;
          Pred** preds = new Pred*[numPreds];
          for (int i = 3; i < tokens.size(); i++)
            preds[idx++] = createPred(tokens[i]);
          Clause* clause = new Clause(preds, numPreds);
          candsByLen_[len]->insert(clause);

          //get the ids of DBs supporting this path
          tokens.clear();
          Util::tokenize(supDBIdStr, tokens, " ");
          int numSupDBIds = tokens.size()-1;
          int* supDBIds = new int[numSupDBIds];
          for (int s = 1; s < tokens.size(); s++)
          {
            supDBIds[s-1] = atoi( tokens[s].c_str() );
            Util::assertt( isdigit(tokens[s].at(0)), "expect DB id", -1);
          }
          clause->setDBIds(supDBIds, numSupDBIds);
        }
      }
    }

    cands_.growToSize( numChosenPaths, NULL);
    int idx = 0;
    for (int i = 1; i < candsByLen_.size(); i++)
    {
      ClauseSet* cset =candsByLen_[i];
      if (cset == NULL) continue;
      for (ClauseSet::iterator it = cset->begin(); it != cset->end(); it++)
        cands_[idx++] = (*it);
      cset->clear();
    }
    Util::assertt(idx == cands_.size(), "idx == cands_.size()", -1);

    cout << "CHOSEN_PATHS  " << numChosenPaths               << " / " << totalNumPaths << endl;
    cout << "PRUNED PATHS  " << totalNumPaths-numChosenPaths << " / " << totalNumPaths << endl;
    in.close();
  }

  Pred* createPred(const string& predStr)
  {
    string relName; Array<string> varStrs;
    UUtil::readRelArgs(predStr, relName, varStrs);
    StringToIntMap::iterator it = relNameToIdMap_.find(relName);  Util::assertt(it != relNameToIdMap_.end(), "relName not found " + relName, -1);
    int relId = (*it).second;
    int* varIds = new int[ varStrs.size() ];
    for (int i = 0; i < varStrs.size(); i++)
    {
      Util::assertt(isdigit(varStrs[i][0]), "expect args to be numbers " + predStr, -1);
      varIds[i] = atoi( varStrs[i].c_str() );
    }
    Pred* pred = new Pred(relId, false, varIds, varStrs.size());
    return pred;
  }

  Pred* createPred2(const string& predStr)
  {
    string relName; Array<string> varStrs;
    UUtil::readRelArgs(predStr, relName, varStrs);
    StringToIntMap::iterator it = relNameToIdMap_.find(relName);  Util::assertt(it != relNameToIdMap_.end(), "relName not found " + relName, -1);
    int relId = (*it).second;
    int* varIds = new int[ varStrs.size() ];

    StringToIntMap varToIdMap;

    for (int i = 0; i < varStrs.size(); i++)
    {  
      string varStr = varStrs[i];
      int varId;
      it = varToIdMap.find(varStr);
      if (it == varToIdMap.end()) { varId = varToIdMap.size(); varToIdMap[varStr] = varId; }
      else                          varId = (*it).second;

      varIds[i] = varId;
    }
    Pred* pred = new Pred(relId, false, varIds, varStrs.size());
    return pred;
  }

  void getNumAtomsInDBs(const string& commaDelimitedDBFiles)
  {
    string dbFiles    = commaDelimitedDBFiles;
    string mlnFile, outMLNFile, logFile;
    getFileNames(mlnFile, outMLNFile, logFile);

    createMLNFile(mlnFile, NULL);

    sprintf(command_, "%s -g -i %s -o %s -t %s -multipleDatabases %s %s > %s",
            learnWtsExec_.c_str(), mlnFile.c_str(), outMLNFile.c_str(), dbFiles.c_str(), CONV_THRESH.c_str(), "-countGndings", logFile.c_str());
    //cout << "command: " << command_ << endl;
    system(command_);

    numAtomsInDBs_.clear();
    ifstream in(logFile.c_str());  Util::assertGoodInStream(in, logFile);
    string buf;
    while(getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty()) continue;
      if (buf.find("numTotalGndings_ in domain ") == 0)
      {
        istringstream iss(buf);
        string tmp; int domainIdx; double numAtoms;
        iss >> tmp >> tmp >> tmp >> domainIdx >> tmp >> numAtoms;
        numAtomsInDBs_.append(numAtoms);
      }
    }
    in.close();

    for(int i = 0; i < numAtomsInDBs_.size(); i++)
      cout << "NUM_ATOMS_IN_DB_" << i << "  " << numAtomsInDBs_[i] << endl;
    cout << numAtomsInDBs_.size() << endl; //MYEDIT
    cout << dbFiles_.size() << endl;       //MYEDIT
    Util::assertt(numAtomsInDBs_.size() == dbFiles_.size(), "expect numAtomsInDB_.size() == dbFiles_.size()", -1);

    totalNumAtoms_ = 0;
    for (int i = 0; i < numAtomsInDBs_.size(); i++)
      totalNumAtoms_ += numAtomsInDBs_[i];
    cout << "TOTAL_NUM_ATOMS_IN_DBS  " << totalNumAtoms_ << endl;

    unlink(mlnFile.c_str()); unlink(outMLNFile.c_str()); unlink(logFile.c_str());
  }

  bool createMLNFile(const string& mlnFile, const Array<Clause*>& clauses)
  {
    ofstream out(mlnFile.c_str());  
    if (out.fail()) { cout << "ERROR: (a) failed to open " << mlnFile << endl; return false; }

    out << "//predicate declarations" << endl;
    for (int i = 0; i < predDecls_.size(); i++)
      out << predDecls_[i] << endl;

    out << endl;
    for (int i = 0; i < clauses.size(); i++)
      out << clauseStrRep(clauses[i]) << endl;
    out <<  endl;

    for (int i = 0; i < unitClausesStr_.size(); i++)
      out << unitClausesStr_[i] << endl;
    out.close();
    return true;
  }

  bool createMLNFile(const string& mlnFile, const Clause* const& clause)
  {
    ofstream out(mlnFile.c_str());
    if (out.fail()) { cout << "ERROR: (b) failed to open " << mlnFile << endl; return false; }

    out << "//predicate declarations" << endl;
    for (int i = 0; i < predDecls_.size(); i++)
      out << predDecls_[i] << endl;

    out << endl << clauseStrRep(clause) << endl <<  endl;

    for (int i = 0; i < unitClausesStr_.size(); i++)
      out << unitClausesStr_[i] << endl;
    out.close();
    return true;
  }

  bool createMLNFileNoUnitClauses(const string& mlnFile, const Clause* const& clause)
  {
    ofstream out(mlnFile.c_str());
    if (out.fail()) { cout << "ERROR: (b) failed to open " << mlnFile << endl; return false; }

    out << "//predicate declarations" << endl;
    for (int i = 0; i < predDecls_.size(); i++)
      out << predDecls_[i] << endl;

    out << endl << clauseStrRep(clause) << endl << endl;
    out.close();
    return true;
  }

  void getFileNames(string& mlnFile, string& outMLNFile, string& logFile)
  {
    mlnFile    = tmpDir_ + filePrefix_ + TMP_MLN;
    outMLNFile = tmpDir_ + filePrefix_ + TMP_OUT_MLN;
    logFile    = tmpDir_ + filePrefix_ + TMP_LOG;
  }

 private:
  void createFlipClauses(Array<Clause*>& clauses, const Clause* const& cand)
  {
    clauses.clear();
    if (numFlips_ >= cand->numPreds())  createAllFlipClauses(clauses, cand);
    else if (numFlips_ <= 0)            clauses.append(new Clause(*cand));
    else                                createSomeFlipClauses(clauses, cand);
   
    if (areTwoSymPreds(cand)) removeRedundantTwoSymPreds(clauses);
    for (int i = 0; i < clauses.size(); i++) canonicalize(clauses[i]);
    removeDuplicates(clauses);
  }

  void createAllFlipClauses(Array<Clause*>& clauses, const Clause* const& cand)
  {
    int numPreds = cand->numPreds();

    clauses.growToSize( int(pow(2.0,numPreds)) );
    int clauseIdx = 0;

    ArraysAccessor<bool> acc;
    for (int i = 0; i < numPreds; i++)
    {
      Array<bool>* barr = new Array<bool>(2);
      barr->append(true); barr->append(false);
      acc.appendArray(barr);
    }

    while(acc.hasNextCombination())
    {
      Clause* clause = new Clause(*cand);
      Pred** preds = clause->preds();

      bool sign;
      int idx = 0;
      while (acc.nextItemInCombination(sign))             
        preds[idx++]->setSign(sign);
      
      clause->setHashCode();
      clauses[ clauseIdx++ ] = clause;
    }

    acc.deleteArraysAndClear();
    Util::assertt(clauseIdx == clauses.size(), "expect clauseIdx == clauses.size()",-1);
  }

  void createSomeFlipClauses(Array<Clause*>& clauses, const Clause* const& cand)
  {
    for (int flip = 1; flip <= numFlips_; flip++)
    {
      Array<int> curIdxs;
      createSomeFlipClauses(flip, curIdxs, clauses, cand);
    }

    //add the clause with all negated predicates (i.e. no flips)
    Clause* clause = new Clause(*cand);
    Pred**  preds  = clause->preds();
    int numPreds   = clause->numPreds();
    for (int i = 0; i < numPreds; i++)
      preds[i]->setSign(false);
    clause->setHashCode();
    clauses.append(clause);    
  }

  void createSomeFlipClauses(const int& numFlip, Array<int>& curIdxs, Array<Clause*>& clauses, const Clause* const& cand)
  {
    if (numFlip == 0)
    {
      Clause* clause = new Clause(*cand);
      Pred**  preds  = clause->preds();
      for (int i = 0; i < curIdxs.size(); i++)
        preds[ curIdxs[i] ]->setSign(true);
      clause->setHashCode();
      clauses.append(clause);

    }
    else
    {
      int startIdx = curIdxs.empty() ? 0 : curIdxs.lastItem()+1;
      int endIdx   = (cand->numPreds()-1)-numFlip+1;
      for (int i = startIdx; i <= endIdx; i++)
      {
        curIdxs.append(i);
        createSomeFlipClauses(numFlip-1, curIdxs, clauses, cand);
        curIdxs.removeLastItem();
      }
    }
  }

  void removeRedundantTwoSymPreds(Array<Clause*>& clauses)
  {
    //remove  R(x,y) v !R(y,x), !R(x,y) v !R(y,x),  R(x,y) v  R(y,x)
    Array<Clause*> tmpClauses(clauses);
    clauses.clear();
    for (int i = 0; i < tmpClauses.size(); i++)
    {        
      bool sign0 = tmpClauses[i]->pred(0)->sign();
      bool sign1 = tmpClauses[i]->pred(1)->sign();
      if (!sign0 && sign1) clauses.append(tmpClauses[i]);
      else                 delete tmpClauses[i];
    }
  }

  void canonicalize(Clause* const& clause)
  {
    Pred** preds = clause->preds();
    int numPreds = clause->numPreds();
    qsort(preds, numPreds, sizeof(Pred*), comparePredByIdAndSign);
    renumVars(preds, numPreds);
    qsort(preds, numPreds, sizeof(Pred*), comparePredByIdAndSign);
    bool sswitch = switchSymBinPredVarIds(clause);
    if (sswitch) qsort(preds, numPreds, sizeof(Pred*), comparePredByIdAndSign);
    clause->setHashCode();
  }

  void removeDuplicates(Array<Clause*>& clauses)
  {
    ClauseSet cset;
    Array<Clause*> tmpClauses(clauses);
    clauses.clear();
    for (int i = 0; i < tmpClauses.size(); i++)
    {
      Clause* clause = tmpClauses[i];
      pair<ClauseSet::iterator, bool> pr = cset.insert(clause);
      if (pr.second)   clauses.append(clause);
      else           { cout << "remove duplicate: " << clauseStrRep(clause) << endl; delete clause; }
    }
  }

 private:
  void createSubClauses(Array<Clause*>& subClauses, const Clause* const& cand, const int& len)
  {
    if (len >= cand->numPreds()) return;

    Pred** preds = cand->preds();
    int numPreds = cand->numPreds();

    Array<Clause*> allChosen;
    Array<int> curIdxs;
    choose(len, preds, curIdxs, &allChosen, NULL, len, numPreds);

    //append clauses from shortest to longest
    subClauses.clear();
    subClauses.growToSize( allChosen.size() );
    int idx = 0;
    for (int i = 0; i < allChosen.size(); i++)
    {
      canonicalize( allChosen[i] );
      subClauses[idx++] = allChosen[i];
    }
  }

  void createSubClauses(Array<Clause*>& subClauses, const Clause* const& cand)
  {
    Pred** preds = cand->preds();
    int numPreds = cand->numPreds();
    int halfLen  = numPreds/2;

    Array<Clause*> allChosen, allChosen2;
    for (int i = 1; i <= halfLen; i++)
    {
      int numToChoose = i;
      Array<int> curIdxs;
      choose(numToChoose, preds, curIdxs, &allChosen, &allChosen2, i, numPreds);
    }

    //append clauses from shortest to longest
    subClauses.clear();
    subClauses.growToSize( allChosen.size() + allChosen2.size() );
    int idx = 0;
    for (int i = 0; i < allChosen.size(); i++)
    {
      canonicalize( allChosen[i] );
      subClauses[idx++] = allChosen[i];
    }
    for (int i = allChosen2.size()-1; i >= 0; i--)
    {
      canonicalize( allChosen2[i] );
      subClauses[idx++] = allChosen2[i];
    }
  }

  void choose(const int& numToChoose, Pred** const& preds, Array<int>& curIdxs, Array<Clause*>* const& chosen, Array<Clause*>* const& chosen2,
              const int& origNumToChoose, const int& numPreds)
  {
    if (numToChoose == 0)
    {
      IntHashArray chosenIdxs;
      for (int i = 0; i < curIdxs.size(); i++)
        chosenIdxs.append(curIdxs[i]);

      Array<Pred*> preds1, preds2;
      for (int i = 0; i < numPreds; i++)
      {
        if (chosenIdxs.contains(i)) preds1.append(preds[i]);
        else                        preds2.append(preds[i]);
      }

      if (origNumToChoose > 1 && chosen)                                   chosen->append(  createClause(preds1)  );
      if ((origNumToChoose != numPreds/2 || numPreds % 2 != 0) && chosen2) chosen2->append( createClause(preds2) );
      return;
    }

    int startIdx = curIdxs.empty() ? 0 : curIdxs.lastItem()+1;
    int endIdx   = (numPreds-1)-numToChoose+1;
    for (int i = startIdx; i <= endIdx; i++)
    {
      curIdxs.append(i);
      choose(numToChoose-1, preds, curIdxs, chosen, chosen2, origNumToChoose, numPreds);
      curIdxs.removeLastItem();
    }
  }

  Clause* createClause(const Array<Pred*>& ppreds)
  {
    int numPreds = ppreds.size();
    Pred** preds = new Pred*[numPreds];
    for (int i = 0; i < numPreds; i++)
      preds[i] = new Pred(*ppreds[i]);
    normalizeVar(preds, numPreds);
    Clause* clause = new Clause(preds, numPreds);
    return clause;
  }

  void normalizeVar(Pred** const& preds, const int& numPreds)
  {
    renumVars(preds, numPreds);

    for (int i = 0; i < numPreds; i++)
    {
      int j = i;
      for (; j < numPreds; j++)
        if (preds[i]->relId() != preds[j]->relId()) break;
      j--;

      if (j > i)  qsort(&(preds[i]), j-i+1, sizeof(Pred*), comparePred);

      i = j;
    }
  }

  void renumVars(Pred** const& preds, const int& numPreds)
  {
    IntToIntMap oldToNewVar;
    for (int i = 0; i < numPreds; i++)
    {
      Pred* pred      = preds[i];
      int*  varIds    = pred->varIds();
      int   numVarIds = pred->numVarIds();

      for (int j = 0; j < numVarIds; j++)
      {
        int oldVar = varIds[j];
        IntToIntMap::iterator it = oldToNewVar.find(oldVar);
        int newVar;
        if (it == oldToNewVar.end()) { newVar = oldToNewVar.size(); oldToNewVar[oldVar] = newVar; }
        else                         { newVar = (*it).second; }
        varIds[j] = newVar;
      }
    }
  }

  string clauseStrRep(const Clause* const& clause)
  {
    if (clause == NULL) return "";
    Pred** preds = clause->preds();
    int numPreds = clause->numPreds();
    string str = predStrRep(preds[0]);
    for (int i = 1; i < numPreds; i++)
      str += " v " + predStrRep(preds[i]);
    return str;
  }

  string predStrRep(const Pred* const& pred)
  {
    int  relId     = pred->relId();
    int* varIds    = pred->varIds();
    int  numVarIds = pred->numVarIds();
    bool sign      = pred->sign();

    string str = ((sign)?"":"!") + relIdToNameMap_[relId] + "(v" + Util::intToString(varIds[0]);
    for (int i = 1; i < numVarIds; i++)
      str += ",v" + Util::intToString(varIds[i]);
    str += ")";
    return str;
  }

 private:
  void checkCora(Array<Clause*>& clauses)
  {
    Array<Clause*> copies(clauses);
    clauses.clear();
    for (int i = 0; i < copies.size(); i++)    
      if (checkCoraHelper(copies[i])) clauses.append(copies[i]);
      else                            delete copies[i];     
  }

  bool checkCoraHelper(const Clause* const& clause)
  {
    int numSamePred = 0;
    int numNonNegSamePred = 0;
    int numNonNeg = 0;

    Pred** preds = clause->preds();
    int numPreds = clause->numPreds();
    for (int i = 0; i < numPreds; i++)
    {
      Pred* pred = preds[i];
      int  relId = pred->relId();
      bool sign  = pred->sign();
      string predName = relIdToNameMap_[relId];
      bool isSamePred = Util::startsWith(predName,"Same");

      if (isSamePred) numSamePred++;
      if (sign) numNonNeg++;
      if (isSamePred && sign) numNonNegSamePred++;
    }

    //must have at least one SameX pred
    if (numSamePred == 0) return false;

    //if have non-negated, at least one must be SameX pred
    if (numNonNeg > 0 && numNonNegSamePred == 0) return false;
    
    return true;
  }
};

#endif
