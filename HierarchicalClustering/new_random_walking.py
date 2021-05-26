import numpy as np
from Community import Community

def _kulback_lieber_div(p,q):
    return sum(p * np.log(p / q) for p, q in zip(p, q) if p != 0)

def _jenson_shannon_divergence(p, q):
    m = 0.5 * (p + q)
    return 0.5 * _kulback_lieber_div(p, m) + 0.5 * _kulback_lieber_div(q,m)

def merge_node_paths(path_probs_1, path_probs_2):
    path_sums = dict(Counter(path_probs_1) + Counter(path_probs_2))
    return {path_string : path_sums[path_string] / 2 for path_string in path_sums.keys()}

def compute_jenson_shannon_divergence(path_probs_1, path_probs_2):
    pass

def find_single_nodes_and_clusters(nodes):
    # 1) finding potentially symmetric nodes with theta_sym parameter
    # 2) cluster into symmetric nodes using JS divergence criterion


# Make this a method of enhanced hypergraph?
def get_random_neighbour_of_node(hypergraph, node):
    # returns a random neighbouring node as well as the id of the hyperedge that both nodes belong to
    return neighbour_node, hyperedge_id

def get_nearest_nodes(hypergraph, theta_hit):
    return

def find_single_nodes_and_clusters(nodes):
    pass

def generate_communities(config, hypergraph):
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

    # TODO: check that the config parameters are valid

    source_nodes = []
    communities = []

    #for each node in the hypergraph
    for node in hypergraph.nodes():
        # Get number of samples from criterion (explain)
        num_samples = min(config['num_walks'],
                          config['walk_scaling_param'] * hypergraph.number_of_nodes() * hypergraph.number_of_edges())

        # run random walks from the node
        run_random_walks(num_samples, config, hypergraph, node)

        # get the nearest nodes (using theta_hit)  - shall this be a method or a function?
        nearest_nodes = get_nearest_nodes(hypergraph, config['theta_hit'])  # or method?

        single_nodes, node_clusters = cluster_nodes(nearest_nodes, hypergraph)

        # create community from single nodes and cluster
        community = Community(single_nodes, node_clusters, source_node=node)

        hypergraph.reset_nodes()

        communities.append(community)
        #unmerged_community = Community() - TODO: figure out how this would work

    #return communities, unmerged communities, source nodes
    return communities, source_nodes

def cluster_nodes(nodes, hypergraph):
    single_nodes = []
    node_clusters = []
    # cluster nodes only if they are of the same type
    for node_type in hypergraph.node_types:
        nodes = [node for node in hypergraph.type_to_nodes_map(node_type) if node in nodes]
        singles, clusters = find_single_nodes_and_clusters(nodes)  # (using theta_sym, theta_js, num_top params)

        # append the single nodes and clusters onto a running total
        single_nodes.append(singles)
        node_clusters.append(clusters)

    return single_nodes, node_clusters

def run_random_walks(num_samples, config, hypergraph, source_node):
    for walk_id in range(num_samples):
        run_random_walk(config, hypergraph, source_node)

def run_random_walk(config, hypergraph, source_node):
    current_node = source_node
    sample_path = []
    for step in range(config['max_length']):
        next_node, next_hyperedge_id = get_random_neighbour_of_node(hypergraph, current_node)  # or method?

        sample_path.append(str(step))
        sample_path.append(next_hyperedge_id)

        hitting_time = step + 1

        #TODO: make sure this only happens if it wasn't already hit
        next_node.increment_number_of_hits()
        next_node.add_to_accumulated_hitting_time(hitting_time)
        next_node.add_sample_path(sample_path)

        current_node = next_node


