#ifndef PATH_H_OCT_23_2009
#define PATH_H_OCT_23_2009

#include "hashstring.h"
#include "atom.h"

class Path
{
 private:
  Atom** atoms_; //array of atoms
  int    numAtoms_;
  int    hashCode_;
  int    support_;
  StringHashArray* supportIdStrs_;

  int         numRel_;
  Array<int>* relIdToCntMap_;
  Array<IntHashArray>* typeIdToConstsMap_;

 public:
  Path(Atom** const& atoms, const int& numAtoms) : atoms_(atoms), numAtoms_(numAtoms), support_(0), supportIdStrs_(NULL),
                                                   numRel_(0), relIdToCntMap_(NULL), typeIdToConstsMap_(NULL)
  {
    hashCode_ = 1;
    for (int i = 0; i < numAtoms_; i++)
      hashCode_ = 31*hashCode_ + atoms_[i]->hashCode();
  }

  ~Path()
  {
    for (int i = 0; i < numAtoms_; i++) delete atoms_[i];
    delete [] atoms_; delete supportIdStrs_; delete relIdToCntMap_; delete typeIdToConstsMap_;
  
  }

  Atom** atoms()    const { return atoms_;    }
  int    numAtoms() const { return numAtoms_; }
  int    hashCode() const { return hashCode_; }
  int    support()  const { return support_;  }
  void   incrSupport()                  { support_++; }
  void   addSupport(const int& support) { support_ += support; }
  void   setSupport(const int& support) { support_ = support; }
  Atom*  atom(const int& idx) const { return atoms_[idx]; }
  
  void   addSupportIdStr(const string& idStr) { if (supportIdStrs_==NULL) supportIdStrs_ = new StringHashArray; supportIdStrs_->append(idStr); }
  void   addSupportIdStr(const StringHashArray& idStrs) 
  { 
    if (supportIdStrs_==NULL) supportIdStrs_ = new StringHashArray; 
    for (int i = 0; i < idStrs.size(); i++)
      supportIdStrs_->append(idStrs[i]); 
  }

  StringHashArray* supportIdStrs() const { return supportIdStrs_; }

  int computeHashCode()
  {
    hashCode_ = 1;
    for (int i = 0; i < numAtoms_; i++)
      hashCode_ = 31*hashCode_ + atoms_[i]->computeHashCode();
    return hashCode_;
  }

  Path* copy() const
  {
    Atom** atoms = new Atom*[numAtoms_];
    for (int i = 0; i < numAtoms_; i++)
      atoms[i] = atoms_[i]->copy();
    Path* path = new Path(atoms, numAtoms_);
    path->setSupport(support_);
    return path;
  }

  void deleteAtoms() { for (int i = 0; i < numAtoms_; i++) delete atoms_[i]; }

  static Array<int>* getConstIdToNumAppearMap(Atom** const& atoms, const int& numAtoms)
  {
    Array<int>* constIdToNumAppearMap = new Array<int>(100);
    for (int i = 0; i < numAtoms; i++)
    {
      Atom* atom = atoms[i];
      int numConstIds = atom->numConstIds();
      for (int j = 0; j < numConstIds; j++)
      {
        int constId = atom->constId(j);
        if (constIdToNumAppearMap->size() < constId+1) { constIdToNumAppearMap->growToSize(constId+1,0); }
        (*constIdToNumAppearMap)[constId]++;
      }
    }
    return constIdToNumAppearMap;
  }

