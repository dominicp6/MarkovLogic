import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import normaltest

trials = 10000


def KL(p, q):
    return sum(p * np.log(p/q))


def SK(p, q):
    return 0.5 * KL(p,q) + 0.5 * KL(q,p)


mu_x = 50
mu_y = 50
s_x = 1
s_y = 1


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
    return mu_x * np.log(mu_x/mu_y) + s_x**2 / (2*mu_x) + (s_y**2 * mu_x) / (2 * mu_y**2)

def std_Z(mu_x, mu_y, s_x, s_y):
    return np.sqrt(s_x **2  * (1 + np.log(mu_x/mu_y))**2 + s_y **2 * mu_x ** 2 / mu_y**2)


Z = X * W
print('Z normal: ', normaltest(Z)[1] > 0.05)
plt.hist(Z, bins=100)
plt.title('Z')
print('Z')
print(np.mean(Z), "estimated: ", mean_Z(mu_x, mu_y, s_x, s_y))
print(np.std(Z), "estimated: ", std_Z(mu_x, mu_y, s_x, s_y))
plt.show()

# TODO check multinomial distribution approximation
# TODO check covariance calculation for xlog(x/y) type terms


# The big test
pis = [0.1, 0.05, 0.025, 0.0125]
assert (1-sum(pis)) > 0
pis.append(1-sum(pis))
N = 10000

mus = pis * N
sigmas = [pi * N ** 0.5 for pi in pis]
ratios = [mu/sigma for (mu,sigma) in zip(mus,sigmas)]
print(ratios)

SKs = []
for trial in range(trials):
    c_P = np.random.multinomial(N, pvals=pis)
    c_Q = np.random.multinomial(N, pvals=pis)
    p = c_P[:-1]/N
    q = c_Q[:-1]/N
    SKs.append(SK(p, q))

def mu_SK(N, pis):
    return (1/N) * sum((1-pi) for pi in pis)

def std_SK(N, pis):
    return np.sqrt((1/N) * sum(pi*(1-pi) for pi in pis))

plt.hist(SKs, bins=100)
plt.title('SK')
print(np.mean(SKs), "estimated: ", mu_SK(N, pis[0:-1]))
print(np.std(SKs), "estimated: ", std_SK(N, pis[0:-1]))
plt.show()


