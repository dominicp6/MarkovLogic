import numpy as np

from HierarchicalClustering.NodeRandomWalkData import NodeRandomWalkData
from HierarchicalClustering.stats_utils import compute_generalised_chi_squared_critical_value
from clustering_nodes_by_path_similarity import compute_top_paths


def test_quality_of_clusters(cluster_node_path_counts: list[np.array], number_of_walks: int, significance_level: float):
    """
    Tests whether each cluster is a list of clusters passes the hypothesis test of the path count distributions
    being statistically similar.

    returns: True/False
    """
    for node_path_counts in cluster_node_path_counts:
        result = hypothesis_test_path_symmetric_nodes(node_path_counts, number_of_walks, significance_level)
        if not result:
            return result

    return True


def covariance_matrix_of_count_residues(N: int, V: int, P: int, c_vector: np.array):
    """
    N - number of walks ran
    V - number of nodes
    P - number of paths
    c_vector - vector of average path counts

    """

    Sigma = np.zeros((P, P))
    for i in range(P):
        for j in range(P):
            if i == j:
                Sigma[i][j] = (c_vector[i] / N) * (1 - c_vector[j] / N)
            else:
                Sigma[i][j] = - (c_vector[i] * c_vector[j]) / (N ** 2)

    Sigma *= N * (1 - 1 / V)

    return Sigma


def compute_critical_Q_value(lambda_ks: np.array, N: int, V: int, P: int, significance_level: float):
    # construct weight and degree vectors of length V * P
    weight_vector = [lambda_ks] * V
    dof_vector = [V] * P * V
    centrality_vector = [0] * P * V
    normal_coefficient = 0

    return compute_generalised_chi_squared_critical_value(weight_vector, centrality_vector, dof_vector,
                                                          normal_coefficient, significance_level, V * N)


def append_null_counts(node_path_counts: np.array, number_of_walks: int):
    # size (1, number_of_nodes)
    zero_counts = number_of_walks - np.sum(node_path_counts, axis=0)

    return np.vstack([node_path_counts, zero_counts])


def hypothesis_test_path_symmetric_nodes(nodes: list[NodeRandomWalkData],
                                         number_of_walks: int,
                                         max_path_length: int,
                                         significance_level: float):
    """
    Given an array of node path counts, runs a statistical test on the path count distributions to test whether they
    violate the null hypothesis of being path symmetric.

    param: node_path_counts: array of node path counts of size (number of paths) x (number of nodes)
    param: number_of_walks: the total number of random walks that were run on the cluster
    param: significance_level: smaller values mean than larger deviations are permitted in the nodes path distributions
    and for them to still be considered as path symmetric.
    """

    # A single node is trivially of the same probability distribution as itself
    if len(nodes) == 1:
        return True

    # Attempt to run a hypothesis test on paths of decreasing length
    for path_length in range(max_path_length, 1):
        node_path_counts = compute_top_paths(nodes, , path_length)

        # If the nodes have no paths of this length then continue; try will a smaller path length
        if node_path_counts is None:
            continue

        # Otherwise run a hypothesis test
        else:
            node_path_counts = append_null_counts(node_path_counts, number_of_walks)
            number_of_paths, number_of_nodes = node_path_counts.shape
            mean_path_counts = np.mean(node_path_counts, axis=1)
            cov_matrix = covariance_matrix_of_count_residues(N=number_of_walks,
                                                             V=number_of_nodes,
                                                             P=number_of_paths,
                                                             c_vector=mean_path_counts)
            covariance_eigenvalues = np.linalg.eigvals(cov_matrix)

            Q_critical = compute_critical_Q_value(lambda_ks=covariance_eigenvalues,
                                                  N=number_of_walks,
                                                  V=number_of_nodes,
                                                  P=number_of_paths,
                                                  significance_level=significance_level)

            return Q_test(Q_critical=Q_critical,
                          c_matrix=node_path_counts,
                          c_vector=mean_path_counts,
                          V=number_of_nodes,
                          P=number_of_paths)


def Q_test(Q_critical: float, c_matrix: np.array, c_vector: np.array, V: int, P: int):
    """
    Tests whether the path count distributions are statistically similar for all nodes.

    c_matrix: counts of number of hits of each path for each node
    c_vector: mean count of each path averaged over the set of nodes
    V: the number of nodes
    P: the number of paths

    returns: True/False
    """

    Q = 0
    for i in range(P):
        for k in range(V):
            Q += (c_vector[i] - c_matrix[i][k]) ** 2

            if Q > Q_critical:
                return False

    return True
