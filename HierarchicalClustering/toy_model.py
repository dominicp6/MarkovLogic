import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from scipy.stats import pearsonr
from scipy.stats import normaltest
from chi2comb import chi2comb_cdf, ChiSquared


# Testing hypothesis test
c = [0.2, 0.15, 0.07, 0.05, 0.02, 0.01]
N = 10000
assert (1-sum(c)) > 0
c.append(1-sum(c))
trials = 10000

Qs = []
for trial in range(trials):
    X = np.random.multinomial(N, pvals=c)
    Y = np.random.multinomial(N, pvals=c)
    Z = np.random.multinomial(N, pvals=c)
    W = np.random.multinomial(N, pvals=c)
    mean_counts = (X + Y + Z + W)/4
    Q = np.dot((mean_counts - X), (mean_counts - X)) + \
        np.dot((mean_counts - Y), (mean_counts - Y)) + \
        np.dot((mean_counts - Z), (mean_counts - Z)) + \
        np.dot((mean_counts - W), (mean_counts - W))
    Qs.append(Q)


def compute_sigma(c_vector, P, N, V):

    Sigma = np.zeros((P, P))

    for i in range(P):
        for j in range(P):
            if i == j:
                Sigma[i][j] = (c_vector[i] / N) * (1 - c_vector[j] / N)
            else:
                Sigma[i][j] = - (c_vector[i] * c_vector[j]) / (N ** 2)

    Sigma *= N * (1 - 1 / V)

    return Sigma

eigenvalues = np.linalg.eigvals(compute_sigma(mean_counts, len(X), N, 4))


mean = np.mean(Qs)
var = np.var(Qs)
scale = var/mean
k = mean/scale
x = np.linspace(min(Qs), max(Qs), 1000)
y = scipy.stats.gamma.pdf(x, a=k, scale=scale)
plt.plot(x, y)
sns.distplot(Qs, hist=True, kde=True, bins=80)
plt.title('Hypothesis Test Check')
plt.show()






#
# trials = 100000
#
# mu_x = 50
# mu_y = 50
# s_x = 0.2
# s_y = 0.2
#
#
# X = np.random.normal(mu_x, s_x, size=trials)
# print('X normal: ', normaltest(X)[1] > 0.05)
# Y = np.random.normal(mu_y, s_y, size=trials)
# print('Y normal: ', normaltest(Y)[1] > 0.05)
#
# D = X-Y
# V = np.log(X/Y)
# print(np.mean(V), - s_x**2 / mu_x **2)
# print(np.mean(D), 0)
# print(np.std(V), np.sqrt(2 * s_x **2 / mu_x ** 2))
# print(np.std(D), np.sqrt(2* s_x **2))
# plt.title("D")
# plt.hist(D, bins=100)
# plt.show()
# plt.title("V")
# plt.hist(V, bins=100)
# plt.show()
# plt.title("DV")
# plt.hist(D*V, bins=100)
# plt.show()
# print("Pearson: ", pearsonr(D, V))
#
# # Verifying V preliminary Theorem F.0.1
# def mean_V(mu_x, mu_y, s_x, s_y):
#     return (mu_x/mu_y)*(1 + s_y ** 2 / mu_y ** 2)
#
# def std_V(mu_x, mu_y, s_x, s_y):
#     return np.sqrt((mu_x/mu_y)**2 * (s_x ** 2 / mu_x ** 2 + s_y ** 2 / mu_y ** 2))
#
# def verify_V(X, Y, mu_x, mu_y, s_x, s_y):
#     V = X/Y
#     print('V normal: ', normaltest(V)[1] > 0.05)
#     plt.hist(V, bins=100)
#     plt.title('V')
#     print('V')
#     print(np.mean(V), "estimated: ", mean_V(mu_x, mu_y, s_x, s_y))
#     print(np.std(V), "estimated: ", std_V(mu_x, mu_y, s_x, s_y))
#     plt.show()
#
# # Verifying W preliminary Theorem F.0.1
# def mean_W(mu_x, mu_y, s_x, s_y):
#     return np.log(mu_x/mu_y) - s_x **2  / (mu_x ** 2)
#
# def std_W(mu_x, mu_y, s_x, s_y):
#     return np.sqrt(s_x**2 / mu_x**2 + s_y**2/mu_y**2)
#
# def verify_W(X, Y, mu_x, mu_y, s_x, s_y):
#     V = X/Y
#     W = np.log(V)
#     print('W normal: ', normaltest(W)[1] > 0.05)
#     plt.hist(W, bins=100)
#     plt.title('W')
#     print('W')
#     print(np.mean(W), "estimated: ", mean_W(mu_x, mu_y, s_x, s_y))
#     print(np.std(W), "estimated: ", std_W(mu_x, mu_y, s_x, s_y))
#     plt.show()
#
# # Verifying Z Theorem F.0.1
# def mean_Z(mu_x, mu_y, s_x, s_y):
#     return mu_x * np.log(mu_x/mu_y) + s_x**2 / (2*mu_x) + (s_y**2 * mu_x) / (2 * mu_y**2)
#
# def std_Z(mu_x, mu_y, s_x, s_y):
#     return np.sqrt(s_x **2  * (1 + np.log(mu_x/mu_y))**2 + s_y **2 * mu_x ** 2 / mu_y**2)
#
# def verify_Z(X, Y, mu_x, mu_y, s_x, s_y):
#     V = X/Y
#     W = np.log(V)
#     Z = X * W
#     print('Z normal: ', normaltest(Z)[1] > 0.05)
#     plt.hist(Z, bins=100)
#     plt.title('Z')
#     print('Z')
#     print(np.mean(Z), "estimated: ", mean_Z(mu_x, mu_y, s_x, s_y))
#     print(np.std(Z), "estimated: ", std_Z(mu_x, mu_y, s_x, s_y))
#     plt.show()
#
#
# # Verifying SK
pis = [0.2, 0.15, 0.07, 0.05, 0.02, 0.01]
assert (1-sum(pis)) > 0
pis.append(1-sum(pis))


