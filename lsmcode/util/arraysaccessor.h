#ifndef ARRAYSACCESSOR_H_OCT_17_2005
#define ARRAYSACCESSOR_H_OCT_17_2005

#include "array.h"


template <typename Type>
class ArraysAccessor
{
 public:
  ArraysAccessor() : arrays_(new Array<const Array<Type>*>), 
                     indexes_(new Array<int>), 
                     itemIdx_(0), freeze_(false), reset_(false), noComb_(true){}

  ~ArraysAccessor() { delete arrays_; delete indexes_; }


  void appendArray(const Array<Type>* const & arr) 
  {
    assert(!freeze_);
    if (arrays_->size() == 0)
    {
      if (arr->size() == 0) noComb_ = true;
      else                  noComb_ = false;
    }
    else
    {
      if (arr->size() == 0) noComb_ = true;
    }
    arrays_->append(arr);
  }

  
  const Array<Type>* getArray(const int& idx) const { return (*arrays_)[idx]; }

  int getNumArrays() const { return arrays_->size();}


  void clear() 
  { 
    arrays_->clear(); 
    indexes_->clear(); 
    itemIdx_ = 0;
    freeze_ = false; 
    noComb_ = true;
  }
  

  void deleteArraysAndClear()
  {
    for (int i = 0; i < arrays_->size(); i++)
      delete (*arrays_)[i];
    clear();
  }


    // Start from first combination again.
  void reset()  { reset_ = true; }

  
    // returns false if there are no more elements
    // a contains the next combination of elements in the arrays that were added
  bool getNextCombination(Array<Type>& itemArr, Array<int>* idxArr=NULL)
  {
    if (noComb_) return false;
    if (!freeze_) prepareAccess();
    if (reset_) { reset_ = false; prepareAccess(); }
    if ((*indexes_)[0] < 0) return false;
    itemArr.clear();
    if (idxArr)  idxArr->clear();
    for (int i = 0; i < arrays_->size(); i++)
    {
      itemArr.append( (*((*arrays_)[i]))[ (*indexes_)[i] ] );
      if (idxArr) idxArr->append((*indexes_)[i]);
    }

    for (int i = arrays_->size()-1; i >= 0; i--)
    {
      (*indexes_)[i]++;
      if ((*indexes_)[i] < (*arrays_)[i]->size()) return true;
      (*indexes_)[i] = 0;
    }
    (*indexes_)[0] = -1;
    return true;    
  }
  

  int numItemsInCombination() const { return (*arrays_)[0]->size(); }

  
  bool hasNextCombination()
  {
    if (noComb_) return false;
    if (!freeze_) prepareAccess();
    if (reset_) { reset_ = false; prepareAccess(); }
    if ((*indexes_)[0] < 0) return false;
    itemIdx_ = 0;
    return true;
  }


  bool nextItemInCombination(Type& item, int&idx)
  {
    if (itemIdx_ >= indexes_->size()) 
    {
      for (int i = arrays_->size()-1; i >= 0; i--)
      {
        (*indexes_)[i]++;
        if ((*indexes_)[i] < (*arrays_)[i]->size()) return false;
        (*indexes_)[i] = 0;
      }
      (*indexes_)[0] = -1;
      return false;
    }

    
    idx = (*indexes_)[itemIdx_];
    item = (*((*arrays_)[itemIdx_]))[idx];
    itemIdx_++;
    return true;
  }


  bool nextItemInCombination(Type& item) 
  {
    int i; 
    return nextItemInCombination(item,i);
  }


  int numCombinations() const
  {
    if (arrays_->size() == 0) return 0;
    int n = 1;
    for (int i = 0; i < arrays_->size(); i++)
      n *= (*arrays_)[i]->size();
    return n;    
  }

  
 private:

  void prepareAccess()
  {
    freeze_ = true;
    if (noComb_ || arrays_->size() == 0) return;
    indexes_->growToSize(arrays_->size());
    for (int i = 0; i < arrays_->size(); i++) (*indexes_)[i] = 0;
    //arrays_->compress();
    //indexes_->compress();
  }

 private:

    // the contents of arrays_ are not owned by ArraysAccessor;
  Array<const Array<Type>*>* arrays_;
  Array<int>* indexes_;
  int itemIdx_;
  bool freeze_;
  bool reset_;
  bool noComb_;
};


#endif
