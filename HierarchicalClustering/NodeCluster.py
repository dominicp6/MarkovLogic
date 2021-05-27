import operator


class NodeCluster(object):

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes
        self.path_counts, self.total_count = self._initialise_path_counts()

    def _initialise_path_counts(self):
        path_counts = {}
        for node in self.nodes:
            path_counts.update(node.path_counts)

        total_count = sum(path_counts.values())

        return path_counts, total_count

    def merge(self, node_cluster):
        self.nodes = self.nodes.extend(node_cluster.nodes)
        self.path_counts = self.path_counts.update(node_cluster.path_counts)

    def number_of_nodes(self):
        return len(self.nodes)

    def get_top_n_path_probabilities(self, n):
        path_probabilities = {key: value / self.total_count for key, value in self.path_counts.items()}
        sorted_probabilities = sorted(path_probabilities.items(), key=operator.itemgetter(1), reverse=True)

        top_n_paths_probabilities = sorted_probabilities[0:n]

        return top_n_paths_probabilities