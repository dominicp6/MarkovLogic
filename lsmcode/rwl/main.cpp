#include <cstdlib>
#include <iostream>
using namespace std;
#include "rwlearner.h"

int main(int argc, char* argv[])
{
  if (argc != 15+1)
  {
    cout << "usage: " << argv[0] << " <declarationFile> <dbFile> <typeFile> <numSamples> <maxLen> <delta> <eps> <timeThresh> <mergeTimeThresh> <jsThresh> <jsTopN> <seed> <outFile> <unmergedOutFile> <outSrcAndClustsFile>" << endl;
    cout << "dbFile should not have duplicate atoms" << endl;
    exit(-1);
  }
  string declFile   = argv[1];
  string dbFile     = argv[2];
  string typeFile   = argv[3];
  int    numSamples = atoi(argv[4]);
  int    maxLen     = atoi(argv[5]);
  double delta      = atof(argv[6]);
  double eps        = atof(argv[7]);
  double timeThresh = atof(argv[8]);
  double mergeThr   = atof(argv[9]);
  double jsThresh   = atof(argv[10]);
  int    jsTopN     = atoi(argv[11]);
  int    seed       = atoi(argv[12]);
  string outFile    = argv[13];
  string unmergedOutFile = argv[14];
  string outSrcAndClustsFile =argv[15];
  //*/

  srandom(seed);


  cout << "--------------- PARAMS -----------------" << endl;
  cout << "declFile   = " << declFile   << endl;
  cout << "dbFile     = " << dbFile     << endl;
  cout << "typeFile   = " << typeFile   << endl;
  cout << "numSamples = " << numSamples << endl;
  cout << "maxLen     = " << maxLen     << endl;
  cout << "delta      = " << delta      << endl;
  cout << "eps        = " << eps        << endl;
  cout << "timeThresh = " << timeThresh << endl;
  cout << "mergeThr   = " << mergeThr   << endl;
  cout << "jsThresh   = " << jsThresh   << endl;
  cout << "jsTopN     = " << jsTopN     << endl;
  cout << "seed       = " << seed       << endl;
  cout << "outFile    = " << outFile    << endl;
  cout << "unmergedOutFile = " << unmergedOutFile << endl;
  cout << "outSrcAndClustsFile = " << outSrcAndClustsFile << endl;
  cout << "----------------------------------------" << endl;

  Timer timer;
  double startSec = timer.time();

  RWLearner rwl(declFile, dbFile, typeFile, numSamples, maxLen, delta, eps, timeThresh, mergeThr, jsThresh, jsTopN, outFile, unmergedOutFile, outSrcAndClustsFile);
  rwl.run();

  cout << "TOTAL TIME TAKEN = "; timer.printTime(cout, timer.time()-startSec); cout << endl;
  return 1;
}
