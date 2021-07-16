#ifndef PRED_H_OCT_23_2009
#define PRED_H_OCT_23_2009

class Pred
{
 private:
  int  relId_;
  bool sign_;
  int* varIds_;
  int  numVarIds_;

 public:
  Pred(const int& relId, const bool& sign, int* const& varIds, const int& numVarIds)
    : relId_(relId), sign_(sign), varIds_(varIds), numVarIds_(numVarIds) {}

  Pred(const Pred& pred)
  {
    relId_     = pred.relId();
    sign_      = pred.sign();
    numVarIds_ = pred.numVarIds();
    varIds_    = new int[numVarIds_];
    for (int i = 0; i < numVarIds_; i++)
      varIds_[i] = pred.varId(i);
  }

  ~Pred() { delete [] varIds_; }

  int computeHashCode()
  {
    int hashCode = relId_;
    if (sign_) hashCode = 31*hashCode + 1;
    else       hashCode = 31*hashCode + 2;
    for (int i = 0; i < numVarIds_; i++)
      hashCode = 31*hashCode + varIds_[i];
    return hashCode;
  }

  int   relId()     const { return relId_;   }
  bool  sign()      const { return sign_; }
  int*  varIds()    const { return varIds_;  }
  int   numVarIds() const { return numVarIds_;}
  int   varId(const int& idx) const { return varIds_[idx]; }
  void  setSign(const bool& sign)   { sign_ = sign; }
  void  setVarId(const int& idx, const int& varId) { varIds_[idx] = varId; }

  bool equal(const Pred& other) const
  {
    if (this == &other) return true;
    if (relId_     != other.relId())     return false;
    if (sign_      != other.sign())      return false;
    Util::assertt(numVarIds_ == other.numVarIds(), "expect same num of varIds", -1);
    for (int i = 0; i < numVarIds_; i++)
      if (varIds_[i] != other.varId(i)) return false;
    return true;
  }

  int compare(const Pred& other) const
  {
    if (this == &other) return 0;
    if (relId_ < other.relId()) return -1;
    if (relId_ > other.relId()) return  1;
    Util::assertt(numVarIds_ == other.numVarIds(), "expect same num of varIds", -1);
    for (int i = 0; i < numVarIds_; i++)
    {
      if (varIds_[i] < other.varId(i)) return -1;
      if (varIds_[i] > other.varId(i)) return  1;
    }
    return 0;
  }

  int compareByIdAndSign(const Pred& other) const
  {
    if (this == &other) return 0;
    if (relId_ < other.relId())  return -1;
    if (relId_ > other.relId())  return  1;
    if (!sign_ &&  other.sign()) return -1;
    if ( sign_ && !other.sign()) return  1;
    Util::assertt(numVarIds_ == other.numVarIds(), "expect same num of varIds", -1);
    for (int i = 0; i < numVarIds_; i++)
    {
      if (varIds_[i] < other.varId(i)) return -1;
      if (varIds_[i] > other.varId(i)) return  1;
    }
    return 0;
  }

};

int comparePred(const void * p0, const void * p1)
{
  Pred* pred0 = (*(Pred**)p0);
  Pred* pred1 = (*(Pred**)p1);
  Util::assertt(pred0->relId() == pred1->relId(), "expect same pred of same rel", -1);
  return pred0->compare(*pred1);
}

int comparePredByIdAndSign(const void * p0, const void * p1)
{
  Pred* pred0 = (*(Pred**)p0);
  Pred* pred1 = (*(Pred**)p1);
  return pred0->compareByIdAndSign(*pred1);
}


#endif
