from collections import defaultdict
import operator


class NodeRandomWalkData():
    def __init__(self, name, node_type):
        self.name = name
        self.node_type = node_type
        self.path_counts = defaultdict(lambda: 0)
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0
        self.average_hitting_time = 0

    def add_path(self, path):
        self.path_counts[path] += 1

    def update_accumulated_hitting_time(self, hitting_time):
        self.accumulated_hitting_time += hitting_time

    def calculate_average_hitting_time(self, number_of_walks, max_length):
        # asset self.average_hitting_time == 0, else this method was called more than once before
        # resetting node properties, which is unintended behaviour
        assert self.average_hitting_time == 0
        self.average_hitting_time = (self.accumulated_hitting_time + (number_of_walks - self.number_of_hits)
                                     * max_length) / number_of_walks


class NodeClusterRandomWalkData(object):

    def __init__(self, nodes_random_walk_data):
        super().__init__()
        self.nodes_random_walk_data = nodes_random_walk_data
        self.path_counts, self.total_count = self._initialise_path_counts()

    def _initialise_path_counts(self):
        path_counts = {}
        for node in self.nodes_random_walk_data:
            path_counts.update(node.path_counts)

        total_count = sum(path_counts.values())

        return path_counts, total_count

    def merge(self, node_cluster):
        self.nodes_random_walk_data.extend(node_cluster.nodes_random_walk_data)
        self.path_counts.update(node_cluster.path_counts)

    def number_of_nodes(self):
        return len(self.nodes_random_walk_data)

    def get_top_n_path_probabilities(self, n):
        if self.total_count > 0:
            path_probabilities = {key: value / self.total_count for key, value in self.path_counts.items()}
            sorted_probabilities = sorted(path_probabilities.items(), key=operator.itemgetter(1), reverse=True)

            top_n_paths_probabilities = dict(sorted_probabilities[0:n])
        else:
            # if no paths found in cluster then return an empty path probability dictionary
            top_n_paths_probabilities = {'': 0}

        return top_n_paths_probabilities
