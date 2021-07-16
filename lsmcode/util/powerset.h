#ifndef POWERSET_H_SEP_6_2005
#define POWERSET_H_SEP_6_2005

#include "array.h"

  //maximum number of elements from which subsets are composed
const int MAX_SIZE_TO_STORE = 10;


struct PowerSetInstanceVars
{
  int tempMaxSize;
  int sizeIdx;
  int lastNumIdx;
  int combIdx;  
  bool smallSizeFirst;
};


class PowerSet
{
  //private:
 public:
  PowerSet() : setSizeArr_(new Array<Array<Array<Array<int>*>*>*>)
  {
    instanceVars_.tempMaxSize = 0;
    instanceVars_.sizeIdx = 1;
    instanceVars_.lastNumIdx = 0;
    instanceVars_.combIdx = 0;
  }


 public:
  static PowerSet* getPowerSet() 
  { 
    if (ps_ == NULL) ps_ = new PowerSet; 
    return ps_;
  }

  static void deletePowerSet() { if (ps_) delete ps_; }


  ~PowerSet()
  {
    for (int i = 0; i < setSizeArr_->size(); i++)
    {
      if ((*setSizeArr_)[i] == NULL) continue;
      for (int j = 0; j < (*setSizeArr_)[i]->size(); j++)
      {
        if ((*(*setSizeArr_)[i])[j] == NULL) continue;
        for (int k = 0; k < (*(*setSizeArr_)[i])[j]->size(); k++)
          delete (*(*(*setSizeArr_)[i])[j])[k];
        delete (*(*setSizeArr_)[i])[j];
      }
      delete (*setSizeArr_)[i];
    }
    delete setSizeArr_;
  }


  void create(const int& maxSize)
  {
    int curMaxSize = setSizeArr_->size()-1;
    //commented out because user can choose not to delete the power set
    //assert(curMaxSize <= MAX_SIZE_TO_STORE);
    if (maxSize <= curMaxSize) return;
    setSizeArr_->growToSize(maxSize+1, NULL);

      // if there are no combinations with only one item, then create them
    if (curMaxSize < 0) (*setSizeArr_)[1] = new Array<Array<Array<int>*>*>;
    Array<Array<Array<int>*>*>* unitCombs = (*setSizeArr_)[1];
    unitCombs->growToSize(maxSize,NULL);
    for (int i = (curMaxSize<0)?0:curMaxSize; i < maxSize; i++)
    {
      Array<Array<int>*>* unitComb = new Array<Array<int>*>;
      unitComb->append(new Array<int>);
      unitComb->lastItem()->append(i);
      unitComb->lastItem()->compress();
      unitComb->compress();
      (*unitCombs)[i] = unitComb;
    }
    if (curMaxSize < 0) curMaxSize = 1;

      // create combinations with more than one item
    for (int s = 2; s <= maxSize; s++)
    {
      int remainingSize = s-1;
      Array<Array<Array<int>*>*>* combs = (*setSizeArr_)[remainingSize];

        // for each index that can be appended to an existing combination
      for (int i = curMaxSize; i < maxSize; i++)
      {
        for (int j = 0; j < i; j++)
        {
          Array<Array<int>*>* combsEndInJ = (*combs)[j];
            // if there are no combinations ending in j
          if (combsEndInJ == NULL) continue;
          for (int k = 0; k < combsEndInJ->size(); k++)
          {
            Array<int>* comb = (*combsEndInJ)[k];
            assert (comb->lastItem() == j);
            assert (comb->lastItem() < i);
            Array<int>* newComb = new Array<int>(*comb);
            newComb->append(i);
            newComb->compress();
            assert(newComb->size() == s);
            if ((*setSizeArr_)[s] == NULL) 
              (*setSizeArr_)[s] = new Array<Array<Array<int>*>*>;              
            if ((*setSizeArr_)[s]->size() < maxSize)
              (*setSizeArr_)[s]->growToSize(maxSize,NULL);            
            if ((*(*setSizeArr_)[s])[i] == NULL)
              (*(*setSizeArr_)[s])[i] = new Array<Array<int>*>;
            (*(*setSizeArr_)[s])[i]->append(newComb);
          }
          (*(*setSizeArr_)[s])[i]->compress();
        }
      } //for each index that can be appended to an existing combination
    } //create combinations with more than one item
  }


