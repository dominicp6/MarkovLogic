#ifndef GRAPH_H_OCT_23_2009
#define GRAPH_H_OCT_23_2009

#include <list>
using namespace std;
#include <cstdlib>
#include "uuutil.h"
#include "gndnode.h"
#include "gndedge.h"
#include "clustnode.h"
#include "clustedge.h"
#include "nodeids.h"

//////////////////////// Graph ///////////////////////////
typedef hash_map<string, GndNode*,      HashString, EqualString> StringToGndNodeMap;
typedef hash_map<string, ClustNode*,    HashString, EqualString> StringToClustNodeMap;
typedef hash_map<string, ClustEdgeSet*, HashString, EqualString> StringToClustEdgeSetMap;

struct EdgePair
{
  EdgePair(ClustEdge* const& E, GndEdge* const& e) : E_(E), e_(e) {}
  ClustEdge* E_;
  GndEdge*   e_;
};

class Graph
{
 private:
  int srcId_;
  Array<ClustEdge*> clustEdges_;
  StringToClustNodeMap nodeNameToClustNodeMap_; //maps a clustered or single node to clustNode representing it
  StringToGndNodeMap   nodeNameToGndNodeMap_;

 public:
  Graph(const Array<string>& clustAtoms, const Array<string>& gndAtoms, const int& srcId,
        const Array<int>& singleNodeIds, const Array<Array<int>*>& clustIdToNodeIds) : srcId_(srcId)
  {
    for (int i = 0; i < clustAtoms.size(); i++)
      createClustEdgeAndClustNodes(clustAtoms[i]);
    createGndNodes(singleNodeIds, clustIdToNodeIds); //and map clustNode <-> gndNodes
    createGndEdges(gndAtoms); //and map clustEdge -> gndEdge
    for (int i = 0; i < clustEdges_.size(); i++)
      clustEdges_[i]->createGndNodeToGndEdgesMap();
  }

  ~Graph()
  {
    for (StringToClustNodeMap::const_iterator it = nodeNameToClustNodeMap_.begin(); it != nodeNameToClustNodeMap_.end(); it++)
      delete (*it).second;
    for (StringToGndNodeMap::const_iterator it = nodeNameToGndNodeMap_.begin(); it != nodeNameToGndNodeMap_.end(); it++)
      delete (*it).second;
    clustEdges_.deleteItemsAndClear();
  }

  bool extractCom(Array<GndEdge*>& E1, Array<GndNode*>& V1)
  {
    //Array<GndEdge*> E1; //E'
    //Array<GndNode*> V1; //V'

    list<EdgePair*> queue;

    for (int i = 0; i < clustEdges_.size(); i++)
      clustEdges_[i]->setVisited(false);

    if (clustEdges_.size() == 0)  return false;
    ClustEdge* E_i = clustEdges_[ random() % clustEdges_.size() ];
    const Array<GndEdge*>& gndEdges = E_i->gndEdges();
    if (gndEdges.size() == 0)  return false;
    GndEdge* e_i = gndEdges[ random() % gndEdges.size() ];
    queue.push_back( new EdgePair(E_i, e_i) );
    E_i->setVisited(true);
    while (!queue.empty())
    {
      EdgePair* edgePair = queue.front();  queue.pop_front();
      //ClustEdge* E = edgePair->E_; cout << "  POP  " << E << "  " << E->visited() << "  " << *E << endl;

      GndEdge*   e = edgePair->e_;
      delete edgePair;
      //E->setVisited(true);
      E1.append(e);
      
      const Array<GndNode*>& gndNodes = e->gndNodes();
      for (int i = 0; i < gndNodes.size(); i++)
      {
        GndNode* v = gndNodes[i];
        V1.append(v);
        ClustNode* V_v = v->clustNode();
        const ClustEdgeSet& clustEdgeSet = V_v->clustEdges();
        for (ClustEdgeSet::iterator it = clustEdgeSet.begin(); it != clustEdgeSet.end(); it++)
        {
          ClustEdge* E_j =  (*it);
          if (!E_j->visited())
          {
            //cout << "v = " << *v << endl;
            //cout << "PUSH  " << E_j->getAtomStr() << "  " << E_j << "  " << E_j->visited() << endl;

            GndEdge* e_j = E_j->getGndEdge(v);
            if (e_j) queue.push_back( new EdgePair(E_j, e_j) ); //get a com that this gnded com supports
            E_j->setVisited(true);
            
            /*
            GndEdge* e_j = E_j->getGndEdge(v);
            if (e_j == NULL) //bad approximation of symmetrical nodes, ignore this graph
            { 
              E1.clear(); 
              for (list<EdgePair*>::iterator it = queue.begin(); it != queue.end(); it++)  delete (*it);
              return false; 
            } 
            queue.push_back( new EdgePair(E_j, e_j) );
            E_j->setVisited(true);
            */
          }
        }
      }
    }
    return true;
  }

