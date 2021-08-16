import numpy as np
import math
import heapq
from HierarchicalClustering.NodeRandomWalkData import *
from sklearn.decomposition import PCA
from sklearn.cluster import Birch
from sklearn.cluster import KMeans
from scipy.stats import norm, t
from HierarchicalClustering.probability_distance_metrics import compute_divergence_of_top_n_paths

from HierarchicalClustering.hypothesis_test import hypothesis_test_path_symmetric_nodes, test_quality_of_clusters
import matplotlib.pyplot as plt
from typing import List, Dict, Set


def compute_theta_sym(alpha, number_of_walks_ran, length_of_walk):
    """
    Computes the threshold difference in the truncated hitting times of two nodes for the null hypothesis of the
    two nodes being path-symmetric to be violated at a significance level given by alpha_sym.

    return: theta_sym: used as a parameter for clustering based on truncated hitting time
    """
    # divide alpha sym by 2 because of the two-tailed nature of the t test (we are testing if the absolute value
    # of the difference in truncated hitting time exceeds a threshold)
    return ((length_of_walk - 1) / (2 ** 0.5 * number_of_walks_ran)) * t.isf(alpha / 2, df=number_of_walks_ran - 1)


def get_close_nodes_based_on_truncated_hitting_time(nodes_random_walk_data: Dict[str, NodeRandomWalkData],
                                                    theta_hit: float,
                                                    length_of_random_walks: int):
    """
    Returns those nodes from a list of nodes that have average truncated hitting time less than a threshold
    """
    return {node for node in nodes_random_walk_data.values() if node.average_hitting_time
            < theta_hit * length_of_random_walks}


def get_close_nodes_based_on_path_count(nodes_random_walk_data: Dict[str, NodeRandomWalkData]):
    """
    Returns those nodes from a list of nodes that have robust enough path count data to be subsequently merged based
    on path count distribution (i.e. their third most common path has at least 15 counts).
    """
    return {node for node in nodes_random_walk_data.values() if node.get_count_of_nth_path(n=3) >= 15}


def cluster_nodes_by_truncated_hitting_times(nodes: List[NodeRandomWalkData], threshold_hitting_time_difference: float):
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


def cluster_nodes_by_path_similarity(nodes: List[NodeRandomWalkData],
                                     number_of_walks: int,
                                     theta_sym: float,
                                     config: dict,
                                     threshold=None,
                                     num_top_paths=None,
                                     use_js_div=False):
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

    single_nodes.update(NodeClusterRandomWalkData([single_node]) for single_node in distance_symmetric_single_nodes)

    for distance_symmetric_cluster in distance_symmetric_clusters:
        path_symmetric_single_nodes, path_symmetric_clusters = cluster_nodes_by_path_distributions(
            distance_symmetric_cluster,
            number_of_walks,
            config,
            threshold=threshold,
            num_top_paths=num_top_paths,
            use_js_div=use_js_div
        )

        single_nodes.update(path_symmetric_single_nodes)
        clusters.extend(path_symmetric_clusters)

    return single_nodes, clusters


