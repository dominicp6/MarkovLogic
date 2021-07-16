#include "gndnode.h"

int GndNode::idCnt_ = 0;

ostream& GndNode::print(ostream& out) const { out << name_ << " " << clustNode_; return out; }
