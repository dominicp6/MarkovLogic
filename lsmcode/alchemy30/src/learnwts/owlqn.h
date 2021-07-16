#ifndef OWLQN_H_OCT_25_2008
#define OWLQN_H_OCT_25_2008

extern "C"{
#include "lbfgs.h"
}

static lbfgsfloatval_t evaluate(
    void *instance,
    const lbfgsfloatval_t *x,
    lbfgsfloatval_t *g,
    const int n,
    const lbfgsfloatval_t step
    )
{
  PseudoLogLikelihood* pll = (PseudoLogLikelihood*) instance;
  lbfgsfloatval_t value = pll->getValueAndGradient(g, x, n);

  bool print = false;
  //bool print = true;
  if (print)
  {
    printf("Evaluated value = %4.10f\n", value);
    printf("  x[0] = %4.10f, x[1] = %4.10f, x[2] = %4.10f\n", x[0], x[1], x[2]);
    printf("  g[0] = %4.10f, g[1] = %4.10f, g[2] = %4.10f\n", g[0], g[1], g[2]);
    printf("  step = %4.10f\n",  step);
    printf("\n");
  }


  return value;
}

static int progress(
    void *instance,
    const lbfgsfloatval_t *x,
    const lbfgsfloatval_t *g,
    const lbfgsfloatval_t fx,
    const lbfgsfloatval_t xnorm,
    const lbfgsfloatval_t gnorm,
    const lbfgsfloatval_t step,
    int n,
    int k,
    int ls
    )
{
  PseudoLogLikelihood* pll = (PseudoLogLikelihood*) instance;
  pll->setNumSteps(k);

  bool print = false;
  //bool print = true;
  if (print)
  {
    printf("Iteration %d:\n", k);
    printf("  fx = %4.10f, x[0] = %4.10f, x[1] = %4.10f, x[2] = %4.10f\n", fx, x[0], x[1],x[2]);
    printf("  xnorm = %4.10f, gnorm = %4.10f, step = %4.10f\n", xnorm, gnorm, step);
    printf("\n");
  }
  return 0;
}


class OWLQN
{
 public:
  OWLQN(const int& maxIter, const double& ftol, 
        PseudoLogLikelihood* const& pll, const int& numWts, const double& L1c) 
    : maxIter_(maxIter), numIter_(0), ftol_(ftol), pll_(pll), numWts_(numWts),
      L1c_(L1c) {}

  ~OWLQN() {}

  double minimize(double* const & wts, int& iter, bool& error)
  {
    lbfgsfloatval_t fx;
    lbfgsfloatval_t* x = wts;

    //set to defaults
    lbfgs_parameter_t param;
    param.m = 6;
    param.epsilon = ftol_;
    param.max_iterations = maxIter_;
    param.linesearch = 0;
    param.max_linesearch = 20;
    param.min_step = 1e-20;
    param.max_step = 1e20;
    param.ftol = 1e-4;
    param.gtol = 0.9;
    param.xtol = 1.0e-16;
    param.orthantwise_start = 0;
    param.orthantwise_c = L1c_;

    int ret = lbfgs(numWts_, x, &fx, evaluate, progress, (void*)pll_, &param);

    cout << "OWLQN returns with " << getRetString(ret) << endl;
    return fx;
  }

  void setNumIter(const int& i) { numIter_ = i; }

  PseudoLogLikelihood* pll() const { return pll_; }

 private:
  string getRetString(const int& ret)
  {
    if (ret==LBFGS_SUCCESS) return "SUCCESS";
    if (ret==LBFGS_ALREADY_MINIMIZED) return "ALREADY_MINIMIZED";
    if (ret==LBFGSERR_UNKNOWNERROR) return "UNKNOWNERROR";
    if (ret==LBFGSERR_LOGICERROR) return "LOGICERROR";
    if (ret==LBFGSERR_OUTOFMEMORY) return "OUTOFMEMORY";
    if (ret==LBFGSERR_CANCELED) return "CANCELED";
    if (ret==LBFGSERR_INVALID_N) return "INVALID_N";
    if (ret==LBFGSERR_INVALID_N_SSE) return "INVALID_N_SSE";
    if (ret==LBFGSERR_INVALID_X_SSE) return "INVALID_X_SSE";
    if (ret==LBFGSERR_INVALID_LINESEARCH) return "INVALID_LINESEARCH";
    if (ret==LBFGSERR_INVALID_MINSTEP) return "INVALID_MINSTEP";
    if (ret==LBFGSERR_INVALID_MAXSTEP) return "INVALID_MAXSTEP";
    if (ret==LBFGSERR_INVALID_FTOL) return "INVALID_FTOL";
    if (ret==LBFGSERR_INVALID_GTOL) return "INVALID_GTOL";
    if (ret==LBFGSERR_INVALID_XTOL) return "INVALID_XTOL";
    if (ret==LBFGSERR_INVALID_MAXLINESEARCH) return "INVALID_MAXLINESEARCH";
    if (ret==LBFGSERR_INVALID_ORTHANTWISE) return "INVALID_ORTHANTWISE";
    if (ret==LBFGSERR_INVALID_ORTHANTWISE_START) return "INVALID_ORTHANTWISE_START";
    if (ret==LBFGSERR_OUTOFINTERVAL) return "OUTOFINTERVAL";
    if (ret==LBFGSERR_INCORRECT_TMINMAX) return "INCORRECT_TMINMAX";
    if (ret==LBFGSERR_ROUNDING_ERROR) return "ROUNDING_ERROR";
    if (ret==LBFGSERR_MINIMUMSTEP) return "MINIMUMSTEP";
    if (ret==LBFGSERR_MAXIMUMSTEP) return "MAXIMUMSTEP";
    if (ret==LBFGSERR_MAXIMUMLINESEARCH) return "MAXIMUMLINESEARCH";
    if (ret==LBFGSERR_MAXIMUMITERATION) return "MAXIMUMITERATION";
    if (ret==LBFGSERR_WIDTHTOOSMALL) return "WIDTHTOOSMALL";
    if (ret==LBFGSERR_INVALIDPARAMETERS) return "INVALIDPARAMETERS";
    if (ret==LBFGSERR_INCREASEGRADIENT) return "INCREASEGRADIENT";
    return "UNKNOWN RETURN CODE";
   }

 private:
  int maxIter_;
  int numIter_;
  double ftol_;
  PseudoLogLikelihood* pll_;
  int numWts_;
  double L1c_;
};


#endif
