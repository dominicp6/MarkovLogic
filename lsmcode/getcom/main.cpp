#include <cstring>
#include "graph.h"
#include "comcreator.h"

int main(int argc, char* argv[])
{
  if (argc != 9+1)
  {
    cout << "usage: " << argv[0] << " <comma-delimited ldbFiles> <comma-delimited uldbFiles> <comma-delimited srcClustsFiles> <inDeclFile> <minSup> <outLDBFile> <learnwtsExec> <mergePaths> <seed>" << endl;
    exit(-1);
  }
  string ldbFiles       = argv[1];
  string uldbFiles      = argv[2];
  string srcClustsFiles = argv[3];
  string declFile       = argv[4];
  int    minSup         = atoi(argv[5]);
  string outFile        = argv[6];
  string learnWtsExec   = argv[7];
  bool   mergePaths     = (strcmp(argv[8],"true")==0);
  int    seed           = atoi(argv[9]);
  //*/


  cout << "------------------ PARAMETERS ---------------" << endl;
  cout << "ldFiles        = " << ldbFiles       << endl;
  cout << "uldbFiles      = " << uldbFiles      << endl;
  cout << "srcClustsFiles = " << srcClustsFiles << endl;
  cout << "declFile       = " << declFile       << endl;
  cout << "minSup         = " << minSup         << endl;
  cout << "outFile        = " << outFile        << endl;
  cout << "learnWtsExec   = " << learnWtsExec   << endl;
  cout << "mergePaths     = " << (mergePaths?"true":"false") << endl;
  cout << "seed           = " << seed           << endl;
  cout << "---------------------------------------------" << endl;


  Array<string> ldbFilesArr, uldbFilesArr, srcClustsFilesArr;
  Util::getStrings(ldbFilesArr, ldbFiles);
  Util::getStrings(uldbFilesArr, uldbFiles);
  Util::getStrings(srcClustsFilesArr, srcClustsFiles);
  srandom(seed);

  ComCreator comCreator(ldbFilesArr, uldbFilesArr, srcClustsFilesArr, declFile, minSup, outFile, learnWtsExec, mergePaths);
  comCreator.createComs();

  return 1;
}
