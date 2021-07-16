#ifndef NODE_H_OCT_11_2009
#define NODE_H_OCT_11_2009

#include <ext/hash_set>
#include <ext/hash_map>
using namespace __gnu_cxx;
#include <cstdlib>
using namespace std;
#include "util.h"
#include "hashint.h"
#include "uutil.h"
#include "array.h"
#include "constant.h"
#include "predicate.h"
#include "outlink.h"
#include "samplepath.h"

const bool   ADD_SMALL_PROB_BREAK_SYM = false;
const double MIN_RAND_PROB = 0.005;
const double MAX_RAND_PROB = 0.01;


struct ProbRange
{
  double lower_;
  double upper_;
  ProbRange(const double& l, const double& u) : lower_(l), upper_(u) {}
};

class Node
{
 public:
  enum NodeType { NONE = 0, CONSTANT = 1, PREDICATE = 3 };

 protected:
  Array<OutLink*>   outLinks_;
  Array<ProbRange*> probRanges_;
  int    id_;
  int    startNodeId_;
  int    sampleId_;
  double accHitTime_;
  int    numHits_;
  double hitTime_;
  bool   uniform_; //uniformly select outlink
  SamplePathSet* samplePathSet_;

 public:
  Node() : id_(-1), startNodeId_(-1), sampleId_(-1), accHitTime_(0.0), numHits_(0), hitTime_(-1.0),  uniform_(false), samplePathSet_(NULL) {};
  virtual ~Node()
  {
    outLinks_.deleteItemsAndClear();
    probRanges_.deleteItemsAndClear();
    deleteSamplePathSet();
  }

  void deleteSamplePathSet()
  {
    if (samplePathSet_ == NULL) return;
    Array<SamplePath*> delPaths( samplePathSet_->size() );
    for (SamplePathSet::iterator it = samplePathSet_->begin(); it != samplePathSet_->end(); it++)
      delPaths.append(*it);
    delPaths.deleteItemsAndClear();
    delete samplePathSet_;
    samplePathSet_ = NULL;
  }

  SamplePathSet* samplePathSet() const  { return samplePathSet_; }

  int    id() const                     { return id_; }
  void   setId(const int& id)           { id_ = id; }
  int    startNodeId() const            { return startNodeId_; }
  void   setStartNodeId(const int& id)  { startNodeId_ = id; }
  int    sampleId() const               { return sampleId_; }
  void   setSampleId(const int& id)     { sampleId_ = id; }
  double accHitTime() const             { return accHitTime_; }
  void   setAccHitTime(const double& t) { accHitTime_ = t; }
  void   addAccHitTime(const double& t) { accHitTime_ += t; }
  int    numHits() const                { return numHits_; }
  void   setNumHits(const int& h)       { numHits_ = h; }
  void   incrNumHits()                  { numHits_++; }
  double hitTime() const                { return hitTime_; }
  void   setHitTime(const double& t)    { hitTime_ = t; }
  void   computeHitTime(const int& numSamples, const int& maxLen)
  {
    hitTime_ = (accHitTime_ + (numSamples-numHits_)*maxLen)/numSamples;
    Util::assertt(0 < numHits_ && numHits_ <= numSamples, "expect 0 < numHits && numHits_ <= numSamples, " + Util::intToString(numHits_), -1);
  }
  bool   uniform() const                { return uniform_; }
  bool   determineUniform()
  {
    uniform_ = true;
    for (int i = 1; i < outLinks_.size(); i++)
      if (outLinks_[i]->prob() != outLinks_[i-1]->prob()) { uniform_ = false; break; }
    return uniform_;
  }