def cluster_nodes_by_path_distributions(nodes: List[NodeRandomWalkData],
                                        number_of_walks: int,
                                        config: dict,
                                        threshold=None,
                                        num_top_paths=None,
                                        use_js_div=False):
    """
    Clusters a list of nodes based on their empirical path distributions into path-symmetric clusters as follows

    1) Test statistically whether the path distributions of the nodes violate the null hypothesis of them being
    all path-symmetric.
    2) If the null hypothesis is violated, and the cluster is smaller than a threshold size, then cluster nodes by
    agglomerative clustering of the Jensen-Shannon divergence in path probability distributions. For larger clusters,
    Birch clustering of dimensionality-reduced path count features is used instead.
    """
    assert len(nodes) > 1, "Clustering by path distribution requires more than one node"

    try:
        clustering_type = config['clustering_type']
    except:
        clustering_type = None

    if threshold or clustering_type == 'agglomerative_clustering':
        single_nodes, clusters = cluster_nodes_by_distribution_divergence(nodes=nodes,
                                                                          significance_level=config['alpha'],
                                                                          number_of_walks=number_of_walks,
                                                                          threshold=threshold,
                                                                          num_top_paths=num_top_paths,
                                                                          use_js_div=use_js_div)
    else:
        node_path_counts = compute_top_paths(nodes, max_number_of_paths=config['max_num_paths'])

        if hypothesis_test_path_symmetric_nodes(node_path_counts,
                                                number_of_walks=number_of_walks,
                                                significance_level=config['alpha']):
            single_nodes = set()
            clusters = [NodeClusterRandomWalkData(nodes)]
        else:
            # if the number of nodes is smaller than then then the threshold size required for k-means clustering,
            # then cluster nodes based on agglomerative clustering of distribution divergence instead
            if len(nodes) <= config['clustering_method_threshold']:
                single_nodes, clusters = cluster_nodes_by_distribution_divergence(nodes=nodes,
                                                                                  significance_level=config['alpha'],
                                                                                  number_of_walks=number_of_walks,
                                                                                  threshold=None,
                                                                                  num_top_paths=num_top_paths,
                                                                                  use_js_div=use_js_div)

            # else cluster using Birch clustering on a PCA reduction of the path counts features
            else:
                single_nodes, clusters = \
                    cluster_nodes_by_path_count_features(nodes=nodes,
                                                         clustering_type=clustering_type,
                                                         pca_target_dimension=config['pca_dim'],
                                                         max_number_of_paths=config['max_num_paths'],
                                                         number_of_walks=number_of_walks,
                                                         significance_level=config['alpha'])

    return single_nodes, clusters


def cluster_nodes_by_distribution_divergence(nodes: List[NodeRandomWalkData],
                                             significance_level: float,
                                             number_of_walks: int,
                                             num_top_paths=None,
                                             threshold=None,
                                             use_js_div=False):
    """
    Performs agglomerative clustering of nodes based on the divergence between the distributions of their paths.

    Every node starts in its own cluster. The two clusters which have the smallest divergence in the
    distribution of their paths are then merged (providing that this divergence is strictly less than
    a threshold). This is repeated until all clusters have a divergence greater than the threshold.

    :param nodes:              the set of nodes to be clustered
    :param significance_level: the desired significance level for the hypothesis test of nodes being path symmetric.
                               Smaller values means that a larger difference between the distribution of the node's
                               paths is tolerated before they are considered not path-symmetric.
    :param number_of_walks:    the number of random walks that were run on the cluster to generate the random walk data
    :param num_top_paths:      the number of paths to consider when calculating the divergence
                               between the distributions (we consider only the top number_of_paths most common).
    :param threshold:          if not None, then use this (fixed) value as the distribution threshold i.e. don't
                               calculate the distribution threshold using a statistical significance level.
    :param use_js_div:         if False (default) then use symmetric Kulbeck-Liebler divergence, if True then use
                               Jensen-Shannon divergence as the divergence metric

    :return single_nodes, node_clusters: partitioning of the nodes into path-symmetric sets
    """

    # z-score for hypothesis test
    z = norm.isf(significance_level)
    clusters = [NodeClusterRandomWalkData([node]) for node in nodes]

    max_divergence = float('inf')
    cluster_to_merge1 = None
    cluster_to_merge2 = None

    while True:
        smallest_divergence = max_divergence
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                divergence, threshold_divergence = \
                    compute_divergence_of_top_n_paths(clusters[i],
                                                      clusters[j],
                                                      number_of_walks,
                                                      number_of_top_paths=num_top_paths,
                                                      z_score=z,
                                                      threshold=threshold,
                                                      use_js_div=use_js_div)

                if divergence < smallest_divergence and divergence < threshold_divergence:
                    smallest_divergence = divergence
                    cluster_to_merge1 = i
                    cluster_to_merge2 = j

        # if we've found a pair of clusters to merge, merge the two clusters and continue
        if smallest_divergence < max_divergence:
            clusters[cluster_to_merge1].merge(clusters[cluster_to_merge2])
            del clusters[cluster_to_merge2]
        # otherwise, stop merging
        else:
            break

    single_nodes, node_clusters = split_into_single_nodes_and_clusters(clusters)

    return single_nodes, node_clusters


