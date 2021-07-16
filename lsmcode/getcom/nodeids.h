#ifndef NODEIDS_H_OCT_23_2009
#define NODEIDS_H_OCT_23_2009

#include <iostream>
#include "array.h"

class NodeIds
{
 private:
  IntHashArray ids_;
  int srcId_;
  int hashCode_;
  string comIdStr_;
  int domId_;

 public:
  NodeIds(const Array<int>& ids, const int& srcId, const string& comIdStr, const int& domId) : srcId_(srcId), comIdStr_(comIdStr), domId_(domId)
  {
    for (int i = 0; i < ids.size(); i++)
      ids_.append(ids[i]);
    
    //hashCode_ = 1;
    hashCode_ = domId_;

    for (int i = 0; i < ids_.size(); i++)
      hashCode_ = 31*hashCode_ + ids_[i];
  }
  ~NodeIds() {}

  const IntHashArray& ids() const    { return ids_;      }
  int srcId() const                  { return srcId_;    }
  int hashCode() const               { return hashCode_; }
  string comIdStr() const            { return comIdStr_; }
  int domId() const                  { return domId_;    }
  bool contains(const int& id) const { return ids_.contains(id); }

  ostream& print(ostream& out) const 
  {
    out << "hashCode " << hashCode_ << endl;
    out << "domId    " << domId_     << endl;
    out << "comIdStr " << comIdStr_ << endl;
    out << "srcId " << srcId_ << endl;
    out << "numIds " << ids_.size() << endl;
    for (int i = 0; i < ids_.size(); i++)
      out << ids_[i] << "  ";
    out << endl;
    return out;
  }

  bool equal(const NodeIds& ni) const
  {
    if (domId_ != ni.domId()) return false;
    if (srcId_ != ni.srcId()) return false;
    const IntHashArray& ids = ni.ids();    
    if (ids_.size() != ids.size()) return false;
    for (int i = 0; i < ids_.size(); i++)
      if (ids_[i] != ids[i]) return false;
    return true;
  }

};
inline ostream& operator<<(ostream& out, const NodeIds& n) { return n.print(out); }


class HashNodeIds
{
 public:
  size_t operator()(const NodeIds* const& ni) const { return ni->hashCode(); }
};

class EqualNodeIds
{
 public:
  bool operator()(const NodeIds* const& n1, const NodeIds* const& n2) const 
  {
    if (n1->domId() != n2->domId()) return false;
    const IntHashArray& ids1 = n1->ids();
    const IntHashArray& ids2 = n2->ids();
    if (ids1.size() != ids2.size()) return false;
    for (int i = 0; i < ids1.size(); i++)    
      if (ids1[i] != ids2[i]) return false;
    return true;
  }
};
typedef hash_set<NodeIds*, HashNodeIds, EqualNodeIds> NodeIdsSet;
typedef hash_map<NodeIds*, Array<NodeIds*>*, HashNodeIds, EqualNodeIds> NodeIdsToNodeIdsArrMap;



#endif
