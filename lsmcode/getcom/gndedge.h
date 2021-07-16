#ifndef GNDEDGE_H_OCT_23_2009
#define GNDEDGE_H_OCT_23_2009

#include <iostream>
#include <sstream>
#include "hashstring.h"
#include "array.h"
#include "gndnode.h"

class GndEdge
{
 private:
  string relName_;
  Array<GndNode*> gndNodes_;
  int numUniqNodes_;

 public:
  GndEdge(const string& relName, const Array<GndNode*>& gndNodes) : relName_(relName), gndNodes_(gndNodes) 
  {
    StringSet sset;
    for (int i = 0; i < gndNodes_.size(); i++)
      sset.insert(gndNodes_[i]->name());
    numUniqNodes_ = sset.size();
  }

  ~GndEdge() {}
  string relName() const                    { return relName_;  }
  const Array<GndNode*>& gndNodes() const   { return gndNodes_; }
  int numUniqNodes() const                  { return numUniqNodes_; }

  string atomStr() const  { ostringstream oss; print(oss); return oss.str(); }

  ostream& print(ostream& out) const
  {
    out << relName_ << "(" << gndNodes_[0]->name();
    for (int i = 1; i < gndNodes_.size(); i++)
      out << "," << gndNodes_[i]->name();
    out << ")";
    return out;
  }
};
inline ostream& operator<<(ostream& out, const GndEdge& ge) { return ge.print(out); }


#endif