def split_into_single_nodes_and_clusters(clusters):
    single_nodes = set()
    node_clusters = []
    for cluster in clusters:
        if cluster.number_of_nodes() == 1:
            single_nodes.add(cluster)
        else:
            node_clusters.append(cluster)

    return single_nodes, node_clusters


def compute_top_paths(nodes: List[NodeRandomWalkData], max_number_of_paths: int):
    """
    From each node in the list, finds the most common paths and constructs a path count vector.
    Returns a path-count feature array of the nodes of size (number of paths) x (number of nodes) where the (i,j) entry
    corresponds to the number of times that the ith indexed path occurred for the jth indexed node.
    """

    top_paths_of_each_node = []  # List[dict(path: path_counts)]
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


def cluster_nodes_by_path_count_features(nodes: List[NodeRandomWalkData],
                                         pca_target_dimension: int,
                                         max_number_of_paths: int,
                                         number_of_walks: int,
                                         significance_level: float,
                                         clustering_type: str):
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

    clustering_labels = compute_optimal_clustering(node_path_counts,
                                                   pca_target_dimension,
                                                   number_of_walks,
                                                   significance_level,
                                                   clustering_type)

    single_nodes, clusters = group_nodes_by_clustering_labels(nodes, clustering_labels)

    return single_nodes, clusters


def compute_optimal_clustering(node_path_counts: np.array,
                               pca_target_dimension: int,
                               number_of_walks: int,
                               significance_level: float,
                               clustering_type: str):
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
        if not clustering_type or clustering_type == 'kmeans':
            clusterer = KMeans(n_clusters=number_of_clusters, max_iter=30, n_init=8)
        elif clustering_type == 'birch':
            clusterer = Birch(n_clusters=number_of_clusters, threshold=0.05)
        else:
            raise ValueError('Invalid clustering type configuration')
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


def group_nodes_by_clustering_labels(nodes: List[NodeRandomWalkData], cluster_labels: List[int]):
    """
    Groups a list of nodes into single nodes and clusters from a list of cluster labels.

    :param nodes: the nodes to be grouped
    :param cluster_labels: a list of integers assigning each node to a given cluster
    """

    number_of_clusters = len(set(cluster_labels))
    original_clusters = [[] for _ in range(number_of_clusters)]
    for node_index, cluster_index in enumerate(cluster_labels):
        original_clusters[cluster_index].append(nodes[node_index])

    # split into single nodes and clusters
    single_nodes = set()
    clusters = []
    for cluster in original_clusters:
        if len(cluster) == 1:
            node = cluster[0]
            single_nodes.add(NodeClusterRandomWalkData([node]))
        else:
            clusters.append(NodeClusterRandomWalkData(cluster))

    return single_nodes, clusters


def _plot_clustering(principal_components: np.array, cluster_labels: List[int]):
    x, y = zip(*principal_components)
    x = np.array(x)
    y = np.array(y)
    fig, ax = plt.subplots()
    for g in np.unique(cluster_labels):
        ix = np.where(cluster_labels == g)
        ax.scatter(x[ix], y[ix], label=g, s=100)
    ax.legend()
    plt.show()


