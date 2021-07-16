#ifndef PARSER_H_OCT_11_2009
#define PARSER_H_OCT_11_2009

#include <fstream>
#include <ctype.h>
using namespace std;
#include "hashstring.h"
#include "rbtree.h"
#include "util.h"
#include "uutil.h"
#include "graph.h"
#include "type.h"
#include "predicate.h"

typedef hash_map<string, Type*, HashString, EqualString> StringToTypeMap;
typedef hash_map<string, Predicate*, HashString, EqualString> StringToPredMap;
typedef RBTree<ConstNode*, ConstNodeCompByName> ConstNodeTree;
typedef ConstNodeTree::RBNode ConstNodeNode;


class Parser
{
 public:
  Parser() {}
  ~Parser() {}

  void readDeclFile(const string& declFile, Array<Type*>& types, Array<Predicate*>& preds)
  {
    StringHashArray typeNames;
    StringHashArray predNames;

    ifstream in(declFile.c_str());  Util::assertGoodInStream(in, declFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;
      Util::assertt(isalpha(buf.at(0)), "expect predicate declaration to start with alpha", buf, -1);

      //create predicates
      string predName; Array<string> curTypeNames;
      UUtil::readRelArgs(buf, predName, curTypeNames);
      addPredicateAndTypes(predName, curTypeNames, predNames, typeNames, types, preds);
    }
    in.close();
    //print(cout, preds, types);
  }

