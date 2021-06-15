from NodeRandomWalkData import NodeRandomWalkData
from GraphObjects import Hypergraph
from Node import Node


def generate_node_random_walk_data(hypergraph: Hypergraph, source_node: Node, number_of_walks: int,
                                   max_path_length: int):
    """
    Runs a total of 'number_of_walks' random walks on 'hypergraph', each originating from the 'source_node' with a
    maximum length of 'max_path_length'. Returns a data structure which holds information about the number of times
    each node was hit, the average hitting time, and the frequency distribution of unique random walks paths that
    led to hitting the node.
    """

    nodes_random_walk_data = {node.name: NodeRandomWalkData(node.name, node.node_type) for node in hypergraph.nodes()}

    for walk in range(number_of_walks):
        nodes_random_walk_data = update_node_data_with_random_walk(hypergraph, source_node, max_path_length,
                                                                   nodes_random_walk_data)

    for node in hypergraph.nodes():
        nodes_random_walk_data[node.name].calculate_average_hitting_time(number_of_walks, max_path_length)

    return nodes_random_walk_data  # dict[str, NodeRandomWalkData]


def update_node_data_with_random_walk(hypergraph: Hypergraph, source_node: Node, max_path_length: int,
                                      nodes_random_walk_data: dict[str, NodeRandomWalkData]):
    """
    Runs a single random walk on a hypergraph, then returns the updated random walk data.
    """
    current_node = source_node
    encountered_nodes = set()
    path = ''
    for step in range(max_path_length):

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
