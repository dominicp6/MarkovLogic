import numpy as np
from NodeRandomWalkData import *
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from js_divergence_utils import compute_js_divergence_of_top_n_paths
import matplotlib.pyplot as plt


def get_close_nodes(nodes_random_walk_data: dict[str, NodeRandomWalkData], threshold_hitting_time: float):
    return {node for node in nodes_random_walk_data.values() if node.average_hitting_time < threshold_hitting_time}


def cluster_nodes_by_path_similarity(nodes: list[NodeRandomWalkData], config: dict):
    """
    Clusters nodes from a hypergraph into groups which are symmetrically related relative to a source node.

    Firstly, nodes are grouped into distance-symmetric clusters; sets of nodes where the difference in the average
    truncated hitting times from the source node for any two nodes in the set is no greater than a specified threshold.

    Secondly, within each distance-symmetric cluster, we identify path-symmetric nodes through agglomerative clustering
    of the nodes based on their Jensen-Shannon divergence in their distribution of paths.

    Finally, from these sets of path-symmetric nodes we output single nodes (a list of the nodes in all the
    singleton sets) and clusters (a list of all the non-singleton sets).
    """
    single_nodes = set()
    clusters = []
    distance_symmetric_single_nodes, distance_symmetric_clusters = cluster_nodes_by_truncated_hitting_times(
        nodes, threshold_hitting_time_difference=config['theta_sym'])

    single_nodes.update(node.name for node in distance_symmetric_single_nodes)

    for distance_symmetric_cluster in distance_symmetric_clusters:
        path_symmetric_single_nodes, path_symmetric_clusters = cluster_nodes_by_path_distributions(
            distance_symmetric_cluster,
            number_of_paths=config['num_top'],
            max_js_divergence=config['max_js_div'],
            threshold_js_divergence=config['theta_js'],
            pca_target_dimension=config['pca_dim'],
            threshold_for_pca_clustering=config['pca_threshold'],
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


def cluster_nodes_by_path_distributions(nodes: list[NodeRandomWalkData], number_of_paths: int, max_js_divergence=0.003,
                                        pca_target_dimension=2, threshold_for_pca_clustering=4,
                                        threshold_js_divergence=0.0005):

    assert len(nodes) > 1, "Clustering by path distribution requires more than one node"
    assert threshold_for_pca_clustering >= 4, "PCA clustering requires at least 4 nodes"

    # if the largest js divergence is smaller than a max_js_divergence parameter, then all the nodes are considered
    # path symmetric and so appear in a single cluster
    largest_js_divergence = compute_largest_js_divergence(nodes, number_of_paths)
    if largest_js_divergence < max_js_divergence:
        single_nodes = set()
        clusters = [[node.name for node in nodes]]
    else:
        # if the number of nodes is smaller than then then the threshold size required for pca clustering,
        # then cluster nodes based on agglomerative clustering of js divergence
        if len(nodes) <= threshold_for_pca_clustering:
            single_nodes, clusters = cluster_nodes_by_js_divergence(nodes=nodes,
                                                                    threshold_js_divergence=threshold_js_divergence,
                                                                    number_of_paths=number_of_paths)
        # else cluster based on a pca reduction of the path counts
        else:
            single_nodes, clusters = cluster_nodes_by_pca_of_path_counts(nodes=nodes,
                                                                         pca_target_dimension=pca_target_dimension,
                                                                         number_of_paths=number_of_paths)

    return single_nodes, clusters


def compute_largest_js_divergence(nodes: list[NodeRandomWalkData], number_of_paths: int):
    """
    Given a list of NodeRandomWalkData, computes the largest Jensen-Shannon divergence between the path
    distributions of all possible pairings of nodes.

    :param nodes: the set of nodes to calculate the Jensen-Shannon divergence between
    :param number_of_paths: the number of paths to consider when calculating the Jensen-Shannon divergence
                            between the path distributions (we consider only the top number_of_paths most common).
    :return largest_divergence: the largest Jensen-Shannon divergence between any two node pairings
    """
    js_clusters = [NodeClusterRandomWalkData([node]) for node in nodes]
    largest_divergence = - float('inf')
    for i in range(len(js_clusters)):
        for j in range(i + 1, len(js_clusters)):
            js_divergence = compute_js_divergence_of_top_n_paths(js_clusters[i], js_clusters[j], number_of_paths)

            if js_divergence > largest_divergence:
                largest_divergence = js_divergence

    return largest_divergence


def cluster_nodes_by_js_divergence(nodes: list[NodeRandomWalkData],
                                   threshold_js_divergence: float, number_of_paths: int):
    """
    Performs agglomerative clustering of nodes based on the Jensen-Shannon divergence between the distributions of
    their paths.

    Every node starts in its own cluster. The two clusters which have the smallest Jensen-Shannon divergence in the
    distribution of their paths are then merged (providing that this divergence is strictly less than
    threshold_js_divergence). This is repeated until all clusters have a divergence greater than the threshold.

    :param nodes: the set of nodes to be clustered
    :param threshold_js_divergence: the maximum permitted Jensen-Shannon divergence for merging two clusters
    :param number_of_paths: the number of paths to consider when calculating the Jensen-Shannon divergence
                            between the distributions (we consider only the top number_of_paths most common).
    :return single_nodes, clusters: the final clustering of the nodes
    """
    js_clusters = [NodeClusterRandomWalkData([node]) for node in nodes]

    max_divergence = float('inf')
    cluster_to_merge1 = None
    cluster_to_merge2 = None

    while True:
        smallest_divergence = max_divergence
        for i in range(len(js_clusters)):
            for j in range(i + 1, len(js_clusters)):
                js_divergence = compute_js_divergence_of_top_n_paths(js_clusters[i], js_clusters[j], number_of_paths)

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


def cluster_nodes_by_pca_of_path_counts(nodes: list[NodeRandomWalkData],
                                        pca_target_dimension: int,
                                        number_of_paths: int):
    """
    Considers the top number_of_paths most frequent paths for each node, standardises these path distributions, then
    dimensionality reduces them using PCA (from a space of dimension equal to the number of distinct paths into a space
    of dimension equal to pca_target_dimension), then finally performs k-means clustering on these principal components,
    where the optimal number of clusters is the clustering which maximises the silhouette score [1].

    [1] https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html.

    :param nodes: The nodes to be clustered.
    :param pca_target_dimension: The dimension of feature space after dimensionality reduction with PCA.
    :param number_of_paths: The number of paths to consider for the path distribution feature vectors (we consider the
                            number_of_paths most common).
    :return: single_nodes, clusters: the final clustering of the nodes
    """
    standardized_path_distributions, number_of_unique_paths = \
        compute_standardized_path_distributions_and_number_of_unique_paths(nodes, number_of_paths)

    path_distribution_principal_components = compute_principal_components(
        feature_vectors=standardized_path_distributions,
        target_dimension=pca_target_dimension)

    clustering_labels = compute_optimal_k_means_clustering(path_distribution_principal_components)

    plot_clustering(path_distribution_principal_components, clustering_labels)

    single_nodes, clusters = group_nodes_by_clustering_labels(nodes, clustering_labels)

    return single_nodes, clusters


def compute_standardized_path_distributions_and_number_of_unique_paths(nodes: list[NodeRandomWalkData],
                                                                       number_of_paths: int):
    """
    From a list of node random walk data, finds the top number_of_paths most common paths for each node and
    constructs a path count vector. A feature vector is then constructed from the path counts via the transformation:
    (path_count) -> ( (path_count - mean_path_count) / mean_path_count )
    where mean_path_count is the average count for that path across all of the nodes in the list of node random walk
    data.

    :param nodes: The nodes to compute the standardized path distributions for.
    :param number_of_paths: The number of most common paths to consider for each node.
    :return number_unique_paths: The number of unique paths appearing amongst the nodes' top number_of_paths most
                                 common paths.
            mean_adjusted_path_counts: (number of unique paths) x (number of nodes)
    """

    top_paths_of_each_node = []  # list[dict(path: path_counts)]
    [top_paths_of_each_node.append(node.get_top_paths(number_of_paths)) for node in nodes]

    unique_paths = set()
    [unique_paths.update(paths.keys()) for paths in top_paths_of_each_node]
    number_unique_paths = len(unique_paths)
    del unique_paths

    path_string_to_path_index = {}
    # Array size (number of paths) x (number of nodes), each entry is the count of that path for that node:
    node_path_counts = np.zeros([number_unique_paths, len(nodes)])
    path_index = -1
    for node_index, node_paths in enumerate(top_paths_of_each_node):
        for path, path_count in node_paths.items():
            if path not in path_string_to_path_index:
                path_index += 1
                path_string_to_path_index[path] = path_index
            else:
                path_index = path_string_to_path_index[path]

            node_path_counts[path_index][node_index] = path_count

    # This choice of standardization means that paths which have larger fractional variations in their counts between
    # the nodes, and so are better indicators for distinguishing nodes, have higher-weighted features.
    node_path_features = (
            (node_path_counts - np.mean(node_path_counts, axis=1)[:, None]) / np.mean(node_path_counts, axis=1)[:,
                                                                              None]).T

    return node_path_features, number_unique_paths


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


def compute_optimal_k_means_clustering(feature_vectors: np.array):
    """
    Clusters feature vectors (shape (number_of_feature_vectors)x(dimensionality_of_feature_vector)) into an optimal
    number of clusters. Returns a vector of cluster labels which indicates which cluster each feature vector belongs to.
    """

    number_of_feature_vectors = feature_vectors.shape[0]

    # to limit unnecessary computation, only check clusterings up to number_clusters = (1/2) * number_of_feature_vectors
    max_number_of_clusters = int(number_of_feature_vectors / 2)

    silhouette_scores_of_clusterings = np.zeros(max_number_of_clusters - 1)
    cluster_labellings = np.zeros((max_number_of_clusters - 1, number_of_feature_vectors), dtype=int)

    for number_of_clusters in range(2, max_number_of_clusters):  # start from 2 since zero/one clusters is invalid
        clusterer = KMeans(n_clusters=number_of_clusters, max_iter=30, n_init=8)
        cluster_labels = clusterer.fit_predict(feature_vectors)
        clustering_index = number_of_clusters - 2
        cluster_labellings[clustering_index, :] = cluster_labels
        silhouette_score_of_clustering = silhouette_score(feature_vectors, cluster_labels)
        silhouette_scores_of_clusterings[clustering_index] = silhouette_score_of_clustering

    optimal_clustering_index = np.argmax(silhouette_scores_of_clusterings)
    cluster_labels = cluster_labellings[optimal_clustering_index, :]  # list[int]

    return cluster_labels


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
