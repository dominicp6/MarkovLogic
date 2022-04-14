import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.stats import normaltest
from scipy.integrate import dblquad

N = 100000
pis = [0.1, 0.05, 0.03, 0.02, 0.01]
assert (1-sum(pis)) > 0
pis.append(1-sum(pis))

trials = 100000


def KL(p, q):
    return sum(p * np.log(p/q))


def SK(p, q):
    return 0.5 * KL(p,q) + 0.5 * KL(q,p)


def estimated_mean(N, p, q):
    return (2/N)*sum(1-(p+q)/2)


def estimated_std(N, p, q):
    return np.sqrt((1/N)*sum((p+q)*(2-(p+q)/2)/2))


mu_x = 50
mu_y = 60
s_x = 0.5
s_y = 0.5


X = np.random.normal(mu_x, s_x, size=trials)
print('X normal: ', normaltest(X)[1] > 0.05)
Y = np.random.normal(mu_y, s_y, size=trials)
print('Y normal: ', normaltest(Y)[1] > 0.05)


# Verifying V preliminary Theorem F.0.1
def mean_V(mu_x, mu_y, s_x, s_y):
    return (mu_x/mu_y)*(1 + s_y ** 2 / mu_y ** 2)

def std_V(mu_x, mu_y, s_x, s_y):
    return np.sqrt((mu_x/mu_y)**2 * (s_x ** 2 / mu_x ** 2 + s_y ** 2 / mu_y ** 2))

V = X/Y
print('V normal: ', normaltest(V)[1] > 0.05)
plt.hist(V, bins=100)
plt.title('V')
print('V')
print(np.mean(V), "estimated: ", mean_V(mu_x, mu_y, s_x, s_y))
print(np.std(V), "estimated: ", std_V(mu_x, mu_y, s_x, s_y))
plt.show()

# Verifying W preliminary Theorem F.0.1
def mean_W(mu_x, mu_y, s_x, s_y):
    return np.log(mean_V(mu_x, mu_y, s_x, s_y)) - std_V(mu_x, mu_y, s_x, s_y)**2 / (2 * mean_V(mu_x, mu_y, s_x, s_y) **2)

def std_W(mu_x, mu_y, s_x, s_y):
    """
    TODO Corrected this calculation
    """
    return np.sqrt(s_x**2 / mu_x**2 + s_y**2/mu_y**2) #np.sqrt(std_V(mu_x,mu_y,s_x,s_y)**2 / mean_V(mu_x,mu_y,s_x,s_y))

W = np.log(V)
print('W normal: ', normaltest(W)[1] > 0.05)
plt.hist(W, bins=100)
plt.title('W')
print('W')
print(np.mean(W), "estimated: ", mean_W(mu_x, mu_y, s_x, s_y))
print(np.std(W), "estimated: ", std_W(mu_x, mu_y, s_x, s_y))
plt.show()


# Verifying Z Theorem F.0.1
def mean_Z(mu_x, mu_y, s_x, s_y):
    return mu_y * (mean_W(mu_x, mu_y, s_x, s_y) + std_W(mu_x,mu_y,s_x,s_y)**2) \
           * np.exp(mean_W(mu_x,mu_y,s_x,s_y) + 0.5 * (std_W(mu_x,mu_y,s_x,s_y)**2))

def mean_Z2(mu_x, mu_y, s_x, s_y):
    return mu_x * (np.log(mu_x/mu_y)) + s_x **2 / mu_x + s_y **2 * (mu_x/(2 * mu_y**2))

E_X2 = mu_x**2 + s_x**2
E_logY = np.log(mu_y) - 0.5 * (s_y/mu_y)**2
E_log2Y = np.log(mu_y)**2 - 0.5 * (s_y/mu_y)**2 * (1- np.log(mu_y))
E_X2logX = (mu_x**2)*np.log(mu_x) - 0.5 * (s_x**2) * (1.5 + np.log(mu_x))
E_X2log2X = (mu_x**2)*(np.log(mu_x)**2) - 0.5 * (s_x**2) * (np.log(mu_x))**2 - 0.5 * (s_x ** 2) * (1- 3*np.log(mu_x))