  ostream& print(ostream& out) const
  {
    out << "------------------ CLUST NODE -----------------------" << endl;
    for (StringToClustNodeMap::const_iterator it = nodeNameToClustNodeMap_.begin(); it != nodeNameToClustNodeMap_.end(); it++)
    {
      string nodeName = (*it).first;
      ClustNode* clustNode = (*it).second;
      out << "  " << nodeName << " " << clustNode << endl;
      out << *clustNode << endl;
    }

    out << "------------------- GND NODE ------------------------" << endl;
    for (StringToGndNodeMap::const_iterator it = nodeNameToGndNodeMap_.begin(); it != nodeNameToGndNodeMap_.end(); it++)
    {
      string nodeName = (*it).first;
      GndNode* gndNode = (*it).second;
      out << "  " << nodeName << endl;
      out << *gndNode << endl;
    }

    out << "------------------- CLUST EDGES ------------------------" << endl;
    for (int i = 0; i < clustEdges_.size(); i++)
      out << *clustEdges_[i] << endl << endl;

    return out;
  }


 private:
  void createClustEdgeAndClustNodes(const string& clustAtom)
  {
    string relName; Array<string> args;
    UUUtil::readRelArgs(clustAtom, relName, args);

    //get the clustNodes that args correspond to
    cout <<  "ClustEdge: " + relName + " "; //! Dom edit
    Array<ClustNode*> clustNodes;
    for (int j = 0; j < args.size(); j++)
    {
      ClustNode* clustNode;
      string clustNodeName = args[j];
      StringToClustNodeMap::iterator itt = nodeNameToClustNodeMap_.find( clustNodeName );
      if (itt == nodeNameToClustNodeMap_.end()) { clustNode = new ClustNode(clustNodeName);
                                                  nodeNameToClustNodeMap_[ clustNodeName ] = clustNode; }
      else                                      { clustNode = (*itt).second; }
      clustNodes.append(clustNode);
      cout << clustNodeName + ","; //! Dom edit
    }

    cout << "\n"; //! Dom edit

    ClustEdge* clustEdge = new ClustEdge(relName, clustNodes);
    clustEdges_.append(clustEdge);
    for (int j = 0; j < clustNodes.size(); j++)
      clustNodes[j]->addClustEdge(clustEdge);

  }

  void createGndNodes(const Array<int>& singleNodeIds, const Array<Array<int>*>& clustIdToNodeIds)
  {
    for (int i = 0; i < singleNodeIds.size(); i++)
    {
      string nodeName = "NODE_" + Util::intToString( singleNodeIds[i] );
      StringToClustNodeMap::iterator it = nodeNameToClustNodeMap_.find(nodeName);  
      if (it == nodeNameToClustNodeMap_.end()) continue;    
      GndNode* gndNode = new GndNode(nodeName);
      ClustNode* clustNode = (*it).second;
      clustNode->addGndNode(gndNode);
      gndNode->setClustNode(clustNode);
      StringToGndNodeMap::iterator itt = nodeNameToGndNodeMap_.find(nodeName);  Util::assertt(itt == nodeNameToGndNodeMap_.end(), "don't expect " + nodeName, -1);
      nodeNameToGndNodeMap_[nodeName] = gndNode;
    }

    for (int i = 0; i < clustIdToNodeIds.size(); i++)
    {
      string nodeName = "CLUST_" + Util::intToString(i);
      StringToClustNodeMap::iterator it = nodeNameToClustNodeMap_.find(nodeName);  
      
      //Util::assertt(it != nodeNameToClustNodeMap_.end(), nodeName + " not found B", -1);
      if (it == nodeNameToClustNodeMap_.end()) continue;
      
      ClustNode* clustNode = (*it).second;

      Array<int>& nodeIds = *( clustIdToNodeIds[i] );
      for (int j = 0; j < nodeIds.size(); j++)
      {
        int nodeId = nodeIds[j];
        string nodeName = "NODE_" + Util::intToString(nodeId);
        GndNode* gndNode = new GndNode(nodeName);
        clustNode->addGndNode(gndNode);
        gndNode->setClustNode(clustNode);
        StringToGndNodeMap::iterator it = nodeNameToGndNodeMap_.find(nodeName);  Util::assertt(it == nodeNameToGndNodeMap_.end(), "don't expect " + nodeName, -1);
        nodeNameToGndNodeMap_[nodeName] = gndNode;
        cout << "nn2gnm " + nodeName + "\n";
      }
    }
  }