  void readTypeFile(const string& typeFile, Array<string>& typeNames)
  {
    ifstream in(typeFile.c_str());  Util::assertGoodInStream(in, typeFile);
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;
      typeNames.append(buf);
    }
    cout << typeNames[0];
    in.close();
  }

  Graph* createGraph(const string& dbFile, const Array<Type*>& types, const Array<Predicate*>& foPreds, ConstNodeTree*& constNodeTree)
  {
    StringToTypeMap typeNameToTypeMap;
    for (int i = 0; i < types.size(); i++)
      typeNameToTypeMap[types[i]->name()] = types[i];

    StringToPredMap predNameToFOPredMap;
    for (int i = 0; i < foPreds.size(); i++)
      predNameToFOPredMap[foPreds[i]->name()] = foPreds[i];

    constNodeTree = new ConstNodeTree;
    createConstNodeTree(dbFile, *constNodeTree, predNameToFOPredMap, typeNameToTypeMap);

    //create the graph
    Graph* graph = new Graph();
    StringToConstNodesMap& typeToConstNodesMap = graph->typeToConstNodesMap();
    StringToPredNodesMap& predToPredNodesMap = graph->predToPredNodesMap();
    populateTypeToConstNodesMap(typeToConstNodesMap, *constNodeTree);
    populatePredToPredNodesMap(dbFile, predToPredNodesMap, *constNodeTree);
    setGraphEdges(predToPredNodesMap, *constNodeTree);
    graph->compress();
    graph->setNumNodesAndLinkProbsAndAssignNodeIds();
    //cout << *graph << endl;
    return graph;
  }

 private:
  void addPredicateAndTypes(const string& predName, const Array<string>& curTypeNames,
                            StringHashArray& predNames, StringHashArray& typeNames,
                            Array<Type*>& types, Array<Predicate*>& preds)
  {
    if (predNames.append(predName) < 0) Util::exit("duplicate predicate", predName, -1);

    Array<Constant*> args( curTypeNames.size() );
    for (int i = 0; i < curTypeNames.size(); i++)
    {
      string typeName = curTypeNames[i];
      int idx = typeNames.append(typeName);
      if (idx >= types.size()) types.append( new Type(idx, typeName) );
      else { idx = typeNames.find(typeName); }

      Type* type = types[idx];  Util::assertt(type->name().compare(typeName)==0, "diff type names", -1);
      Constant* typeConst = new Constant(idx, typeName, type);
      args.append(typeConst);
    }

    int idx = predNames.find(predName);
    Predicate* pred = new Predicate(idx, predName, args);

    preds.append(pred);  Util::assertt(preds.size()-1 == idx, "expect preds.size()-1==idx",-1);
  }

  void createConstNodeTree(const string& dbFile, ConstNodeTree& constNodeTree,
                           /*const*/ StringToPredMap& predNameToFOPredMap,
                           /*const*/ StringToTypeMap& typeNameToTypeMap)
  {
    ifstream in(dbFile.c_str());  Util::assertGoodInStream(in, dbFile);
    string buf;
    while (getline(in, buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;

      double prob = 1.0;
      if (isdigit(buf.at(0)))
      {
        string::size_type sp = buf.find(' ');  Util::assertt(sp != string::npos, "expect space after prob", -1);
        string probStr = buf.substr(0,sp);
        prob = atof(probStr.c_str());
        buf = Util::substr(buf, (unsigned int) sp+1, (unsigned int) buf.length());
        buf = Util::trim(buf);
      }

      Util::assertt(isalpha(buf.at(0)), "expect atom to start with alphabet", buf, -1);
      string predName; Array<string> args;
      UUtil::readRelArgs(buf, predName, args);

      Predicate* foPred = predNameToFOPredMap[predName];
      const Array<Constant*>& argTypes = foPred->args();
      Util::assertt(argTypes.size() == args.size(), "expect same #args", -1);

      for (int i = 0; i < args.size(); i++)
      {
        string constName = args[i];
        string typeName = argTypes[i]->name();

        Type* type = typeNameToTypeMap[typeName];
        int constId = constNodeTree.size();
        Constant* constant = new Constant(constId, constName, type);
        ConstNode* cnode = new ConstNode(constant);
        ConstNodeNode* existingNode = NULL;
        bool inserted = constNodeTree.insert(cnode, existingNode);
        if (!inserted)
        {
          if (existingNode->data()->typeId() != type->id())
            Util::exit("constant with different types ", constName, type->name(), existingNode->data()->typeName(), -1);
          delete cnode;
        }
      }
    }
    in.close();
  }

  void populateTypeToConstNodesMap(StringToConstNodesMap& typeToConstNodesMap, const ConstNodeTree& constNodeTree)
  {
    ConstNodeNode* node = constNodeTree.head();
    while (node)
    {
      ConstNode* constNode = node->data();
      string typeName = constNode->typeName();

      Array<ConstNode*>* constNodeArr;
      StringToConstNodesMap::iterator it = typeToConstNodesMap.find(typeName);
      if (it != typeToConstNodesMap.end())   constNodeArr = (*it).second;
      else                                 { constNodeArr = new Array<ConstNode*>; typeToConstNodesMap[typeName] = constNodeArr; }
      constNodeArr->append(constNode);

      node = node->next();
    }
  }

  void populatePredToPredNodesMap(const string& dbFile, StringToPredNodesMap& predToPredNodesMap,
                                  const ConstNodeTree& constNodeTree)
  {
    int predCnt = 0;

    ifstream in(dbFile.c_str());  Util::assertGoodInStream(in, dbFile);
    string buf;
    while (getline(in, buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || buf.find("//")==0) continue;

      double prob = 1.0;
      if (isdigit(buf.at(0)))
      {
        string::size_type sp = buf.find(' ');  Util::assertt(sp != string::npos, "expect space after prob", -1);
        string probStr = buf.substr(0,sp);
        prob = atof(probStr.c_str());
        buf = Util::substr(buf, (unsigned int) sp+1, (unsigned int) buf.length());
        buf = Util::trim(buf);
      }

      Util::assertt(isalpha(buf.at(0)), "expect atom to start with alphabet", buf, -1);
      string predName; Array<string> args;
      UUtil::readRelArgs(buf, predName, args);

      Array<Constant*> constants( args.size() );
      addConstantsToArr(constants, args, constNodeTree);

      //ASSUMPTION: dbFile does not have duplicate atoms

      Array<PredNode*>* gndPredsArr;
      StringToPredNodesMap::iterator it = predToPredNodesMap.find(predName);
      if (it != predToPredNodesMap.end())   gndPredsArr = (*it).second;
      else                                { gndPredsArr = new Array<PredNode*>; predToPredNodesMap[predName] = gndPredsArr; }

      Predicate* gndPred = new Predicate(predCnt++, predName, constants);
      gndPredsArr->append(new PredNode(gndPred, prob));
    }
    in.close();
  }

  void addConstantsToArr(Array<Constant*>& constants, const Array<string>& args, const ConstNodeTree& constNodeTree)
  {
    for (int i = 0; i < args.size(); i++)
    {
      string constName = args[i];
      ConstNode* constNode = getConstNode(constName, constNodeTree);
      constants.append(constNode->constant());
    }
  }

  ConstNode* getConstNode(const string& constName, const ConstNodeTree& constNodeTree)
  {
    static Constant tmpConstant;
    static ConstNode tmpConstNode;
    tmpConstant.setName(constName);
    tmpConstNode.setConstant(&tmpConstant);
    ConstNode* foundConstNode = NULL;
    bool found = constNodeTree.find(&tmpConstNode, foundConstNode);
    Util::assertt(found && foundConstNode, "constant not found", constName, -1);
    tmpConstNode.setConstant(NULL); //present deletion error
    return foundConstNode;
  }

  void setGraphEdges(const StringToPredNodesMap& predToPredNodesMap, const ConstNodeTree& constNodeTree)
  {
    //create mapping from pred name to id
    int cnt = 0;
    StringToIntMap predNameToIdMap;
    StringToPredNodesMap::const_iterator pit;
    for (pit = predToPredNodesMap.begin(); pit != predToPredNodesMap.end(); pit++)
      predNameToIdMap[ (*pit).first ] = cnt++;

    //link constant nodes
    for (pit = predToPredNodesMap.begin(); pit != predToPredNodesMap.end(); pit++)
    {
      string predName = (*pit).first;
      int predId = predNameToIdMap[predName];

      Array<PredNode*>& predNodes = *( (*pit).second );
      for (int i = 0; i < predNodes.size(); i++) //for each predNode
      {
        PredNode* predNode = predNodes[i];
        double prob = predNode->prob();
        const Array<Constant*>& args = predNode->args();
        Array<ConstNode*> constNodes( args.size() );
        for (int j = 0; j < args.size(); j++)
        {
          string constName = args[j]->name();
          ConstNode* constNode = getConstNode(constName, constNodeTree);
          constNodes.append(constNode);
          constNode->addPredNode(predNode);
        }

        for (int j = 0; j < constNodes.size(); j++)
          for (int k = 0; k < constNodes.size(); k++)
            if (k != j) constNodes[j]->addOutLink( new OutLink(constNodes[k], prob/(constNodes.size()-1), predId) );
      }
    }
  }

  void print(ostream& out, const Array<Predicate*>& preds, const Array<Type*>& types)
  {
    out << "-------- PREDICATES ---------" << endl;
    for (int i = 0; i < preds.size(); i++)
      out << i << ": " << *preds[i] << endl;

    out << "-------- TYPES ---------" << endl;
    for (int i = 0; i < types.size(); i++)
      out << i << ": " << *types[i] << endl;
  }
};




#endif














































