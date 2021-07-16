#ifndef CLAUSE_H_OCT_23_2009
#define CLAUSE_H_OCT_23_2009

#include <cfloat>
#include "pred.h"

class Clause
{
 private:
  Pred** preds_;
  int    numPreds_;
  int    hashCode_;
  double score_;
  int*   dbIds_;    //ids of DBs supporting this path
  int    numDBIds_;

 public:
  Clause(Pred** const& preds, const int& numPreds) : preds_(preds), numPreds_(numPreds), score_(DBL_MAX), dbIds_(NULL), numDBIds_(0) { setHashCode(); }

  Clause(const Clause& clause)
  {
    score_    = clause.score();
    numPreds_ = clause.numPreds();
    preds_    = new Pred*[numPreds_];
    for (int i = 0; i < numPreds_; i++)
      preds_[i] = new Pred( *clause.pred(i) );

    numDBIds_ = clause.numDBIds();
    if (numDBIds_ == 0) dbIds_ = NULL;
    else
    {
      int* otherIds = clause.dbIds();
      dbIds_ = new int[numDBIds_];
      for (int i = 0; i < numDBIds_; i++)
        dbIds_[i] = otherIds[i];
    }
   
    setHashCode();
  }

  ~Clause()
  {
    for (int i = 0; i < numPreds_; i++)
      delete preds_[i];
    delete [] preds_;
    delete [] dbIds_;
  }

  void setHashCode()
  {
    hashCode_ = 1;
    for (int i = 0; i < numPreds_; i++)
      hashCode_ = 31*hashCode_ + preds_[i]->computeHashCode();
  }

  Pred** preds()    const { return preds_;    }
  int    numPreds() const { return numPreds_; }
  int    hashCode() const { return hashCode_; }
  Pred*  pred(const int& idx) const { return preds_[idx]; }
  double score()    const { return score_;    }
  int*   dbIds()    const { return dbIds_;    }
  int    numDBIds() const { return numDBIds_; }
  void   setScore(const double& score) { score_ = score; }
  void   setDBIds(int*const& dbIds, const int& numDBIds) { dbIds_ = dbIds; numDBIds_ = numDBIds; }

  bool equal(const Clause& other)
  {
    if (this == &other) return true;
    if (numPreds_ != other.numPreds()) return false;
    for (int i = 0; i < numPreds_; i++)
      if ( !preds_[i]->equal(*other.pred(i)) ) return false;
    return true;
  }
};

class HashClause
{
 public:
  size_t operator()(Clause* const& c) const { return c->hashCode(); }
};

class EqualClause
{
 public:
  bool operator()(Clause* const& c0, Clause* const& c1) const { return c0->equal(*c1); }
};

typedef hash_set<Clause*, HashClause, EqualClause> ClauseSet;

int compareClausesByScore(const void * c0, const void * c1)
{
  if ((*(Clause**)c0)->score() < (*(Clause**)c1)->score()) return  1;
  if ((*(Clause**)c0)->score() > (*(Clause**)c1)->score()) return -1;
  return 0;
}


#endif
