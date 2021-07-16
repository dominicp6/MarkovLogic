#ifndef AUCCLL_H_NOV_08_2008
#define AUCCLL_H_NOV_08_2008

struct PrecThreshs 
{ 
  PrecThreshs() : prec(0) {}
  PrecThreshs(double pprec) : prec(pprec) {}
  double prec; Array<double> threshs; 
};

class AucCll
{
 public:
  //prob: array of prob that atom is true
  //cls:  actual class of atom (0/1)
  static void prob2auc(Array<double>& prob, Array<int>& cls,
                       double& retauc, double& retstddev,
                       const int& numThresholds=100)
  {
    prob2auc(prob, cls, retauc, retstddev, false, "", numThresholds);
  }

  static void prob2auc(Array<double>& prob, Array<int>& cls,
                       double& retauc, double& retstddev,
                       const bool& printFValues, const string& fValueFile,
                       const int& numThresholds)
  {
    //istream *in = &cin;
    //Array<double> prob;
    //Array<int> cls;
    //readData(*in, prob, cls);

    Array<PrecThreshs> precision;
    
    //fix number of intervals to compute precision, recall
    getPrecisions(prob, cls, numThresholds, precision);
    
    //get all possible precision-recall by considering every interval between
    //probabilities
    //getPrecisions2(prob, cls, numThresholds, precision);
    
    
    Array<double> weight;
    getWeights(precision, weight);
    
    Array<double> fs;
    getFs(prob, cls, precision, weight, fs);
    
    double auc = 0;
    double stddev = 0;
    if (fs.size() > 0)
    {
      double sum = 0;
      for (int i = 0; i < fs.size(); i++)
      {
        sum += fs[i];
        //cout << fs[i] << endl;
      }
      auc = sum/fs.size();
      
      double sumfja2 = 0;
      for (int i = 0; i < fs.size(); i++)
        sumfja2 += (fs[i]-auc)*(fs[i]-auc);
      sumfja2 /= fs.size()-1;
      stddev = sqrt(sumfja2)/sqrt(fs.size());
    }
    //cout << "AUC = " << auc << "  " << stddev << endl;
    retauc = auc; 
    retstddev = stddev;


    if (printFValues)
    {
      int numPos = 0;
      for (int i = 0; i < cls.size(); i++)
        if (cls[i] == 1) numPos++;

      Util::assertt(numPos == fs.size(), "expect #F_i's == numPos", -1);

      ofstream out(fValueFile.c_str());
      Util::assertt(!out.fail(), "failed to open", fValueFile, -1);
      for (int i = 0; i < fs.size(); i++)
        out << fs[i] << endl;
      out.close();
    }
  }

 private:
  AucCll() {}
  ~AucCll() {}
  
 private:
  //////////////////////// compute all possible prec and recall by ///////////
  //////////////////////// considering all intervals b/w probs ///////////////
  static
  void sort(const int& l, const int& r, Array<double>& prob, Array<int>& cls)
  {
    if (l >= r) return;
    double tmpProb = prob[l];
    int    tmpCls  = cls[l];
    
    prob[l] = prob[(l+r)/2];
    prob[(l+r)/2] = tmpProb;
    cls[l] = cls[(l+r)/2];
    cls[(l+r)/2] = tmpCls;
    
    int last = l;
    for (int i = l+1; i <= r; i++)
    {
      if (prob[i] < prob[l])
      {
        ++last;
        tmpProb = prob[last];
        prob[last] = prob[i];
        prob[i] = tmpProb;
        tmpCls = cls[last];
        cls[last] = cls[i];
        cls[i] = tmpCls;      
      }
    }
    
    tmpProb = prob[l];
    prob[l] = prob[last];
    prob[last] = tmpProb;
    tmpCls = cls[l];
    cls[l] = cls[last];
    cls[last] = tmpCls;
    
    sort(l, last-1, prob, cls);
  sort(last+1, r, prob, cls);  
  }

  static void getPrecisions2(Array<double>& prob, Array<int>& cls, 
                             int numThresholds, Array<PrecThreshs>& precision)
  {
    sort(0, prob.size()-1, prob, cls);
    
    Array<double> thresh(prob.size()+1);
    thresh.append((0.0+prob[0])/2);
    for (int i = 0; i < prob.size()-1; i++)
      thresh.append( (prob[i]+prob[i+1])/2 );
    thresh.append((prob.lastItem() + 1)/2);
    
    //double stepSize = 1.0/numThresholds;
    //numThresholds++;
    
    assert(prob.size() == cls.size());
    int numData = prob.size();
    
    precision.clear();
    precision.append(PrecThreshs(0.0));
    precision[0].threshs.append(0.0); //r0 == r1
    
    for (int t = 0; t < thresh.size(); t++) 
    {
      //double threshold = (t-1) * stepSize;
      double threshold = thresh[t];
      //cout << t << "/" << thresh.size() << endl;
      
      int numPositive = 0;
      int numTruePositive = 0;
      for (int i = 0; i < numData; i++) 
      {
        if (prob[i] > threshold) 
        {
          numPositive++;
          if (cls[i] == 1) numTruePositive++;
        }
      }
      
      if (numPositive > 0)
      {
        double precVal = numTruePositive/(double)numPositive;
        
        if (precision.lastItem().prec == precVal)
          precision.lastItem().threshs.append(threshold);
      else
      {
        precision.append(PrecThreshs(precVal));
        precision.lastItem().threshs.append(threshold);
      }
      }
    }
    
    /*
    for (int i = 0; i < precision.size(); i++)
    {
      cout << "thresh = ";
      for (int j = 0; j < precision[i].threshs.size(); j++)
      cout << precision[i].threshs[j] << " ";
      cout << ", prec = " << precision[i].prec << endl;
    }
    */
  }

