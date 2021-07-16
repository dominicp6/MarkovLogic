#ifndef MULTIDARRAY_H_SEP_12_2005
#define MULTIDARRAY_H_SEP_12_2005

#include "array.h"


template <typename Type> 
class MultDArray
{
 public:
    // Caller should delete dim if required
  MultDArray(const Array<int>* const & dim)
  {
    arr_ = new Array<Type>;
    int n = 1;
    for (int i = 0; i < dim->size(); i++) n *= (*dim)[i];
    arr_->growToSize(n);

    multiplier_ = new Array<int>;
    for (int i = 0; i < dim->size(); i++)
    {
      n /= (*dim)[i];
      multiplier_->append(n);
    }
  }


  ~MultDArray() 
  { 
    if (multiplier_) delete multiplier_; 
    if (arr_) delete arr_; 
  }    


  const Array<Type>* get1DArray() { return arr_; }
  

  Type getItem(const Array<int>* const & indexes) const
  { return (*arr_)[getIndex(indexes)]; }


  void setItem(const Array<int>* const & indexes, const Type& item)
  { (*arr_)[getIndex(indexes)] = item; }


  void addItem(const Array<int>* const & indexes, const Type& item)
  { (*arr_)[getIndex(indexes)] += item; }


 private:
  int getIndex(const Array<int>* const & indexes) const
  {
    assert(indexes->size() == multiplier_->size());
    int idx = 0;
    for (int i = 0; i < indexes->size(); i++)
      idx += (*indexes)[i] * (*multiplier_)[i];
    return idx;
  }


 private:
  Array<int>* multiplier_;
  Array<Type>* arr_;

};

#endif
