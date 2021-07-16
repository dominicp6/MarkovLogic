#ifndef CLUSTEDGE_H_OCT_23_2009
#define CLUSTEDGE_H_OCT_23_2009

#include <climits>
#include "win.h"
#include "util.h"
#include "gndedge.h"


class ClustNode;

class ClustEdge
{
 private:
  string relName_;
  Array<ClustNode*> clustNodes_;
  Array<GndEdge*> gndEdges_;
  bool visited_;
  GndNodeToGndEdgesMap gndNodeToGndEdgesMap_;
  int id_;

  static int idCnt_;

 public:
  ClustEdge(const string& relName, const Array<ClustNode*>& clustNodes) : relName_(relName), clustNodes_(clustNodes), visited_(false), id_(idCnt_++) {}

  ~ClustEdge()
  {
    //TODO: fix delete Array<GndEdge*>* problem
    //for (GndNodeToGndEdgesMap::iterator it = gndNodeToGndEdgesMap_.begin(); it != gndNodeToGndEdgesMap_.end(); it++)
    //  delete (*it).second;
    gndEdges_.deleteItemsAndClear();
  }

  void addGndEdge(GndEdge* const& gndEdge)    { gndEdges_.append(gndEdge); }
  string relName() const                      { return relName_;    }
  const Array<ClustNode*>& clustNodes() const { return clustNodes_; }
  const Array<GndEdge*>& gndEdges() const     { return gndEdges_;   }
  bool visited() const                        { return visited_;    }
  void setVisited(const bool& v)              { visited_ = v;       }
  int  id() const                             { return id_;         }

  void createGndNodeToGndEdgesMap()
  {
    for (int i = 0; i < gndEdges_.size(); i++)
    {
      GndEdge* gndEdge = gndEdges_[i];
      const Array<GndNode*>& gndNodes = gndEdge->gndNodes();
      for (int j= 0; j < gndNodes.size(); j++)
      {
        GndNode* gndNode = gndNodes[j];
        Array<GndEdge*>* gndEdges;
        GndNodeToGndEdgesMap::iterator it = gndNodeToGndEdgesMap_.find(gndNode);
        if (it == gndNodeToGndEdgesMap_.end()) { gndEdges = new Array<GndEdge*>; gndNodeToGndEdgesMap_[gndNode] = gndEdges; }
        else                                   { gndEdges = (*it).second; }
        gndEdges->append(gndEdge);
      }
    }

    //only store gnd edges with min unique gnd nodes
    for (GndNodeToGndEdgesMap::iterator it = gndNodeToGndEdgesMap_.begin(); it != gndNodeToGndEdgesMap_.end(); it++)
    {
      Array<GndEdge*>& gndEdges = *( (*it).second );

      int minNodes = INT_MAX;
      int numMin = 0;
      for (int i = 0; i < gndEdges.size(); i++)    
      {
        if (gndEdges[i]->numUniqNodes() < minNodes) 
        {
          minNodes = gndEdges[i]->numUniqNodes();
          numMin = 1;
        }
        else 
        if (gndEdges[i]->numUniqNodes() == minNodes) 
          numMin++;
      }

      Util::assertt(gndEdges.size() >= numMin, "expect gndEdges->size() >= numMin", -1); 

      if (numMin < gndEdges.size())
      {
        for (int i = 0; i < gndEdges.size(); i++)    
        {
          if (gndEdges[i]->numUniqNodes() != minNodes) 
          {
            gndEdges.removeItemFastDisorder(i);
            i--;
          }
        }
      }
    }
  }

  GndEdge* getGndEdge(const GndNode* const& gndNode)
  {  
    if ( gndNodeToGndEdgesMap_[(GndNode*)gndNode] == NULL) return NULL;
    Array<GndEdge*>& gndEdges = *( gndNodeToGndEdgesMap_[(GndNode*)gndNode] );
    return gndEdges[ random() % gndEdges.size() ];
  }

  string getAtomStr() const;

  ostream& print(ostream& out) const;

};
inline ostream& operator<<(ostream& out, const ClustEdge& ce) { return ce.print(out); }



class ClustEdge;
class HashClustEdge
{
public:
  size_t operator()(const ClustEdge* const& e) const { return hash<int>()(e->id()); }
};

class EqualClustEdge
{
 public:
  bool operator()(const ClustEdge* const& e1, const ClustEdge* const& e2) const { return (e1 == e2); }
};
typedef hash_set<ClustEdge*, HashClustEdge, EqualClustEdge> ClustEdgeSet;



#endif
