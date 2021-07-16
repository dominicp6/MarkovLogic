#ifndef COMGNDER_H_OCT_23_2009
#define COMGNDER_H_OCT_23_2009

#include "util.h"
#include "path.h"
#include "hashint.h"

struct CAtom
{
  CAtom(const int& relId, const int& numVarIds, int* const& varIds) : relId_(relId), numVarIds_(numVarIds), varIds_(varIds) {}
  ~CAtom() { delete [] varIds_; }
  int relId_;
  int numVarIds_;
  int* varIds_;
};


class ComGnder
{
 private:
  Array< Array<CAtom*> > relIdToAtoms_; //database
  Array<Array<int*> > varIdToVarPos_;
  Array<CAtom*> atoms_;
  bool enforceVarDiff_;

  Array<bool> constIdGnded_;
  int maxConstId_;
  const Array<string>* relIdToNameMap_;


 public:
  ComGnder(const Path* const& path, const Path* const& dbPath, const int& maxRelId, const bool& enforceVarDiff, const Array<string>* const& relIdToNameMap)
    : enforceVarDiff_(enforceVarDiff), maxConstId_(-1), relIdToNameMap_(relIdToNameMap)
  {
    init(path);
    createRelIdToAtoms(dbPath, maxRelId); //create constIdGnded_ too
  }

  ~ComGnder()
  {
    atoms_.deleteItemsAndClear();
    for (int r = 0; r < relIdToAtoms_.size(); r++)
      relIdToAtoms_[r].deleteItemsAndClear();
  }

  bool hasTrueGnding() { return hasTrueGnding(0); }

 private:
  bool hasTrueGnding(const int& atomPos)
  {
    CAtom* atom = atoms_[atomPos];
   
    //store all the var/const ids of the atom
    int  numVarIds = atom->numVarIds_;
    int* varIds    = atom->varIds_;
    Array<int> initialVarIds(numVarIds);
    for (int i = 0; i < numVarIds; i++)
      initialVarIds.append( varIds[i] );

    Array<CAtom*> candAtoms;
    getCandAtoms(candAtoms, atom);

    //for each atom that can ground atoms_[atomPos]
    for (int i = 0; i < candAtoms.size(); i++)
    {
      IntHashArray constIdUsed;
      gndAtom(initialVarIds, varIds, candAtoms[i], constIdUsed);
      
      if (atomPos == atoms_.size()-1) return true;
      if (hasTrueGnding(atomPos+1))   return true;

      for (int j = 0; j < constIdUsed.size(); j++)
        constIdGnded_[ constIdUsed[j] ] = false;
    }

    //restore initial varIds;
    for (int i = 0; i < initialVarIds.size(); i++)
    {
      int initVarId = initialVarIds[i];
      if (initVarId < 0) //if a variable
      {
        Array<int*>& varPos = varIdToVarPos_[-initVarId-1];
        for (int k = 0; k < varPos.size(); k++)
          *(varPos[k]) = initVarId;
      }
    }

    return false;
  }

  void gndAtom(const Array<int>& initialVarIds, int*const& varIds, CAtom* const& candAtom, IntHashArray& constIdUsed)
  {
    int  cnumVarIds = candAtom->numVarIds_;
    int* cvarIds    = candAtom->varIds_;
    int  numVarIds  = initialVarIds.size();
    Util::assertt(cnumVarIds = numVarIds, "expect cnumVarIds == numVarIds, " + Util::intToString(cnumVarIds) + " " + Util::intToString(numVarIds), -1);

    for (int j = 0; j < cnumVarIds; j++)
    {
      int varId  = initialVarIds[j];
      int cvarId = cvarIds[j];
      if (varId >= 0) //if constant
      {
        Util::assertt( cvarId == varId, "expect cvarId == varId, " + Util::intToString(cvarId) + " " + Util::intToString(varId), -1);
      }
      else //is a variable
      {
        Array<int*>& varPos = varIdToVarPos_[ -varId-1 ];
        for (int k = 0; k < varPos.size(); k++)
          *(varPos[k]) = cvarId;
        Util::assertt(varIds[j] == cvarId, "expect gnded varId = cvarId, " + Util::intToString(varIds[j]) + " " + Util::intToString(cvarId), -1);
        
        if (enforceVarDiff_) { constIdGnded_[cvarId] = true; constIdUsed.append(cvarId); }
      }
    }
  }

