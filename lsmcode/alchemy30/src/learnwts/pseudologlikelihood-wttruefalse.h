/*
 * All of the documentation and software included in the
 * Alchemy Software is copyrighted by Stanley Kok, Parag
 * Singla, Matthew Richardson, Pedro Domingos, Marc
 * Sumner, Hoifung Poon, and Daniel Lowd.
 * 
 * Copyright [2004-07] Stanley Kok, Parag Singla, Matthew
 * Richardson, Pedro Domingos, Marc Sumner, Hoifung
 * Poon, and Daniel Lowd. All rights reserved.
 * 
 * Contact: Pedro Domingos, University of Washington
 * (pedrod@cs.washington.edu).
 * 
 * Redistribution and use in source and binary forms, with
 * or without modification, are permitted provided that
 * the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above
 * copyright notice, this list of conditions and the
 * following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the
 * above copyright notice, this list of conditions and the
 * following disclaimer in the documentation and/or other
 * materials provided with the distribution.
 * 
 * 3. All advertising materials mentioning features or use
 * of this software must display the following
 * acknowledgment: "This product includes software
 * developed by Stanley Kok, Parag Singla, Matthew
 * Richardson, Pedro Domingos, Marc Sumner, Hoifung
 * Poon, and Daniel Lowd in the Department of Computer Science and
 * Engineering at the University of Washington".
 * 
 * 4. Your publications acknowledge the use or
 * contribution made by the Software to your research
 * using the following citation(s): 
 * Stanley Kok, Parag Singla, Matthew Richardson and
 * Pedro Domingos (2005). "The Alchemy System for
 * Statistical Relational AI", Technical Report,
 * Department of Computer Science and Engineering,
 * University of Washington, Seattle, WA.
 * http://www.cs.washington.edu/ai/alchemy.
 * 
 * 5. Neither the name of the University of Washington nor
 * the names of its contributors may be used to endorse or
 * promote products derived from this software without
 * specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF WASHINGTON
 * AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY
 * OF WASHINGTON OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
#ifndef LOGPSEUDOLIKELIHOOD_H_AUG_18_2005
#define LOGPSEUDOLIKELIHOOD_H_AUG_18_2005

#include <cmath>
#include "util.h"
#include "array.h"
#include "random.h"
#include "domain.h"
#include "clause.h"
#include "mln.h"
#include "indextranslator.h"

//NOTE: "domain index" and "database index" are used interchangeably

  // expl and logl aren't available in cygwin / windows, so use exp and log
#ifndef expl
# define expl exp
# define logl log
#endif

////////////////////////// helper data structures //////////////////////////////

  //LogPseudolikelihood is used in weight learning which makes the closed-world
  //assumption, so there is no ground predicate whose truth value is UNKNOWN
const bool DB_HAS_UNKNOWN_PREDS = false;

struct IndexAndCount 
{
  IndexAndCount() : index(NULL), count(0) {}
  IndexAndCount(int* const & i, const double& c) : index(i), count(c) {}
  int* index;
  double count;
};

  // used to info required to undo the addition/removal of IndexAndCount
struct UndoInfo
{
  UndoInfo(Array<IndexAndCount*>* const & affArr, 
           IndexAndCount* const & iac, const int& remIdx, const int& domIdx)
    : affectedArr(affArr), remIac(iac), remIacIdx(remIdx), domainIdx(domIdx) {}
  ~UndoInfo() {if (remIac) delete remIac; }
  Array<IndexAndCount*>* affectedArr;
  IndexAndCount* remIac; //appended or removed IndexAndCount
  int remIacIdx; //index of remIac before it was removed from affectedArr
  int domainIdx;
};


struct SampledGndings
{
  IntHashArray trueGndings;
  IntHashArray falseGndings;
  int totalTrue;
  int totalFalse;
};


/////////////////////////////////////////////////////////////////////////////

  //This class returns the negative of the weighted pseudo-log-likelihood.
class PseudoLogLikelihood
{
 public:
  PseudoLogLikelihood(const Array<bool>* const & areNonEvidPreds,
                      const Array<Domain*>* const & domains,
                      const bool& wtFOPred, const bool& sampleGndPreds, 
                      const double& fraction, const int& minGndPredSamples, 
                      const int& maxGndPredSamples) 
    : domains_(new Array<Domain*>) , numMeans_(-1), 
      priorMeans_(NULL), priorStdDevs_(NULL), wtFOPred_(wtFOPred),
      sampleGndPreds_(sampleGndPreds), idxTrans_(NULL), 
      numClauseGndings_(NULL), numTotalGndings_(NULL), numPreds_(NULL),
      totalGndings_(0.0)
  {
    if (areNonEvidPreds)
    {
      areNonEvidPreds_ = new Array<bool>(*areNonEvidPreds);
      assert(areNonEvidPreds_->size() == (*domains)[0]->getNumPredicates());
    }
    else
    {
      areNonEvidPreds_ = new Array<bool>;
      areNonEvidPreds_->growToSize((*domains)[0]->getNumPredicates(), true);
    }

    int numDomains = domains->size();
    assert(numDomains > 0);
    domains_->growToSize(numDomains,NULL);
    for (int i = 0; i < numDomains; i++)
      (*domains_)[i] = (*domains)[i];

    gndPredClauseIndexesAndCountsArr_ 
      = new Array<Array<Array<Array<Array<IndexAndCount*>*>*>*>*>;
    gndPredClauseIndexesAndCountsArr_->growToSize(numDomains,NULL);
    for (int i = 0; i < numDomains; i++)
    {        
      (*gndPredClauseIndexesAndCountsArr_)[i] 
        = new Array<Array<Array<Array<IndexAndCount*>*>*>*>;
      (*gndPredClauseIndexesAndCountsArr_)[i]->growToSize(
                                       (*domains_)[i]->getNumPredicates(),NULL);
    }

    //TODO: CHANGED 2
    gndPredTruthValues_ = new Array<Array<Array<bool>*>*>;
    gndPredTruthValues_->growToSize(numDomains,NULL);
    for (int i = 0; i < numDomains; i++)
    {
      (*gndPredTruthValues_)[i] = new Array<Array<bool>*>;
      (*gndPredTruthValues_)[i]->growToSize((*domains_)[i]->getNumPredicates(),NULL);
    }
    
    
    createNumGndings();

    if (sampleGndPreds_)
    {
      sampledGndingsMaps_ = new Array<Array<SampledGndings*>*>;
      sampledGndingsMaps_->growToSize(numDomains, NULL);
      for (int i = 0; i < numDomains; i++)
      {
        (*sampledGndingsMaps_)[i] = new Array<SampledGndings*>;
        (*sampledGndingsMaps_)[i]->growToSize((*domains_)[i]->getNumPredicates()
                                              , NULL);
      }
      random_ = new Random;
      random_->init(-3);
      samplePredGroundings(fraction, minGndPredSamples,  maxGndPredSamples);
    }
    else
    {
      sampledGndingsMaps_ = NULL;      
      random_ = NULL;
    }
  }

  
  ~PseudoLogLikelihood()
  {    
    delete areNonEvidPreds_;
    delete domains_;

    for (int i = 0; i < gndPredClauseIndexesAndCountsArr_->size(); i++)
    {
      Array<Array<Array<Array<IndexAndCount*>*>*>*>*
      gndPredClauseIndexesAndCounts
        = (*gndPredClauseIndexesAndCountsArr_)[i];

      int numPreds = gndPredClauseIndexesAndCounts->size();
      for (int p = 0; p < numPreds; p++) // for each predicate
      {
        if ( (*gndPredClauseIndexesAndCounts)[p] )
        {
          Array<Array<Array<IndexAndCount*>*>*>* gndingsToClauseIndexesAndCounts
            = (*gndPredClauseIndexesAndCounts)[p];
          int numGnds = gndingsToClauseIndexesAndCounts->size();
          for (int g = 0; g < numGnds; g++) // for each grounding
          {
            for (int h = 0; h < (*gndingsToClauseIndexesAndCounts)[g]->size(); 
                 h++)
            {
              for (int j = 0;
                   j < (*(*gndingsToClauseIndexesAndCounts)[g])[h]->size();
                   j++)
              {
                delete (*(*(*gndingsToClauseIndexesAndCounts)[g])[h])[j];
              }
              delete (*(*gndingsToClauseIndexesAndCounts)[g])[h];
            }
            delete (*gndingsToClauseIndexesAndCounts)[g];
          }
          delete gndingsToClauseIndexesAndCounts;
        }
      }
      delete gndPredClauseIndexesAndCounts;      
    }
    delete gndPredClauseIndexesAndCountsArr_;

    
    //TODO: CHANGED 2   
    for (int d = 0; d < gndPredTruthValues_->size(); d++)
      (*gndPredTruthValues_)[d]->deleteItemsAndClear();
    gndPredTruthValues_->deleteItemsAndClear();
    delete gndPredTruthValues_;
    //TODO: CHANGED 2
    numGndingsTrue_->deleteItemsAndClear();
    numGndingsFalse_->deleteItemsAndClear();
    delete numGndingsTrue_;
    delete numGndingsFalse_;
    
    numGndings_->deleteItemsAndClear();      
    delete numGndings_;
    delete numTotalGndings_;
    delete numPreds_;
    
    if (sampledGndingsMaps_)
    {
      for (int i = 0; i < sampledGndingsMaps_->size(); i++)
      {
        (*sampledGndingsMaps_)[i]->deleteItemsAndClear();
        delete (*sampledGndingsMaps_)[i];
      }
      delete sampledGndingsMaps_;
    }

    if (random_) delete random_;
  }


  void compress()
  {
    for (int i = 0; i < gndPredClauseIndexesAndCountsArr_->size(); i++)
    {
      Array<Array<Array<Array<IndexAndCount*>*>*>*>*
      gndPredClauseIndexesAndCounts 
        = (*gndPredClauseIndexesAndCountsArr_)[i];
      
      int numPreds = gndPredClauseIndexesAndCounts->size();
      for (int p = 0; p < numPreds; p++) // for each predicate
      {

        if ((*gndPredClauseIndexesAndCounts)[p])
        {
          Array<Array<Array<IndexAndCount*>*>*>* gndingsToClauseIndexesAndCounts
            = (*gndPredClauseIndexesAndCounts)[p];
          int numGnds = gndingsToClauseIndexesAndCounts->size();
          for (int g = 0; g < numGnds; g++) // for each grounding
          {
            Array<Array<IndexAndCount*>*>* combosToClauseIndexesAndCounts
              = (*gndingsToClauseIndexesAndCounts)[g];
            int numCombos = combosToClauseIndexesAndCounts->size();
            for (int c = 0; c < numCombos; c++) // for each combo
              (*combosToClauseIndexesAndCounts)[c]->compress();
          }
        }
      }
    }

    //TODO: CHANGED 2
    for (int i = 0; i < gndPredTruthValues_->size(); i++)
    {
      Array<Array<bool>*>* domTVs = (*gndPredTruthValues_)[i];
      for (int p = 0; p < domTVs->size(); p++)
      {
        Array<bool>* tvs = (*domTVs)[p];
        if (tvs) tvs->compress();
      }
    }


    //numGndings_ not compress because set to exact size in constructor
  }

  
    //similar to computeAndSetCounts()
  void insertCounts(int* const & clauseIdxInMLN,
                    Array<UndoInfo*>* const & undoInfos,
                    Array<Array<Array<CacheCount*>*>*>* const & cache,
                    const int& d)
  {
    Array<Array<Array<Array<IndexAndCount*>*>*>*>*
    gndPredClauseIndexesAndCounts;

    Array<IndexAndCount*>* gArr;
    CacheCount* cc;
    assert(cache->size() == domains_->size());

    gndPredClauseIndexesAndCounts = (*gndPredClauseIndexesAndCountsArr_)[d];
    for (int p = 0; p < (*cache)[d]->size(); p++)
    {
      Array<CacheCount*>* ccArr = (*(*cache)[d])[p];
      if (ccArr == NULL) continue;
      for (int i = 0; i < ccArr->size(); i++)
      {
        assert((*gndPredClauseIndexesAndCounts)[p] != NULL);
        cc = (*ccArr)[i];
        gArr = (*(*(*gndPredClauseIndexesAndCounts)[p])[cc->g])[cc->c];
          //gth grounding of clause's pred should not have been looked at
        assert(gArr->size()==0 ||*(gArr->lastItem()->index)!=*clauseIdxInMLN);
        assert(cc->cnt != 0);
        gArr->append(new IndexAndCount(clauseIdxInMLN, cc->cnt));
        if (undoInfos) undoInfos->append(new UndoInfo(gArr, NULL, -1, d));
      }
    }
  } 


    //similar to computeAndSetCounts()
  void insertCounts(const Array<int*>& clauseIdxInMLNs,
                    Array<UndoInfo*>* const & undoInfos,
                    Array<Array<Array<CacheCount*>*>*>* const & cache)
  {
    assert(cache->size() == domains_->size());
    assert(clauseIdxInMLNs.size() == domains_->size());

    for (int d = 0; d < cache->size(); d++) 
      insertCounts(clauseIdxInMLNs[d], undoInfos, cache, d);
  }


    //If undoInfos is not NULL, it is used to store pointers to 
    //Array<IndexAndCount*> that have new entries appended so that the new
    //entries can be easily removed later.
  void computeCountsForNewAppendedClause(const Clause* const & c,
                                         int* const & clauseIdxInMLN,
                                         const int& domainIdx,
                                         Array<UndoInfo*>* const & undoInfos,
                                         const bool& sampleClauses,
                              Array<Array<Array<CacheCount*>*>*>* const & cache)
  {
    computeCountsRemoveCountsHelper(true, c, clauseIdxInMLN, domainIdx, 
                                    undoInfos, sampleClauses, cache);
  }


  void removeCountsForClause(const Clause* const & c, 
                             int* const & clauseIdxInMLN, const int& domainIdx,
                             Array<UndoInfo*>* const & undoInfos)
  {
    computeCountsRemoveCountsHelper(false, c, clauseIdxInMLN, domainIdx, 
                                    undoInfos, false, NULL);
  }


    //the contents of undoInfos will be deleted
  void undoAppendRemoveCounts(const Array<UndoInfo*>* const & undoInfos)
  {
    for (int i = undoInfos->size() - 1; i >= 0; i--)
    {
      if ((*undoInfos)[i]->remIacIdx >= 0) // if this was a removal
      {
        Array<IndexAndCount*>* affectedArr = (*undoInfos)[i]->affectedArr;
        IndexAndCount* remIac = (*undoInfos)[i]->remIac;
        (*undoInfos)[i]->remIac = NULL; //so that it won't get deleted later
        int remIacIdx = (*undoInfos)[i]->remIacIdx;

        if (affectedArr->size() == remIacIdx) //if removed item was the last one
          affectedArr->append(remIac);
        else
        {
          assert(remIacIdx < affectedArr->size());
          IndexAndCount* tmpRemIac = (*affectedArr)[remIacIdx];
          (*affectedArr)[remIacIdx] = remIac;
          affectedArr->append(tmpRemIac);
        }
      }
      else
      {    // this was an addition
        IndexAndCount* iac = (*undoInfos)[i]->affectedArr->removeLastItem();
        delete iac;
      }

      assert(noRepeatedIndex((*undoInfos)[i]->affectedArr));
      delete (*undoInfos)[i];
    }
  }


  double getValueAndGradient(double* const & gradient, const double* const & wt, const int& arrSize)
  {
    double wpll = 0;
    memset(gradient, 0, arrSize*sizeof(double));

        //if there is one database, or the clauses for all databases line up
    if (idxTrans_ == NULL)
    {
      for (int i = 0; i < domains_->size(); i++)
        wpll += getValueAndGradientForDomain(gradient, wt, arrSize, i);
    }
    else
    {
      cout<<"ERROR: expect clauses for multiple DBs to line up"<<endl;//CHANGED:
      exit(-1);

      //the clauses for multiple databases do not line up
      Array<Array<double> >* wtsPerDomain = idxTrans_->getWtsPerDomain();
      Array<Array<double> >* gradsPerDomain = idxTrans_->getGradsPerDomain();
      const Array<Array<Array<IdxDiv>*> >* cIdxToCFIdxsPerDomain 
        = idxTrans_->getClauseIdxToClauseFormulaIdxsPerDomain();
      
      for (int i = 0; i < domains_->size(); i++)
      {
        Array<double>& wts = (*wtsPerDomain)[i];
        Array<double>& grads = (*gradsPerDomain)[i];
        assert(grads.size() == wts.size()); //size is num of clauses in domain i
        memset((double*)wts.getItems(), 0, wts.size()*sizeof(double));
        memset((double*)grads.getItems(), 0, grads.size()*sizeof(double));

        //NOTE: wts, grads and *cIdxToCFIdxsPerDomain)[i] may be larger than
        //      the actual number of clauses in domain i. This occurs in order
        //      to avoid the cost of resizing the the arrays, and is why we need
        //      the two "if ((*idxDivs)[k].idx < arrSize)" checks below.

          //map clause/formula weights to clause weights
        for (int j = 0; j < wts.size(); j++)
        {
          Array<IdxDiv>* idxDivs =(*cIdxToCFIdxsPerDomain)[i][j];          
          for (int k = 0; k < idxDivs->size(); k++)
            if ((*idxDivs)[k].idx < arrSize)
              wts[j] += wt[ (*idxDivs)[k].idx ] / (*idxDivs)[k].div;
        }
                
        wpll += getValueAndGradientForDomain((double*)grads.getItems(), 
                                            (double*)wts.getItems(), 
                                            wts.size(), i);
        
          // map clause gradient to clause/formula gradients
        for (int j = 0; j < grads.size(); j++)
        {
          Array<IdxDiv>* idxDivs =(*cIdxToCFIdxsPerDomain)[i][j];          
          for (int k = 0; k < idxDivs->size(); k++)
            if ((*idxDivs)[k].idx < arrSize)            
              gradient[ (*idxDivs)[k].idx ] += grads[j] / (*idxDivs)[k].div;
        }
      } // for each domain
    }

    //printWtsGradsWPLL(wt, gradient, arrSize, wpll); //for testing //DEBUG:

    //bool useLBFGSB = false;
    bool useLBFGSB = true;

    bool useGaussianPriors;
    if (useLBFGSB) { useGaussianPriors = (numMeans_ > 0); }
    else           { useGaussianPriors = false; }

      // if there are prior penalties
    //if (numMeans_ > 0)
    if (useGaussianPriors)
    {
      //commented out: numMeans_ can be larger than arrSize,so just consider
      //               the first arrSize items in priorMeans & priorStdDevs
      //assert(numMeans_ == arrSize);
        
        // subtract the gaussian priors
      for (int i = 0; i < arrSize; i++)
      {
        //since at this point the value and gradient have been negated,
        //add the priors
        
        double n=(numClauseGndings_)?(*numClauseGndings_)[i]:1.0;//CHANGED:

        wpll += (wt[i]-priorMeans_[i])*(wt[i]-priorMeans_[i])/
                (2*priorStdDevs_[i]*priorStdDevs_[i])
                 * n;
        
        gradient[i] += (wt[i]-priorMeans_[i])/
                       (priorStdDevs_[i]*priorStdDevs_[i])
                       * n;
      }
    }
    
    //printWtsGradsWPLL(wt, gradient, arrSize, wpll); //for testing //DEBUG:
   
    return wpll;
  } 

    //set numMeans to -1 if there is no prior
  void setMeansStdDevs(const int& arrSize, const double* const & priorMeans, 
                       const double* const & priorStdDevs)
  {
    numMeans_ = arrSize;
    priorMeans_ = priorMeans;
    priorStdDevs_ = priorStdDevs;
  }


  void setSampleGndPreds(const bool& sgp) 
  { 
    if (sgp) { assert(sampledGndingsMaps_); assert(random_); }
    sampleGndPreds_ = sgp; 
  }


  bool checkNoRepeatedIndex(const MLN* const & mln=NULL)
  {
    bool ret = true;
    for (int d = 0; d < domains_->size(); d++)
    {
      Array<Array<Array<Array<IndexAndCount*>*>*>*>*
      gndPredClauseIndexesAndCounts
        = (*gndPredClauseIndexesAndCountsArr_)[d];

      int numPreds = gndPredClauseIndexesAndCounts->size();
      for (int p = 0; p < numPreds; p++) // for each predicate
      {
        Array<Array<Array<IndexAndCount*>*>*>* gndingsToClauseIndexesAndCounts 
          = (*gndPredClauseIndexesAndCounts)[p];
        
        if (gndingsToClauseIndexesAndCounts == NULL) continue;
        
        int numGnds = gndingsToClauseIndexesAndCounts->size();
        for (int g = 0; g < numGnds; g++) // for each grounding
        {
          Array<Array<IndexAndCount*>*>* gndings 
            = (*gndingsToClauseIndexesAndCounts)[g];

          for (int c = 0; c < gndings->size(); c++)
          {
            bool ok = noRepeatedIndex((*gndings)[c], mln);
            if (!ok) 
            {
              cout << "ERROR: repeated index in domain " << d << " for pred " 
                   << (*domains_)[0]->getPredicateName(p) << " gnding " << g 
                   << " combination " << c << endl;
              ret = false;
            }
          }
        }
      } // for each predicate
    } // for each domain
    return ret;
  }


  void printGndPredClauseIndexesAndCounts(const MLN* const & mln=NULL)
  {
    for (int d = 0; d < domains_->size(); d++)
    {
      cout << "domainIdx: " << d << endl;
      cout << "gndPredClauseIndexesAndCounts[predIdx][gndingIdx][combIdx][i]"
           << endl;

      Array<Array<Array<Array<IndexAndCount*>*>*>*>*
      gndPredClauseIndexesAndCounts
        = (*gndPredClauseIndexesAndCountsArr_)[d];

      int numPreds = gndPredClauseIndexesAndCounts->size();
      for (int p = 0; p < numPreds; p++) // for each predicate
      {
        Array<Array<Array<IndexAndCount*>*>*>* gndingsToClauseIndexesAndCounts 
          = (*gndPredClauseIndexesAndCounts)[p];
        
        if (gndingsToClauseIndexesAndCounts == NULL) 
        {
          cout << "gndPredClauseIndexesAndCounts[" << p << "] = NULL" << endl;
          continue;
        }
        
        int numGnds = gndingsToClauseIndexesAndCounts->size();
        for (int g = 0; g < numGnds; g++) // for each grounding
        {
          Array<Array<IndexAndCount*>*>* gndings 
            = (*gndingsToClauseIndexesAndCounts)[g];

          for (int c = 0; c < gndings->size(); c++)
          {
            Array<IndexAndCount*>* combos 
              = (*gndings)[c];
            int numClauseIdx = combos->size();
          
            if (numClauseIdx == 0)
            {
              cout << "gndPredClauseIndexesAndCounts[" << p << "][" << g 
                   << "][" << c << "] = empty" << endl;
              continue;
            }
          
            for (int i = 0; i < numClauseIdx; i++)
            {
              cout << "gndPredClauseIndexesAndCounts[" << p << "][" << g << "]["
                   << c << "][" << i << "] (clauseIndex,count) = "
                   << *((*combos)[i]->index)
                   << ", " << (*combos)[i]->count 
                   << ",  " << (*combos)[i] << endl;
            
              if (mln)
              {
                cout << "                                      \t";
                mln->getClause(*((*combos)[i]->index)) ->print(cout, 
                                                               (*domains_)[0]);
                cout << endl;
              }
            }
          }

        }
      } // for each predicate
    } // for each domain
  }

  
  void setIndexTranslator(IndexTranslator* const & it) { idxTrans_ = it; }


  IndexTranslator* getIndexTranslator() const { return idxTrans_; }

  void setNumSteps(const int& i) { numSteps_ = i; }
  int numSteps() const           { return numSteps_; }

  Array<double>* numClauseGndings() const { return numClauseGndings_; }
  void setNumClauseGndings(Array<double>* const& ncg) { numClauseGndings_= ncg;}

  //CHANGED: used for infering pll of gnd atoms of one FOPred in one domain
  void printGndPredPll(ostream& out)
  {
    if (gndPredStrs_.size() != gndPredTVs_.size() || 
        gndPredStrs_.size() != gndPredPlls_.size())
    {
      cout << "ERROR: expect gndPredStrs_, gndPredTVs_, gndPredPlls_ "
           << "to have same size" << " " << gndPredStrs_.size() 
           << " " << gndPredTVs_.size() << " " << gndPredPlls_.size() << endl;
      exit(-1);
    }
    for (int g = 0; g < gndPredStrs_.size(); g++)
    {
      long double logProb  = gndPredPlls_[g];
      long double prob     = expl(logProb);
      if (gndPredTVs_[g] == false) prob = 1 - prob;     
      out << gndPredStrs_[g] << " " << prob << endl;
      if (prob < 0.0 || prob > 1.0)
      {
        cout << "ERROR: invalid prob " << gndPredStrs_[g] << " " << logProb 
             << " " << prob << endl;
        exit(-1);
      }
    }
  }

 private:
  void createNumGndings()
  {
    numGndings_ = new Array<Array<double>*>; 
    numGndings_->growToSize(domains_->size());
    for (int i = 0; i < domains_->size(); i++)
    {
      (*numGndings_)[i] = new Array<double>;
      (*numGndings_)[i]->growToSize((*domains_)[i]->getNumPredicates(), -1);
    }

    for (int i = 0; i < domains_->size(); i++)
    {
      const Domain* domain = (*domains_)[i];
      for (int j = 0; j < domain->getNumPredicates(); j++)
      {
        if (!(*areNonEvidPreds_)[j]) continue;
        const PredicateTemplate* pt = domain->getPredicateTemplate(j);
          //compute num groundings of pred
        double numGndings = 1;
        for (int t = 0; t < pt->getNumTerms(); t++)
        {
          int typeId = pt->getTermTypeAsInt(t);
          numGndings *= domain->getNumConstantsByType(typeId);
        }
        (*((*numGndings_)[i]))[j] = numGndings;
      }
    }

    //TODO: CHANGED 2
    numGndingsTrue_  = new Array<Array<double>*>; 
    numGndingsFalse_ = new Array<Array<double>*>; 
    numGndingsTrue_->growToSize(domains_->size());
    numGndingsFalse_->growToSize(domains_->size());
    for (int i = 0; i < domains_->size(); i++)
    {
      (*numGndingsTrue_)[i] = new Array<double>;
      (*numGndingsFalse_)[i] = new Array<double>;
      (*numGndingsTrue_)[i]->growToSize((*domains_)[i]->getNumPredicates(), -1);
      (*numGndingsFalse_)[i]->growToSize((*domains_)[i]->getNumPredicates(), -1);
    }
    for (int i = 0; i < domains_->size(); i++)
    {
      const Domain* domain = (*domains_)[i];
      for (int j = 0; j < domain->getNumPredicates(); j++)
      {
        if (!(*areNonEvidPreds_)[j]) continue;

        const PredicateTemplate* pt = domain->getPredicateTemplate(j);

        //create the predicate
        Predicate* pred = new Predicate(pt);
        pred->setSense(true);
        for (int k = 0; k < pt->getNumTerms(); k++)
          pred->appendTerm( new Term(-(k+1), (void*)pred, true) );
        Clause unitClause;
        pred->setParent(&unitClause);
        unitClause.appendPredicate(pred);
        unitClause.canonicalize();

        double numTrue  = unitClause.getNumTrueGroundings(domain, domain->getDB(), false);
        double numTotal = unitClause.getNumGroundings(domain);
        double numFalse = numTotal - numTrue;
        (*((*numGndingsTrue_)[i]))[j]  = numTrue;
        (*((*numGndingsFalse_)[i]))[j] = numFalse;

        cout << "NUM_GNDINGS_TRUE  " << pt->getName() << " : " << numTrue  << endl;
        cout << "NUM_GNDINGS_FALSE " << pt->getName() << " : " << numFalse << endl << endl;
      }
    }


    numTotalGndings_ = new Array<double>; //CHANGED:
    numPreds_        = new Array<int>;
    numTotalGndings_->growToSize( domains_->size(), -1.0 );
    numPreds_->growToSize( domains_->size(), -1 );
    for (int i = 0; i < domains_->size(); i++)
    {
      double numTotalGndings = 0.0;
      int numPreds = 0;
      const Domain* domain = (*domains_)[i];
      for (int j = 0; j < domain->getNumPredicates(); j++)
      {
        if (!(*areNonEvidPreds_)[j]) continue;
        numTotalGndings += (*((*numGndings_)[i]))[j];
        numPreds++;
      }
      (*numTotalGndings_)[i] = numTotalGndings;
      (*numPreds_)[i] = numPreds;
    }

    totalGndings_ = 0.0;
    for (int i = 0; i < numTotalGndings_->size(); i++)
    {
      totalGndings_ += (*numTotalGndings_)[i];
      cout << "numTotalGndings_ in domain " << i << " = " 
           << (*numTotalGndings_)[i] << endl;
    }
    cout << "numTotalGndings across domains = " << totalGndings_ << endl;


    //for (int i = 0; i < numPreds_->size(); i++)
    //  cout << "numPreds_ " << i << " = " << (*numPreds_)[i] << endl;
  }


  void createAllPossiblePredsGroundings(const Predicate* const & pred,
                                        const Domain* const & domain,
                                        ArraysAccessor<int>& acc)
  {
    for (int i = 0; i < pred->getNumTerms(); i++)
    {
      int typeId = pred->getTermTypeAsInt(i);
      const Array<int>* constArr = domain->getConstantsByType(typeId);
      acc.appendArray(constArr);
    }
  }

  
  bool isSampledGndPred(const int& g, const SampledGndings* const & sg)
  {
    if (sg->falseGndings.contains(g)) return true;
    if (sg->trueGndings.contains(g)) return true;
    return false;
  }


  void computeCountsRemoveCountsHelper(bool computeCounts,
                                       const Clause* const & c,
                                       int* const & clauseIdxInMLN,
                                       const int& domainIdx,
                                       Array<UndoInfo*>* const & undoInfos,
                                       const bool& sampleClauses,
                              Array<Array<Array<CacheCount*>*>*>* const & cache)
  {
    //cout << "before: c = " << *c << endl;
    const Domain* domain = (*domains_)[domainIdx];
    Database* db = domain->getDB();

      //to store index of 1st pred in c that has terms which are all diff vars
    Array<int> predIdxWithAllTermsDiffVars(domain->getNumPredicates());
    predIdxWithAllTermsDiffVars.growToSize(domain->getNumPredicates());
    int* parr = (int*) predIdxWithAllTermsDiffVars.getItems();
    memset(parr, -1, domain->getNumPredicates()*sizeof(int));

      //find out which preds have terms that are all different variables
    Array<bool> predAllTermsAreDiffVars(c->getNumPredicates());
    createPredAllTermsAreDiffVars(c, predAllTermsAreDiffVars, 
                                  predIdxWithAllTermsDiffVars);

      //used to store canonicalized predicates (before they are grounded)
    PredicateHashArray seenPreds;

        //for each pred that clause contains
    for (int p = 0; p < c->getNumPredicates(); p++)
    {
      Predicate* pred = c->getPredicate(p);
      int predId = pred->getId();
      if (!(*areNonEvidPreds_)[predId]) continue;

      Predicate gndPred(*pred);
      gndPred.canonicalize();
      bool predIsInitiallyGnded = gndPred.isGrounded();

      SampledGndings* sg = NULL;
      if (sampleGndPreds_) sg = (*(*sampledGndingsMaps_)[domainIdx])[predId];

      Predicate* seenPred = new Predicate(gndPred);
        //if the predicate has been seen before
      if (seenPreds.append(seenPred) < 0) { delete seenPred; continue; }

      if (predAllTermsAreDiffVars[p])
      {
        //cout << "all terms DIFF vars, predIdx = " << p << endl;        
        
          //create all possible groundings of pred
        ArraysAccessor<int> acc;
        createAllPossiblePredsGroundings(&gndPred, domain, acc);

          // for each grounding of pred
        int g = -1; //gth grounding
        while (acc.hasNextCombination())
        {
          ++g;

          int t = 0; int constId; 
          while (acc.nextItemInCombination(constId))
            ((Term*) gndPred.getTerm(t++))->setId(constId);

          //CHANGED: used for infering pll of gnd atoms of one FOPred in one domain
          /*if (c->getNumPredicates() == 1)
          {
            ostringstream oss;
            gndPred.print(oss, domain);
            string gndPredStr = oss.str();
            bool tv = (db->getValue(&gndPred) == TRUE);
            int idx  = gndPredStrs_.append( gndPredStr );
            int idx2 = gndPredTVs_.append( tv );
            cout << "gndPred " << idx << " : " << gndPredStr 
                 << (tv?" true":" false") << endl;
            if (idx < 0) 
            {
              cout << "ERROR: duplicate gndPred " << gndPredStr << endl;
              exit(-1);
            }
            if (idx != idx2 || g != idx)
            {
              cout << "expect idx == idx2, " << idx << " " << idx2 << " " 
                   << g << endl;
              exit(-1);
            }
          }//*/


          if (sampleGndPreds_ && !isSampledGndPred(g,sg)) continue;

          if (computeCounts)
          {
            computeAndSetCounts(c, clauseIdxInMLN, predId, gndPred, g, db,
                                domainIdx, undoInfos, sampleClauses, cache);
          }
          else
            removeCounts(clauseIdxInMLN, predId, g, domainIdx, undoInfos);
        } //for each grounding of pred 
      }
      else
      {  //there are constant terms or repeated variables

          //if there is a pred with this id that has terms that are all vars
        if (predIdxWithAllTermsDiffVars[predId] >= 0) continue;

        //cout << "all terms NOT diff vars, predIdx = " << p << endl;

          //create multipliers that are used to determine the index of a gnding
        Array<int> multipliers(gndPred.getNumTerms());
        createMultipliers(multipliers, gndPred, domain);

          //fix offset due to constants in gndPred that is used to determine
          //the index of a grounding  
        int offsetDueToConstants = 0; 

          //compute mapping of varId to array of multipliers, create all 
          //groundings of variables, and compute fix offset due to constants
          //pair.first is the multiplier, pair.second is the Term that the 
          //multiplier that the corresponds to
        Array<Array<pair<int,Term*> >* > varIdToMults;
        Array<int> negVarIdsArr;
        ArraysAccessor<int> groundings;
        createMappingOfVarIdToMultipliersAndVarGroundingsAndOffset(
          gndPred, domain, multipliers, offsetDueToConstants, varIdToMults, 
          negVarIdsArr, groundings);
        
          //if the predicate has some variables
        if (!predIsInitiallyGnded)
        {
            // ground gndPred
          int constId, constIdx;
          while (groundings.hasNextCombination())
          {
            int g = offsetDueToConstants; //index of grounding
            int j = -1;
            while (groundings.nextItemInCombination(constId, constIdx))
            {
              ++j;
              int negVarId = negVarIdsArr[j];
              Array<pair<int,Term*> >* multsAndTerms = varIdToMults[negVarId];
              for (int m = 0; m < multsAndTerms->size(); m++)
              {
                g += constIdx * (*multsAndTerms)[m].first;
                (*multsAndTerms)[m].second->setId(constId); //ground gndPred
              }
            }

            if (sampleGndPreds_ && !isSampledGndPred(g,sg)) continue;

            if (computeCounts)
              computeAndSetCounts(c, clauseIdxInMLN, predId, gndPred, g, db, 
                                  domainIdx, undoInfos, sampleClauses, cache);
            else
              removeCounts(clauseIdxInMLN, predId, g, domainIdx, undoInfos);
          }
        }
        else
        {  // the predicate is initially grounded
          int g = offsetDueToConstants;

          bool ok = true;
          if (sampleGndPreds_) ok = isSampledGndPred(g,sg);

          if (ok)
          {
            if (computeCounts)
              computeAndSetCounts(c, clauseIdxInMLN, predId, gndPred, g, db, 
                                  domainIdx, undoInfos, sampleClauses, cache);
            else
              removeCounts(clauseIdxInMLN, predId, g, domainIdx, undoInfos);
          }
        }

        for (int j = 0; j < varIdToMults.size(); j++) delete varIdToMults[j];
      } //there are constant terms or repeated variables
    } //for each pred that clause contains

    for (int i = 0; i < seenPreds.size(); i++)  delete seenPreds[i];

    //cout << "after : c = " << *c << endl;
  } //computeCountsRemoveCountsHelper()

  /*    
  void computePerPredPllAndGrad(const Array<Array<Array<IndexAndCount*>*>*>*
                                const& gndingsToClauseIndexesAndCounts,
                                const int& g, const double* const & wt, 
                                long double& perPredPll, 
                                long double * const & perPredGrad,
                                const int& arrSize)
  {
      // compute W.(N^bar-N)
   
	  // Changed to logl, expl because otherwise changing
	  // order of .mln files changes weight results
    long double wdotn = 0;
      // pmb = 1 + sum(exp(wdotn))
    long double pmb = 1;
    
    Array<Array<IndexAndCount*>*>* gndings =
      (*gndingsToClauseIndexesAndCounts)[g];

      // For each valid assignment of vars in block
    if (gndings->size() != 1) { cout<<"ERROR: no blocking!" << endl; exit(-1); }
    for (int c = 0; c < gndings->size(); c++)
    {
      Array<IndexAndCount*>* clauseIndexesAndCounts = (*gndings)[c];
      assert(noRepeatedIndex(clauseIndexesAndCounts));
    
      int numClausesUnifyWith = clauseIndexesAndCounts->size();
      //cout << "numClausesUnifyWith " << numClausesUnifyWith << endl;

      for (int i = 0; i < numClausesUnifyWith; i++)
      {
        //cout << "Clause " << (*clauseIndexesAndCounts)[i]->index << endl;
        //cout << "Count " << (*clauseIndexesAndCounts)[i]->count << endl<<endl;
          // grounding g unifies with clause (*clauseIndexesAndCounts)[i].idx
        wdotn += wt[ *( (*clauseIndexesAndCounts)[i]->index ) ] * 
          (*clauseIndexesAndCounts)[i]->count;
      }      

      pmb += expl(wdotn);
      //cout << "  wdotn=" << wdotn << " , pmb=" << pmb << endl; //DEBUG:
    }


    perPredPll -= logl(pmb);
    //cout << "  perPredPll " << perPredPll << " , "<< endl; //DEBUG:

      // Is this still right with blocking?
      // update gradient
    for (int c = 0; c < gndings->size(); c++)
    {
      Array<IndexAndCount*>* clauseIndexesAndCounts = (*gndings)[c];
      
      for (int i = 0; i < clauseIndexesAndCounts->size(); i++)
      {
        if (*( (*clauseIndexesAndCounts)[i]->index ) >= arrSize) continue;
        perPredGrad[ *( (*clauseIndexesAndCounts)[i]->index ) ]
          += ( (1.0/pmb-1) * (*clauseIndexesAndCounts)[i]->count );
      }
    }
  }
  */

  void computePerPredPllAndGrad(const Array<Array<Array<IndexAndCount*>*>*>*
                                const& gndingsToClauseIndexesAndCounts,
                                const int& g, const double* const & wt, 
                                long double& perPredPll, 
                                long double * const & perPredGrad,
                                const int& arrSize) 
  {
      // compute W.(N^bar-N)
   
	  // Changed to logl, expl because otherwise changing
	  // order of .mln files changes weight results
    long double wdotn = 0;
    // pmb = 1 + sum(exp(wdotn))
    
    Array<Array<IndexAndCount*>*>* gndings =
      (*gndingsToClauseIndexesAndCounts)[g];

    if (gndings->size() != 1) { cout<<"ERROR: no blocking!" << endl; exit(-1); }

    Array<IndexAndCount*>* clauseIndexesAndCounts = (*gndings)[0];
    assert(noRepeatedIndex(clauseIndexesAndCounts));
    
    int numClausesUnifyWith = clauseIndexesAndCounts->size();

    for (int i = 0; i < numClausesUnifyWith; i++)
    {
      // grounding g unifies with clause (*clauseIndexesAndCounts)[i].idx
      wdotn += wt[*( (*clauseIndexesAndCounts)[i]->index )] 
               * (*clauseIndexesAndCounts)[i]->count;
    }      
    
    //cout << "  wdotn=" << wdotn << endl; //DEBUG:
  
    long double lpmb = (wdotn > 0) ? -logl(1+expl(-wdotn))-wdotn 
                                   : -logl(1+expl(wdotn));
    perPredPll += lpmb;

    //cout << "  perPredPll " << perPredPll << " , "<< endl; //DEBUG:

      // update gradient
    for (int i = 0; i < numClausesUnifyWith; i++)
    {
      if (*( (*clauseIndexesAndCounts)[i]->index ) >= arrSize) continue;
      perPredGrad[*( (*clauseIndexesAndCounts)[i]->index )] 
        += (expl(lpmb)-1) * (*clauseIndexesAndCounts)[i]->count;
    }
  }

  void computeSampledPerPredPllAndGrad(IntHashArray& gndings, 
                                       const int& totalGndings,
                                       long double& tmpPerPredPll,
                                       long double* const & tmpPerPredGrad,
                                       long double& perPredPll,
                                       long double* const & perPredGrad,
                                       const int& arrSize,
                                       const double* const & wt,
                                    const Array<Array<Array<IndexAndCount*>*>*>*
                                       const& gndingsToClauseIndexesAndCounts)
  {
    tmpPerPredPll = 0;
    memset(tmpPerPredGrad, 0, arrSize*sizeof(long double));

    for (int i = 0; i < gndings.size(); i++)
      computePerPredPllAndGrad(gndingsToClauseIndexesAndCounts, 
                               gndings[i], wt, tmpPerPredPll, 
                               tmpPerPredGrad, arrSize);


    if (gndings.size() > 0)
    {
      perPredPll += totalGndings * tmpPerPredPll/gndings.size();
      for (int i = 0; i < arrSize; i++)
        perPredGrad[i] += totalGndings * tmpPerPredGrad[i]/gndings.size();

    }
    
  }


    //Returns value. Gradients are set in gradient.
  double getValueAndGradientForDomain(double* const & gradient, 
                                      const double* const & wt,
                                      const int& arrSize, const int& domainIdx)
  {
    long double wpll = 0; // weighted pseudo-log-likelihood

    //TODO: CHANGED2
    //long double* perPredGrad = new long double[arrSize];
    long double* perPredGradTrue  = new long double[arrSize];
    long double* perPredGradFalse = new long double[arrSize];  

      //used if sampling ground predicates
    //TODO: CHANGED 2
    //long double tmpPerPredPll;
    //long double* tmpPerPredGrad = NULL;
    //if (sampleGndPreds_) tmpPerPredGrad = new long double[arrSize];    
    long double tmpPerPredPllTrue, tmpPerPredPllFalse;
    long double* tmpPerPredGradTrue = NULL, *tmpPerPredGradFalse = NULL; 
    if (sampleGndPreds_) 
    {
      tmpPerPredGradTrue  = new long double[arrSize];
      tmpPerPredGradFalse = new long double[arrSize];
    }


    Array<Array<Array<Array<IndexAndCount*>*>*>*>* gndPredClauseIndexesAndCounts
      = (*gndPredClauseIndexesAndCountsArr_)[domainIdx];

    //TODO: CHANGED 2
    Array<Array<bool>*>* domTVs = (*gndPredTruthValues_)[domainIdx];

    int numPreds = gndPredClauseIndexesAndCounts->size();
    for (int p = 0; p < numPreds; p++) // for each predicate
    {
      if (!(*areNonEvidPreds_)[p]) continue; 

      //commented out: even though pred does not appear in any clause, each
      //of its groundings contribute -ln(2) to the wpll
      //if ((*gndPredClauseIndexesAndCounts)[p] == NULL) continue;


      //TODO: CHANGED 2
      //long double perPredPll = 0;
      //memset(perPredGrad, 0, arrSize*sizeof(long double));
      long double perPredPllTrue = 0, perPredPllFalse = 0;
      memset(perPredGradTrue,  0, arrSize*sizeof(long double));
      memset(perPredGradFalse, 0, arrSize*sizeof(long double));

        //if pred p appears in one or more clauses
      if ((*gndPredClauseIndexesAndCounts)[p] != NULL)
      {
        Array<Array<Array<IndexAndCount*>*>*>* gndingsToClauseIndexesAndCounts 
          = (*gndPredClauseIndexesAndCounts)[p];

        //TODO: CHANGED 2
        Array<bool>* tvs = (*domTVs)[p];

        if (sampleGndPreds_)
        {
          SampledGndings* sg = (*(*sampledGndingsMaps_)[domainIdx])[p];

          //TODO: CHANGED 2
          /*
          computeSampledPerPredPllAndGrad(sg->trueGndings, sg->totalTrue, 
                                          tmpPerPredPll, tmpPerPredGrad,
                                          perPredPll, perPredGrad, arrSize, 
                                          wt, gndingsToClauseIndexesAndCounts);
          computeSampledPerPredPllAndGrad(sg->falseGndings, sg->totalFalse, 
                                          tmpPerPredPll, tmpPerPredGrad,
                                          perPredPll, perPredGrad, arrSize, 
                                          wt, gndingsToClauseIndexesAndCounts);
          */
          computeSampledPerPredPllAndGrad(sg->trueGndings, sg->totalTrue, 
                                          tmpPerPredPllTrue, tmpPerPredGradTrue,
                                          perPredPllTrue, perPredGradTrue, arrSize, 
                                          wt, gndingsToClauseIndexesAndCounts);

          computeSampledPerPredPllAndGrad(sg->falseGndings, sg->totalFalse, 
                                          tmpPerPredPllFalse, tmpPerPredGradFalse,
                                          perPredPllFalse, perPredGradFalse, arrSize, 
                                          wt, gndingsToClauseIndexesAndCounts);
        }
        else
        {   //use all groundings of predicate
          int numGnds = gndingsToClauseIndexesAndCounts->size();
          assert(numGnds == (*((*numGndings_)[domainIdx]))[p]);
          for (int g = 0; g < numGnds; g++) // for each grounding
          {
            //TODO: CHANGED 2
            //computePerPredPllAndGrad(gndingsToClauseIndexesAndCounts, g, wt, 
            //                         perPredPll, perPredGrad, arrSize);
            if ((*tvs)[g]) 
            { 
              computePerPredPllAndGrad(gndingsToClauseIndexesAndCounts, g, wt, 
                                       perPredPllTrue, perPredGradTrue, arrSize);
            }
            else
            {
              computePerPredPllAndGrad(gndingsToClauseIndexesAndCounts, g, wt, 
                                       perPredPllFalse, perPredGradFalse, arrSize);

            }
          }

          //CHANGED: used for infering pll of gnd atoms of one FOPred in one domain          
          /*long double* noop = new long double[arrSize];
          for (int g = 0; g < numGnds; g++) // for each grounding
          {
            long double gndPredPll = 0.0;
            computePerPredPllAndGrad(gndingsToClauseIndexesAndCounts, g, wt, 
                                     gndPredPll, noop, arrSize);
            int idx = gndPredPlls_.append( gndPredPll );
            if (idx != g)
            {
              cout << "ERROR: expect idx == g " << idx << ", " << g << endl;
              exit(-1);
            }            
          }
          delete [] noop;//*/
        }
      }
      else
      {   //pred p does not appear in any clauses        
        //TODO: CHANGED 2
        //perPredPll = (*((*numGndings_)[domainIdx]))[p] * -log(2);
        //perPredGrad entries are all zeroes
        perPredPllTrue  = (*((*numGndingsTrue_)[domainIdx]))[p]  * -log(2);
        perPredPllFalse = (*((*numGndingsFalse_)[domainIdx]))[p] * -log(2);
      }
      
      if (wtFOPred_) 
      {
        //negate the value and gradient here

        //wpll -= perPredPll / (*((*numGndings_)[domainIdx]))[p];

        //CHANGED
        //wpll -= perPredPll / (*((*numGndings_)[domainIdx]))[p] * (*numTotalGndings_)[domainIdx] / totalGndings_;

        //TODO: CHANGED 2
        double numGndingsTrue  = (*((*numGndingsTrue_)[domainIdx]))[p];
        double numGndingsFalse = (*((*numGndingsFalse_)[domainIdx]))[p];
        wpll -= (perPredPllTrue / numGndingsTrue + perPredPllFalse / numGndingsFalse)  * (*numTotalGndings_)[domainIdx] / totalGndings_;

        if (isnan(wpll) || isinf(wpll))
        {
          cout << "ERROR: wpll = " << wpll << endl;
          
          //TODO: CHANGED 2
          //cout << "perPredPll = " << perPredPll << endl;
          cout << "perPredPllTrue  = " << perPredPllTrue  << endl;
          cout << "perPredPllFalse = " << perPredPllFalse << endl;
          
          cout << "numGndings = " << (*((*numGndings_)[domainIdx]))[p] << endl;
          exit(-1);
        }
        
        //DEBUG:
        //cout << "domain " << domainIdx << " , wpll pred " << p 
        //     << " , perPredPll " << perPredPll
        //     << " , numGndings " << (*((*numGndings_)[domainIdx]))[p] << endl;

        for (int i = 0; i < arrSize; i++) 
        {
          {
            //gradient[i] -= perPredGrad[i]/(*((*numGndings_)[domainIdx]))[p];
            //CHANGED
            //gradient[i] -= perPredGrad[i]/(*((*numGndings_)[domainIdx]))[p] * (*numTotalGndings_)[domainIdx] / totalGndings_;

            //TODO: CHANGED 2
            double numGndingsTrue  = (*((*numGndingsTrue_)[domainIdx]))[p];
            double numGndingsFalse = (*((*numGndingsFalse_)[domainIdx]))[p];
            gradient[i] -= (perPredGradTrue[i]/numGndingsTrue + perPredGradFalse[i]/numGndingsFalse) * (*numTotalGndings_)[domainIdx] / totalGndings_;
          }

          if (isnan(gradient[i]) || isinf(gradient[i]))
          {
            cout << "ERROR: gradient " << i << " = " << gradient[i] << endl;

            //TODO: CHANGED 2
            //cout << "perPredGrad = " << perPredGrad[i] << endl;
            cout << "perPredGradTrue  = " << perPredGradTrue[i]  << endl;
            cout << "perPredGradFalse = " << perPredGradFalse[i] << endl;

            cout << "numGndings  = " << (*((*numGndings_)[domainIdx]))[p]<<endl;
            exit(-1);
          }
        }
      }
      else
      {
          //negate the value and gradient here
        //TODO: CHANGED 2
        //wpll -= perPredPll;
        wpll -= perPredPllTrue + perPredPllFalse;

        if (isnan(wpll) || isinf(wpll))
        {
          cout << "ERROR: wpll = " << wpll << endl;

          //TODO: CHANGED 2 
          //cout << "perPredPll = " << perPredPll << endl;
          cout << "perPredPll = " << perPredPllTrue + perPredPllFalse << endl;

          cout << "numGndings = " << (*((*numGndings_)[domainIdx]))[p] << endl;
          exit(-1);
        }

        for (int i = 0; i < arrSize; i++) 
        {
          //TODO: CHANGED 2
          //gradient[i] -= perPredGrad[i]; 
          gradient[i] -= perPredGradTrue[i] + perPredGradFalse[i]; 

          if (isnan(gradient[i]) || isinf(gradient[i]))
          {
            cout << "ERROR: gradient " << i << " = " << gradient[i] << endl;

            //TODO: CHANGED
            //cout << "perPredGrad = " << perPredGrad[i] << endl;
            cout << "perPredGrad = " << perPredGradTrue[i]+perPredGradFalse[i] << endl;

            exit(-1);
          }

        }
      }
    } // for each predicate

    //TODO: CHANGED 2
    //delete [] perPredGrad;
    //if (sampleGndPreds_) delete [] tmpPerPredGrad;
    delete [] perPredGradTrue; 
    delete [] perPredGradFalse;
    if (sampleGndPreds_) { delete [] tmpPerPredGradTrue; delete tmpPerPredGradFalse; }

    return wpll;
  }

  void createClauseIndexesAndCountsArrays(const int& predId, 
                                          const int& domainIdx)
  {
    Array<Array<Array<Array<IndexAndCount*>*>*>*>* gndPredClauseIndexesAndCounts
      = (*gndPredClauseIndexesAndCountsArr_)[domainIdx];
    if ((*gndPredClauseIndexesAndCounts)[predId] != NULL) return;

    Array<Array<Array<IndexAndCount*>*>*>* arr =
      new Array<Array<Array<IndexAndCount*>*>*>;
    double numGndings = (*((*numGndings_)[domainIdx]))[predId];

      //for each grounding, create a record of the indexes and counts of the
      //clauses in which the grounding appears
    for (int g = 0; g < numGndings; g++) 
      arr->append(new Array<Array<IndexAndCount*>*>);
    arr->compress();
    (*gndPredClauseIndexesAndCounts)[predId] = arr;

    //TODO: CHANGED 2
    Array<Array<bool>*>* domTVs = (*gndPredTruthValues_)[domainIdx];
    Array<bool>*& tvs = (*domTVs)[predId];    
    if (tvs == NULL) { tvs = new Array<bool>; tvs->growToSize((int)numGndings, false); }
    else { if (tvs->size() != numGndings) { cout << "expect tvs->size() == numGndings" << endl; exit(-1); } }
  }

  void createComboClauseIndexesAndCountsArrays(const int& predId, 
                                               const int& domainIdx,
                                               Predicate* const & gndPred,
                                               const int& g)
  {
    Array<Array<Array<Array<IndexAndCount*>*>*>*>* gndPredClauseIndexesAndCounts
      = (*gndPredClauseIndexesAndCountsArr_)[domainIdx];

    Array<Array<IndexAndCount*>*>* comboClauseIndexesAndCounts
      = (*(*gndPredClauseIndexesAndCounts)[predId])[g];
    if (comboClauseIndexesAndCounts->size() > 0) return;

        // Check if this grounding is in a block
    int numCombInBlock = 1;
      
    int blockIdx = (*domains_)[domainIdx]->getBlock(gndPred);
    if (blockIdx >= 0)
      numCombInBlock = (*domains_)[domainIdx]->getBlockSize(blockIdx) - 1;
      
    comboClauseIndexesAndCounts->growToSize(numCombInBlock, NULL);
    for (int c = 0; c < numCombInBlock; c++)
    {
      (*comboClauseIndexesAndCounts)[c] = new Array<IndexAndCount*>;
    }
    comboClauseIndexesAndCounts->compress();
  }

    //Returns false if grounding g of gndPred with predId has been looked at;
    //otherwise returns true. The difference between the number of true 
    //groundings of clause c when gndPred is held to the opposite of its truth 
    //value and to its actual value is computed, and appended to an 
    //Array<IndexAndCount*>. If undoInfos is not NULL, a pointer to that 
    //Array<IndexAndCount*> is added in undoInfos.
    //Similar to insertCounts().
  bool computeAndSetCounts(const Clause* const clause, 
                           int* const & clauseIdxInMLN, 
                           const int& predId, Predicate& gndPred, 
                           const int& g, Database* const & db, 
                           const int& domainIdx,
                           Array<UndoInfo*>* const & undoInfos,
                           const bool& sampleClauses,
                           Array<Array<Array<CacheCount*>*>*>* const & cache)
  {
    Array<Array<Array<Array<IndexAndCount*>*>*>*>* gndPredClauseIndexesAndCounts
      = (*gndPredClauseIndexesAndCountsArr_)[domainIdx];
    const Domain* domain = (*domains_)[domainIdx];

    if ((*gndPredClauseIndexesAndCounts)[predId] == NULL)
      createClauseIndexesAndCountsArrays(predId, domainIdx);

    createComboClauseIndexesAndCountsArrays(predId, domainIdx, &gndPred, g);

    //TODO: CHANGED 2
    TruthValue tv = db->getValue(&gndPred);  if (tv != FALSE && tv != TRUE) { cout <<  "expect TRUE/FALSE truth value" << endl; exit(-1); }
    Array<Array<bool>*>* domTVs = (*gndPredTruthValues_)[domainIdx];
    Array<bool>* tvs = (*domTVs)[predId];
    (*tvs)[g] = tv;

    Array<Array<IndexAndCount*>*>* comboClauseIndexesAndCounts
      = (*(*gndPredClauseIndexesAndCounts)[predId])[g];

    //cout << "Clause: ";
    //clause->printWithoutWtWithStrVar(cout, domain);
    //cout << endl;
    //cout << "Pred: ";
    //gndPred.printWithStrVar(cout, domain);
    //cout << endl;

    //cout << "PredId: " << predId << " Gnding: " << g << " # of combos: "
    //     << comboClauseIndexesAndCounts->size() << endl;
     
      // For each combination
    for (int c = 0; c < comboClauseIndexesAndCounts->size(); c++)
    {
      //cout << endl << "Combo " << c << endl;
      //if gth grounding of pred with predId has been looked at, ignore it
      Array<IndexAndCount*>* gArr = (*comboClauseIndexesAndCounts)[c];
      if (gArr->size() > 0 && *( gArr->lastItem()->index ) == *clauseIdxInMLN)
      {
        //cout << "Already looked at" << endl;
        //return false;
        continue;
      }

      double cnt =
        ((Clause*)clause)->countDiffNumTrueGroundings(&gndPred, domain, db,
                                                      DB_HAS_UNKNOWN_PREDS,
                                                      sampleClauses, c);
      //cout << "Count " << cnt << endl;
        //ignore clauses if the difference in counts is zero
      if (cnt != 0)
      {
        //cout << "Appending " << cnt << " " << *clauseIdxInMLN << endl;
        gArr->append(new IndexAndCount(clauseIdxInMLN, cnt));
        if (undoInfos)
          undoInfos->append(new UndoInfo(gArr, NULL, -1, domainIdx));

        if (cache) 
        {
          Array<CacheCount*>*& ccArr = (*(*cache)[domainIdx])[predId];
          if (ccArr == NULL) ccArr = new Array<CacheCount*>;
          ccArr->append(new CacheCount(g, c, cnt));
        }
      }

      assert(noRepeatedIndex(gArr));
    }
    
    return true;
  }


    //returns true if an IndexCount is removed; return false otherwise
  bool removeCounts(int* const & clauseIdxInMLN, const int& predId, 
                    const int& g,  const int& domainIdx,
                    Array<UndoInfo*>* const & undoInfos)
  {
    bool removed = false;
    Array<Array<Array<Array<IndexAndCount*>*>*>*>* gndPredClauseIndexesAndCounts
      = (*gndPredClauseIndexesAndCountsArr_)[domainIdx];

    if ((*gndPredClauseIndexesAndCounts)[predId] == NULL) return false;

    Array<Array<IndexAndCount*>*>* comboClauseIndexesAndCounts
      = (*(*gndPredClauseIndexesAndCounts)[predId])[g];
      // For each combination
    for (int c = 0; c < comboClauseIndexesAndCounts->size(); c++)
    {
      Array<IndexAndCount*>* gArr =(*comboClauseIndexesAndCounts)[c];
      for (int i = 0; i < gArr->size(); i++)
      {
        if ((*gArr)[i]->index == clauseIdxInMLN)
        {
          IndexAndCount* ic = gArr->removeItemFastDisorder(i);

          if (undoInfos) // this is a temporary removal
          {
            undoInfos->append(new UndoInfo(gArr, ic, i, domainIdx));
            assert(noRepeatedIndex(gArr));
            //return true;
            removed = true;
          }
          else
          { // removing this IndexCount for good
            delete ic;
            assert(noRepeatedIndex(gArr));
            //return true;
            removed = true;
          }
        }
      }
    assert(noRepeatedIndex(gArr));
    }

    //return false;
    return removed;
  }
  

  void createPredAllTermsAreDiffVars(const Clause* const & c,
                                      Array<bool>& predAllTermsAreDiffVars,
                                      Array<int>& predIdxWithAllTermsDiffVars)
  {
    for (int p = 0; p < c->getNumPredicates(); p++)
    {
      Predicate* pred = c->getPredicate(p);
      bool allDiffVars;
      
      if (c->isDirty())
      {
          //force a complete check whether all terms are different variables
        allDiffVars = pred->checkAllTermsAreDiffVars();
      }
      else
      {
        assert(!pred->isDirty());
        allDiffVars = pred->allTermsAreDiffVars();
      }
      
      predAllTermsAreDiffVars.append(allDiffVars);
      if (allDiffVars)
      {
        int predId = pred->getId();
        if (predIdxWithAllTermsDiffVars[predId] < 0)
          predIdxWithAllTermsDiffVars[predId] = p;
      }
    }
    predAllTermsAreDiffVars.compress();
  }


  void createMultipliers(Array<int>& multipliers, 
                         const Predicate& gndPred,
                         const Domain* const & domain)
  {
    int mult = 1;
    int numTerms = gndPred.getNumTerms();
    multipliers.growToSize(numTerms);
    for (int j = numTerms-1; j >= 0; j--)
    {
      multipliers[j] = mult;
      int typeId = gndPred.getTermTypeAsInt(j);
      mult *= domain->getNumConstantsByType(typeId);
    }
  }


  void createMappingOfVarIdToMultipliersAndVarGroundingsAndOffset(
                                 const Predicate& gndPred,
                                 const Domain* const & domain,
                                 Array<int>& multipliers,
                                 int& offsetDueToConstants,
                                 Array<Array<pair<int,Term*> >* >& varIdToMults,
                                 Array<int>& negVarIdsArr,
                                 ArraysAccessor<int>& groundings)
  {
    for (int j = 0; j < gndPred.getNumTerms(); j++)
    {
      const Term* t =  gndPred.getTerm(j);
      if (t->getType() == Term::VARIABLE)
      {
        assert(t->getId()<0);
        int id = -(t->getId());
        if (id >= varIdToMults.size()) varIdToMults.growToSize(id+1,NULL);
        if (varIdToMults[id] == NULL) 
        {
          negVarIdsArr.append(id);
          varIdToMults[id] = new Array<pair<int,Term*> >; 
          int typeId = gndPred.getTermTypeAsInt(j);
          const Array<int>* constants = domain->getConstantsByType(typeId);
          groundings.appendArray(constants);
        }
        varIdToMults[id]->append(pair<int,Term*>(multipliers[j], (Term*)t));
      }
      else
      if (t->getType() == Term::CONSTANT)
      {
        int id = t->getId();
        assert(id >= 0);
        int typeId = gndPred.getTermTypeAsInt(j);
        const Array<int>* constants = domain->getConstantsByType(typeId);
        assert(constants->size() > 0);
          //ASSUMPTION: constants of the same type are consecutively numbered in
          //the constants array
        for (int i = 0; i < constants->size(); i++)
        {
          if ((*constants)[i] == id)
          {
            offsetDueToConstants += i*multipliers[j];
            break;
          }
        }
        //delete constants;
      }
      else
      {
        assert(false);
      }
    }
  }


  void randomlySelect(IntHashArray& gndings, const double& fraction,
                      const int& min, const int& max)
  {
    int size = int(fraction * gndings.size() + 0.5);
    if (min >= 0 && size < min)      size = min;
    else if (max >= 0 && size > max) size = max;
    while (gndings.size() > size)
      gndings.removeItemFastDisorder(random_->randomOneOf(gndings.size()));
  }


  void samplePredGroundingsForDomain(const Predicate* const& foPred, 
                                     const Domain* const & domain,
                                     SampledGndings* sampledGndings,
                                     const double& fraction, 
                                     const int& min, const int& max)
  {
    cout << "sampling predicate "; foPred->printWithStrVar(cout, domain); 
    cout << endl;

    assert(((Predicate*)foPred)->allTermsAreDiffVars());
    ArraysAccessor<int> acc;
    createAllPossiblePredsGroundings(foPred, domain, acc);
    Predicate* gndPred = (Predicate*) foPred;
    const Database* db = domain->getDB();

    IntHashArray& trueGndings = sampledGndings->trueGndings;
    IntHashArray& falseGndings = sampledGndings->falseGndings;

    int g = -1; //gth grounding
    while (acc.hasNextCombination()) //for each grounding of pred 
    {
      ++g;
      int t = 0;
      int constId; 
      while (acc.nextItemInCombination(constId))
        ((Term*) gndPred->getTerm(t++))->setId(constId);

      TruthValue tv = db->getValue(gndPred);
      if (tv == TRUE) trueGndings.append(g);
      else if (tv == FALSE) falseGndings.append(g);      
    }
    //acc.deleteArraysAndClear();

    sampledGndings->totalTrue = trueGndings.size();
    sampledGndings->totalFalse = falseGndings.size();
    randomlySelect(trueGndings, fraction, min, max);
    randomlySelect(falseGndings, fraction, min, max);

    trueGndings.compress();
    falseGndings.compress();

    cout << "\tsampled/total (true ground atoms) = " 
         << trueGndings.size() << "/" << sampledGndings->totalTrue << endl;
    cout << "\tsampled/total (false ground atoms) = " 
         << falseGndings.size() << "/" << sampledGndings->totalFalse << endl;
  }


  void samplePredGroundings(const double& fraction, 
                            const int& min, const int& max)
  {
    for (int d = 0; d < domains_->size(); d++)
    {
      cout << "domain " << d << endl;
      const Domain* domain = (*domains_)[d];
      Array<SampledGndings*>* sgm = (*sampledGndingsMaps_)[d];
      for (int p = 0; p < domain->getNumPredicates(); p++)
      {
        if (!(*areNonEvidPreds_)[p]) continue;
        SampledGndings* sg = new SampledGndings;
        assert((*sgm)[p] == NULL);
        (*sgm)[p] = sg;
        Predicate* foPred = domain->createPredicate(p, true);
        assert(foPred);
        samplePredGroundingsForDomain(foPred, domain, sg, fraction, min, max);
        delete foPred;
      }
    }
  }
  

  bool noRepeatedIndex(const Array<IndexAndCount*>* const & gArr,
                       const MLN* const & mln0=NULL)
  {
    hash_set<int> set;
    for (int i = 0; i < gArr->size(); i++)
    {
      int ii = *((*gArr)[i]->index);
      if (set.find(ii) != set.end()) 
      {
        cout << "ERROR: in PseudoLogLikelihood::noRepeatedIndex. "
             << "Repeated index " << ii << " found. ";
        if (mln0) 
          mln0->getClause(ii)->printWithoutWtWithStrVar(cout, (*domains_)[0]);
        cout << endl;
        return false;
      }
      set.insert(ii);
    }
    return true;
  }


  void printWtsGradsWPLL(const double* const & wts, const double* const & grads,
                         const int& arrSize, const double& wpll)
  {
    cout.precision(10);
    cout << "wts = " << endl;
    for (int i = 0; i < arrSize; i++) 
    {
      if (i != 0 && (i % 5) == 0) cout << endl;
      cout << "  w" << i << ":" << wts[i];
    }
    cout << endl;
    cout << "grads = " << endl;
    for (int i = 0; i < arrSize; i++) 
    {
      if (i != 0 && (i % 5) == 0) cout << endl;
      cout << "  g" << i << ":" << grads[i];
    }
    cout << endl;
    cout << "wpll = " << wpll << endl;
    cout << endl;
    cout.precision(6);
  }


 private:
  Array<bool>* areNonEvidPreds_;

    //contents of array are not owned by PseudoLogLikelihood; do not delete them
  Array<Domain*>* domains_;

    //gndPredClauseIndexesAndCountsArr_[d][p][g][i]->index is the index into an 
    //MLN of the ith clause that the grounding g of pred p unifies with in 
    //domain d. 
    //The index indexes into the wt and gradient parameter of 
    //getValueAndGradient().
    //gndPredClauseIndexesAndCountsArr_[d][p][g][i]->count is the difference
    //between the number of true groundings of the ith clause when g takes the  
    //opposite of its true value and its true value.
  Array<Array<Array<Array<Array<IndexAndCount*>*>*>*>*>* 
    gndPredClauseIndexesAndCountsArr_;

  //TODO: CHANGED 2
  Array<Array<Array<bool>*>*>* gndPredTruthValues_;
  Array<Array<double>*>* numGndingsTrue_;
  Array<Array<double>*>* numGndingsFalse_;

  int numMeans_; // size priorMeans_ and priorStdDevs_ arrays
  const double* priorMeans_; //not owned by PseudoLogLikelihood, so don't delete
  const double* priorStdDevs_;//not owned by PseudoLogLikelihood,so don't delete

  bool wtFOPred_;  
  Array<Array<double>*>* numGndings_;

  bool sampleGndPreds_;
    // sampledGndingsMaps_[d][p] is the SampledGndings of the predicate with 
    // id p in domain d
  Array<Array<SampledGndings*>*>* sampledGndingsMaps_;
  Random* random_;

  IndexTranslator* idxTrans_; //not owned by PseudoLogLikelihood; do not delete

  //CHANGED:
  int numSteps_; //number of steps taken by OWLQN
  Array<double>* numClauseGndings_;//number of clauseGndings over all domains
  Array<double>* numTotalGndings_; //total gnd preds per domain (exclude evid)
  Array<int>*    numPreds_;        //num of FO preds per domain (exclude evid)
  double         totalGndings_;

  //CHANGED: used for infering pll of gnd atoms of one FOPred in one domain
  StringHashArray gndPredStrs_;
  Array<bool>     gndPredTVs_;
  Array<long double>   gndPredPlls_;
};


#endif
