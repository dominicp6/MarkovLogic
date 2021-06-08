from collections import defaultdict

from js_divergence_utils import compute_js_divergence_of_top_n_paths
from NodeRandomWalkData import NodeRandomWalkData, NodeClusterRandomWalkData


def run_random_walks(hypergraph, source_node, number_of_walks: int, max_path_length: int):
    """
    Runs a total of 'number_of_walks' random walks on 'hypergraph', each originating from the 'source_node' with a
    maximum length of 'max_path_length'.
    """

    # initialise empty random walk data
    nodes_random_walk_data = {}
    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name] = NodeRandomWalkData(node.name, node.node_type)

    for walk in range(number_of_walks):
        run_random_walk(hypergraph, source_node, max_path_length, nodes_random_walk_data)

    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name].calculate_average_hitting_time(number_of_walks, max_path_length)

    # the source node should never be clustered with other nodes; setting its average hitting time to be large
    # and negative enforces this
    nodes_random_walk_data[source_node.name].average_hitting_time = - float('inf')

    return nodes_random_walk_data


def run_random_walk(hypergraph, source_node, max_path_length: int, nodes_random_walk_data):
    """
    Runs a single random walk on a hypergraph, then returns the updated random walk data.
    """
    current_node = source_node
    encountered_nodes = set()
    path = ''
    for step in range(max_path_length):

        next_node, next_edge = hypergraph.get_random_neighbor_and_edge_of_node(current_node)
        path += str(next_edge.predicate) + ','

        if next_node.name not in encountered_nodes:
            nodes_random_walk_data[next_node.name].number_of_hits += 1
            nodes_random_walk_data[next_node.name].add_path(path)
            hitting_time = step + 1
            nodes_random_walk_data[next_node.name].update_accumulated_hitting_time(hitting_time)
            encountered_nodes.add(next_node.name)

        current_node = next_node


def get_close_nodes(nodes_random_walk_data, threshold_hitting_time: float):
    return [node for node in nodes_random_walk_data.values() if node.average_hitting_time < threshold_hitting_time]


def get_community(close_nodes: list[NodeRandomWalkData], node_types: set, config: dict):
    single_nodes = []
    clusters = []
    for node_type in node_types:
        nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
        if nodes_of_type:
            single_nodes_of_type, clusters_of_type = cluster_nodes(nodes_of_type, config)

            single_nodes.extend(single_nodes_of_type)
            clusters.extend(clusters_of_type)

    community = {'single_nodes': single_nodes, 'clusters': clusters}

    return community


def cluster_nodes(nodes: list[NodeRandomWalkData], config: dict):
    single_nodes = []
    clusters = []
    distance_symmetric_single_nodes, distance_symmetric_clusters = cluster_nodes_by_truncated_hitting_times(
        nodes, threshold_hitting_time_difference=config['theta_sym'])

    single_nodes.extend([node.name for node in distance_symmetric_single_nodes])

    for distance_symmetric_cluster in distance_symmetric_clusters:
        js_single_nodes, js_clusters = cluster_nodes_by_js_divergence(distance_symmetric_cluster,
                                                                      threshold_js_divergence=
                                                                      config['theta_js'],
                                                                      number_of_paths=config['num_top'])
        single_nodes.extend(js_single_nodes)
        clusters.extend(js_clusters)

    return single_nodes, clusters


def cluster_nodes_by_truncated_hitting_times(nodes: list[NodeRandomWalkData], threshold_hitting_time_difference: float):
    """
    Clusters a list of nodes into groups based on the truncated hitting
    criterion as follows:

    Let h_{j} be the average truncated hitting time of node v_{j}. Nodes v_{j} are grouped into disjoint sets A_{k}
    such that: for all v_{j} in A_{k} there exists a node v_{j'} in A_{k} such that |h_{j} - h_{j'}| <= merge_threshold.
    Ref: https://alchemy.cs.washington.edu/papers/kok10/kok10.pdf
    """

    # sort the nodes in the hypergraph in increasing order of average hitting time
    nodes = sorted(nodes, key=lambda n: n.average_hitting_time)
    current_hitting_time = nodes[0].average_hitting_time
    distance_symmetric_clusters = []
    distance_symmetric_single_nodes = []
    distance_symmetric_cluster = []
    for node in nodes:
        if (node.average_hitting_time - current_hitting_time) < threshold_hitting_time_difference:
            distance_symmetric_cluster.append(node)
        else:
            if len(distance_symmetric_cluster) == 1:
                distance_symmetric_single_nodes.append(distance_symmetric_cluster[0])
            else:
                distance_symmetric_clusters.append(distance_symmetric_cluster.copy())

            distance_symmetric_cluster.clear()
            distance_symmetric_cluster.append(node)

        current_hitting_time = node.average_hitting_time

    # append the last cluster to the list if it is not empty
    if distance_symmetric_cluster is not None:
        distance_symmetric_clusters.append(distance_symmetric_cluster)

    return distance_symmetric_single_nodes, distance_symmetric_clusters


