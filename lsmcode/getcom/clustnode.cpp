#include "clustnode.h"

bool ClustNode::addClustEdge(const ClustEdge* const& clustEdge)
{
  pair<ClustEdgeSet::iterator,bool> pr = clustEdges_.insert((ClustEdge*) clustEdge);
  return pr.second;
}

ostream& ClustNode::print(ostream& out) const
{
  out << name_ << ": " << gndNodes_[0]->name();
  for (int i = 1; i < gndNodes_.size(); i++)
    out << " " << gndNodes_[i]->name();
  out << endl;
  return out;
}
