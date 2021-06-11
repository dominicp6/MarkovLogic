import numpy as np
from NodeRandomWalkData import NodeClusterRandomWalkData


def compute_js_divergence_of_top_n_paths(node_cluster1: NodeClusterRandomWalkData,
                                         node_cluster2: NodeClusterRandomWalkData, n):
    """
    Computes the Jensen-Shannon divergence between the probability distributions of the top n most common
    paths in the path distributions of two node clusters.
    """
    p = node_cluster1.get_top_n_path_probabilities(n)
    q = node_cluster2.get_top_n_path_probabilities(n)

    return js_divergence(p, q)


def js_divergence(p: dict, q: dict):
    """
    Computes the Jensen-Shannon divergence between two discrete probability distributions p and q.
    """
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
