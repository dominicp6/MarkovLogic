import numpy as np
from NodeRandomWalkData import NodeClusterRandomWalkData


def compute_sk_divergence_of_top_n_paths(node_cluster1: NodeClusterRandomWalkData,
                                         node_cluster2: NodeClusterRandomWalkData,
                                         number_of_top_paths: int,
                                         number_of_walks: int,
                                         z_score=None):
    """
    Computes the symmetric Kulbeck-Liebler divergence between the probability distributions of the top n most common
    paths in the path distributions of two node clusters.

    If a z-score is provided, then also computes the corresponding threshold JS divergence at which the null hypothesis
    of the two node clusters being path-symmetric is rejected.
    """
    p = node_cluster1.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    q = node_cluster2.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)

    m = compute_average_distribution(p, q)

    sk_div = sk_divergence(p, q, m)

    if z_score is not None:
        theta_sk = compute_threshold_sk_divergence(N=number_of_walks,
                                                   m=m,
                                                   number_of_top_paths=number_of_top_paths,
                                                   significance_level=significance_level)
        return sk_div, theta_sk
    else:
        return sk_div


def compute_threshold_sk_divergence(N: int, m: dict, number_of_top_paths: int, significance_level: float):
    """
    Given the number of random walks ran, and the average path distribution of the two clusters, calculates a
    symmetric Kulbeck-Liebler divergence threshold for merger of the node clusters.
    """
    m_values = np.sort(np.array(m.values()), reversed=True)

    # number of paths to include in calculation of the critical value
    n = min(len(m_values), number_of_top_paths)
    weight_vector = (1/N) * (1 - m_values[:n])
    dof_vector = [1] * n



    return theta_JS


def sk_divergence(p: dict, q: dict, m=None):
    """
    Computes the symmetric Kulbeck-Liebler divergence between two discrete probability distributions p and q.
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