  int numOutLinks() const { return outLinks_.size(); }
  const Array<OutLink*>& outLinks() const { return outLinks_; }
  void  addOutLink(OutLink* l) { outLinks_.append(l); }
  void compressOutLinks() { outLinks_.compress(); }
  void clearOutLinks() { outLinks_.deleteItemsAndClear(); }
  virtual void setOutLinkProbs()
  {
    if (ADD_SMALL_PROB_BREAK_SYM)
    {
      normalizeOutLinkProbs();

      //sort outlinks by prob
      qsort((void*)outLinks_.getItems(), outLinks_.size(), sizeof(OutLink*), compareOutLinkByProb);

      //randomly add small prob to outLinks with diff relId
      Array<OutLink*> sameProbLinks(10);
      sameProbLinks.append(outLinks_[0]);
      for (int i = 1; i < outLinks_.size()+1; i++)
      {
        if (i == outLinks_.size()  || outLinks_[i]->prob() != outLinks_[i-1]->prob())
        {
          if (sameProbLinks.size() > 1)
          {
            //sort outlinks by rel id
            qsort((void*)sameProbLinks.getItems(), sameProbLinks.size(), sizeof(OutLink*), compareOutLinkByRelId);
            randAddProbs(sameProbLinks);
          }
          sameProbLinks.clear();
        }
        if (i < outLinks_.size()) sameProbLinks.append( outLinks_[i] );
      }

      normalizeOutLinkProbs();
      determineUniform();
      if (!uniform_) setProbRanges();
    }
    else
    {
      determineUniform();
      if (!uniform_) { normalizeOutLinkProbs();  setProbRanges(); }
    }
  }

  static double randSmallProb() { return random()/(double)RAND_MAX  * (MAX_RAND_PROB-MIN_RAND_PROB) + MIN_RAND_PROB; }

  OutLink* randomOutLink()
  {
    if (uniform_) return randomOutLinkUniform();
    return randomOutLinkNonUniform();
  }

  OutLink* randomOutLinkUniform()
  { 
    if (outLinks_.empty()) return NULL;
    return outLinks_[ random() % outLinks_.size() ]; 
  }

  OutLink* randomOutLinkNonUniform()
  {
    if (outLinks_.empty()) return NULL;
    if (outLinks_.size() == 1) return outLinks_[0];
    double val = UUtil::randDouble();
    int mid = -1;
    int min = 0;
    int max = outLinks_.size()-1;
    do
    {
      mid = (int)((min + max)/ 2.0);
      if      (val >  probRanges_[mid]->upper_)  min = mid + 1;
      else if (val <= probRanges_[mid]->lower_)  max = mid - 1;
    }
    while ((val <= probRanges_[mid]->lower_ || val > probRanges_[mid]->upper_) && (min <= max));
    return outLinks_[mid];
  }

  void addSamplePath(Array<int>& path)
  {
    if (samplePathSet_ == NULL) samplePathSet_ = new SamplePathSet;
    int* copyPath = new int[path.size()];
    for (int i = 0; i < path.size(); i++) copyPath[i] = path[i];
    SamplePath* samplePath = new SamplePath(copyPath, path.size(), 1.0);
    pair<SamplePathSet::iterator,bool> pr = samplePathSet_->insert(samplePath);
    if (!pr.second) { (*(pr.first))->incrCount(); delete samplePath; }
  }

  void printSamplePathSet(ostream& out) const
  {
    if (samplePathSet_ == NULL) return;
    for (SamplePathSet::iterator it = samplePathSet_->begin(); it != samplePathSet_->end(); it++)
      out << *(*it) << endl;
  }

  virtual NodeType nodeType() const { return NONE; }
  virtual string strRep() const { return "NODE_STR_REP"; }

 protected:
  void normalizeOutLinkProbs()
  {
    double sumProb = 0.0;
    for (int i = 0; i < outLinks_.size(); i++)
      sumProb += outLinks_[i]->prob();
    for (int i = 0; i < outLinks_.size(); i++)
      outLinks_[i]->setProb( outLinks_[i]->prob()/sumProb );
  }

  void randAddProbs(const Array<OutLink*>& sameProbLinks)
  {
    Array<OutLink*> sameRelIdLinks;
    sameRelIdLinks.append( sameProbLinks[0] );
    for (int i = 1; i < sameProbLinks.size()+1; i++)
    {
      if (i == sameProbLinks.size() || sameProbLinks[i]->relId() != sameProbLinks[i-1]->relId())
      {
        if (sameRelIdLinks.size() < sameProbLinks.size() )
        {
          double probChange = Node::randSmallProb();
          for (int j = 0; j < sameRelIdLinks.size(); j++)
            sameRelIdLinks[j]->setProb( sameRelIdLinks[j]->prob() + probChange );
        }
        sameRelIdLinks.clear();
      }
      if (i < sameProbLinks.size()) sameRelIdLinks.append(sameProbLinks[i]);
    }
  }