def merge_single_nodes_into_clusters(single_nodes_of_type: Dict[str, Set[NodeClusterRandomWalkData]],
                                     clusters: List[NodeClusterRandomWalkData],
                                     max_number_of_single_nodes: int):
    """
    Iteratively merge single nodes into node clusters based on the similarity of their path distribution
    until a desired number of single nodes remains.

    :param single_nodes_of_type:        A dictionary mapping from node type to lists of single nodes of that type.
    :param clusters:                    A list of all node clusters.
    :param max_number_of_single_nodes:  The desired maximum number of single nodes.
    """
    valid_types = {cluster.node_type for cluster in clusters}
    number_of_single_nodes_of_type = {node_type: len(nodes) for node_type, nodes in single_nodes_of_type.items()}
    number_of_single_nodes_of_valid_type = {node_type: num_nodes for node_type, num_nodes
                                            in number_of_single_nodes_of_type.items()
                                            if node_type in valid_types}
    number_of_single_nodes = sum(number_of_single_nodes_of_type.values())
    number_of_valid_single_nodes = sum(number_of_single_nodes_of_valid_type.values())

    number_of_nodes_to_merge = compute_number_of_nodes_to_merge(max_number_of_single_nodes,
                                                                number_of_single_nodes,
                                                                number_of_valid_single_nodes)

    single_nodes = set()
    if number_of_nodes_to_merge < 1:
        # single nodes are the same as those in single_nodes_of_type dict
        [single_nodes.update(node.node_names) for typed_single_nodes in single_nodes_of_type.values()
         for node in typed_single_nodes]
    else:
        single_nodes.update(get_single_nodes_that_cannot_be_merged(single_nodes_of_type, valid_types))
        order_of_node_types_to_merge = [node_type for node_type, _ in
                                        sorted(number_of_single_nodes_of_valid_type.items(),
                                               key=lambda item: item[1],
                                               reverse=True)]
        number_of_nodes_remaining_to_merge = number_of_nodes_to_merge
        # merge nodes of each type in turn until no more nodes left to merge
        for node_type in order_of_node_types_to_merge:
            if number_of_nodes_remaining_to_merge >= 1:
                number_of_nodes_to_merge_of_this_type = min(math.ceil(number_of_nodes_to_merge * (
                        number_of_single_nodes_of_valid_type[node_type] / number_of_valid_single_nodes)),
                                                            number_of_nodes_remaining_to_merge)
                nodes_of_type = single_nodes_of_type[node_type]

                remaining_nodes_of_type, clusters = merge_nodes(
                    list(nodes_of_type),
                    clusters,
                    number_of_nodes_to_merge_of_this_type)

                assert len(remaining_nodes_of_type) == len(nodes_of_type) - number_of_nodes_to_merge_of_this_type

                single_nodes.update(remaining_nodes_of_type)
                number_of_nodes_remaining_to_merge -= number_of_nodes_to_merge_of_this_type
            else:
                [single_nodes.update(node.node_names) for node in single_nodes_of_type[node_type]]

    clusters = [cluster.node_names for cluster in clusters]

    return single_nodes, clusters


def compute_number_of_nodes_to_merge(max_number_of_single_nodes, number_of_single_nodes, number_of_valid_single_nodes):
    if max_number_of_single_nodes:
        number_of_nodes_to_merge = number_of_single_nodes + 1 - max_number_of_single_nodes
        if number_of_nodes_to_merge > number_of_valid_single_nodes:
            print('Warning: Attempting to merge more single nodes than is '
                  'possible in merge_single_nodes_into_clusters.')
            number_of_nodes_to_merge = max_number_of_single_nodes
    else:
        number_of_nodes_to_merge = 0

    return number_of_nodes_to_merge


def get_single_nodes_that_cannot_be_merged(single_nodes_of_type: Dict[str, Set[NodeClusterRandomWalkData]],
                                           valid_types: Set):
    """
    Finds the set of all nodes of a type different from a set of valid types.
    """
    invalid_nodes = set()
    [invalid_nodes.update(node.node_names) for node_type, nodes_of_type in single_nodes_of_type.items()
     for node in nodes_of_type if node_type not in valid_types]
    return invalid_nodes


def merge_nodes(single_nodes: List[NodeClusterRandomWalkData],
                clusters: List[NodeClusterRandomWalkData],
                number_of_nodes_to_merge: int,
                use_js_div=False):
    """
    Recursively merge single nodes into clusters, merging at each step the single node with a path distribution
    most similar to the path distribution in a node cluster.
    """
    assert number_of_nodes_to_merge >= 1
    max_divergence = float('inf')
    single_node_to_merge = None
    cluster_to_merge_into = None
    number_of_nodes_remaining_to_merge = number_of_nodes_to_merge
    while True:
        smallest_divergence = max_divergence
        for i in range(len(single_nodes)):
            for j in range(len(clusters)):
                if clusters[j].node_type == single_nodes[i].node_type:
                    divergence = compute_divergence_of_top_n_paths(single_nodes[i],
                                                                   clusters[j],
                                                                   z_score=None,
                                                                   use_js_div=use_js_div)

                    if divergence < smallest_divergence:
                        smallest_divergence = divergence
                        single_node_to_merge = i
                        cluster_to_merge_into = j
                else:
                    continue

        assert smallest_divergence < max_divergence

        clusters[cluster_to_merge_into].merge(single_nodes[single_node_to_merge])
        del single_nodes[single_node_to_merge]

        number_of_nodes_remaining_to_merge -= 1
        if number_of_nodes_remaining_to_merge > 0:
            continue
        else:
            break

    single_node_names = set()
    [single_node_names.update(node.node_names) for node in single_nodes]

    return single_node_names, clusters