E_XlogX = mu_x * np.log(mu_x) + s_x ** 2 / mu_x

print('X2LOG2X')
print(E_X2log2X, np.mean(X**2 * np.log(X)**2), 100 * (E_X2log2X-np.mean(X**2 * np.log(X)**2))/E_X2log2X)
print('X2LOGX')
print(E_X2logX, np.mean(X**2 * np.log(X)), 100 * (E_X2logX-np.mean(X**2 * np.log(X)))/E_X2logX)
print('XLOGX')
print(E_XlogX, np.mean(X * np.log(X)))
print('LOGY')
print(E_logY, np.mean(np.log(Y)), 100 * (E_logY-np.mean(np.log(Y)))/E_logY)
print('X2')
print(E_X2, np.mean(X**2), 100 * (E_X2 - np.mean(X**2))/E_X2)
print('LOG2Y')
print(E_log2Y, np.mean(np.log(Y)**2), 100 * (E_log2Y - np.mean(np.log(Y)**2))/E_log2Y)
print('X2W2')
print((E_X2log2X - 2 * E_X2logX * E_logY + E_X2 * E_log2Y), np.mean(X**2 * W**2))

print('STD')
print(E_X2log2X - 2 * E_X2logX * E_logY + E_X2 * E_log2Y)
print(np.mean(X**2 * W**2))
print(np.mean(X*W)**2)
print(np.sqrt(np.mean(X**2 * W**2) - np.mean(X*W)**2))
# def std_Z(mu_x, mu_y, s_x, s_y):
#     return np.sqrt((E_X2log2X - 2 * E_X2logX * E_logY + E_X2 * E_log2Y) - (E_XlogX - mu_x * E_logY)**2)
# # def std_Z(mu_x, mu_y, s_x, s_y):
#     return np.sqrt(mu_x**2 * std_W(mu_x, mu_y, s_x, s_y)**2 - 2.57 * mean_W(mu_x, mu_y, s_x, s_y)**2 * s_x **2)
# def std_Z(mu_x, mu_y, s_x, s_y):
#     return np.sqrt(mu_x ** 2 * std_W(mu_x,mu_y,s_x,s_y)**2 + mean_W(mu_x, mu_y, s_x, s_y)**2 * s_x ** 2)
# def mean_F01(mu_x, mu_y, s_x, s_y):
#     return mu_x * (np.log(mu_x/mu_y) * (1 + (s_y ** 2) / (mu_y ** 2))
#                    + 0.5 * (s_x ** 2 / mu_x ** 2 + 3 * s_y ** 2 / mu_y ** 2))
#
# def std_FO1(mu_x, mu_y, s_x, s_y):
#     return np.sqrt(mu_x ** 2 * ((1+2*np.log(mu_x/mu_y)) * (s_x ** 2 / mu_x ** 2 + s_y ** 2 / mu_y ** 2)
#                                 + np.log(mu_x/mu_y) ** 2 * (s_x ** 2 / mu_x ** 2 + 2 * s_y ** 2 / mu_y ** 2)))

def std_Z(mu_x, mu_y, s_x, s_y):
    return mu_x * std_W(mu_x, mu_y, s_x, s_y)    # a slight overestimate

Z = X * W
print('Z normal: ', normaltest(Z)[1] > 0.05)
plt.hist(Z, bins=100)
plt.title('Z')
print('Z')
print(np.mean(Z), "estimated: ", mean_Z(mu_x, mu_y, s_x, s_y), mean_Z2(mu_x, mu_y, s_x, s_y))
print(np.std(Z), "estimated: ", std_Z(mu_x, mu_y, s_x, s_y))
plt.show()




# SKs = []
# for trial in range(trials):
#     c_P = np.random.multinomial(N, pvals=pis)
#     c_Q = np.random.multinomial(N, pvals=pis)
#     p = c_P/N
#     q = c_Q/N
#     SKs.append(SK(p, q))
#
# plt.hist(SKs, bins=100)
# print(np.mean(SKs), "estimated: ", estimated_mean(N,p,q))
# print(np.std(SKs), "estimated: ", estimated_std(N,p,q))
# plt.show()
#

