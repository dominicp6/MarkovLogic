#ifndef NODECLUSTER_H_OCT_11_2009
#define NODECLUSTER_H_OCT_11_2009

#include <climits>
#include "node.h"

class NodeCluster
{
 private:
  Array<Node*>* nodes_;
  SamplePathSet samplePathSet_;
  int topN_; //number of top sample paths to keep

 public:
  NodeCluster(Node* const& node, const int& topN) : nodes_(new Array<Node*>(20)), topN_(topN)
  {
    nodes_->append(node);
    initSamplePathSet(*node->samplePathSet()); //get the topN sample paths
    node->deleteSamplePathSet();
  }

  ~NodeCluster()
  {
    delete nodes_;
    Array<SamplePath*> delPaths( samplePathSet_.size() );
    for (SamplePathSet::iterator it = samplePathSet_.begin(); it != samplePathSet_.end(); it++)
      delPaths.append(*it);
    delPaths.deleteItemsAndClear();
  }

  const Array<Node*>   nodes()         const { return *nodes_; }
  const SamplePathSet& samplePathSet() const { return samplePathSet_; }

  void merge(NodeCluster& other)
  {
    nodes_->append(other.nodes());

    //insert paths which are in otherPaths but not in current node's path, into latter's path
    const SamplePathSet& otherPaths = other.samplePathSet();
    for (SamplePathSet::const_iterator it = otherPaths.begin(); it != otherPaths.end(); it++)
    {
      SamplePath* path = *it;
      if (samplePathSet_.find(path) == samplePathSet_.end()) //other path is not among cur node's paths
      {
        SamplePath* newPath = new SamplePath(*path);
        newPath->setProb(0.0);
        samplePathSet_.insert(newPath);
      }
    }

    //take the average probability, for each path
    double totalProb = 0.0;
    for (SamplePathSet::iterator it = samplePathSet_.begin(); it != samplePathSet_.end(); it++)
    {
      SamplePath* path = *it;
      SamplePathSet::const_iterator itt = otherPaths.find(path);
      if (itt == otherPaths.end()) path->setProb( path->prob()/2.0 );
      else                         path->setProb( (path->prob()+(*itt)->prob())/2.0 );
      totalProb += path->prob();
    }

    if ((int)samplePathSet_.size() > topN_)
    {
      Array<SamplePath*> topPaths(topN_);
      getTopPaths(topPaths, samplePathSet_);

      SamplePathSet tmpPathSet(topN_);
      for (int i = 0; i < topPaths.size(); i++)
        tmpPathSet.insert( topPaths[i] );

      Array<SamplePath*> remPaths(topN_);
      for (SamplePathSet::iterator it = samplePathSet_.begin();  it != samplePathSet_.end(); it++)
        if (tmpPathSet.find(*it) == tmpPathSet.end()) remPaths.append(*it);

      tmpPathSet.clear();

      for (int i = 0; i < remPaths.size(); i++)
      {
        SamplePathSet::iterator it = samplePathSet_.find(remPaths[i]);
        SamplePath* path = *it;
        totalProb -= path->prob();
        samplePathSet_.erase(it);
        delete path;
      }
    }

    //renormalize prob
    for (SamplePathSet::iterator it = samplePathSet_.begin(); it != samplePathSet_.end(); it++)
      (*it)->setProb( (*it)->prob()/totalProb );
  }

  double jsDiv(NodeCluster& other)
  {
    SamplePathSet avePathSet(topN_*2);
    for (SamplePathSet::iterator it = samplePathSet_.begin(); it != samplePathSet_.end(); it++)
      avePathSet.insert( new SamplePath(*(*it)) ) ;

    const SamplePathSet& otherPathSet = other.samplePathSet();
    for (SamplePathSet::const_iterator it = otherPathSet.begin(); it != otherPathSet.end(); it++)
    {
      SamplePath* path = *it;
      SamplePathSet::iterator itt = avePathSet.find(path);
      if (itt != avePathSet.end()) (*itt)->setProb( ((*itt)->prob()+path->prob())/2.0 );
      else                         { SamplePath* newPath = new SamplePath(*path); newPath->setProb(newPath->prob()/2.0); avePathSet.insert(newPath); }
    }

    double klDiv0 = klDiv(samplePathSet_, avePathSet);
    double klDiv1 = klDiv(otherPathSet,   avePathSet);
    double js = (klDiv0 + klDiv1)/2.0;

    Array<SamplePath*> delPaths(avePathSet.size());
    for (SamplePathSet::iterator it = avePathSet.begin(); it != avePathSet.end(); it++)
      delPaths.append(*it);
    delPaths.deleteItemsAndClear();

    return js;
  }

 private:
  void initSamplePathSet(SamplePathSet& samplePathSet)
  {
    Array<SamplePath*> topPaths(topN_);
    getTopPaths(topPaths,samplePathSet);

    double totalCount = 0;
    for (int i = 0; i < topPaths.size(); i++)
    {
      SamplePath* sp = new SamplePath(*topPaths[i]);
      samplePathSet_.insert(sp);
      totalCount += sp->count();
    }

    for (SamplePathSet::iterator it = samplePathSet_.begin(); it != samplePathSet_.end(); it++)
      (*it)->setProb( (*it)->count()/totalCount );
  }

  void getTopPaths(Array<SamplePath*>& topPaths, SamplePathSet& samplePathSet)
  {
    for (SamplePathSet::iterator it = samplePathSet.begin(); it != samplePathSet.end(); it++)
    {
      SamplePath* path = *it;

      if (topPaths.size() < topN_) topPaths.append(path);
      else
      {
        double smallestCnt = DBL_MAX;
        int smallestCntIdx = INT_MAX;
        for (int i = 0; i < topPaths.size(); i++)
        {
          if (path->count() > topPaths[i]->count() && topPaths[i]->count() < smallestCnt)
          {
            smallestCnt = topPaths[i]->count();
            smallestCntIdx = i;
          }
        }

        if (smallestCntIdx < topPaths.size())
          topPaths[smallestCntIdx] = path;
      }
    }
  }

  double klDiv(const SamplePathSet& pathSet, SamplePathSet& avePathSet)
  {
    double div = 0.0;
    for (SamplePathSet::const_iterator it = pathSet.begin(); it != pathSet.end(); it++)
    {
      SamplePath* path = *it;
      SamplePathSet::iterator itt = avePathSet.find(path);
      SamplePath* avePath = *itt;

      double prob = path->prob();
      double aveProb = avePath->prob();

      div += prob * log(prob/aveProb);
    }
    return div;
  }

};


#endif
