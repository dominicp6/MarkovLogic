#ifndef CONSTANT_H_OCT_11_2009
#define CONSTANT_H_OCT_11_2009

#include <string>
#include <iostream>
using namespace std;

class Type;

class Constant
{
 private:
  int    id_;
  string name_;
  Type*  type_;

 public:
  Constant() : id_(-1) , name_(""), type_(NULL) {}
  Constant(int id, string name, Type* type) : id_(id) , name_(name), type_(type) {}
  ~Constant() {}

  int    id()   const { return id_; }
  string name() const { return name_; }
  Type* type()  const { return type_; }

  void setId(const int& id)        { id_   = id; }
  void setName(const string& name) { name_ = name; }
  void setType(Type* type)         { type_ = type; }

  int    typeId()   const;
  string typeName() const;

  ostream& print(ostream& out) const;
};

inline ostream& operator <<(ostream& out, const Constant& c) { return c.print(out); }

#endif