  void createGndEdges(const Array<string>& gndAtoms)
  {
    //create map from set of clustNodes to clustEdge
    StringToClustEdgeSetMap nodeNamesToClustEdgesMap;
    createNodeNamesToClustEdgesMap( nodeNamesToClustEdgesMap );

    for (int i = 0; i < gndAtoms.size(); i++)
    {
      string relName; Array<string> argStrs;
      UUUtil::readRelArgs(gndAtoms[i], relName, argStrs);

      Array<GndNode*> gndNodes( argStrs.size() );
      string nodeNames = "";
      for (int j = 0; j < argStrs.size(); j++)
      {
        cout << "Node Name: " + argStrs[j] + "\n"; //!Dom edit
        GndNode* gndNode = nodeNameToGndNodeMap_[ argStrs[j] ];  Util::assertt(gndNode != NULL,   "gndNode == NULL for "   + argStrs[j], -1);
        ClustNode* clustNode = gndNode->clustNode();             Util::assertt(clustNode != NULL, "clustNode == NULL for " + argStrs[j], -1);
        nodeNames += clustNode->name() + "+";
        gndNodes.append(gndNode);
      }

      GndEdge* gndEdge = new GndEdge(relName,gndNodes);
      cout << nodeNames + '\n'; //! Dom edit
      ClustEdgeSet* clustEdgeSet = nodeNamesToClustEdgesMap[ nodeNames ];  Util::assertt(clustEdgeSet != NULL, "clustEdgeSet == NULL", -1);

      //NOTE: can speed this up in the future by indexing the clustEdges by relName
      ClustEdge* clustEdge = NULL;
      for (ClustEdgeSet::iterator it = clustEdgeSet->begin(); it != clustEdgeSet->end(); it++)
        if (relName.compare( (*it)->relName() ) == 0) { clustEdge = (*it); break; }
      Util::assertt(clustEdge != NULL, "clustEdge == NULL", -1);

      clustEdge->addGndEdge(gndEdge);
    }

    for (StringToClustEdgeSetMap::iterator it = nodeNamesToClustEdgesMap.begin(); it != nodeNamesToClustEdgesMap.end(); it++)
      delete (*it).second;
  }

  void createNodeNamesToClustEdgesMap(StringToClustEdgeSetMap& nodeNamesToClustEdgesMap)
  {
    for (int i = 0; i < clustEdges_.size(); i++)
    {
      ClustEdge* clustEdge = clustEdges_[i];
      const Array<ClustNode*>& clustNodes = clustEdge->clustNodes();
      string nodeNames = "";
      for (int j = 0; j < clustNodes.size(); j++)
        nodeNames += clustNodes[j]->name() + "+";

      ClustEdgeSet* clustEdgeSet;
      StringToClustEdgeSetMap::iterator it = nodeNamesToClustEdgesMap.find( nodeNames );
      if (it == nodeNamesToClustEdgesMap.end()) { clustEdgeSet = new ClustEdgeSet; nodeNamesToClustEdgesMap[nodeNames] = clustEdgeSet; }
      else                                      { clustEdgeSet = (*it).second; }

      clustEdgeSet->insert(clustEdge);
    }
  }



};
inline ostream& operator<<(ostream& out, const Graph& g) { return g.print(out); }

#endif
