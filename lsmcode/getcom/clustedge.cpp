#include "clustedge.h"
#include "clustnode.h"

int ClustEdge::idCnt_ = 0;

string ClustEdge::getAtomStr() const
{
  ostringstream out;
  out << relName_ << "(" << clustNodes_[0]->name();
  for (int i = 1; i < clustNodes_.size(); i++)
    out << "," << clustNodes_[i]->name();
  out << ")";
  return out.str();
}

ostream& ClustEdge::print(ostream& out) const
{
  out << relName_ << "(" << clustNodes_[0]->name();
  for (int i = 1; i < clustNodes_.size(); i++)
    out << "," << clustNodes_[i]->name();
  out << ")";
  out << endl;
  for (int i = 0; i < gndEdges_.size(); i++)
    out << "  " << *gndEdges_[i] << endl;
  return out;
}
