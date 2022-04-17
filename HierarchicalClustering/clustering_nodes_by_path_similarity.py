import numpy as np
from NodeRandomWalkData import *
from sklearn.decomposition import PCA
from sklearn.cluster import Birch
from scipy.stats import norm, t
from js_divergence_utils import compute_js_divergence_of_top_n_paths

from hypothesis_test import hypothesis_test_path_symmetric_nodes, test_quality_of_clusters
import matplotlib.pyplot as plt


def compute_theta_sym(alpha_sym, number_of_walks_ran, length_of_walk):
    """
    Computes the threshold difference in the truncated hitting times of two nodes for the null hypothesis of the
    two nodes being path-symmetric to be violated at a significance level given by alpha_sym.

    return: theta_sym: used as a parameter for clustering based on truncated hitting time
    """

    return ((length_of_walk - 1) / (2 * number_of_walks_ran) ** 0.5) * t.isf(alpha_sym, df=number_of_walks_ran - 1)


def get_commonly_encountered_nodes(nodes_random_walk_data: dict[str, NodeRandomWalkData],
                                   number_of_walks_ran: int,
                                   epsilon: float):
    """
    Returns those nodes from a list of nodes that have robust enough path count data to be subsequently merged based
    on path count distribution (i.e. their third most common path has at least 10 counts).
    """
    return {node for node in nodes_random_walk_data.values()
            if node.get_count_of_nth_path(n=3) >= number_of_walks_ran/(number_of_walks_ran*epsilon**2 + 1)}


def cluster_nodes_by_path_similarity(nodes: list[NodeRandomWalkData], number_of_walks: int, theta_sym: float,
                                     config: dict):
    """
    Clusters nodes from a hypergraph into groups which are symmetrically related relative to a source node.

    Firstly, nodes are grouped into distance-symmetric clusters; sets of nodes where the difference in the average
    truncated hitting times from the source node for any two nodes in the set is no greater than a specified threshold.

    Secondly, within each distance-symmetric cluster, we further cluster together nodes based on the similarity
    in their distribution of paths to yield a set of path-symmetric clusters. If the cluster is a singleton set then we
    add its member to a set of 'single nodes'.

    returns: the set of single nodes and a list of path-symmetric node clusters
    """
    single_nodes = set()
    clusters = []

    distance_symmetric_single_nodes, distance_symmetric_clusters = cluster_nodes_by_truncated_hitting_times(
        nodes, threshold_hitting_time_difference=theta_sym)

    single_nodes.update(node.name for node in distance_symmetric_single_nodes)

    for distance_symmetric_cluster in distance_symmetric_clusters:
        path_symmetric_single_nodes, path_symmetric_clusters = cluster_nodes_by_path_distributions(
            distance_symmetric_cluster,
            number_of_walks,
            config
        )

        single_nodes.update(path_symmetric_single_nodes)
        clusters.extend(path_symmetric_clusters)

    return single_nodes, clusters


def cluster_nodes_by_truncated_hitting_times(nodes: list[NodeRandomWalkData], threshold_hitting_time_difference: float):
    """
    Clusters a list of nodes from a hypergraph into groups based on the truncated hitting criterion as follows:

    Let h_{j} be the average truncated hitting time of node v_{j}. Nodes v_{j} are grouped into disjoint sets A_{k}
    such that: for all v_{j} in A_{k} there exists a node v_{j'} in A_{k} such that
    |h_{j} - h_{j'}| <= threshold_hitting_time_difference.
    Ref: https://alchemy.cs.washington.edu/papers/kok10/kok10.pdf
    """

    # sort the nodes in the hypergraph in increasing order of average hitting time
    nodes = sorted(nodes, key=lambda n: n.average_hitting_time)
    current_hitting_time = nodes[0].average_hitting_time
    distance_symmetric_clusters = []
    distance_symmetric_single_nodes = set()
    distance_symmetric_cluster = []
    for node in nodes:
        if (node.average_hitting_time - current_hitting_time) < threshold_hitting_time_difference:
            distance_symmetric_cluster.append(node)
        else:
            if len(distance_symmetric_cluster) == 1:
                distance_symmetric_single_nodes.update(distance_symmetric_cluster)
            else:
                distance_symmetric_clusters.append(distance_symmetric_cluster.copy())

            distance_symmetric_cluster.clear()
            distance_symmetric_cluster.append(node)

        current_hitting_time = node.average_hitting_time

    # if distance_symmetric_cluster is not empty, classify it as a single node or a cluster
    if distance_symmetric_cluster is not None:
        if len(distance_symmetric_cluster) > 1:
            distance_symmetric_clusters.append(distance_symmetric_cluster)
        else:
            distance_symmetric_single_nodes.update(distance_symmetric_cluster)

    return distance_symmetric_single_nodes, distance_symmetric_clusters