def prune_nodes(single_nodes_of_type: Dict[str, Set[NodeClusterRandomWalkData]],
                pruning_value: int,
                use_js_div=False):
    """
    Given a dictionary mapping node type to single nodes, removes nodes of each type in proportion to their
    population until the number of single nodes remaining is equal to the specified pruning_value.

    For each node type, the nodes that are removed are those which have path distributions most dissimilar to
    all other nodes of that type, as measured by their Jensen-Shannon divergence.
    """
    number_of_nodes_of_type = {node_type: len(nodes) for node_type, nodes in single_nodes_of_type.items()}
    number_of_single_nodes = sum(number_of_nodes_of_type.values())
    if pruning_value:
        number_of_nodes_to_prune = number_of_single_nodes + 1 - pruning_value  # +1 to account for the source node
    else:
        number_of_nodes_to_prune = 0

    single_nodes = set()
    if number_of_nodes_to_prune < 1:
        # no need to prune nodes
        [single_nodes.update(node.node_names) for typed_single_nodes in single_nodes_of_type.values()
         for node in typed_single_nodes]
    else:
        order_of_node_types_to_prune = [node_type for node_type, _ in
                                        sorted(number_of_nodes_of_type.items(),
                                               key=lambda item: item[1],
                                               reverse=True)]
        number_of_nodes_remaining_to_prune = number_of_nodes_to_prune
        # prune nodes of each type in turn until no more node left to prune
        for node_type in order_of_node_types_to_prune:
            if number_of_nodes_remaining_to_prune >= 1:
                number_of_nodes_to_prune_of_this_type = min(math.ceil(number_of_nodes_to_prune * (
                        number_of_nodes_of_type[node_type] / number_of_single_nodes)),
                                                            number_of_nodes_remaining_to_prune)

                nodes_to_remove = get_nodes_to_remove(nodes=list(single_nodes_of_type[node_type]),
                                                      num_nodes_to_prune=number_of_nodes_to_prune_of_this_type,
                                                      use_js_div=use_js_div)

                nodes_of_type = set()
                [nodes_of_type.update(node.node_names) for node in single_nodes_of_type[node_type]]
                remaining_nodes_of_type = nodes_of_type.difference(nodes_to_remove)
                single_nodes.update(remaining_nodes_of_type)
                number_of_nodes_remaining_to_prune -= number_of_nodes_to_prune_of_this_type
            else:
                [single_nodes.update(node.node_names) for node in single_nodes_of_type[node_type]]

    return single_nodes


def get_nodes_to_remove(nodes: List[NodeClusterRandomWalkData], num_nodes_to_prune, use_js_div=False):
    """
    Given a list of nodes, identifies the num_nodes_to_prune many nodes which have the the largest Jensen-Shannon
    divergence in path-distributions compared to the remaining nodes.
    """
    minimal_divergence_of_node = defaultdict(lambda: float('inf'))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            divergence = compute_divergence_of_top_n_paths(nodes[i],
                                                           nodes[j],
                                                           use_js_div=use_js_div,
                                                           z_score=None)
            (node_i_name,) = nodes[i].node_names
            (node_j_name,) = nodes[j].node_names
            minimal_divergence_of_node[node_i_name] = min(minimal_divergence_of_node[node_i_name], divergence)
            minimal_divergence_of_node[node_j_name] = min(minimal_divergence_of_node[node_j_name], divergence)

    nodes_to_prune = heapq.nlargest(num_nodes_to_prune,
                                    minimal_divergence_of_node.items(), key=lambda item: item[1])
    node_names_to_prune = [node_name for node_name, largest_minimal_divergence in nodes_to_prune]

    return node_names_to_prune