  static void sortAtoms(Atom** const& atoms, const int& l, const int& r, const Array<int>& constIdToNumAppearMap)
  {
    if (l >= r) return;
    Atom** items = atoms;

    Atom* tmp = items[l];  items[l] = items[(l+r)/2];  items[(l+r)/2] = tmp;

    int last = l;
    for (int i = l+1; i <= r; i++)
    {
      Atom* iatom = items[i];
      Atom* latom = items[l];

      int cmp = 0;
      if      (iatom->relId() < latom->relId())  cmp = -1;
      else if (iatom->relId() > latom->relId())  cmp =  1;
      else
      {
        for (int c = 0; c < iatom->numConstIds(); c++)
        {
          int iconstId = iatom->constId(c);
          int lconstId = latom->constId(c);
          int iNumAppear = constIdToNumAppearMap[iconstId];
          int lNumAppear = constIdToNumAppearMap[lconstId];
          if      (iNumAppear > lNumAppear) cmp = -1;
          else if (iNumAppear < lNumAppear) cmp =  1;
          else if (iconstId   < lconstId)   cmp = -1;
          else if (iconstId   > lconstId)   cmp =  1;
          if (cmp != 0) break;
        }
      }

      if (cmp < 0) { ++last; tmp = items[last]; items[last] = items[i]; items[i] = tmp; }
    }

    tmp = items[l];  items[l] = items[last];  items[last] = tmp;
    sortAtoms(atoms, l, last-1, constIdToNumAppearMap);
    sortAtoms(atoms, last+1, r, constIdToNumAppearMap);
  }

  bool equal(const Path& other)
  {
    if (this == &other) return true;
    if (numAtoms_ != other.numAtoms_) return false;
    for (int i = 0; i < numAtoms_; i++)
      if (!atoms_[i]->equal(*(other.atom(i)))) return false;
    return true;
  }

  ostream& print(ostream& out) const
  {
    for (int i = 0; i < numAtoms_; i++)    
      out << *atoms_[i] << " ";
    out << endl;
    return out;
  }


  int getNumRel() const { return numRel_; }

  Array<int>* getRelIdToCntMap(const int& maxRelId)
  {
    if (relIdToCntMap_) return relIdToCntMap_;
    relIdToCntMap_ = new Array<int>;
    relIdToCntMap_->growToSize(maxRelId+1,0);
    for (int i = 0; i < numAtoms_; i++)
      (*relIdToCntMap_)[ atoms_[i]->relId() ]++;

    numRel_ = 0;
    for (int i = 0; i < relIdToCntMap_->size(); i++)
      if ((*relIdToCntMap_)[i] > 0) numRel_++;

    return relIdToCntMap_;
  }

  Array<IntHashArray>* getTypeIdToConstsMap(const int& maxTypeId, const Array<Array<int>*>& relIdToTypeIdsMap)
  {
    if (typeIdToConstsMap_) return typeIdToConstsMap_;
    typeIdToConstsMap_ = new Array<IntHashArray>;
    typeIdToConstsMap_->growToSize(maxTypeId+1);
 
    for (int i = 0; i < numAtoms_; i++)
    {
      int relId       = atoms_[i]->relId();
      int numConstIds = atoms_[i]->numConstIds();
      int* constIds   = atoms_[i]->constIds();
      Array<int>* typeIds = relIdToTypeIdsMap[relId];  Util::assertt(typeIds->size() == numConstIds, "expect same #typeId,#constIds",-1);
      for (int t = 0; t < typeIds->size(); t++)
        (*typeIdToConstsMap_)[ (*typeIds)[t] ].append( constIds[t] );
    }

    return typeIdToConstsMap_;
  }
};

inline ostream& operator<<(ostream& out, const Path& p) { return p.print(out); }


int comparePathsBySupport(const void* p0, const void* p1)
{
  return ((*(Path**)p1)->support() - (*(Path**)p0)->support());
}

int comparePathsByLen(const void* p0, const void* p1)
{
  return ((*(Path**)p1)->numAtoms() - (*(Path**)p0)->numAtoms());
}

class HashPath
{
 public:
  size_t operator()(Path* const& p) const { return hash<int>()(p->hashCode()); }
};

class EqualPath
{
 public:
  bool operator()(Path* const& p0, Path* const& p1) const { return p0->equal(*p1); }
};

typedef hash_set<Path*, HashPath, EqualPath> PathSet;




#endif
