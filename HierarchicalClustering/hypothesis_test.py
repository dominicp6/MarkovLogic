import numpy as np
from numba import njit
from scipy.stats import chi2


def test_quality_of_clusters(clusters: list[np.array], number_of_walks: int, significance_level: float):
    """
    Tests whether each cluster is a list of clusters passes the hypothesis test of the path count distributions
    being statistically similar.

    returns: True/False
    """
    for node_path_counts in clusters:
        result = hypothesis_test_path_symmetric_nodes(node_path_counts, number_of_walks, significance_level)
        if not result:
            return result

    return True


def hypothesis_test_path_symmetric_nodes(node_path_counts, number_of_walks, significance_level=0.5):
    """
    Given an array of node path counts, runs a statistical test on the path count distributions to test whether they
    violate the null hypothesis of being path symmetric.

    param: node_path_counts: array of node path counts of size (number of paths) x (number of nodes)
    param: number_of_walks: the total number of random walks that were run on the cluster
    param: significance_level: smaller values mean than larger deviations are permitted in the nodes path distributions
    and for them to still be considered as path symmetric.
    """

    number_of_paths, number_of_nodes = node_path_counts.shape

    # A single node is trivially of the same probability distribution as itself
    if number_of_nodes == 1:
        return True

    node_path_count_means = np.mean(node_path_counts, axis=1)

    # For one path, a different statistical test is required than when there is more than one path
    if number_of_paths == 1:
        Q_max = chi2.isf(significance_level, df=number_of_nodes)
        return Q_test_if_single_path(Q_max,
                                     node_path_counts[0],
                                     node_path_count_means[0],
                                     number_of_nodes,
                                     number_of_walks)
    else:
        number_of_hits = np.sum(node_path_counts, axis=0)
        mean_number_of_hits = np.mean(number_of_hits)

        Q_max = chi2.isf(significance_level, df=number_of_nodes * number_of_paths)
        return Q_test_if_multiple_paths(Q_max,
                                        node_path_counts,
                                        node_path_count_means,
                                        number_of_nodes,
                                        number_of_paths,
                                        mean_number_of_hits)


@njit
def Q_test_if_single_path(Q_max: float, node_path_counts: np.array, mean_path_count: int, number_of_nodes: int,
                          number_of_walks: int):
    """
    Tests whether the counts of a particular path are statistically similar for all nodes.

    node_path_counts: (1) x (number_of_nodes)
    returns: True/False
    """

    Q = 0
    prefactor = 1 / ((1 + 1 / number_of_nodes) * mean_path_count * (1 - mean_path_count / number_of_walks))

    for j in range(number_of_nodes):
        Q += prefactor * (mean_path_count - node_path_counts[j]) ** 2

        if Q > Q_max:
            return False

    return True


@njit
def Q_test_if_multiple_paths(Q_max: float, node_path_counts: np.array, node_path_count_means: np.array,
                             number_of_nodes: int, number_of_paths: int, mean_number_of_hits: np.array):
    """
    Tests whether the path count distributions are statistically similar for all nodes.

    node_path_counts: (number of paths) x (number of nodes)
    node_path_count_means: (1) x (number of paths)
    mean_number_of_hits: (1) x (number of nodes)
    returns: True/False
    """

    Q = 0
    for i in range(number_of_paths):
        prefactor = 1 / (node_path_count_means[i] * (1 + 1 / number_of_nodes) *
                         (1 - node_path_count_means[i] / mean_number_of_hits))
        for j in range(number_of_nodes):
            Q += prefactor * (node_path_count_means[i] - node_path_counts[i][j]) ** 2

            if Q > Q_max:
                return False

    return True


