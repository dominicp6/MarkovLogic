#ifndef COMMUNITY_H_OCT_11_2009
#define COMMUNITY_H_OCT_11_2009

#include "node.h"

class NodeArr
{
 private:
  Node** nodes_;
  int    size_;

 public:
  NodeArr(Node** const& nodes, const int& size) : nodes_(nodes), size_(size) {}
  ~NodeArr() { delete [] nodes_; }
  Node** nodes() const  { return nodes_; }
  int    size() const   { return size_; }
};

int compareNodeArr(const void * n0, const void * n1)
{
  Node** nodes0 = (*(NodeArr**)n0)->nodes();
  Node** nodes1 = (*(NodeArr**)n1)->nodes();
  int id0 = ((ConstNode*)nodes0[0])->constant()->id();
  int id1 = ((ConstNode*)nodes1[0])->constant()->id();
  if (id0 < id1) return -1;
  if (id0 > id1) return  1;
  return 0;
}


class Community
{
 private:
  Node**    singleNodes_; //array of unclustered nodes
  int       numSingleNodes_;
  NodeArr** clusts_;  //array of cluster, each cluster being an array of nodes
  int       numClusts_;
  int       totalNodes_;
  int       totalClusts_; //unit clusts + non-unit clusts
  int       hashCode_;

 public:
  Community(Node** const& singleNodes, const int& numSingleNodes, NodeArr** const& clusts, const int& numClusts)
    : numSingleNodes_(numSingleNodes), clusts_(clusts), numClusts_(numClusts)
  {
    singleNodes_ = new Node*[numSingleNodes_];
    for (int i = 0; i < numSingleNodes_; i++)
      singleNodes_[i] = singleNodes[i];

    //sort
    qsort(singleNodes_, numSingleNodes_, sizeof(Node*), compareNodeConstId);
    for (int i = 0; i < numClusts_; i++)
      qsort(clusts_[i]->nodes(), clusts_[i]->size(), sizeof(Node*), compareNodeConstId);
    qsort(clusts_, numClusts_, sizeof(NodeArr*), compareNodeArr);

    //compute hash code
    totalNodes_ = numSingleNodes_;
    hashCode_ = 1;
    for (int i = 0; i < numSingleNodes_; i++)
      hashCode_ = 31*hashCode_ + singleNodes_[i]->id();
    for (int i = 0; i < numClusts_; i++)
    {
      Node** nodes = clusts_[i]->nodes();
      int numNodes = clusts_[i]->size();
      for (int j = 0; j < numNodes; j++)
        hashCode_ = 31*hashCode_ +  nodes[j]->id();
      totalNodes_ += numNodes;
    }

    totalClusts_ = numSingleNodes_ + numClusts_;
  }

  ~Community()
  {
    delete [] singleNodes_;
    for (int i = 0; i < numClusts_; i++)
      delete clusts_[i];
    delete [] clusts_;
  }

  Node**    singleNodes()    const { return singleNodes_;   }
  int       numSingleNodes() const { return numSingleNodes_; }
  NodeArr** clusts()         const { return clusts_;    }
  int       numClusts()      const { return numClusts_; }
  int       totalNodes()     const { return totalNodes_;}
  int       totalClusts()    const { return totalClusts_; }
  int       hashCode()       const { return hashCode_;  }

  ostream& print(ostream& out) const
  {
    for (int i = 0; i < numSingleNodes_; i++)
      out << "SINGLE: " << singleNodes_[i]->strRep() << endl;
    for (int i = 0; i < numClusts_; i++)
    {
      Node** nodes = clusts_[i]->nodes();
      int numNodes = clusts_[i]->size();
      out << "CLUST: " << endl;
      for (int j = 0; j < numNodes; j++)
      {
        out << "  " << nodes[j]->strRep() << endl;
      }
    }
    return out;
  }
};

inline ostream& operator <<(ostream& out, const Community& c) { return c.print(out); }

class HashCommunity
{
 public:
  size_t operator()(Community* const& c) const { return hash<int>()(c->hashCode()); }
};

class EqualCommunity
{
 public:
  bool operator()(Community* const& c0, Community* const& c1) const
  {
    if (c0->totalNodes()     != c1->totalNodes())     return false;
    if (c0->numSingleNodes() != c1->numSingleNodes()) return false;
    if (c0->numClusts()      != c1->numClusts())      return false;

    for (int i = 0; i < c0->numSingleNodes(); i++)
      if ( (c0->singleNodes())[i]->id() != (c1->singleNodes())[i]->id() ) return false;

    NodeArr** clusts0 = c0->clusts();
    NodeArr** clusts1 = c1->clusts();
    for (int i = 0; i < c0->numClusts(); i++)
    {
      Node** nodes0 = clusts0[i]->nodes();
      Node** nodes1 = clusts1[i]->nodes();
      int numNodes0 = clusts0[i]->size();
      int numNodes1 = clusts1[i]->size();
      if (numNodes0 != numNodes1) return false;
      for (int j = 0; j < numNodes0; j++)
        if (nodes0[j]->id() != nodes1[j]->id()) return false;
    }
    return true;
  }
};

typedef hash_set<Community*, HashCommunity, EqualCommunity> CommunitySet;


#endif
