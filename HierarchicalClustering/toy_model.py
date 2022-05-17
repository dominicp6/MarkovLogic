import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from scipy.stats import pearsonr
from scipy.stats import normaltest
from chi2comb import chi2comb_cdf, ChiSquared
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


path_counts = [[14,4,1],[10,4,1],[4,3,1],[3,2,1]]
print(path_counts)

scaler = StandardScaler()
scaler.fit(path_counts)
standardized = scaler.transform(path_counts)
print(standardized)

pca = PCA(2)
pca.fit(standardized)
embedding = pca.transform(standardized)
print(embedding)
#
# def get_cc_ij(data):
#     P = np.shape(data)[1]
#     CC = np.zeros((P, P))
#     for i in range(P):
#         for j in range(P):
#             CC[i][j] = np.mean(data[:, i] * data[:, j])
#
#     return CC
#
#
# def get_ccc_ij(data):
#     P = np.shape(data)[1]
#     CC = np.zeros((P, P))
#     for i in range(P):
#         for j in range(P):
#             CC[i][j] = np.mean(data[:, i] ** 2 * data[:, j])
#
#     return CC
#
#
# # # Testing hypothesis test
# path_probs = [0.25, 0.1, 0.05, 0.02]
# N = 10000
# assert (1 - sum(path_probs)) > 0
# path_probs.append(1 - sum(path_probs))
# trials = 100000
#
# Qs = []
# Xs = []
# for trial in range(trials):
#     X = np.random.multinomial(N, pvals=path_probs)
#     Y = np.random.multinomial(N, pvals=path_probs)
#     Z = np.random.multinomial(N, pvals=path_probs)
#     W = np.random.multinomial(N, pvals=path_probs)
#     all_data = np.array([X, Y, X, W])
#
#     c = (X + Y + Z + W) / 4
#
#     if trial == 0:
#         c2 = (X**2 + Y**2 + Z**2 + W**2)/4
#         cc_ij = get_cc_ij(all_data)
#         ccc_ij = get_ccc_ij(all_data)
#
#     Q = np.dot((1 - X/c), (1 - X/c))  + \
#         np.dot((1 - Y/c), (1 - Y/c))  + \
#         np.dot((1 - Z/c), (1 - Z/c))  + \
#         np.dot((1 - W/c), (1 - W/c))
#
#     Qs.append(Q)
#
#
#
# def sigma_ij(c, N):
#     P = len(c)
#     Sigma = np.zeros((P, P))
#
#     for i in range(P):
#         for j in range(P):
#             if i == j:
#                 Sigma[i][j] = (c[i]) * (1 - c[j] / N)
#             else:
#                 Sigma[i][j] = - (c[i] * c[j]) / (N)
#
#     return Sigma
#
# def mean_theory(Sigma, c, c2):
#     mu = 0
#     for i in range(len(c)):
#         mu += (Sigma[i][i]/(c[i]**2))*(len(c) + c2[i]/c[i]**2 - 2)
#
#     number_of_paths = len(c)
#     print("Number of paths ", number_of_paths)
#
#     #mu *= (number_of_paths - 1)
#
#     return mu
#
# def variance_theory(Sigma, c, c2, cc_ij, ccc_ij):
#     number_of_paths = len(c)
#
#     var = 0
#
#     for i in range(len(c)):
#         for j in range(len(c)):
#             var += (Sigma[i][j]**2 / (c[i]**2 * c[j]**2)) * (number_of_paths
#                                                              - 4 + c2[i]/c[i]**2
#                                                              + c2[j]/c[j]**2
#                                                              + c2[i]*c2[j]/(c[i]**2 * c[j]**2)
#                                                              + 4*(cc_ij[i][j]/(c[i]*c[j]))
#                                                              - 2*ccc_ij[i][j]/(c[i]*c[j]**2)
#                                                              - 2*ccc_ij[j][i]/(c[i]**2 * c[j]) )
#     var *= 2
#
#     return var
#
#
# mean_expected = mean_theory(sigma_ij(c, N), c, c2)
# var_expected = variance_theory(sigma_ij(c, N), c, c2, cc_ij, ccc_ij)
#
# print(mean_expected, np.mean(Qs))
# print(np.sqrt(var_expected), np.std(Qs))
# # mean = np.mean(Qs)
# # var = np.var(Qs)
# # scale = np.var(Qs)/np.mean(Qs)
# # k = np.mean(Qs)/scale
# # print(np.shape(Qs))
# # x = np.linspace(min(Qs), max(Qs), 1000)
# # y = scipy.stats.gamma.pdf(x, a=k, scale=scale)
# # plt.plot(x, y)
#
# scale = var_expected/mean_expected
# k = mean_expected/scale
# x = np.linspace(min(Qs), max(Qs), 1000)
# y = scipy.stats.gamma.pdf(x, a=k, scale=scale)
# plt.plot(x, y)
#
# sns.distplot(Qs, hist=True, kde=True, bins=80)
# plt.title('Hypothesis Test Check')
# plt.show()
# #
# # print('Mean theory: ', mean_theory)
# print('Mean easier theory: ', mean_easier_theory)
# print('Variance theory: ', variance_theory)
# print('Variance easier theory: ', variance_easier_theory)
#
# sns.distplot(Xs, hist=True, kde=True, bins=80)
# x = np.linspace(min(Xs), max(Xs), 1000)
# z = scipy.stats.norm.pdf(x, loc=0, scale=np.sqrt((1 - 1/3)*(N)*(c[0]*(1-c[0]))))
# plt.title('Testing X distribution')
# print(np.mean(Xs))
# print(np.std(Xs))
# plt.plot(x, z)
# plt.show()
#
#
#
#
# def compound_matrix(submatrix, number_of_tesselations, A_prefactor):
#     num_rows, num_cols = submatrix.shape
#     C = np.zeros((num_rows * number_of_tesselations, num_cols * number_of_tesselations))
#
#     for i in range(num_rows * number_of_tesselations):
#         for j in range(num_rows * number_of_tesselations):
#             a = np.remainder(i, num_rows)
#             b = np.remainder(j, num_rows)
#             if np.floor(i/num_rows) == np.floor(j/num_rows):
#                 prefactor = A_prefactor
#             else:
#                 prefactor = 1
#             if a == b:
#                 C[i][j] = prefactor * submatrix[a][b]
#             else:
#                 C[i][j] = prefactor * submatrix[a][b]
#
#     return C
#
# M = np.array([[1, 2, 3], [2, 1, 4], [3, 4, 1]])
# print(M)
# print(np.linalg.eigvals(M))
# C = compound_matrix(M, 4, 2)
# print(C)
# print(np.linalg.eigvals(C))
#
#
# #
# # trials = 100000
# #
# # mu_x = 50
# # mu_y = 50
# # s_x = 0.2
# # s_y = 0.2
# #
# #
# # X = np.random.normal(mu_x, s_x, size=trials)
# # print('X normal: ', normaltest(X)[1] > 0.05)
# # Y = np.random.normal(mu_y, s_y, size=trials)
# # print('Y normal: ', normaltest(Y)[1] > 0.05)
# #
# # D = X-Y
# # V = np.log(X/Y)
# # print(np.mean(V), - s_x**2 / mu_x **2)
# # print(np.mean(D), 0)
# # print(np.std(V), np.sqrt(2 * s_x **2 / mu_x ** 2))
# # print(np.std(D), np.sqrt(2* s_x **2))
# # plt.title("D")
# # plt.hist(D, bins=100)
# # plt.show()
# # plt.title("V")
# # plt.hist(V, bins=100)
# # plt.show()
# # plt.title("DV")
# # plt.hist(D*V, bins=100)
# # plt.show()
# # print("Pearson: ", pearsonr(D, V))
# #
# # # Verifying V preliminary Theorem F.0.1
# # def mean_V(mu_x, mu_y, s_x, s_y):
# #     return (mu_x/mu_y)*(1 + s_y ** 2 / mu_y ** 2)
# #
# # def std_V(mu_x, mu_y, s_x, s_y):
# #     return np.sqrt((mu_x/mu_y)**2 * (s_x ** 2 / mu_x ** 2 + s_y ** 2 / mu_y ** 2))
# #
# # def verify_V(X, Y, mu_x, mu_y, s_x, s_y):
# #     V = X/Y
# #     print('V normal: ', normaltest(V)[1] > 0.05)
# #     plt.hist(V, bins=100)
# #     plt.title('V')
# #     print('V')
# #     print(np.mean(V), "estimated: ", mean_V(mu_x, mu_y, s_x, s_y))
# #     print(np.std(V), "estimated: ", std_V(mu_x, mu_y, s_x, s_y))
# #     plt.show()
# #
# # # Verifying W preliminary Theorem F.0.1
# # def mean_W(mu_x, mu_y, s_x, s_y):
# #     return np.log(mu_x/mu_y) - s_x **2  / (mu_x ** 2)
# #
# # def std_W(mu_x, mu_y, s_x, s_y):
# #     return np.sqrt(s_x**2 / mu_x**2 + s_y**2/mu_y**2)
# #
# # def verify_W(X, Y, mu_x, mu_y, s_x, s_y):
# #     V = X/Y
# #     W = np.log(V)
# #     print('W normal: ', normaltest(W)[1] > 0.05)
# #     plt.hist(W, bins=100)
# #     plt.title('W')
# #     print('W')
# #     print(np.mean(W), "estimated: ", mean_W(mu_x, mu_y, s_x, s_y))
# #     print(np.std(W), "estimated: ", std_W(mu_x, mu_y, s_x, s_y))
# #     plt.show()
# #
# # # Verifying Z Theorem F.0.1
# # def mean_Z(mu_x, mu_y, s_x, s_y):
# #     return mu_x * np.log(mu_x/mu_y) + s_x**2 / (2*mu_x) + (s_y**2 * mu_x) / (2 * mu_y**2)
# #
# # def std_Z(mu_x, mu_y, s_x, s_y):
# #     return np.sqrt(s_x **2  * (1 + np.log(mu_x/mu_y))**2 + s_y **2 * mu_x ** 2 / mu_y**2)
# #
# # def verify_Z(X, Y, mu_x, mu_y, s_x, s_y):
# #     V = X/Y
# #     W = np.log(V)
# #     Z = X * W
# #     print('Z normal: ', normaltest(Z)[1] > 0.05)
# #     plt.hist(Z, bins=100)
# #     plt.title('Z')
# #     print('Z')
# #     print(np.mean(Z), "estimated: ", mean_Z(mu_x, mu_y, s_x, s_y))
# #     print(np.std(Z), "estimated: ", std_Z(mu_x, mu_y, s_x, s_y))
# #     plt.show()
# #
# #
# # # Verifying SK
# # pis = [0.2, 0.15, 0.07, 0.05, 0.02, 0.01]
# # assert (1 - sum(pis)) > 0
# # pis.append(1 - sum(pis))
# #
# #
# # def KL(p, q):
# #     return sum(p * np.log(p / q))
# #
# #
# # def SK(p, q):
# #     return 0.5 * KL(p, q) + 0.5 * KL(q, p)
# #
# #
# # # # Number of random walks
# # N = 10000
# # trials = 10000
# #
# # SKs = []
# # p = 0
# # q = 0
# # for trial in range(trials):
# #     c_P = np.random.multinomial(N, pvals=pis)
# #     c_Q = np.random.multinomial(N, pvals=pis)
# #     p = c_P[:-1] / N
# #     q = c_Q[:-1] / N
# #     SKs.append(SK(p, q))
# #
# # mean = np.mean(SKs)
# # var = np.var(SKs)
# # scale = var / mean
# # k = mean / scale
# # x = np.linspace(min(SKs), max(SKs), 1000)
# # y = scipy.stats.gamma.pdf(x, a=k, scale=scale)
# # plt.plot(x, y)
# # sns.distplot(SKs, hist=True, kde=True, bins=80)
# # plt.title('SK Divergence Check')
# # plt.show()
# #
# # chi_squared_distribution_coefficients = (1 / N) * (1 - (p + q) / 2)
# # gcoef = 0
# # nu_central_coeffs = [0, 0, 0, 0, 0, 0, 0, 0]
# # dofs = [1, 1, 1, 1, 1, 1, 1, 1]
# # chi2s = [ChiSquared(chi_squared_distribution_coefficients[i], nu_central_coeffs[i], dofs[i])
# #          for i in range(len(pis[:-1]))]
# #
# #
# # def theoretical_probability_less_than_q(q, chi2s, gcoef):
# #     result, error, info = chi2comb_cdf(q, chi2s, gcoef)
# #     return result
# #
# #
# # def empirical_probability_less_than_q(q, SKs):
# #     return sum(SKs < q) / len(SKs)
# #
# #
# # plt.hist(SKs, bins=100)
# # plt.show()
# #
# # min = 0
# # max = 0.0025
# # tests = 100
# #
# # x_values = np.arange(min, max, (max - min) / tests)
# # theory = []
# # experiment = []
# #
# # SKs_numpy = np.array(SKs)
# #
# # for i in x_values:
# #     theory.append(theoretical_probability_less_than_q(i, chi2s, gcoef))
# #     experiment.append(empirical_probability_less_than_q(i, SKs_numpy))
# #
# # plt.xlabel("z")
# # plt.ylabel("P(SK < z)")
# # plt.plot(x_values, experiment, "-k", label="Experiment")
# # plt.plot(x_values, theory, "r", label="Theory")
# # plt.legend()
# # plt.show()
# #
# #
# # def critical_value_of_test(significance_level, accuracy):
# #     number_of_samples = 1 / accuracy
# #     for q_value in np.arange(0, 0.005, 0.005/number_of_samples):
# #         if 1 - theoretical_probability_less_than_q(q_value, chi2s, gcoef) <= significance_level:
# #             return q_value
# #
# #
# # print('alpha = 0.5')
# # print(critical_value_of_test(significance_level=0.5, accuracy=0.000001))
# # print('alpha = 0.1')
# # print(critical_value_of_test(significance_level=0.1, accuracy=0.000001))
# # print('alpha = 0.01')
# # print(critical_value_of_test(significance_level=0.01, accuracy=0.000001))
# # print('alpha = 0.001')
# # print(critical_value_of_test(significance_level=0.001, accuracy=0.000001))
