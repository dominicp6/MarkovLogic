#ifndef STRINT_H_JUN_27_2005
#define STRINT_H_JUN_21_2005

#include <cstdlib>
#include <ext/hash_map>
using namespace __gnu_cxx;


struct StrInt
{
 public:
  StrInt() : str_(NULL), int_(-1) {}

  StrInt(const char* const & s, const int& i) 
  {
    str_ = new char[strlen(s)+1];
    strcpy(str_,s);
    int_ = i;
  }

  StrInt(const char* const & s) 
  {
    str_ = new char[strlen(s)+1];
    strcpy(str_,s);
    int_ = -1;
  }

  ~StrInt() { delete [] str_; }

  char* str_;
  int int_;
};


class HashStrInt
{
 public:
  size_t operator()(const StrInt* const & s) const
  {
    return hash<char const *>()(s->str_);
  }
};


class EqualStrInt
{
 public:
  bool operator()(const StrInt* const & s1, const StrInt* const & s2) const
  {
    return strcmp(s1->str_, s2->str_) == 0;
  }
};



#endif
