#include "path.h"

Path::~Path()
{
  for (int i = 0; i < numAtoms_; i++) delete atoms_[i];
  delete [] atoms_; delete supportIdStrs_; delete relIdToCntMap_; delete typeIdToConstsMap_; delete seenPaths_;

}

PathSet* Path::getSeenPaths() { if (seenPaths_ == NULL) seenPaths_ = new PathSet; return seenPaths_; }
