#ifndef UUTIL_H_OCT_11_2009
#define UUTIL_H_OCT_11_2009

#include <cstdlib>
#include <string>
#include "win.h"
#include "array.h"
#include "util.h"

class UUtil
{
 public:
  static void readRelArgs(string str, string& relStr, Array<string>& argStrs)
  {
    string::size_type ltparen = str.find("(");
    assert(ltparen != string::npos);
    relStr = Util::trim( str.substr(0, ltparen) );
    int i = ltparen+1;
    while (true)
    {
      string::size_type comma = str.find(",",i);
      if (comma == string::npos) break;
      string argStr = Util::trim( str.substr(i, comma-i) );
      argStrs.append(argStr);
      i = comma+1;
    }
    string::size_type rtparen = str.find(")",i);
    assert(rtparen != string::npos);
    string argStr = Util::trim( str.substr(i, rtparen-i) );
    argStrs.append(argStr);
  }

  static double randDouble() { return random() / (double) RAND_MAX; }

};


#endif
