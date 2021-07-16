#ifndef HASH_H_JUN_28_2005
#define HASH_H_JUN_28_2005

#include "array.h"


class Hash
{
 public:
  static int hash(const Array<int>& arr) 
  {
    int hashCode = 1;
    int size = arr.size();
    for (int i = 0; i < size; i++)
      hashCode = 31*hashCode + arr[i];
    return hashCode;
  }


  static int hash(const Array<unsigned int>& arr) 
  {
    int hashCode = 1;
    int size = arr.size();
    for (int i = 0; i < size; i++)
      hashCode = 31*hashCode + arr[i];
    return hashCode;
  }


};

struct IntPairHash :
public unary_function< pair<unsigned int, unsigned int>, size_t >
{
  size_t operator()(const pair<unsigned int, unsigned int> p) const
  {
    return p.first * 31 + p.second;
  }
};

#endif
