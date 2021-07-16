#include <cstdlib>
#include <iostream>
#include <unistd.h>
#include <sys/time.h>
using namespace std;
#include "mlncreator.h"

int main(int argc, char* argv[])
{
  if (argc != 23+1 && argc != 24+1)
  {
    cout << "usage: " << argv[0] << " <candFile> <minSup> <dbFiles> <combLDBFile> <unmergedLDBFiles> <declFile> <learnWtsExec> <tmpDir> <fractAtoms> "
         << "<lenPenalty> <quickLenPenalty> <numFlips> <maxLen> <minAtoms> <maxAtoms> <numQuickPruneDBs> <outMLN> <seed> <trivialBinFile> <symRelFile> "
         << "<cfAllSub> <cora> <noQuickPrune> [secLimit]" << endl;
    cout << "#args " << argc-1 << endl;
    exit(-1);
  }
  string candFile        = argv[1];
  int    minSup          = atoi(argv[2]);
  string dbFiles         = argv[3];
  string combLDBFile     = argv[4];
  string unmergeLDBFiles = argv[5];
  string declFile        = argv[6];
  string learnWtsExec    = argv[7];
  string tmpDir          = argv[8];
  double fractAtoms      = atof(argv[9]);
  double lenPenalty      = atof(argv[10]);
  double quickLenPenalty = atof(argv[11]);
  int    numFlips        = atoi(argv[12]);
  int    maxLen          = atoi(argv[13]);
  int    minAtoms        = atoi(argv[14]);
  int    maxAtoms        = atoi(argv[15]);
  int    numQuickPruneDBs= atoi(argv[16]);
  string outMLN          = argv[17];
  int    seed            = atoi(argv[18]);
  string trivialBinFile  = argv[19];
  string symRelFile      = argv[20];
  bool   cfAllSub        = (strcmp(argv[21],"true")==0)?true:false;
  bool   cora            = (strcmp(argv[22],"true")==0)?true:false;
  bool   noQuickPrune    = (strcmp(argv[23],"true")==0)?true:false;

  double secLimit = -1;
  if (argc == 24+1) secLimit = atof(argv[24]);
  //*/


  if (trivialBinFile.compare("-") == 0) trivialBinFile = "";
  if (symRelFile.compare("-") == 0)     symRelFile = "";

  cout << "--------------- PARAMS --------------"  << endl;
  cout << "candFile        = " << candFile         << endl;
  cout << "minSup          = " << minSup           << endl;
  cout << "dbFiles         = " << dbFiles          << endl; 
  cout << "combLDBFile     = " << combLDBFile      << endl;
  cout << "unmergeLDBFiles = " << unmergeLDBFiles  << endl;
  cout << "declFile        = " << declFile         << endl;
  cout << "learnWtsExec    = " << learnWtsExec     << endl;
  cout << "tmpDir          = " << tmpDir           << endl;
  cout << "fractAtoms      = " << fractAtoms       << endl;
  cout << "lenPenalty      = " << lenPenalty       << endl;
  cout << "quickLenPenalty = " << quickLenPenalty  << endl;
  cout << "numFlips        = " << numFlips         << endl;
  cout << "maxLen          = " << maxLen           << endl;
  cout << "minAtoms        = " << minAtoms         << endl;
  cout << "maxAtoms        = " << maxAtoms         << endl;
  cout << "numQuickPruneDBs= " << numQuickPruneDBs << endl;
  cout << "outMLN          = " << outMLN           << endl;
  cout << "seed            = " << seed             << endl;
  cout << "trivialBinFile  = " << trivialBinFile   << endl;
  cout << "symRelFile      = " << symRelFile       << endl;
  cout << "cfAllSub        = " << (cfAllSub?"true":"false")     << endl;
  cout << "cora            = " << (cora?"true":"false")         << endl;
  cout << "noQuickPrune    = " << (noQuickPrune?"true":"false") << endl;
  cout << "secLimit        = " << secLimit         << endl;
  cout << "-------------------------------------"  << endl;

  struct timeval tvA; struct timezone tzpA;
  gettimeofday(&tvA,&tzpA);

  MLNCreator mc(candFile, minSup, dbFiles, combLDBFile, unmergeLDBFiles, declFile, learnWtsExec, tmpDir, fractAtoms, lenPenalty, quickLenPenalty, numFlips, maxLen,
                minAtoms, maxAtoms, numQuickPruneDBs, outMLN, seed, trivialBinFile, symRelFile, cfAllSub, cora, noQuickPrune, secLimit);
  mc.run();

  struct timeval tvB; struct timezone tzpB;
  gettimeofday(&tvB,&tzpB);
  cout << "TOTAL TIME "; Timer::printTime(cout, tvB.tv_sec-tvA.tv_sec); cout << endl;

  return 1;
}
