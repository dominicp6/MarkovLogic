from collections import defaultdict

from js_divergence_utils import compute_js_divergence
from NodeRandomWalkData import NodeRandomWalkData, NodeClusterRandomWalkData


def run_random_walk(hypergraph, nodes_random_walk_data, source_node, max_path_length):
    current_node = source_node
    encountered_nodes = set()
    path = ''
    for step in range(max_path_length):

        next_node, next_edge = hypergraph._get_random_neighbor_and_edge_of_node(current_node)
        path += str(next_edge.predicate) + ','

        if next_node.name not in encountered_nodes:
            nodes_random_walk_data[next_node.name].number_of_hits += 1
            nodes_random_walk_data[next_node.name].add_path(path)
            hitting_time = step + 1
            nodes_random_walk_data[next_node.name].update_accumulated_hitting_time(hitting_time)
            encountered_nodes.add(next_node.name)

        current_node = next_node


def run_random_walks(hypergraph, source_node, number_of_walks, max_path_length):

    # initialise empty random walk data
    nodes_random_walk_data = {}
    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name] = NodeRandomWalkData(node.name, node.node_type)

    for walk in range(number_of_walks):
        run_random_walk(hypergraph, nodes_random_walk_data, source_node, max_path_length)

    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name].calculate_average_hitting_time(number_of_walks, max_path_length)

    # the source node should never be clustered with other nodes; setting its average hitting time to be large
    # and negative enforces this
    nodes_random_walk_data[source_node.name].average_hitting_time = - float('inf')

    return nodes_random_walk_data


def get_close_nodes(nodes_random_walk_data, threshold_hitting_time):
    return [node for node in nodes_random_walk_data.values() if node.average_hitting_time < threshold_hitting_time]


def cluster_nodes_by_truncated_hitting_times(nodes_random_walk_data, threshold_hitting_time_difference):
    """
    Clusters a list of nodes into groups based on the truncated hitting
    criterion as follows:

    Let h_{j} be the average truncated hitting time of node v_{j}.
    Nodes v_{j} are grouped into disjoint sets A_{k} such that:
    for all v_{j} in A_{k} there exists a node v_{j'} in A_{k}
    such that |h_{j} - h_{j'}| <= merge_threshold.
    Ref: https://alchemy.cs.washington.edu/papers/kok10/kok10.pdf
    """

    # sort the nodes in the hypergraph in increasing order of average hitting time
    nodes = sorted(nodes_random_walk_data, key=lambda n: n.average_hitting_time)
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


def cluster_nodes_by_js_divergence(node_random_walk_data, threshold_js_divergence, max_frequent_paths):

    js_clusters = [NodeClusterRandomWalkData([node]) for node in node_random_walk_data]

    max_divergence = float('inf')
    cluster_to_merge1 = None
    cluster_to_merge2 = None

    while True:
        smallest_divergence = max_divergence
        for i in range(len(js_clusters)):
            for j in range(i + 1, len(js_clusters)):
                js_divergence = compute_js_divergence(js_clusters[i], js_clusters[j], max_frequent_paths)

                if js_divergence < smallest_divergence and js_divergence < threshold_js_divergence:
                    smallest_divergence = js_divergence
                    cluster_to_merge1 = i
                    cluster_to_merge2 = j

                if js_divergence > threshold_js_divergence:  # TODO: to remove - for debugging only
                    print('Exceeded threshold')

        # if we've found a pair of clusters to merge, merge the two clusters and continue
        if smallest_divergence < max_divergence:
            js_clusters[cluster_to_merge1].merge(js_clusters[cluster_to_merge2])
            del js_clusters[cluster_to_merge2]
        # otherwise, stop merging
        else:
            break

    single_nodes = []
    clusters = []
    for js_cluster in js_clusters:
        if js_cluster.number_of_nodes() == 1:
            single_nodes.append(js_cluster.nodes_random_walk_data[0].name)
        else:
            clusters.append([node.name for node in js_cluster.nodes_random_walk_data])

    return single_nodes, clusters


class Communities(object):

    def __init__(self, hypergraph, config):

        """
        Config parameters:
        num_walks : the maximum number of random walks to run per node
        max_length: the maximum length of a random walk
        walk_scaling_param: the number of random walks to run is min(num_walks, walk_scaling_param|V||E|) where
                            |V| and |E| are the number of nodes and hyperedges in the hypergraph respectively
        theta_hit : after running walks, nodes whose truncated hitting times are larger theta_hit are discarded
        theta_sym : of the remaining nodes, those whose truncated hitting times are less than theta_sym apart are considered
                    as potentially symmetric
        theta_js  : agglomerative clustering of symmetric nodes stops when no pairs of clusters have a path-distribution
                    Jenson-Shannon divergence less than theta_js
        num_top   : the number of most frequent paths to consider when computing the Jenson-Shannon divergence between
                        two path sets
        """

        self.communities = defaultdict(lambda: {})

        for node in hypergraph.nodes():
            single_nodes = []
            clusters = []

            nodes_random_walk_data = run_random_walks(hypergraph, source_node=node,
                                                      number_of_walks=config['num_walks'],
                                                      max_path_length=config['max_length'])
            close_nodes_random_walk_data = get_close_nodes(nodes_random_walk_data,
                                                           threshold_hitting_time=config['theta_hit'])

            for node_type in hypergraph.node_types:
                nodes_of_type = [node for node in close_nodes_random_walk_data if node.node_type == node_type]
                if nodes_of_type:
                    distance_symmetric_single_nodes, distance_symmetric_clusters = cluster_nodes_by_truncated_hitting_times(
                        nodes_of_type, threshold_hitting_time_difference=config['theta_sym'])

                    single_nodes.extend([node.name for node in distance_symmetric_single_nodes])

                    for distance_symmetric_cluster in distance_symmetric_clusters:
                        js_single_nodes, js_clusters = cluster_nodes_by_js_divergence(distance_symmetric_cluster,
                                                                                      threshold_js_divergence=
                                                                                            config[
                                                                                                'theta_js'],
                                                                                      max_frequent_paths=config[
                                                                                                'num_top'])
                        single_nodes.extend(js_single_nodes)
                        clusters.extend(js_clusters)

            self.communities[node.name] = {'single_nodes': single_nodes, 'clusters': clusters}
