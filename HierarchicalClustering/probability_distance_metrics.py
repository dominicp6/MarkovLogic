import numpy as np
from HierarchicalClustering.NodeRandomWalkData import NodeClusterRandomWalkData


def compute_divergence_of_top_n_paths(node_cluster1: NodeClusterRandomWalkData,
                                      node_cluster2: NodeClusterRandomWalkData,
                                      number_of_walks=1000,
                                      number_of_top_paths=None,
                                      z_score=None,
                                      threshold=None,
                                      use_js_div=False):
    """
    Computes the divergence between the probability distributions of the top n most common paths in the path
    distributions of two node clusters.

    :param node_cluster1:       The first cluster.
    :param node_cluster2:       The second cluster.
    :param number_of_walks:     The total number of random walks that were run on the hypergraph.
    :param number_of_top_paths: The number of top paths used when calculating the distribution divergence.
    :param z_score:             The z-score for the hypothesis test of merger. If not None, then we also calculate
                                the threshold divergence between the two distributions.
    :param threshold:           If not None then use this as the divergence threshold value rather than by calculation.
    :param use_js_div:          If False (default) then we compute the symmetric Kulbeck-Liebler divergence. If True
                                then we compute the Jensen-Shannon divergence.
    """
    if number_of_top_paths is None:
        number_of_top_paths = min(node_cluster1.number_of_meaningful_paths(),
                                  node_cluster2.number_of_meaningful_paths())

    p = node_cluster1.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    q = node_cluster2.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    m = compute_average_distribution(p, q)

    if use_js_div:
        divergence = js_divergence(p, q, m)
    else:
        divergence = sk_divergence(p, q)

    if z_score is None:
        return divergence
    else:
        if threshold is None:
            divergence_threshold = compute_threshold_divergence(m,
                                                                number_of_walks,
                                                                number_of_top_paths,
                                                                z_score,
                                                                use_js_div)
        else:
            divergence_threshold = threshold

        return divergence, divergence_threshold


def compute_threshold_divergence(average_distribution: dict,
                                 number_of_walks: int,
                                 number_of_top_paths: int,
                                 z_score,
                                 use_js_div=False):
    """
    Uses a statistical hypothesis test to determine the threshold at which the null-hypothesis of two path distributions
    being identically distributed is violated.

    :param average_distribution: The average of the two path distributions.
    :param number_of_walks:      The number of random walks run on the hypergraph to generate the distributions.
    :param number_of_top_paths:  The number of top paths used when calculating the threshold.
    :param z_score:              The z-score for the hypothesis test.
    :param use_js_div:           If False (default) then use the symmetric Kulbeck-Liebler divergence. If True
                                 then use the Jensen-Shannon divergence.
    """
    average_probability = list(average_distribution.values())

    # sort so that we sum over paths in order of decreasing probability
    average_probability.sort(reverse=True)

    # calculate the number of paths to sum over
    k = min(len(average_probability), number_of_top_paths)

    if use_js_div:
        threshold = compute_threshold_js_divergence(average_probability, k, number_of_walks, z_score)
    else:
        threshold = compute_threshold_sk_divergence(average_probability, k, number_of_walks, z_score)

    return threshold


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


def js_divergence(p: dict, q: dict, m=None):
    """
    Computes the Jensen-Shannon divergence between two discrete probability distributions p and q.
    If the average distribution of p and q has been pre-computed then it can be provided as an argument.
    """
    if m is None:
        m = compute_average_distribution(p, q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


def sk_divergence(p: dict, q: dict):
    """
    Computes the symmetric Kulbeck-Liebler divergence between two discrete probability distributions p and q.
    """
    return 0.5 * kl_divergence(p, q) + 0.5 * kl_divergence(q, p)


def kl_divergence(p: dict, q: dict):
    """
    Computes the Kullback-Leibler divergence between two discrete probability distributions p and q.
    """
    kl_div = sum([p[p_path] * np.log(p[p_path] / q[p_path])
                  for p_path in p.keys() if p_path in q.keys() and p[p_path] != 0])

    return kl_div


def compute_threshold_js_divergence(average_probability: list,
                                    k: int,
                                    number_of_walks: int,
                                    z_score: float):
    """
    Given the number of random walks ran, and the average path distribution of the two clusters, calculates a
    Jensen-Shannon divergence threshold for merger of the node clusters.
    """

    raise NotImplementedError


def compute_threshold_sk_divergence(average_probability: list,
                                    k: int,
                                    number_of_walks: int,
                                    z_score: float):
    """
    Given the number of random walks ran, and the average path distribution of the two clusters, calculates a
    symmetric Kulbeck-Liebler divergence threshold for merger of the node clusters.
    """

    # calculate expected variance if the null-hypothesis is true
    sigma_sk_squared = (1 / number_of_walks) * sum([average_probability[i] * (2 - average_probability[i])
                                                          for i in range(k)])
    sigma_sk = np.sqrt(sigma_sk_squared)
    # pre-factor is an empirical correction

    # calculate expected mean if the null-hypothesis is true
    mu_sk = (2 / number_of_walks) * sum([(1 - average_probability[i] / 2) for i in range(k)])
    # pre-factor is an empirical correction

    # compute the threshold for a given z-score
    theta_sk = mu_sk + z_score * sigma_sk

    return theta_sk















