from collections import defaultdict
import operator
import warnings


class NodeRandomWalkData(object):
    """
    Data structure to store hitting time and path count information for each node during random walks.
    """

    def __init__(self, name: str, node_type: str):
        self.name = name
        self.node_type = node_type
        self.path_counts = defaultdict(int)
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0
        self.average_hitting_time = 0

    def add_path(self, path: str):
        """
        A path is an ordered sequence of predicate strings separated by commas (e.g. 'Friends,Smokes,Cancer,Friends,')
        which represents the order in which hyperedges were traversed during a random walk before hitting a node.
        """
        self.path_counts[path] += 1

    def update_accumulated_hitting_time(self, hitting_time: float):
        self.accumulated_hitting_time += hitting_time

    def calculate_average_hitting_time(self, number_of_walks: int, max_length: int):
        if self.average_hitting_time != 0:
            warnings.warn('Method "calculate_average_hitting_time" called more than once when running random walks')

        self.average_hitting_time = (self.accumulated_hitting_time + (number_of_walks - self.number_of_hits)
                                     * max_length) / number_of_walks

    def get_top_n_paths(self, number_of_paths):
        print(self.path_counts)
        if number_of_paths < len(self.path_counts):
            top_paths = sorted(self.path_counts.items(), key=lambda x: x[1], reverse=True)[:number_of_paths]
        else:
            top_paths = sorted(self.path_counts.items(), key=lambda x: x[1], reverse=True)

        print(top_paths)

        return dict(top_paths)


class NodeClusterRandomWalkData(object):
    """
    Data structure to store path count information for a collection of nodes.
    """

    def __init__(self, nodes_random_walk_data: list[NodeRandomWalkData]):
        super().__init__()
        self.node_names = set(node.name for node in nodes_random_walk_data)

        path_counts = defaultdict(int)
        total_count = 0
        for node in nodes_random_walk_data:
            for key, value in node.path_counts.items():
                path_counts[key] += value
                total_count += value

        self.path_counts = path_counts  # dict<str,int>
        self.total_count = total_count  # int

    def merge(self, other):
        self.node_names.update(other.node_names)
        self.total_count += other.total_count
        for key, value in other.path_counts.items():
            self.path_counts[key] += value

    def number_of_nodes(self):
        return len(self.node_names)

    def get_top_n_path_probabilities(self, n):
        path_probabilities = {key: value / self.total_count for key, value in self.path_counts.items()}
        sorted_probabilities = sorted(path_probabilities.items(), key=operator.itemgetter(1), reverse=True)

        if n < len(sorted_probabilities):
            top_n_paths_probabilities = dict(sorted_probabilities[0:n])
        else:
            top_n_paths_probabilities = dict(sorted_probabilities)

        return top_n_paths_probabilities
