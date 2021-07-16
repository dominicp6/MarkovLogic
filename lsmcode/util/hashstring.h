#ifndef HASHSTRING_H_JUL_10_2004
#define HASHSTRING_H_JUL_10_2004

#include <string>
#include <ext/hash_set>
#include <ext/hash_map>
using namespace __gnu_cxx;
#include "hasharray.h"
#include "hashint.h"

class HashString
{
 public:
  size_t operator()(string const& str) const
  {
    return hash<char const *>()(str.c_str());
  }
};

class EqualString
{
 public:
  bool operator()(string const & s1, string const & s2) const
  {
    return (s1.compare(s2)==0);
  }
};

typedef hash_set<string, HashString, EqualString> StringSet;
typedef hash_map<string, int, HashString, EqualString> StringToIntMap;
typedef hash_map<string, double, HashString, EqualString> StringToDoubleMap;
typedef HashArray<string, HashString, EqualString> StringHashArray;
typedef hash_map<string, Array<string>*, HashString, EqualString> StringToStringArrayMap;
typedef hash_map<string, StringHashArray*, HashString, EqualString> StringToStringHashArrayMap;
typedef hash_map<string, IntHashArray*, HashString, EqualString> StringToIntHashArrayMap;
typedef hash_map<string, Array<int>*, HashString, EqualString> StringToIntArrayMap;
typedef hash_map<string, StringSet*, HashString, EqualString> StringToStringSetMap;
typedef hash_map<string, string, HashString, EqualString> StringToStringMap;
typedef hash_map<string, bool, HashString, EqualString> StringToBoolMap;

typedef hash_map<string, Array<Array<string>* >*, HashString, EqualString> StringToStringArrayArrayMap;

typedef hash_map<string, Array<Array<Array<string>*>*>*, HashString, EqualString> StringToStringArray3Map;

#endif
