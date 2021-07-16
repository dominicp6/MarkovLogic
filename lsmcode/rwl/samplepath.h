#ifndef SAMPLEPATH_H_OCT_11_2009
#define SAMPLEPATH_H_OCT_11_2009

#include <ext/hash_set>
using namespace __gnu_cxx;


class SamplePath
{
 private:
  int*   path_;
  int    len_;
  int    hashCode_;
  double count_;

 public:
  SamplePath(int* const& path, const int& len, const double& count) : path_(path), len_(len), count_(count) { setHashCode(); }

  SamplePath(const SamplePath& other)
  {
    int* otherPath = other.path();
    len_ = other.len();
    path_ = new int[len_];
    for (int i = 0; i < len_; i++)
      path_[i] = otherPath[i];
    count_ = other.count();
    setHashCode();
  }

  ~SamplePath() { delete [] path_; }

  void setHashCode()
  {
    hashCode_ = 1;
    for (int i = 0; i < len_; i++)
      hashCode_ = 31*hashCode_ + path_[i];
  }

  int*    path()     const { return path_;  }
  int     len()      const { return len_;   }
  int     hashCode() const { return hashCode_; }
  double  count()    const { return count_; }
  double  prob()     const { return count_; }
  int     path(const int& i) const { return path_[i]; }
  void    incrCount()      { count_ += 1.0; }
  void    setProb(const double& p) { count_ = p; }

  ostream& print(ostream& out) const
  {
    out << count_ << " |";
    for (int i = 0; i < len_; i++)
      out << " " << path_[i];
    out << endl;
    return out;
  }

  bool equal(const SamplePath& other)
  {
    if (this == & other) return true;
    if (len_ != other.len()) return false;
    for (int i = 0; i < len_; i++)
      if (path_[i] != other.path(i)) return false;
    return true;
  }
};

inline ostream& operator <<(ostream& out, const SamplePath& sp) { return sp.print(out); }

class HashSamplePath
{
 public:
  size_t operator()(SamplePath* const& p) const { return p->hashCode(); }
};

class EqualSamplePath
{
 public:
  bool operator()(SamplePath* const& p0, SamplePath* const& p1) const { return p0->equal(*p1); }
};

typedef hash_set<SamplePath*, HashSamplePath, EqualSamplePath> SamplePathSet;


#endif
