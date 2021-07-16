#ifndef UTIL_H_OCT_17_2005
#define UTIL_H_OCT_17_2005

#include <string>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
using namespace std;
#include "array.h"

class Util
{
 public:

  //tokenize commaSepStrs using comma as delimter, and returns strings in strs
  static void getStrings(Array<string>& strs, string commaSepStrs)
  {
    for (unsigned int i = 0; i < commaSepStrs.length(); i++)
      if (commaSepStrs.at(i) == ',') commaSepStrs.at(i) = ' ';
    commaSepStrs += " ::";
    istringstream iss(commaSepStrs);
    string buf; iss >> buf;
    while (buf.compare("::") != 0) { strs.append(buf); iss >> buf; }
  }  
	
  static bool substr(const string& pred, unsigned int& cur, string& outstr,
                     const char* const & delimiter)
  {
    outstr.clear();
    while (cur < pred.length() && isspace(pred.at(cur))) cur++;
    string::size_type dlt = pred.find(delimiter, cur);
    if (dlt == string::npos) return false;
    unsigned int cur2 = dlt-1;
    while (cur2 >= 0 && isspace(pred.at(cur2))) cur2--;
    if (cur2 < cur) return false;
    outstr = pred.substr(cur, cur2+1-cur);
    cur = dlt+1;
    return true;
  }

  static string substr(const string& str, const unsigned int& startIdx, 
                       const unsigned int& endIdxPlusOne)
  {
    return str.substr(startIdx, endIdxPlusOne-startIdx);
  }

  static string trim(const string& str)
  {
    if (str.empty()) return str;
    int lt = 0; 
    while (lt < (int)str.length() && isspace(str.at(lt))) lt++;
    int rt = str.length()-1;
    while (rt >= 0 && isspace(str.at(rt))) rt--;
    return str.substr(lt, rt+1-lt);
  }
  
  //converts an integer to a string
  static string intToString(int i) 
  {
    ostringstream myStream;
    myStream<<i;
    return myStream.str();
  }

  //converts a double to a string
  static string doubleToString(double i) 
  {
	 ostringstream myStream;
	 myStream<<i;
	 return myStream.str();
  }

  static string getLineAndTrim(ifstream& in)
  {
    string buf;
    getline(in,buf);
    return Util::trim(buf);
  }

  static void tokenize(const string& str,
                       Array<string>& tokens,
                       const string& delimiter = " ")
  {

    string::size_type lastPos = str.find_first_not_of(delimiter, 0);
    string::size_type pos     = str.find_first_of(delimiter, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
      string tok = str.substr(lastPos, pos - lastPos);
      tok = trim(tok);
      if (!tok.empty()) tokens.append(tok);
      lastPos = str.find_first_not_of(delimiter, pos);
      pos = str.find_first_of(delimiter, lastPos);
    }
  }

  static bool startsWith(const string& s1, const string& s2) 
  { return (s1.find(s2)==0); }

  static bool copyFile(const string& src, const string& dst, 
                       bool& openSrc, bool& openDst)
  {
    openSrc = true;
    openDst = true;

    ifstream in(src.c_str());  
    if (in.fail()) { openSrc = false; return false; }
    ofstream out(dst.c_str()); 
    if (out.fail()) { openDst = false; return false; }

    string buf;
    while (getline(in,buf)) out << buf << endl;
    in.close();
    out.close();
    return true;
  }

  static void sortIntArray(Array<int>& arr, const int& l, const int& r)
  {
    int* items  = (int*) arr.getItems();
  
    if (l >= r) return;

    int tmp = items[l];
    items[l] = items[(l+r)/2];
    items[(l+r)/2] = tmp;

    int last = l;
    for (int i = l+1; i <= r; i++)
    {    
      if (items[i] < items[l])
      {
        ++last;

        tmp = items[last];
        items[last] = items[i];
        items[i] = tmp;
      }
    }

    tmp = items[l];
    items[l] = items[last];
    items[last] = tmp;

    sortIntArray(arr, l, last-1);
    sortIntArray(arr, last+1, r);
  }


  static string replaceWSWithUScore(string str)
  {
    for (unsigned int i = 0; i < str.length(); i++)
      if (str.at(i) == ' ')  str.at(i) = '_';
    return str;
  }

