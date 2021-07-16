#ifndef ATOM_H_OCT_23_2009
#define ATOM_H_OCT_23_2009

class Atom
{
 private:
  int    relId_;
  int*   constIds_;
  int    numConstIds_;
  int    hashCode_;
  Atom** linkToAtoms_;
  int    numLinkToAtoms_;

 public:
  Atom(const int& relId, const Array<int>& constIds) : relId_(relId), linkToAtoms_(NULL), numLinkToAtoms_(0)
  {
    numConstIds_ = constIds.size();
    constIds_ = new int[numConstIds_];
    for (int i = 0; i < numConstIds_; i++)
      constIds_[i] = constIds[i];

    hashCode_ = relId_;
    for (int i = 0; i < numConstIds_; i++)
      hashCode_ = 31*hashCode_ + constIds_[i];
  }

  Atom(const int& relId, int* const& constIds, const int& numConstIds) : relId_(relId), numConstIds_(numConstIds), linkToAtoms_(NULL), numLinkToAtoms_(0)
  {
    constIds_ = new int[numConstIds_];
    for (int i = 0; i < numConstIds_; i++)
      constIds_[i] = constIds[i];

    hashCode_ = relId_;
    for (int i = 0; i < numConstIds_; i++)
      hashCode_ = 31*hashCode_ + constIds_[i];
  }

  ~Atom() { delete [] constIds_;  delete [] linkToAtoms_; }

  int  relId()       const { return relId_;    }
  int* constIds()    const { return constIds_; }
  int  numConstIds() const { return numConstIds_; }
  int  hashCode()    const { return hashCode_; }
  int  constId(const int& idx) { return constIds_[idx]; }
  void setConstId(const int& idx, const int& constId) { constIds_[idx] = constId; }

  int computeHashCode()
  {
    hashCode_ = relId_;
    for (int i = 0; i < numConstIds_; i++)
      hashCode_ = 31*hashCode_ + constIds_[i];
    return hashCode_;
  }

  void   setLinkToAtoms(Atom** const& linkToAtoms) { linkToAtoms_ = linkToAtoms; }
  Atom** linkToAtoms() const             { return linkToAtoms_; }
  void   setNumLinkToAtoms(const int& n) { numLinkToAtoms_ = n; }
  int    numLinkToAtoms() const          { return numLinkToAtoms_; }

  Atom* copy() const { return new Atom(relId_, constIds_, numConstIds_); }

  bool equal(const Atom& atom)
  {
    if (this == &atom) return true;
    if (relId_ != atom.relId()) return false;
    Util::assertt(numConstIds_ == atom.numConstIds(), "expect same num constIds", -1); 

    int* otherConstIds = atom.constIds();
    for (int i = 0; i < numConstIds_; i++)
      if (constIds_[i] != otherConstIds[i]) return false;
    return true;
  }

  ostream& print(ostream& out) const 
  {
    out << relId_ << "(" << constIds_[0];
    for (int i = 1; i < numConstIds_; i++)
      out << "," << constIds_[i];
    out << ")" << endl;
    return out;
  }

};

inline ostream& operator<<(ostream& out, const Atom& a) { return a.print(out); }

class HashAtom
{
 public:
  size_t operator()(Atom* const& a) const { return hash<int>()(a->hashCode()); }
};

class EqualAtom
{
 public:
  bool operator()(Atom* const& a0, Atom* const& a1) const { return a0->equal(*a1); }
};

typedef hash_set<Atom*, HashAtom, EqualAtom> AtomSet;

int compareAtoms(const void * a0, const void * a1)
{
  Atom* atom0 = (*(Atom**)a0);
  Atom* atom1 = (*(Atom**)a1);

  if (atom0->relId() < atom1->relId()) return -1;
  if (atom0->relId() > atom1->relId()) return  1;
  Util::assertt(atom0->numConstIds() == atom1->numConstIds(), "expect same num of constants", -1);

  if (atom0->numConstIds() == 2)
  {
    int numSame0 = 0, numSame1 = 0;
    if (atom0->constId(0) == atom0->constId(1)) numSame0 = 1;
    if (atom1->constId(0) == atom1->constId(1)) numSame1 = 1;
    if (numSame0 > numSame1) return -1;
    if (numSame0 < numSame1) return  1;
  }

  for (int i = 0; i < atom0->numConstIds(); i++)
  {
    if (atom0->constId(i) < atom1->constId(i)) return -1;
    if (atom0->constId(i) > atom1->constId(i)) return  1;
  }
  return 0;
}



#endif
