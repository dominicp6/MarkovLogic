#ifndef DUALMAP_H_JUN_21_2005
#define DUALMAP_H_JUN_21_2005
  
  
#include <limits>
#include <ext/hash_map>
using namespace __gnu_cxx;
#include "array.h"
#include "equalstr.h"


typedef hash_map<const char*, int, hash<const char*>, EqualStr> StrToIntMap;


  // Maps int to const char* and vice versa.
class DualMap
{ 
 public:
  DualMap() : intToStrArr_(new Array<const char*>), 
              strToIntMap_(new StrToIntMap) {}

  
  DualMap(const DualMap& dm)
  { 
    intToStrArr_ = new Array<const char*>; 
    strToIntMap_ = new StrToIntMap;
    for (int i = 0; i < dm.intToStrArr_->size(); i++)
      insert((*(dm.intToStrArr_))[i]);
    compress();
  }
  

  ~DualMap() 
  {
    for (int i = 0; i < intToStrArr_->size(); i++)
      delete [] (*intToStrArr_)[i];
    delete intToStrArr_;
    delete strToIntMap_;
  }


    // Returns const char* corresponding to i or NULL if there is no such char*.
    // The returned const char* should not be deleted.
  const char* getStr(const int& i) const
  { 
    if (0<= i && i < intToStrArr_->size())
      return (*intToStrArr_)[i];
    return NULL;
  }


    // Returns int corresponding to str or -1 if there is no such str.
    // Caller should delete str if required.
    // Making this function const causes the compiler to complain.
  int getInt(const char* const & str) const
  {
    StrToIntMap::iterator it;
    if ((it=strToIntMap_->find(str)) == strToIntMap_->end())
      return -1;
    return (*it).second;
  }


    // Returns corresponding int (which increases by one each time addType() is 
    // called), or -1 is str has been added before.
    // Caller should delete str if required.
  int insert(const char* const & str)
  {
    StrToIntMap::iterator it;
    if ((it=strToIntMap_->find(str)) != strToIntMap_->end())
    {
      cout << "Warning: In DualMap::insert(), tried to insert duplicate " 
           << str << ", prev id " << (*it).second << endl;
      return -1;
    }
    
    if (((int)intToStrArr_->size()) >= numeric_limits<int>::max()) 
    {
      cout << "Error: In DualMap::insert(), reach int max limit when inserting "
           << str << endl;
      exit(-1);
    }

    char* s = new char[strlen(str)+1];
    strcpy(s,str);
    intToStrArr_->append(s);
    int i = intToStrArr_->size()-1;
    (*strToIntMap_)[s] = i;
    return i;
  }

  
  int getNumInt() const  { return intToStrArr_->size(); }

    // Caller should not delete the returned Array<const char*>*.
  const Array<const char*>* getIntToStrArr() const  { return intToStrArr_; }
  
  void compress() { intToStrArr_->compress(); }


 private:
  Array<const char*>* intToStrArr_;
  StrToIntMap* strToIntMap_;
};

#endif