  void getCandAtoms(Array<CAtom*>& candAtoms, CAtom* const& atom)
  {
    Array<CAtom*>& allAtoms = relIdToAtoms_[atom->relId_];
    for (int i = 0; i < allAtoms.size(); i++)
    {
      CAtom* curAtom = allAtoms[i];

      Array<int> constIdToVarId; //for curAtom
      if (enforceVarDiff_) constIdToVarId.growToSize( maxConstId_+1, 0 );

      int  numVarIds = atom->numVarIds_;
      int* varIds    = atom->varIds_;
      int  curNumVarIds = curAtom->numVarIds_;
      int* curVarIds    = curAtom->varIds_;
      Util::assertt(numVarIds == curNumVarIds, "expect same numVarIds", -1);

      //check whether atom can be gnded as curAtom
      bool gdCand = true;
      for (int j = 0; j < numVarIds; j++)
      {
        int id  = varIds[j];
        int cid = curVarIds[j];
        if (id >= 0) //if constant
        {
          if (id != cid) { gdCand = false; break; }
        }
        else
        {
          //is variable
          if (enforceVarDiff_)
          {
            //if used by prior atoms or diff variable in current atom
            if ( (constIdGnded_[ cid ])  || (constIdToVarId[cid] < 0 && constIdToVarId[cid] != id) ) { gdCand = false; break; } 
            constIdToVarId[cid] = id;
          }
        }
      }
      
      if (gdCand) candAtoms.append(curAtom);
    }
  }

  //createVarIdToVarPos and atoms_
  void init(const Path* const& path)
  {
    Atom** atoms = path->atoms();
    int numAtoms = path->numAtoms();

    //find the max var id
    int maxVarId = -1;
    for (int i = 0; i < numAtoms; i++)
    {
      int* varIds    = atoms[i]->constIds();
      int  numVarIds = atoms[i]->numConstIds();
      for (int j = 0; j < numVarIds; j++)
        if (varIds[j]> maxVarId) maxVarId = varIds[j];
    }
    varIdToVarPos_.growToSize(maxVarId+1);

    //store positions of varIds and create atoms
    atoms_.growToSize(numAtoms,NULL);
    for (int i = 0; i < numAtoms; i++)
    {
      int  relId     = atoms[i]->relId();
      int* varIds    = atoms[i]->constIds();
      int  numVarIds = atoms[i]->numConstIds();
      int* newVarIds = new int[numVarIds];
      for (int j = 0; j < numVarIds; j++)
      {
        newVarIds[j]= -varIds[j]-1;
        varIdToVarPos_[ varIds[j] ].append( &(newVarIds[j]) );
      }
      atoms_[i] = new CAtom(relId, numVarIds, newVarIds);
    }
  }

  void  createRelIdToAtoms(const Path* const& dbPath, const int& maxRelId)
  {
    relIdToAtoms_.growToSize(maxRelId+1);
    maxConstId_ = -1;

    Atom** atoms = dbPath->atoms();
    int numAtoms = dbPath->numAtoms();
    for (int i = 0; i < numAtoms; i++)
    {
      int  relId       = atoms[i]->relId();
      int* constIds    = atoms[i]->constIds();
      int  numConstIds = atoms[i]->numConstIds();

      int* cids = new int[numConstIds];
      for (int j = 0; j < numConstIds; j++)
      {
        cids[j] = constIds[j];   Util::assertt(constIds[j]>=0, "expect +ve constant id, " + Util::intToString(constIds[j]), -1);
        if (constIds[j] > maxConstId_)  maxConstId_ = constIds[j];
      }

      CAtom* atom = new CAtom(relId, numConstIds, cids);
      relIdToAtoms_[relId].append( atom );
    }
    
    constIdGnded_.growToSize(maxConstId_+1, false);
  }

};






#endif
