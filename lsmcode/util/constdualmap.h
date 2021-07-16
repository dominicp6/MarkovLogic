#ifndef CONSTDUALMAP_H_JUN_21_2005
#define CONSTDUALMAP_H_JUN_21_2005


#include <limits>
#include <ext/hash_map>
//using namespace __gnu_cxx;
#include "array.h"
#include "strint.h"


  // StrInt stores the constant name & its type id
typedef hash_map<const StrInt*, int, HashStrInt, EqualStrInt> StrIntToIntMap;


  // Maps int to StrInt* and vice versa.
class ConstDualMap
{  
 public:
  ConstDualMap()  
  {
    intToStrIntArr_ = new Array<const StrInt*>;
    strIntToIntMap_ = new StrIntToIntMap;
  }


  ~ConstDualMap() 
  {
    for (int i = 0; i < intToStrIntArr_->size(); i++)
      delete (*intToStrIntArr_)[i];
    delete intToStrIntArr_;
    delete strIntToIntMap_;
  }


    // Returns const char* corresponding to i or NULL if there is no such char*.
    // The returned const char* should not be deleted.
  const char* getStr(const int& i)
  { 
    if (0 <= i && i < intToStrIntArr_->size())
      return (*intToStrIntArr_)[i]->str_;
    return NULL;
  }


    // Returns the int_ of StrInt corresponding to i; returns -1 if there is no
    // such StrInt.
  int getInt2(const int& i)
  { 
    if (0 <= i && i < intToStrIntArr_->size())
      return (*intToStrIntArr_)[i]->int_;
    return -1;
  }

    // Returns the int_ of StrInt corresponding to i; returns -1 if there is no
    // such StrInt. Caller should delete s if required.
  int getInt2(const char* const & s)
  { 
    int i = getInt(s);
    if (i < 0) return -1;
    return getInt2(i);
  }


    // Returns int corresponding to str or -1 if there is no such str.
    // Caller should delete s if required.
    // Making this function const causes the compiler to complain.
  int getInt(const char* const & s)
  {
    StrInt str(s);
    StrIntToIntMap::iterator it;
    if ((it=strIntToIntMap_->find(&str)) == strIntToIntMap_->end())
      return -1;
    return (*it).second;
  }


    // Returns corresponding int (which increases by one each time addType() is 
    // called), or -1 is str has been added before.
    // Caller should delete s if required.
  int insert(const char* const & s, const int& ii)
  {
    StrInt* strInt = new StrInt(s,ii);

    StrIntToIntMap::iterator it;
    if ((it=strIntToIntMap_->find(strInt)) != strIntToIntMap_->end())
    {
      cout << "Warning: In ConstDualMap::insert(), tried to insert duplicate " 
           << strInt->str_ << ", prev id " << (*it).second << endl;
      delete strInt;
      return -1;
    }
    
    if (((int)intToStrIntArr_->size()) >= numeric_limits<int>::max()) 
    {
      cout << "Error: In ConstDualMap::insert(), reach int max limit when "
           << "inserting " << strInt->str_ << endl;
      delete strInt;
      exit(-1);
    }

    intToStrIntArr_->append(strInt);
    int i = intToStrIntArr_->size()-1;
    (*strIntToIntMap_)[strInt] = i;
    return i;
  }

  
  int getNumInt() const  { return intToStrIntArr_->size(); }

    // Caller should not delete the returned Array<StrInt*>*.
  const Array<const StrInt*>* getIntToStrIntArr() const  
  { 
    return intToStrIntArr_; 
  }

    // Caller should delete the returned Array<const char*>* but not its 
    // contents
  const Array<const char*>* getIntToStrArr() const  
  { 
    Array<const char*>* a = new Array<const char*>;
    for (int i = 0; i < intToStrIntArr_->size(); i++)
      a->append((*intToStrIntArr_)[i]->str_);
    return a; 
  }


    // Caller should delete the returned Array<int>*.
  const Array<int>* getIntToInt2Arr() const  
  { 
    Array<int>* a = new Array<int>;
    for (int i = 0; i < intToStrIntArr_->size(); i++)
      a->append((*intToStrIntArr_)[i]->int_);
    return a; 
  }
  
  void compress() { intToStrIntArr_->compress(); }
 
 private:
  Array<const StrInt*>* intToStrIntArr_;
  StrIntToIntMap* strIntToIntMap_;
};

#endif
