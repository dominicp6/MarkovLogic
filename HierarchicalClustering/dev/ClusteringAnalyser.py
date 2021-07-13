from Communities import Community
from GraphObjects import Hypergraph
from RandomWalker import generate_node_random_walk_data
from clustering_nodes_by_path_similarity import get_commonly_encountered_nodes, cluster_nodes_by_js_divergence, group_nodes_by_clustering_labels, compute_principal_components, compute_standardized_path_distributions_and_number_of_unique_paths, compute_optimal_birch_clustering
from NodeRandomWalkData import NodeRandomWalkData
from HierarchicalClusterer import HierarchicalClusterer
from collections import defaultdict
import numpy as np


class TEST_Communities(object):

    def __init__(self, hypergraph: Hypergraph, config: dict):

        """
        Generates the communities associated with a hypergraph.

        Each node of a hypergraph has a community associated with it. A community is a collection
        of 'single nodes' and 'node clusters'. Node clusters are groups of nodes which have similar symmetry
        properties with respect to the source node (i.e. similar truncated hitting times and similar distributions
         of paths). A node is called a 'single node' if its node cluster contains only itself. Nodes can only be in
        the same cluster if they are of the same type.

        Config parameters:
            epsilon      -  The maximum fractional error for the mean truncated hitting time.
                            Used to determine the number of random walks that need to be run from each source node.
            theta_hit    -  Threshold for the average truncated hitting time (ATHT). Nodes with larger ATHT are excluded
                            from the community.
            theta_sym    -  Threshold difference in ATHT for nodes to be considered as potentially symmetric.
            theta_js     -  Threshold difference in Jensen-Shannon divergence of path distributions for potentially
                            symmetric nodes to be clustered together.
            num_top      -  The num_top most frequent paths to consider when calculating the Jensen-Shannon divergence
                            between path distributions.
        """

        assert type(config['epsilon']) is float and 1 > config['epsilon'] > 0, "epsilon must be a positive float " \
                                                                               "between 0 and 1"
        assert type(config['theta_hit']) is float and config['theta_hit'] > 0, "theta_hit must be a positive float"
        assert type(config['theta_sym']) is float and config['theta_sym'] > 0, "theta_sym must be a positive float"
        assert type(config['theta_js']) is float and config['theta_js'] > 0, "theta_js must be a positive float"
        assert type(config['num_top']) is int and config['num_top'] > 0, "num_top must be a positive int"

        self.hypergraph = hypergraph
        if hypergraph.diameter is None:
            print(f"Warning: Graph diameter of the hypergraph not known. Reverting to using default length of random "
                  f"walks.")

        self.communities = {}

        self.communities = {node: self.get_community(source_node=node, config=config) for node in
                            hypergraph.nodes.keys() if hypergraph.is_source_node[node]}

    def __str__(self):
        output_string = ''
        for community_id, community in enumerate(self.communities.values()):
            output_string += f'COMMUNITY {community_id + 1} \n' + community.__str__()

        return output_string

    def get_community(self, source_node: str, config: dict):
        random_walk_data = generate_node_random_walk_data(self.hypergraph,
                                                          source_node=source_node,
                                                          epsilon=config['epsilon'],
                                                          k=config['k'],
                                                          max_path_length=config['max_path_length'])

        # remove the source node from the random_walk_data and add it to the set of single nodes
        del random_walk_data[source_node]
        single_nodes = {source_node}
        clusters = []

        close_nodes = get_commonly_encountered_nodes(random_walk_data, threshold_hitting_time=config['theta_hit'])

        for node_type in self.hypergraph.node_types:
            nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
            if nodes_of_type:
                single_nodes_of_type, clusters_of_type = cluster_nodes_by_path_similarity(nodes_of_type, config)

                single_nodes.update(single_nodes_of_type)
                clusters.extend(clusters_of_type)

        community = Community(source_node, single_nodes, clusters)

        return community

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

    global single_node_counts
    global cluster_counts
    global js_divergence_method
    global js_div_threshold

    if js_divergence_method or len(nodes) <= 4:
        single_nodes, clusters = cluster_nodes_by_js_divergence(nodes=nodes,
                                                                threshold_js_divergence=js_div_threshold,
                                                                max_number_of_paths=20)

        if len(nodes) > 4:
            single_node_counts.append(len(single_nodes))
            cluster_counts.append(len(clusters))

    else:

        mean_adjusted_path_counts, number_unique_paths = compute_standardized_path_distributions_and_number_of_unique_paths(nodes, number_of_paths)

        principal_components = compute_principal_components(feature_vectors=mean_adjusted_path_counts,
                                                            original_dimension=number_unique_paths)

        number_of_clusters, cluster_labels = compute_optimal_birch_clustering(principal_components)

        single_nodes, clusters = group_nodes_by_clustering_labels(nodes, number_of_clusters, cluster_labels)

        single_node_counts.append(len(single_nodes))
        cluster_counts.append(len(clusters))

    return single_nodes, clusters



if __name__ == "__main__":
    config = {
        'clustering_params': {
            'min_cluster_size': 10,
            'max_lambda2': 0.8,
        },
        'random_walk_params': {
            'epsilon': 0.05,
            'k': 1.25,
            'max_path_length': 5,
            'theta_hit': 4.9,
            'theta_sym': 0.1,
            'theta_js': 1.0,
            'num_top': 3
        }
    }
    number_of_repeats = 10

    js_divergence_method = False
    single_node_counts = []
    cluster_counts = []
    for repeat_number in range(number_of_repeats):
        original_hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')
        hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph,
                                                       config=config['clustering_params'])
        hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()
        hypergraph_communities = [TEST_Communities(hypergraph, config=config['random_walk_params'])
                                  for hypergraph in hypergraph_clusters]

    pca_clustering_mean_single_node_counts = np.mean(single_node_counts)
    pca_clustering_mean_cluster_counts = np.mean(cluster_counts)

    js_divergence_method = True
    js_div_thresholds = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.002, 0.003,
                         0.004, 0.005]
    mean_square_deviations = defaultdict(lambda: [])
    for repeat_number in range(number_of_repeats):
        print(f'Repeat number {repeat_number}')
        for js_div_threshold in js_div_thresholds:
            single_node_counts = []
            cluster_counts = []
            original_hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')
            hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph,
                                                           config=config['clustering_params'])
            hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()
            hypergraph_communities = [TEST_Communities(hypergraph, config=config['random_walk_params'])
                                      for hypergraph in hypergraph_clusters]

            js_div_mean_single_node_counts = np.mean(single_node_counts)
            single_node_mse = (js_div_mean_single_node_counts - pca_clustering_mean_single_node_counts)**2
            js_div_mean_cluster_counts = np.mean(cluster_counts)
            cluster_mse = (js_div_mean_cluster_counts - pca_clustering_mean_cluster_counts)**2
            total_mse = single_node_mse + cluster_mse
            mean_square_deviations[js_div_threshold].append({'SN' : single_node_mse,
                                                             'CL' : cluster_mse,
                                                             'TOT' : total_mse})

    min_mse_js_div = 0
    min_mse = float('inf')
    for js_div, error_dict in mean_square_deviations.items():
        mean_tot_mse = np.mean([error_dict[js_div][i]['TOT'] for i in range(number_of_repeats)])
        if mean_tot_mse < min_mse:
            min_mse = mean_tot_mse
            min_mse_js_div = js_div

    print('The minimum MSE JS divergence is...')
    print(min_mse_js_div)