  static string replaceWithWS(string str, const Array<char>& remChars)
  {
    for (unsigned int i = 0; i < str.length(); i++)
    {
      for (int j = 0; j < remChars.size(); j++)
        if (str.at(i) == remChars[j]) { str.at(i) = ' '; break; }
    }
    return str;
  }

  static double randDouble() { return random() / (double) RAND_MAX; }

  static int choose(const int& n, const int& r)
  {
    double nFact  = factorial(n);
    double rFact  = factorial(r);
    double nrFact = factorial(n-r);
    return (int) (nFact/(rFact*nrFact));
  }

  static double factorial(const int& n)
  {
    double f = 1;
    for (int i = 2; i <= n; i++)
      f *= n;
    return f;
  }


  ////////////////////////////////////////////////////////////////////////////
  
  static void exit(const string& m, const int& errId) 
  { 
    cout << "ERROR: " << m << endl; std::exit(-1);
  }

  static void exit(const string& m, const string& m2, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << m2 << endl; std::exit(-1);
  }

  static void exit(const string& m, const string& m2, const string& m3, 
                   const int& errId) 
  { 
    cout << "ERROR: " << m << " " << m2 << " " << m3 <<  endl; std::exit(-1);
  }


  static void exit(const string& m, const string& m2, const string& m3, 
                   const string& m4, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << m2 << " " << m3 << m4 <<  endl; std::exit(-1);
  }

  static void exit(const string& m, const double& d, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << endl; std::exit(-1);
  }

  static void exit(const string& m, const double& d, const double& d2, 
                   const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << " " << d2 << endl; std::exit(-1);
  }

  static void exit(const string& m, const double& d, const double& d2, 
                   const double& d3, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << " " << d2 << " " << d3 << endl; 
    std::exit(-1);
  }

  static void exit(const string& m, const long double& d, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << endl; std::exit(-1);
  }

  static void exit(const string& m, const long double& d, const long double& d2,
                   const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << " " << d2 << endl; std::exit(-1);
  }

  static void exit(const string& m, const long double& d, const long double& d2,
                   const double& d3, const int& errId) 
  { 
    cout << "ERROR: " << m << " " << d << " " << d2 << " " << d3 << endl; 
    std::exit(-1);
  }

  static void exit(const string& m, const int& i, const int& j,const int& errId)
  { 
    cout << "ERROR: " << m << " " << i << " " << j <<  endl; std::exit(-1);
  }

  ////////////////////////////////////////////////////////////////////////////

  static void assertt(const bool& cond, const string& m, const int& errId) 
  { if (!cond) exit(m, errId); }

  static void assertt(const bool& cond, const string& m, const string& m2, 
                   const int& errId) 
  { if (!cond) exit(m, m2, errId); }

  static void assertt(const bool& cond, const string& m, const string& m2, 
                     const string& m3, const int& errId) 
  { if (!cond) exit(m, m2, m3, errId); }

  static void assertt(const bool& cond, const string& m, const double& d, 
                     const int& errId) 
  { if (!cond) exit(m, d, errId); }

  static void assertt(const bool& cond, const string& m, const double& d, 
                     const double& d2,  const int& errId) 
  { if (!cond) exit(m, d, d2, errId); }

  static void assertt(const bool& cond, const string& m, const double& d, 
                      const double& d2,  const double& d3, const int& errId) 
  { if (!cond) exit(m, d, d2, d3, errId); }

  static void assertt(const bool& cond, const string& m, const long double& d, 
                     const int& errId) 
  { if (!cond) exit(m, d, errId); }

  static void assertt(const bool& cond, const string& m, const long double& d, 
                     const long double& d2,  const int& errId) 
  { if (!cond) exit(m, d, d2, errId); }

  static void assertt(const bool& cond, const string& m, const long double& d, 
                      const long double& d2,  const long double& d3, 
                      const int& errId) 
  { if (!cond) exit(m, d, d2, d3, errId); }


  static void assertt(const bool& cond, const string& m, const int& i, 
                     const int& j, const int& errId)
  { if (!cond) exit(m, i, j, errId); }  

  ////////////////////////////////////////////////////////////////////////////

  static void assertGoodInStream(ifstream& in, const string& inFile)
  {
    Util::assertt(!in.fail(),"failed to open", inFile, -1);
  }
  
  static void assertGoodOutStream(ofstream& out, const string& outFile)
  {
    Util::assertt(!out.fail(),"failed to open", outFile, -1);
  }
};

#endif