def cluster_nodes_by_js_divergence(nodes: list[NodeRandomWalkData],
                                   threshold_js_divergence: float, number_of_paths: int):
    """
    Performs agglomerative clustering of nodes based on the distribution of their paths obtained through random walks.

    Every node starts out in its own cluster. The two clusters which have the smallest Jensen-Shannon
    divergence in the distribution of their paths are then merged (providing that this divergence is strictly less
    than threshold_js_divergence). This is repeated until all clusters have a divergence greater than the threshold.

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
    single_nodes = []
    clusters = []
    for js_cluster in js_clusters:
        if js_cluster.number_of_nodes() == 1:
            (node_name,) = js_cluster.node_names
            single_nodes.append(node_name)
        else:
            clusters.append(list(js_cluster.node_names))

    return single_nodes, clusters


class Communities(object):

    def __init__(self, hypergraph, config: dict):

        """
        Generates the communities associated with a hypergraph.

        Each node of a hypergraph has a community associated with it. A community is a collection
        of 'single nodes' and 'node clusters'. Node clusters are groups of nodes which have similar symmetry
        properties with respect to the source node (i.e. similar truncated hitting times and similar distributions
         of paths). A node is called a 'single node' if its node cluster contains only itself. Nodes can only be in
        the same cluster if they are of the same type.

        Config parameters:
            num_walks    -  The number of random walks to run from each node.
            max_length   -  The maximum length of the random walks.
            theta_hit    -  Threshold for the average truncated hitting time (ATHT). Nodes with larger ATHT are excluded
                            from the community.
            theta_sym    -  Threshold difference in ATHT for nodes to be considered as potentially symmetric.
            theta_js     -  Threshold difference in Jensen-Shannon divergence of path distributions for potentially
                            symmetric nodes to be clustered together.
            num_top      -  The num_top most frequent paths to consider when calculating the Jensen-Shannon divergence
                            between path distributions.
        """

        assert type(config['num_walks']) is int and config['num_walks'] > 0, "num_walks must be a positive integer"
        assert type(config['max_length']) is int and config['max_length'] > 0, "max_length must be a positive integer"
        assert type(config['theta_hit']) is float and config['theta_hit'] > 0, "theta_hit must be a positive float"
        assert type(config['theta_sym']) is float and config['theta_sym'] > 0, "theta_sym must be a positive float"
        assert type(config['theta_js']) is float and config['theta_js'] > 0, "theta_js must be a positive float"
        assert type(config['num_top']) is int and config['num_top'] > 0, "num_top must be a positive int"

        self.communities = defaultdict(lambda: {})

        for node in hypergraph.nodes():
            random_walk_data = run_random_walks(hypergraph, source_node=node,
                                                number_of_walks=config['num_walks'],
                                                max_path_length=config['max_length'])
            close_nodes = get_close_nodes(random_walk_data,
                                          threshold_hitting_time=config['theta_hit'])
            community = get_community(close_nodes=close_nodes, node_types=hypergraph.node_types, config=config)
            self.communities[node.name] = community

    def __str__(self):
        output_str = ""
        for source_node, cluster_dict in self.communities.items():
            source_str = f"SOURCE: {source_node}\n ---------------------------- \n"
            single_nodes_str = "".join([f"SINGLE: {node}\n" for node in cluster_dict['single_nodes']])
            clusters_str = ""
            for cluster_number, cluster in enumerate(cluster_dict['clusters']):
                clusters_str += f"CLUSTER {cluster_number}: \n"
                clusters_str += "".join([f"        {node}\n" for node in cluster])

            output_str += source_str + single_nodes_str + clusters_str + "\n"

        return output_str
