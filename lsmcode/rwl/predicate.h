#ifndef PREDICATE_H_OCT_11_2009
#define PREDICATE_H_OCT_11_2009

#include <ostream>
#include "array.h"

class Constant;

class Predicate
{
 private:
  int    id_;
  string name_; //predicate name
  Array<Constant*> args_;

 public:
  Predicate(int id, string name) : id_(id), name_(name) {}
  Predicate(int id, string name, Array<Constant*>& args) : id_(id), name_(name),args_(args)  {}
  ~Predicate() {}

  int    id()   const { return id_; }
  string name() const { return name_; }
  const Array<Constant*>& args() const { return args_; }

  void addArg(Constant* constant) { args_.append(constant); }
  void compressArgs() { args_.compress(); }

  ostream& print(ostream& out) const
  {
    out << id_ << " " << name_ << "(";
    for (int i = 0; i < args_.size(); ++i)
      out << *args_[i] << ((i<args_.size()-1)?" , " : ")");
    return out;
  }
};

inline ostream& operator <<(ostream& out, const Predicate& p) { return p.print(out); }


#endif
