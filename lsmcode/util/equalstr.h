#ifndef EQUALSTR_H_JUN_23_2005
#define EQUALSTR_H_JUN_23_2005

#include <cstring>

class EqualStr
{
 public:
  bool operator()(const char* const & s1, const char* const & s2) const
  {
    return strcmp(s1, s2) == 0;
  }
};


#endif
