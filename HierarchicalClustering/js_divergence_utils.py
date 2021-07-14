import numpy as np
from NodeRandomWalkData import NodeClusterRandomWalkData


def compute_js_divergence_of_top_n_paths(node_cluster1: NodeClusterRandomWalkData,
                                         node_cluster2: NodeClusterRandomWalkData,
                                         number_of_walks=1000,
                                         number_of_top_paths=None,
                                         z_score=None):
    """
    Computes the Jensen-Shannon divergence between the probability distributions of the top n most common
    paths in the path distributions of two node clusters.

    If a z-score is provided, then also computes the corresponding threshold JS divergence at which the null hypothesis
    of the two node clusters being path-symmetric is rejected.
    """
    if number_of_top_paths is None:
        number_of_top_paths = min(node_cluster1.number_of_meaningful_paths(), node_cluster2.number_of_meaningful_paths())

    p = node_cluster1.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    q = node_cluster2.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)

    m = compute_average_distribution(p, q)

    js_div = js_divergence(p, q, m)

    if z_score is not None:
        theta_js = compute_threshold_js_divergence(number_of_walks=number_of_walks,
                                                   average_path_probabilities=m,
                                                   number_of_top_paths=number_of_top_paths,
                                                   z_score=z_score)
        return js_div, theta_js
    else:
        return js_div


def compute_threshold_js_divergence(number_of_walks: int,
                                    average_path_probabilities: dict,
                                    number_of_top_paths: int,
                                    z_score: float):
    """
    Given the number of random walks ran, and the average path distribution of the two clusters, calculates a
    Jensen-Shannon divergence threshold for merger of the node clusters.

    Computing the threshold requires additionally specifying
    (1) the number of top paths used when calculating the Jensen-Shannon divergence
    (2) the threshold z-score (defines how extreme the deviations between the Jensen-Shannon divergence of
       two distributions is permitted to be before the differences are no longer assumed to be explainable
       due to chance alone)
    """

    average_probability = list(average_path_probabilities.values())
    average_probability.sort(reverse=True)
    k = min(len(average_probability), number_of_top_paths)
    sigma_J_squared = (1 / (2 * number_of_walks)) * sum([average_probability[i] * (1 - average_probability[i])
                                                         for i in range(k)])
    sigma_J = np.sqrt(sigma_J_squared)
    mu_J = (2 / number_of_walks) * sum([(1 - average_probability[i]) for i in range(k)])

    theta_JS = mu_J + z_score * sigma_J

    return theta_JS


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