def KL(p, q):
    return sum(p * np.log(p/q))


def SK(p, q):
    return 0.5 * KL(p,q) + 0.5 * KL(q,p)


# # Number of random walks
N = 10000

SKs = []
p = 0
q = 0
for trial in range(trials):
    c_P = np.random.multinomial(N, pvals=pis)
    c_Q = np.random.multinomial(N, pvals=pis)
    p = c_P[:-1]/N
    q = c_Q[:-1]/N
    SKs.append(SK(p, q))

mean = np.mean(SKs)
var = np.var(SKs)
scale = var/mean
k = mean/scale
x = np.linspace(min(SKs), max(SKs), 1000)
y = scipy.stats.gamma.pdf(x, a=k, scale=scale)
plt.plot(x, y)
sns.distplot(SKs, hist=True, kde=True, bins=80)
plt.title('SK Divergence Check')
plt.show()

# chi_squared_distribution_coefficients = (1/N)*(1-(p+q)/2)
# gcoef = 0
# nu_central_coeffs = [0, 0, 0, 0, 0, 0, 0, 0]
# dofs = [1, 1, 1, 1, 1, 1, 1, 1]
# chi2s = [ChiSquared(chi_squared_distribution_coefficients[i], nu_central_coeffs[i], dofs[i])
#          for i in range(len(pis[:-1]))]
#
# def theoretical_probability_less_than_q(q, chi2s, gcoef):
#     result, error, info = chi2comb_cdf(q, chi2s, gcoef)
#     return result
#
# def empirical_probability_less_than_q(q, SKs):
#     return sum(SKs<q)/len(SKs)
#
# plt.hist(SKs, bins=100)
# plt.show()
#
# min = 0
# max = 0.0025
# tests = 100
#
# x_values = np.arange(min, max, (max-min)/tests)
# theory = []
# experiment = []
#
# SKs_numpy = np.array(SKs)
#
# for i in x_values:
#     theory.append(theoretical_probability_less_than_q(i, chi2s, gcoef))
#     experiment.append(empirical_probability_less_than_q(i, SKs_numpy))
#
# plt.xlabel("z")
# plt.ylabel("P(SK < z)")
# plt.plot(x_values, experiment, "-k", label="Experiment")
# plt.plot(x_values, theory, "r", label="Theory")
# plt.legend()
# plt.show()