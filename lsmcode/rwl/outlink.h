#ifndef OUTLINK_H_OCT_11_2009
#define OUTLINK_H_OCT_11_2009

class Node;

class OutLink
{
 private:
  Node*  toNode_;
  double prob_;
  int    relId_;

 public:
  OutLink(Node* toNode, const double& prob, const int& relId) : toNode_(toNode), prob_(prob), relId_(relId) {}
  ~OutLink() {}

  Node*  toNode() const           { return toNode_; }
  double prob()   const           { return prob_; }
  void   setProb(const double& p) { prob_ = p; }
  int    relId()  const           { return relId_; }
  void   setRelId(const int& rid) { relId_ = rid; }
};

int compareOutLinkByProb(const void * l0, const void * l1)
{
  if ((*(OutLink**)l0)->prob() < (*(OutLink**)l1)->prob()) return -1;
  if ((*(OutLink**)l0)->prob() > (*(OutLink**)l1)->prob()) return  1;
  return 0;
}

int compareOutLinkByRelId(const void * l0, const void * l1)
{
  if ((*(OutLink**)l0)->relId() < (*(OutLink**)l1)->relId()) return -1;
  if ((*(OutLink**)l0)->relId() > (*(OutLink**)l1)->relId()) return  1;
  return 0;
}

#endif