def cluster_nodes_by_path_distributions(nodes: list[NodeRandomWalkData], number_of_walks: int,
                                        config: dict):
    """
    Clusters a list of nodes based on their empirical path distributions into path-symmetric clusters as follows

    1) Test statistically whether the path distributions of the nodes violate the null hypothesis of them being
    all path-symmetric.
    2) If the null hypothesis is violated, and the cluster is smaller than a threshold size, then cluster nodes by
    agglomerative clustering of the Jensen-Shannon divergence in path probability distributions. For larger clusters,
    k-means clustering of dimensionality-reduced path count features is used instead.
    """
    assert len(nodes) > 1, "Clustering by path distribution requires more than one node"

    node_path_counts = compute_top_paths(nodes, max_number_of_paths=config['max_num_paths'])

    if hypothesis_test_path_symmetric_nodes(node_path_counts,
                                            number_of_walks=number_of_walks,
                                            significance_level=config['theta_p']):
        single_nodes = set()
        clusters = [[node.name for node in nodes]]
    else:
        # if the number of nodes is smaller than then then the threshold size required for k-means clustering,
        # then cluster nodes based on agglomerative clustering of js divergence instead
        if len(nodes) <= config['clustering_method_threshold']:
            single_nodes, clusters = cluster_nodes_by_js_divergence(nodes=nodes,
                                                                    significance_level=config['theta_p'],
                                                                    number_of_walks=number_of_walks,
                                                                    max_number_of_paths=3)
        # else cluster based k-means cluster on a PCA reduction of the path counts features
        else:
            single_nodes, clusters = cluster_nodes_by_birch(nodes=nodes,
                                                            pca_target_dimension=config['pca_dim'],
                                                            max_number_of_paths=config['max_num_paths'],
                                                            number_of_walks=number_of_walks,
                                                            significance_level=config['theta_p'])

    return single_nodes, clusters


def compute_top_paths(nodes: list[NodeRandomWalkData], max_number_of_paths: int):
    """
    From each node in the list, finds the most common paths and constructs a path count vector.
    Returns a path-count feature array of the nodes of size (number of paths) x (number of nodes) where the (i,j) entry
    corresponds to the number of times that the ith indexed path occurred for the jth indexed node.
    """

    top_paths_of_each_node = []  # list[dict(path: path_counts)]
    [top_paths_of_each_node.append(node.get_top_paths(max_number_of_paths)) for node in nodes]

    unique_paths = set()
    [unique_paths.update(paths.keys()) for paths in top_paths_of_each_node]
    number_unique_paths = len(unique_paths)
    del unique_paths

    path_string_to_path_index = {}
    # Array size (number of paths) x (number of nodes), each entry is the count of that path for that node:
    node_path_counts = np.zeros([number_unique_paths, len(nodes)])
    for node_index, node_paths in enumerate(top_paths_of_each_node):
        for path, path_count in node_paths.items():
            if path not in path_string_to_path_index.keys():
                path_index = len(path_string_to_path_index)
                path_string_to_path_index[path] = path_index
            else:
                path_index = path_string_to_path_index[path]

            node_path_counts[path_index][node_index] = path_count

    return node_path_counts


