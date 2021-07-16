#ifndef HASHINT_H_NOV_10_2005
#define HASHINT_H_NOV_10_2005

#include <ext/hash_set>
#include <ext/hash_map>
using namespace __gnu_cxx;
#include "hasharray.h"
#include "array.h"

class HashInt
{
 public:
  size_t operator()(const int& i) const { return hash<int>()(i); }
};

class EqualInt
{
 public:
  bool operator()(const int& i1, const int& i2) const { return (i1 == i2); }
};

typedef hash_set<int> IntSet;
typedef HashArray<int, HashInt, EqualInt> IntHashArray;
typedef hash_map<int, int, HashInt, EqualInt> IntToIntMap;
typedef hash_map<int, double, HashInt, EqualInt> IntToDoubleMap;
typedef hash_map<int, string, HashInt, EqualInt> IntToStringMap;
typedef hash_map<int, Array<int>*, HashInt, EqualInt> IntToIntArrayMap;
typedef hash_map<int, IntHashArray*, HashInt, EqualInt> IntToIntHashArrayMap;

#endif