  void destroy()
  {
    if (setSizeArr_->size()-1 <= MAX_SIZE_TO_STORE) return;

    for (int i = 0; i < setSizeArr_->size(); i++)
    {
      if ((*setSizeArr_)[i] == NULL) continue;

      if (i <= MAX_SIZE_TO_STORE)
      {
        for (int j = MAX_SIZE_TO_STORE; j < (*setSizeArr_)[i]->size(); j++)
        {
          if ((*(*setSizeArr_)[i])[j] == NULL) continue;
          for (int k = 0; k < (*(*setSizeArr_)[i])[j]->size(); k++)
            delete (*(*(*setSizeArr_)[i])[j])[k];
          delete (*(*setSizeArr_)[i])[j];
        }
        (*setSizeArr_)[i]->shrinkToSize(MAX_SIZE_TO_STORE);
      }
      else
      {
        for (int j = 0; j < (*setSizeArr_)[i]->size(); j++)
        {
          if ((*(*setSizeArr_)[i])[j] == NULL) continue;
          for (int k = 0; k < (*(*setSizeArr_)[i])[j]->size(); k++)
            delete (*(*(*setSizeArr_)[i])[j])[k];
          delete (*(*setSizeArr_)[i])[j];
        }
        delete (*setSizeArr_)[i];
      }
    }
    setSizeArr_->shrinkToSize(MAX_SIZE_TO_STORE+1);
  }


  void prepareAccess(const int& tempMaxSize, PowerSetInstanceVars& instVars,
                     const bool& smallSizeFirst=true)
  {
    if (tempMaxSize > setSizeArr_->size()-1)
      create(tempMaxSize);

    instVars.tempMaxSize = tempMaxSize;
    instVars.sizeIdx = (smallSizeFirst) ? 1 : tempMaxSize;
    instVars.lastNumIdx = instVars.sizeIdx - 1;
    instVars.combIdx = -1;
    instVars.smallSizeFirst = smallSizeFirst;
  }


  void prepareAccess(const int& tempMaxSize, const bool& smallSizeFirst=true)
  { prepareAccess(tempMaxSize, instanceVars_, smallSizeFirst); }


  bool getNextSet(const Array<int>*& set, PowerSetInstanceVars& instVars)
  {
    int& tempMaxSize = instVars.tempMaxSize;
    int& sizeIdx = instVars.sizeIdx;
    int& lastNumIdx = instVars.lastNumIdx;
    int& combIdx = instVars.combIdx;
    bool& smallSizeFirst = instVars.smallSizeFirst;

    if (++combIdx >= (*(*setSizeArr_)[sizeIdx])[lastNumIdx]->size())
    {
      combIdx = 0;
      ++lastNumIdx;
      while (lastNumIdx == tempMaxSize || 
             (lastNumIdx < tempMaxSize && 
              (*(*setSizeArr_)[sizeIdx])[lastNumIdx] == NULL ))
      {
        ++lastNumIdx;
        if (lastNumIdx >= tempMaxSize)
        {
          if (smallSizeFirst)
          {
            lastNumIdx = sizeIdx - 1;
            while (++sizeIdx <= tempMaxSize && (*setSizeArr_)[sizeIdx]==NULL);
            if (sizeIdx > tempMaxSize) return false;
          }
          else
          {
            lastNumIdx = sizeIdx - 2;
            while (--sizeIdx >= 1 && (*setSizeArr_)[sizeIdx]==NULL);
            if (sizeIdx < 1) return false;
          }
        }
        if ((*(*setSizeArr_)[sizeIdx])[lastNumIdx] != NULL) break;
      }
    }
    set = (*(*(*setSizeArr_)[sizeIdx])[lastNumIdx])[combIdx];
    return true;
  }


  bool getNextSet(const Array<int>*& set) 
  { return getNextSet(set, instanceVars_); }


  Array<Array<Array<Array<int>*>*>*>* getSetSizeArr() const  
  { return setSizeArr_; }


  ostream& print(ostream& out) const
  {
    int n = 0;
    for (int i = 0; i < setSizeArr_->size(); i++)
    {
      if ((*setSizeArr_)[i] == NULL) continue;
      for (int j = 0; j < (*setSizeArr_)[i]->size(); j++)
      {
        if ((*(*setSizeArr_)[i])[j] != NULL) 
        {
          for (int k = 0; k < (*(*setSizeArr_)[i])[j]->size(); k++)
          {
            cout << n++ << ": ";
            for (int l = 0; l < (*(*(*setSizeArr_)[i])[j])[k]->size(); l++)
              cout << (*(*(*(*setSizeArr_)[i])[j])[k])[l] << " ";
            cout << endl;
          }
        }
      }
    }
    return out;
  }


 private:
  static PowerSet* ps_; //singleton

    //setSizeArr_[i][j] are the subsets of size i that ends with index j
  Array<Array<Array<Array<int>*>*>*>* setSizeArr_;
  
  PowerSetInstanceVars instanceVars_;
};


inline
ostream& operator<<(ostream& out, const PowerSet& p) { return p.print(out); }


#endif