def cluster_nodes_by_js_divergence(nodes: list[NodeRandomWalkData],
                                   significance_level: float,
                                   number_of_walks: int,
                                   max_number_of_paths: int):
    """
    Performs agglomerative clustering of nodes based on the Jensen-Shannon divergence between the distributions of
    their paths.

    Every node starts in its own cluster. The two clusters which have the smallest Jensen-Shannon divergence in the
    distribution of their paths are then merged (providing that this divergence is strictly less than
    threshold_js_divergence). This is repeated until all clusters have a divergence greater than the threshold.

    :param nodes: the set of nodes to be clustered
    :param significance_level: the desired significance level for the hypothesis test of nodes being path symmetric.
                               Smaller values means that a larger difference between the distribution of the node's
                               paths is tolerated before they are considered not path-symmetric.
    :param number_of_walks: the number of random walks that were run on the cluster to generate the random walk data
    :param max_number_of_paths: the number of paths to consider when calculating the Jensen-Shannon divergence
                            between the distributions (we consider only the top number_of_paths most common).
    :return single_nodes, clusters: the final clustering of the nodes
    """

    # z-score for hypothesis test
    z = norm.isf(significance_level)
    js_clusters = [NodeClusterRandomWalkData([node]) for node in nodes]

    max_divergence = float('inf')
    cluster_to_merge1 = None
    cluster_to_merge2 = None

    while True:
        smallest_divergence = max_divergence
        for i in range(len(js_clusters)):
            for j in range(i + 1, len(js_clusters)):
                js_divergence, threshold_js_divergence = \
                    compute_js_divergence_of_top_n_paths(js_clusters[i],
                                                         js_clusters[j],
                                                         max_number_of_paths,
                                                         number_of_walks,
                                                         z_score=z)

                if js_divergence < smallest_divergence and js_divergence < threshold_js_divergence:
                    smallest_divergence = js_divergence
                    cluster_to_merge1 = i
                    cluster_to_merge2 = j

        # if we've found a pair of clusters to merge, merge the two clusters and continue
        if smallest_divergence < max_divergence:
            js_clusters[cluster_to_merge1].merge(js_clusters[cluster_to_merge2])
            del js_clusters[cluster_to_merge2]
        # otherwise, stop merging
        else:
            break

    # split up the js_clusters into single nodes and clusters
    single_nodes = set()
    clusters = []
    for js_cluster in js_clusters:
        if js_cluster.number_of_nodes() == 1:
            (node_name,) = js_cluster.node_names
            single_nodes.add(node_name)
        else:
            clusters.append(js_cluster.node_names)

    return single_nodes, clusters


def cluster_nodes_by_birch(nodes: list[NodeRandomWalkData], pca_target_dimension: int, max_number_of_paths: int,
                           number_of_walks: int, significance_level: float):
    """
    Considers the top number_of_paths most frequent paths for each node, standardises these path distributions, then
    dimensionality reduces them using PCA (from a space of dimension equal to the number of distinct paths into a space
    of dimension equal to pca_target_dimension), then finally performs birch clustering on these principal components,
    where the optimal number of clusters is the smallest value whose clusters all pass the hypothesis test of the
    nodes having path distributions consistent with being statistically similar.

    :param nodes: The nodes to be clustered.
    :param pca_target_dimension: The dimension of feature space after dimensionality reduction with PCA.
    :param max_number_of_paths: The number of paths to consider for the path distribution feature vectors (we consider
                                the number_of_paths most common).
    :param number_of_walks: the number of random walks that were run on the cluster to generate the random walk data
    :param significance_level: the desired significance level for the hypothesis test of nodes being path symmetric.
                               Smaller values means that a larger difference between the distribution of the node's
                               paths is tolerated before they are considered not path-symmetric.
    :return: single_nodes, clusters: the final clustering of the nodes
    """
    node_path_counts = compute_top_paths(nodes, max_number_of_paths)

    clustering_labels = compute_optimal_birch_clustering(node_path_counts,
                                                         pca_target_dimension,
                                                         number_of_walks,
                                                         significance_level)

    single_nodes, clusters = group_nodes_by_clustering_labels(nodes, clustering_labels)

    return single_nodes, clusters


