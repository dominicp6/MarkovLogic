#ifndef GNDNODE_H_OCT_23_2009
#define GNDNODE_H_OCT_23_2009

#include <iostream>
#include "util.h"
#include "hashint.h"
#include "array.h"

class ClustNode;

class GndNode
{
 private:
  string name_;
  ClustNode* clustNode_;
  int id_;
  
  static int idCnt_;

 public:
  GndNode(const string& name) : name_(name), clustNode_(NULL), id_(idCnt_++) {}
  ~GndNode() {}
  string name() const                     { return name_; }
  void setClustNode(ClustNode* const& cn) { clustNode_ = cn; }
  ClustNode* clustNode() const            { return clustNode_; }
  int id() const                          { return id_; }

  int getNodeIds() const
  {
    string::size_type u = name_.find('_');
    string intStr = Util::substr(name_, u+1, name_.length());
    return atoi(intStr.c_str());
  }

  ostream& print(ostream& out) const;
};
inline ostream& operator<<(ostream& out, const GndNode& gn) { return gn.print(out); }


class GndEdge;

class HashGndNode
{
 public:
  size_t operator()(const GndNode* const& n) const { return hash<int>()(n->id()); }
};
class EqualGndNode
{
 public:
  bool operator()(const GndNode* const& n1, const GndNode* const& n2) const { return (n1 == n2); }
};

typedef hash_map<GndNode*, Array<GndEdge*>*, HashGndNode, EqualGndNode> GndNodeToGndEdgesMap;


#endif
