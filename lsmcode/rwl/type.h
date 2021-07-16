#ifndef TYPE_H_OCT_11_2009
#define TYPE_H_OCT_11_2009

#include "array.h"
#include "constant.h"

class Type
{
 private:
  int    id_;
  string name_;
  Array<Constant*> constants_;

 public:
  Type(int id, string name) : id_(id), name_(name) {}
  ~Type() { } //ConstNode will delete the constants

  int    id()   const { return id_; }
  string name() const { return name_; }
  const Array<Constant*>& constants() const  { return constants_; }
  Constant* constant(int id) const           { return constants_[id]; }
  void      addConstant(Constant* constant)  { constants_.append(constant); }

  ostream& print(ostream& out) const { out << id_ << " " << name_; return out; }
};

inline ostream& operator <<(ostream& out, const Type& t) { return t.print(out); }


#endif