def compute_optimal_birch_clustering(node_path_counts: np.array,
                                     pca_target_dimension: int,
                                     number_of_walks: int,
                                     significance_level: float):
    """
    Given an array of node path counts, clusters the nodes into an optimal number of clusters using birch clustering.
    The number of clusters is incrementally increased. The optimal number of clusters is the smallest number of clusters
    such that have statistically similar path count distributions at a specified significance level.
    """
    standardized_path_counts = (
            (node_path_counts - np.mean(node_path_counts, axis=1)[:, None]) / np.mean(node_path_counts, axis=1)[:,
                                                                              None]).T

    feature_vectors = compute_principal_components(feature_vectors=standardized_path_counts,
                                                   target_dimension=pca_target_dimension)

    number_of_feature_vectors = feature_vectors.shape[0]

    cluster_labels = None
    for number_of_clusters in range(2, number_of_feature_vectors):  # start from 2 since zero/one clusters is invalid
        # clusterer = KMeans(n_clusters=number_of_clusters, max_iter=30, n_init=8)
        clusterer = Birch(n_clusters=number_of_clusters, threshold=0.05)

        cluster_labels = clusterer.fit_predict(feature_vectors)
        node_path_counts_of_clusters = get_node_path_counts_of_clusters(node_path_counts, cluster_labels)
        if test_quality_of_clusters(node_path_counts_of_clusters, number_of_walks, significance_level):
            return cluster_labels
        else:
            continue

    return cluster_labels


def compute_principal_components(feature_vectors: np.array, target_dimension: int):
    """
    Dimensionality reduces feature vectors into a target dimension using Principal Component Analysis.

    :param feature_vectors: (number_of_feature_vectors) x (dimension_of_feature_vectors)
    :param target_dimension: the desired dimension of the dimensionality-reduced data
    :return: principal_components: the dimensionality-reduced feature vectors
    """
    original_dimension = feature_vectors.shape[1]
    if original_dimension > target_dimension:
        pca = PCA(n_components=target_dimension)
        principal_components = pca.fit_transform(feature_vectors)
    else:
        principal_components = feature_vectors

    return principal_components


def get_node_path_counts_of_clusters(node_path_counts: np.array, cluster_labels: np.array):
    number_of_clusters = len(set(cluster_labels))

    path_counts_for_cluster = [[] for _ in range(number_of_clusters)]

    for node_index, cluster_index in enumerate(cluster_labels):
        path_counts_for_cluster[cluster_index].append(node_path_counts[:, node_index])

    for cluster_index in range(number_of_clusters):
        # transpose the arrays into the standard shape of (# unique paths in cluster) x (# nodes in cluster)
        path_counts_for_cluster[cluster_index] = np.array(path_counts_for_cluster[cluster_index]).T
        # remove any paths that have zero count for every node in the cluster
        path_counts_for_cluster[cluster_index] = path_counts_for_cluster[cluster_index][~np.all(
            path_counts_for_cluster[cluster_index] == 0,
            axis=1)]

    return path_counts_for_cluster


def group_nodes_by_clustering_labels(nodes: list[NodeRandomWalkData], cluster_labels: list[int]):
    """
    Groups a list of nodes into single nodes and clusters from a list of cluster labels.

    :param nodes: the nodes to be grouped
    :param cluster_labels: a list of integers assigning each node to a given cluster
    """
    number_of_clusters = len(set(cluster_labels))
    original_clusters = [[] for _ in range(number_of_clusters)]
    for node_index, cluster_index in enumerate(cluster_labels):
        original_clusters[cluster_index].append(nodes[node_index].name)

    # split into single nodes and clusters
    single_nodes = set()
    clusters = []
    for cluster in original_clusters:
        if len(cluster) == 1:
            node_name = cluster[0]
            single_nodes.add(node_name)
        else:
            clusters.append(cluster)

    return single_nodes, clusters


# TODO: remove after debugging
def plot_clustering(principal_components: np.array, cluster_labels: list[int]):
    x, y = zip(*principal_components)
    x = np.array(x)
    y = np.array(y)
    fig, ax = plt.subplots()
    for g in np.unique(cluster_labels):
        ix = np.where(cluster_labels == g)
        ax.scatter(x[ix], y[ix], label=g, s=100)
    ax.legend()
    plt.show()
