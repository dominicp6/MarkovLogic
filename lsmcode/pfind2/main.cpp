#include <cstdlib>
#include <iostream>
using namespace std;
#include "timer.h"
#include "pathfinder.h"
#include "parser.h"

int main(int argc, char* argv[])
{
  if (argc != 7+1)
  {
    cout << "usage: " << argv[0] << " <ldbFile> <maxLen> <maxFreeVar> <maxVar> <hrLimit> <declFile> <outFile>" << endl;
    exit(-1);
  }
  string ldbFile    = argv[1];
  int    maxLen     = atoi(argv[2]);
  int    maxFreeVar = atoi(argv[3]);
  int    maxVar     = atoi(argv[4]);
  double hrLimit    = atof(argv[5]); //neg: no limit
  string declFile   = argv[6];
  string outFile    = argv[7];
  //*/

  cout << "--------------- PARAMS -----------------" << endl;
  cout << "ldbFile    = " << ldbFile    << endl;
  cout << "maxLen     = " << maxLen     << endl;
  cout << "maxFreeVar = " << maxFreeVar << endl;
  cout << "maxVar     = " << maxVar     << endl;
  cout << "hrLimit    = " << hrLimit    << endl;
  cout << "declFile   = " << declFile   << endl;
  cout << "outFile    = " << outFile    << endl;
  cout << "----------------------------------------" << endl;

  Timer timer;
  double startSec = timer.time();

  PathFinder pfinder(maxLen, maxFreeVar, maxVar, hrLimit, ldbFile, declFile, outFile);  //cout << pfinder << endl << endl;
  pfinder.run();

  cout << "TOTAL TIME "; timer.printTime(cout, timer.time()-startSec); cout << endl;
  return 1;
}
