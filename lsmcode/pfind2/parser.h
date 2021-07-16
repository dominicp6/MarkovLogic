#ifndef PARSER_H_OCT_23_2009
#define PARSER_H_OCT_23_2009

#include <sstream>
#include "util.h"

class Parser
{
 public:
  static bool readCommunityDB(ifstream& in, Array<string>& db, int& numComs, int& comId, Array<string>& supComArr)
  {
    db.clear();
    string buf;
    while (getline(in,buf))
    {
      buf = Util::trim(buf);
      if (buf.empty() || Util::startsWith(buf, "//")) continue;
      if (Util::startsWith(buf, "#START_DB"))
      {
        buf.append(" #");
        istringstream iss(buf); string noop; iss >> noop >> comId >> noop >> numComs >> noop >> noop >> noop;

        supComArr.clear();
        string comStr = "";
        while (true)
        {
          iss >> comStr;
          if (comStr.compare("#") == 0) break;
          supComArr.append(comStr);
        }

        buf = Util::getLineAndTrim(in);
        while (!Util::startsWith(buf, "#END_DB"))
        {
          db.append(buf);
          buf = Util::getLineAndTrim(in);
        }
        return true;
      }
      else if (Util::startsWith(buf, "#END_GRAPH"))
        return false;
    }
    return false;
  }
};


#endif
