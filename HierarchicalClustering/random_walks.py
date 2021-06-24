import numpy as np

from NodeRandomWalkData import NodeRandomWalkData
from GraphObjects import Hypergraph


class RandomWalker:
    """
    An object to run random walks on a hypergraph and compute truncated hitting time and path distribution statistics
    for the nodes.

    :param hypergraph: The hypergraph to run the random walks on
    :param epsilon: The desired fractional precision in the empirical estimations for the average truncated hitting
            times and the path probability distributions of the nodes. Used when calculating the number of random walks
            required to be run.
    :param number_of_paths: Used when calculating the number of random walks required to be run. Only the path
            probabilities of the number_of_paths most common paths will be estimated to the precision set by epsilon.
    :param max_path_length: The maximum length of a random walk. The actual length of the walk will be smaller than
            this, unless the diameter of the hypergraph exceeds max_path_length.

    """

    def __init__(self, hypergraph: Hypergraph, epsilon: float, k=1.25, max_path_length=5, number_of_paths=5):
        self.hypergraph = hypergraph
        self.number_of_paths = number_of_paths
        self.max_path_length = max_path_length
        self.epsilon = epsilon
        self.k = k
        self.fraction_of_max_walks_to_always_complete = 0.25

        self.length_of_walk = self._get_length_of_random_walks()

        self.number_of_walks_for_truncated_hitting_times = \
            self._get_number_of_walks_for_truncated_hitting_times(self.length_of_walk)

        self.number_of_predicates = hypergraph.number_of_predicates()

        self.number_of_walks_for_path_distribution = \
            self._get_number_of_walks_for_path_distribution(M=number_of_paths)

        self.max_number_of_walks = max(self.number_of_walks_for_truncated_hitting_times,
                                       self.number_of_walks_for_path_distribution)

    def _get_length_of_random_walks(self):
        """
        Calculates a suitable value for the length of the random walks based on the estimated diameter of the graph
        that generated the hypergraph.
        """
        if self.hypergraph.estimated_graph_diameter is not None:
            length_of_walk = int(round(self.k * self.hypergraph.estimated_graph_diameter))
        else:
            length_of_walk = self.max_path_length

        return length_of_walk

    def _get_number_of_walks_for_truncated_hitting_times(self, length_of_walk: int):
        """
        Calculates an upper bound on the number of random walks needed to get estimates of a node's average truncated
        hitting time to within a given fractional precision.

        :param length_of_walk: the maximum length of each random walk
        """
        return int(round((length_of_walk - 1) ** 2 / (4 * self.epsilon ** 2)))

    def _get_number_of_walks_for_path_distribution(self, M: int, number_of_unique_paths=None):
        """
        Calculates an upper bound on the number of walks needed to get estimates of a node's distribution of path
        probabilities to within a given fractional precision.

        :param M: specifies that precise estimates for the first M most common paths are required. Larger values of M
                  will require running more random walks.
        :param number_of_unique_paths: if specified, then the statistical calculation of the number of walks is based
                  on this value, else an upperbound on the maximum number of unique paths is calculated based on the
                  length of the random walk and the number of predicates in the hypergraph
        """
        if number_of_unique_paths is None:
            max_num_of_unique_paths = (
                    self.number_of_predicates * (self.number_of_predicates ** self.length_of_walk - 1)
                    / (self.number_of_predicates - 1))
        else:
            max_num_of_unique_paths = number_of_unique_paths

        return int(round(min(M, max_num_of_unique_paths) * np.log(max_num_of_unique_paths) / (self.epsilon ** 2)))

    def generate_node_random_walk_data(self, source_node: str):
        """
        Runs random walks originating from the source_node. Returns a data structure which holds information
        about the number of times each node was hit, the average hitting time, and the frequency distribution
        of unique random walks paths that led to hitting the node.
        """
        nodes_random_walk_data, number_of_walks = self._run_random_walks_from_source_node(source_node)

        [nodes_random_walk_data[node].calculate_average_hitting_time(number_of_walks, self.length_of_walk)
         for node in self.hypergraph.nodes.keys()]

        return nodes_random_walk_data  # dict[str, NodeRandomWalkData]

    def _run_random_walks_from_source_node(self, source_node: str):
        """
        Run random walks from a source node.

        :return nodes_random_walk_data: the data generated whilst running the random walks
                number_of_walks: the number of walks that was required to achieve the desired statistical precision
        """

        nodes_random_walk_data = {node: NodeRandomWalkData(node, node_type) for node, node_type in
                                  self.hypergraph.nodes.items()}

        number_of_walks = int(self.max_number_of_walks * self.fraction_of_max_walks_to_always_complete)

        # run a fraction of the number of walks initially estimated
        [self._update_node_data_with_random_walk(source_node, nodes_random_walk_data)
         for _ in range(number_of_walks)]

        # compute a refined estimate of number of additional walks needed based on the path distribution statistics
        # obtained so far
        number_of_additional_walks = self._compute_number_of_additional_walks(nodes_random_walk_data, number_of_walks)

        # if additional walks are needed, then run them
        if number_of_additional_walks > 0:
            [self._update_node_data_with_random_walk(source_node, nodes_random_walk_data)
             for _ in range(number_of_additional_walks)]
            number_of_walks += number_of_additional_walks

        return nodes_random_walk_data, number_of_walks

    def _update_node_data_with_random_walk(self, source_node: str,
                                           nodes_random_walk_data: dict[str, NodeRandomWalkData]):
        """
        Runs a single random walk from the source node, updating the nodes_random_walk_data in place.
        """
        current_node = source_node
        encountered_nodes = set()
        path = ''
        for step in range(self.length_of_walk):

            next_edge, next_node = self.hypergraph.get_random_edge_and_neighbor_of_node(current_node)
            path += str(self.hypergraph.predicates[next_edge]) + ','

            if next_node not in encountered_nodes:
                nodes_random_walk_data[next_node].number_of_hits += 1
                nodes_random_walk_data[next_node].add_path(path)
                hitting_time = step + 1
                nodes_random_walk_data[next_node].update_accumulated_hitting_time(hitting_time)
                encountered_nodes.add(next_node)

            current_node = next_node

    def _compute_number_of_additional_walks(self, nodes_random_walk_data: dict[str, NodeRandomWalkData],
                                            number_of_completed_walks: int):
        """
        Given the path distributions obtained in nodes_random_walk_data and the number of completed random walks so far.
        Computes an estimate for the number of additional random walks that need to be run.
        """

        number_of_unique_paths = self._compute_number_of_unique_paths(nodes_random_walk_data)

        number_of_additional_walks_for_truncated_hitting_time = \
            self.number_of_walks_for_truncated_hitting_times - number_of_completed_walks

        number_of_additional_walks_for_path_distribution = \
            self._get_number_of_walks_for_path_distribution(M=self.number_of_paths,
                                                            number_of_unique_paths=number_of_unique_paths) \
            - number_of_completed_walks

        number_of_additional_walks = int(max(number_of_additional_walks_for_path_distribution,
                                             number_of_additional_walks_for_truncated_hitting_time))

        return number_of_additional_walks

    @staticmethod
    def _compute_number_of_unique_paths(nodes_random_walk_data: dict[str, NodeRandomWalkData]):
        """
        Calculates the number of unique path signatures that appear anywhere in the nodes_random_walk_data.
        """
        unique_paths = set()
        [unique_paths.update(node.path_counts.keys()) for node in nodes_random_walk_data.values()]
        number_of_unique_paths = len(unique_paths)

        return number_of_unique_paths
