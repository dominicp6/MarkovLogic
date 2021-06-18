from NodeRandomWalkData import NodeRandomWalkData
from GraphObjects import Hypergraph
from Node import Node


def generate_node_random_walk_data(hypergraph: Hypergraph, source_node: Node, epsilon: float, k=1.25, max_path_length=5):
    """
    Runs random walks on 'hypergraph', each originating from the 'source_node'. Returns a data structure which holds
    information about the number of times each node was hit, the average hitting time, and the frequency distribution
    of unique random walks paths that led to hitting the node.

    :param: hypergraph -  The hypergraph to run the random walks on.
    :param: source_node - The node to start each random walk from.
    :param: epsilon - The maximum fractional error for the mean truncated hitting time.
                      Used to determine the number of random walks that need to be run from each source node.
    :param: k       - Used to set the length of the random walks; walk length is set to k multiplied by
                      the estimated graph diameter of the hypergraph.
    :param: L       - The length of the random walk to default to if an estimate of the graph diameter of the hypergraph
                      is not known.
    """
    if hypergraph.estimated_graph_diameter is not None:
        length_of_walk = int(round(k * hypergraph.estimated_graph_diameter))
    else:
        length_of_walk = max_path_length

    number_of_walks = int(round((length_of_walk-1)**2/(4*epsilon**2)))

    nodes_random_walk_data = {node.name: NodeRandomWalkData(node.name, node.node_type) for node in hypergraph.nodes()}

    for walk in range(number_of_walks):
        nodes_random_walk_data = update_node_data_with_random_walk(hypergraph, source_node, length_of_walk,
                                                                   nodes_random_walk_data)

    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name].calculate_average_hitting_time(number_of_walks, length_of_walk)

    return nodes_random_walk_data  # dict[str, NodeRandomWalkData]


def update_node_data_with_random_walk(hypergraph: Hypergraph, source_node: Node, length_of_walk: int,
                                      nodes_random_walk_data: dict[str, NodeRandomWalkData]):
    """
    Runs a single random walk on a hypergraph, then returns the updated random walk data.
    """
    current_node = source_node
    encountered_nodes = set()
    path = ''
    for step in range(length_of_walk):

        next_edge, next_node = hypergraph.get_random_edge_and_neighbor_of_node(current_node)
        path += str(next_edge.predicate) + ','

        if next_node.name not in encountered_nodes:
            nodes_random_walk_data[next_node.name].number_of_hits += 1
            nodes_random_walk_data[next_node.name].add_path(path)
            hitting_time = step + 1
            nodes_random_walk_data[next_node.name].update_accumulated_hitting_time(hitting_time)
            encountered_nodes.add(next_node.name)

        current_node = next_node

    return nodes_random_walk_data
