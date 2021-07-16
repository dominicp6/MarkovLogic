#ifndef CLUSTNODE_H_OCT_23_2009
#define CLUSTNODE_H_OCT_23_2009

#include <iostream>
#include "array.h"
#include "gndnode.h"
#include "clustedge.h"

class ClustNode
{
 private:
  string name_;
  Array<GndNode*> gndNodes_;
  ClustEdgeSet clustEdges_;

 public:
  ClustNode(const string& name) : name_(name) {}
  ~ClustNode() {}
  string  name() const                     { return name_;       }
  const Array<GndNode*>& gndNodes() const  { return gndNodes_;   }
  const ClustEdgeSet& clustEdges() const   { return clustEdges_; }
  void addGndNode(GndNode* const& gndNode) { gndNodes_.append(gndNode); }
  bool addClustEdge(const ClustEdge* const& clustEdge);
  ostream& print(ostream& out) const;
};
inline ostream& operator<<(ostream& out, const ClustNode& cn) { return cn.print(out); }


#endif
