import numpy as np
from NodeRandomWalkData import NodeClusterRandomWalkData


def compute_js_divergence_of_top_n_paths(node_cluster1: NodeClusterRandomWalkData,
                                         node_cluster2: NodeClusterRandomWalkData, n: int, z=None):
    """
    Computes the Jensen-Shannon divergence between the probability distributions of the top n most common
    paths in the path distributions of two node clusters.

    If a z-score is provided, then also computes the corresponding threshold JS divergence at which the null hypothesis
    of the two node clusters being path-symmetric is rejected.
    """
    p = node_cluster1.get_top_n_path_probabilities(n)
    q = node_cluster2.get_top_n_path_probabilities(n)

    m = compute_average_distribution(p, q)

    js_div = js_divergence(p, q, m)

    if z is not None:
        N_p = node_cluster1.total_count
        N_q = node_cluster2.total_count
        theta_js = compute_threshold_js_divergence(N_p, N_q, m, n, z)
        return js_div, theta_js
    else:
        return js_div


def compute_threshold_js_divergence(N_p: int, N_q: int, m: dict, n: int, z: float):
    """
    Given the number of path counts in two clusters, N_p and N_q, and the average path distribution of the two clusters,
     m, calculates a suitable value for the Jensen-Shannon divergence threshold for merger of the node clusters. Only
     if the JS divergence is strictly less than the threshold should the nodes be considered path-symmetric and merged.

    To compute the threshold one must additionally specify:
    n: the number of paths considered in the calculation of the Jensen-Shannon divergence
    z: the threshold z-score which defines how extreme the deviations between the Jensen-Shannon divergence of
       two distributions is permitted to be before the differences are no longer assumed to be explainable
       due to chance alone. The threshold JS divergence depends linearly on z.
    """

    p_bar = list(m.values())
    sigma_J_squared = sum([0.5 * (1 + p_bar[i] ** (-4)) * (1 / N_p + 1 / N_q) *
                           p_bar[i] ** 2 * (1 - p_bar[i]) ** 2 for i in range(n)])
    sigma_J = np.sqrt(sigma_J_squared)

    return z * sigma_J


def js_divergence(p: dict, q: dict, m=None):
    """
    Computes the Jensen-Shannon divergence between two discrete probability distributions p and q.
    If the average distribution of p and q has been pre-computed then it can be provided as an argument.
    """
    if m is None:
        m = compute_average_distribution(p, q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


def compute_average_distribution(p: dict, q: dict):
    """
    Computes the distribution m := 0.5*(p+q) from two discrete probability distributions p and q.
    """
    m = {}
    m.update((path, 0.5 * prob) for path, prob in p.items())
    for path, probability in q.items():
        if path in m.keys():
            m[path] += 0.5 * probability
        else:
            m[path] = 0.5 * probability

    return m


def kl_divergence(p: dict, q: dict):
    """
    Computes the Kullback-Leibler divergence between two discrete probability distributions p and q.
    """
    # When computing KL divergence of path-probability dictionaries of unequal length, the second dictionary must be
    # the larger one. If this is not already the case, reverse their orders:
    if len(q) < len(p):
        q_copy = q.copy()
        q = p
        p = q_copy

    return sum(
        [p[p_path] * np.log(p[p_path] / q[p_path]) for p_path in p.keys() if p_path in q.keys() and p[p_path] != 0])
