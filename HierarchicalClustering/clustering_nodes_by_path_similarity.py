import numpy as np
from NodeRandomWalkData import *
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from js_divergence_utils import compute_js_divergence_of_top_n_paths


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
            number_of_paths=config['num_top'])

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

    # append the last cluster to the list if it is not empty
    if distance_symmetric_cluster is not None:
        distance_symmetric_clusters.append(distance_symmetric_cluster)

    return distance_symmetric_single_nodes, distance_symmetric_clusters


def cluster_nodes_by_path_distributions(nodes: list[NodeRandomWalkData], number_of_paths: int,
                                        pca_target_dimension=2):

    if len(nodes) <= 5:
        print('Small cluster')
        input()
        return cluster_nodes_by_js_divergence(nodes=nodes, threshold_js_divergence=1.0, number_of_paths=3)

    else:
        print('Large cluster')
        input()

        print(f'Number of nodes {len(nodes)}')

        encountered_paths = set()
        path_to_path_id = defaultdict(lambda: -1)
        top_n_paths = []
        for node in nodes:
            top_n_paths.append(node.get_top_n_paths(number_of_paths))

        path_list = []
        [path_list.extend(paths.keys()) for paths in top_n_paths]
        number_unique_paths = len(set(path_list))
        path_count_array = np.zeros([number_unique_paths, len(nodes)])

        print(f'Number of unique paths {number_unique_paths}')

        for node_id, node_paths in enumerate(top_n_paths):
            print(nodes[node_id].name)
            for path, path_count in node_paths.items():
                if path_to_path_id[path] == -1:
                    encountered_paths.add(path)
                    path_id = len(encountered_paths) - 1
                    path_to_path_id[path] = path_id
                else:
                    path_id = path_to_path_id[path]

                path_count_array[path_id][node_id] = path_count

        mean_adjusted_path_count_array = ((path_count_array - np.mean(path_count_array, axis=1)[:, None])/np.mean(path_count_array, axis=1)[:, None]).T
        print(mean_adjusted_path_count_array)

        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(mean_adjusted_path_count_array)
        plt.plot(principal_components)
        plt.show()
        print(principal_components)
        print(pca.explained_variance_)

        max_number_clusters = len(nodes)
        silhouette_scores_for_number_clusters = []

        for n_clusters in range(max_number_clusters - 2):
            n_clusters += 2  # we start counting at 1, since zero or one clusters is invalid
            clusterer = KMeans(n_clusters=n_clusters, random_state=10)
            cluster_labels = clusterer.fit_predict(mean_adjusted_path_count_array)
            silhouette_avg = silhouette_score(mean_adjusted_path_count_array, cluster_labels)
            silhouette_scores_for_number_clusters.append(silhouette_avg)

        print(silhouette_scores_for_number_clusters)
        optimal_number_clusters = np.argmax(silhouette_scores_for_number_clusters) + 2
        clusterer = KMeans(n_clusters=optimal_number_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(mean_adjusted_path_count_array)
        print(optimal_number_clusters)
        print(cluster_labels)

        path_distribution_clusters = [[] for _ in range(optimal_number_clusters)]
        for node_id, cluster_id in enumerate(cluster_labels):
            path_distribution_clusters[cluster_id].append(nodes[node_id].name)

        print(path_distribution_clusters)

        # split up the path_distribution_clusters into single nodes and clusters
        single_nodes = set()
        clusters = []
        for path_distribution_cluster in path_distribution_clusters:
            if len(path_distribution_cluster) == 1:
                node_name = path_distribution_cluster[0]
                single_nodes.add(node_name)
            else:
                clusters.append(path_distribution_cluster)

        return single_nodes, clusters


def cluster_nodes_by_js_divergence(nodes: list[NodeRandomWalkData],
                                   threshold_js_divergence: float, number_of_paths: int):
    """
    Performs agglomerative clustering of nodes based on the distribution of their paths obtained through random walks.

    Every node starts out in its own cluster. The two clusters which have the smallest Jensen-Shannon
    divergence in the distribution of their paths are then merged (providing that this divergence is strictly less
    than threshold_js_divergence). This is repeated until all clusters have a divergence greater than the threshold.

    :param nodes: the set of nodes to be clustered
    :param threshold_js_divergence: the maximum permitted Jensen-Shannon divergence for merging two clusters
    :param number_of_paths: the number of paths to consider when calculating the Jensen-Shannon divergence
                            between the distributions (we consider only the top number_of_paths most common).
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