  static void readData(istream& in, Array<double>& prob, Array<int>& cls) 
  {
    prob.clear();
    cls.clear();
    string buffer;
    double x; int y;
    
    while (getline(in, buffer)) 
    {
      // skip blank line
      if (buffer.length() == 0) continue;
      istringstream iss(buffer);
      iss >> x >> y;
      prob.append(x); cls.append(y);
      
      if (cls.lastItem() != 0 && cls.lastItem() != 1)
      {
        cout << "Error: Class of " << cls.lastItem() << " is not 0 or 1!"<<endl;
        exit(-1);
      }
    }
  }
  

  static void getPrecisions(const Array<double>& prob, const Array<int>& cls, 
                            int numThresholds, Array<PrecThreshs>& precision)
  {
    double stepSize = 1.0/numThresholds;
    numThresholds++;
    
    assert(prob.size() == cls.size());
    int numData = prob.size();
    precision.clear();
    precision.append(PrecThreshs(0.0));
    precision[0].threshs.append(0.0); //r0 == r1
    
    for (int t = 1; t <= numThresholds; t++) 
    {
      double threshold = (t-1) * stepSize;
      
      int numPositive = 0;
      int numTruePositive = 0;
      for (int i = 0; i < numData; i++) 
      {
        if (prob[i] > threshold) 
        {
          numPositive++;
          if (cls[i] == 1) numTruePositive++;
        }
      }
      
      if (numPositive > 0)
      {
        double precVal = numTruePositive/(double)numPositive;
        
        if (precision.lastItem().prec == precVal)
          precision.lastItem().threshs.append(threshold);
        else
        {
          precision.append(PrecThreshs(precVal));
          precision.lastItem().threshs.append(threshold);
        }
      }
    }
    
    /*
    for (int i = 0; i < precision.size(); i++)
    {
      cout << "thresh = ";
      for (int j = 0; j < precision[i].threshs.size(); j++)
      cout << precision[i].threshs[j] << " ";
      cout << ", prec = " << precision[i].prec << endl;
    }
    */
  }


  //Weight of a threshold is the width around it. It is the average of the 
  //difference in precision between its left and right neighbors
  static void getWeights(const Array<PrecThreshs>& precision, 
                         Array<double>& weight) 
  {
    int T = precision.size()-1;
    weight.clear();
    weight.growToSize(T+1);
    for (int t = 0; t <= T; t++)
    {
      double P_tp1 = (t+1 <= T) ? precision[t+1].prec : precision[T].prec;
      double P_tm1 = (t-1 > 0) ? precision[t-1].prec : 0;
      //cout << "t = " << t << "; P[t+1] = " << P_tp1 
      //     << "; P[t-1] = " << P_tm1 <<endl;
      weight[t] = 0.5 * (P_tp1 - P_tm1);
    }
    
    //for (int i = 0; i < weight.size(); i++)
    //  cout << "weight[" << i << "] = " << weight[i] << endl;
  }
  

  // Compute the f_i's, which is, for each label that is true, 
  // the (weighted) average number of thresholds for which it was labelled true
  static void getFs(const Array<double>& prob, const Array<int>& cls, 
                    const Array<PrecThreshs>& precision, 
                    const Array<double>& weight, Array<double>& fs) 
  {
    assert(prob.size() == cls.size());
    assert(precision.size() == weight.size());
    
    int numData = prob.size();  
    for (int i = 0; i < numData; i++) 
    {
      if (cls[i] == 1) 
      {
        int T = precision.size()-1;
        double total = 0;
        for (int t = 0; t <= T;  t++)
        {
          int numAboveThresh = 0;
          Array<double>& threshs = precision[t].threshs;
          for (int j = 0; j < threshs.size(); j++)
          {
            if (prob[i] > threshs[j])
            {
              //cout << "data " << i << " prob " << prob[i] << " > " 
              //     << threshs[j] << endl;
              numAboveThresh++;
            }
          }
          total += weight[t] * numAboveThresh/(double)threshs.size();
          //cout << "\tadd " << weight[t] << ", total = " << total << endl;
        }
        fs.append(total);
      }
    }
  }
  
};

#endif