  void setProbRanges()
  {
    probRanges_.clear();
    probRanges_.growToSize( outLinks_.size() );
    double sum = 0.0;
    for (int i = 0; i < outLinks_.size(); i++)
    {
      double prevSum = sum;
      sum += outLinks_[i]->prob();
      probRanges_[i] = new ProbRange(prevSum, sum);
    }
  }
};

class PredNode : public Node
{
 private:
  Predicate* predicate_;
  double prob_;

 public:
  PredNode(Predicate* pred, const double& prob) : Node(), predicate_(pred), prob_(prob) {}
  virtual ~PredNode() { delete predicate_; }

  virtual NodeType nodeType() const { return PREDICATE; }
  Predicate* predicate() const      { return predicate_; }

  const Array<Constant*>& args() const { return predicate_->args(); }

  double prob() const { return prob_; }
  void setProb(const double& p) { prob_ = p; }

  virtual string strRep() const
  {
    string strRep = Util::doubleToString(prob_) + " " + predicate_->name() + "(";
    const Array<Constant*>& args = predicate_->args();
    for (int j = 0; j < args.size(); j++)
      strRep += args[j]->name() + ((j < args.size()-1)?",":")");
    return strRep;
  }
};

class ConstNode : public Node
{
 private:
  Constant* constant_;
  Array<PredNode*> predNodes_; //ground predicates that constant appears in

 public:
  ConstNode() : Node(), constant_(NULL) {}
  ConstNode(Constant* constant) : Node(), constant_(constant) {}
  virtual ~ConstNode() { delete constant_; }

  virtual NodeType nodeType() const { return CONSTANT; }
  Constant* constant() const        { return constant_; }
  void setConstant(Constant* c)     { constant_ = c; }

  string name() const { return constant_->name(); }

  Type* type() const { return constant_->type(); }
  int typeId() const { return constant_->typeId(); }
  string typeName() const { return constant_->typeName(); }

  const Array<PredNode*>& predNodes()  const { return predNodes_; }
  void addPredNode(PredNode* const& predNode) { predNodes_.append(predNode); }
  void compressPredNodes() { predNodes_.compress(); }

  virtual string strRep() const { return name(); }
};

class ConstNodeComp
{
 public:
  static int compare(const ConstNode* const& n0, const ConstNode* const& n1)
  {
    Constant* c0 = n0->constant();
    Constant* c1 = n1->constant();
    if (c0 == c1) return 0;
    if (c0->id() > c1->id()) return  1;
    if (c0->id() < c1->id()) return -1;
    return 0;
  }
};

class ConstNodeCompByName
{
 public:
  static int compare(const ConstNode* const& n0, const ConstNode* const& n1)
  {
    Constant* c0 = n0->constant();
    Constant* c1 = n1->constant();
    if (c0 == c1) return 0;
    return c0->name().compare(c1->name());
  }
};

class HashNode
{
 public:
  size_t operator()(Node* const& n) const { return hash<int>()(n->id()); }
};

class EqualNode
{
 public:
  bool operator()(Node* const& n0, Node* const& n1) const { return (n0->id() == n1->id()); }
};

typedef hash_set<Node*, HashNode, EqualNode> NodeSet;

int compareNodeHitTime(const void * n0, const void * n1)
{
  if ((*(Node**)n0)->hitTime() < (*(Node**)n1)->hitTime()) return -1;
  if ((*(Node**)n0)->hitTime() > (*(Node**)n1)->hitTime()) return  1;
  return 0;
}

int compareNodeId(const void * n0, const void * n1)
{
  if ((*(Node**)n0)->id() < (*(Node**)n1)->id()) return -1;
  if ((*(Node**)n0)->id() > (*(Node**)n1)->id()) return  1;
  return 0;
}

int compareNodeConstId(const void * n0, const void * n1)
{
  if ((*(ConstNode**)n0)->constant()->id() < (*(ConstNode**)n1)->constant()->id()) return -1;
  if ((*(ConstNode**)n0)->constant()->id() > (*(ConstNode**)n1)->constant()->id()) return  1;
  return 0;
}


#endif
