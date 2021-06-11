from NodeRandomWalkData import *
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
        js_single_nodes, js_clusters = cluster_nodes_by_js_divergence(distance_symmetric_cluster,
                                                                      threshold_js_divergence=
                                                                      config['theta_js'],
                                                                      number_of_paths=config['num_top'])

        single_nodes.update(js_single_nodes)
        clusters.extend(js_clusters)

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
    distance_symmetric_cluster = set()
    for node in nodes:
        if (node.average_hitting_time - current_hitting_time) < threshold_hitting_time_difference:
            distance_symmetric_cluster.add(node)
        else:
            if len(distance_symmetric_cluster) == 1:
                distance_symmetric_single_nodes.update(distance_symmetric_cluster)
            else:
                distance_symmetric_clusters.append(distance_symmetric_cluster.copy())

            distance_symmetric_cluster.clear()
            distance_symmetric_cluster.add(node)

        current_hitting_time = node.average_hitting_time

    # append the last cluster to the list if it is not empty
    if distance_symmetric_cluster is not None:
        distance_symmetric_clusters.append(distance_symmetric_cluster)

    return distance_symmetric_single_nodes, distance_symmetric_clusters


def cluster_nodes_by_js_divergence(nodes: set[NodeRandomWalkData],
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
