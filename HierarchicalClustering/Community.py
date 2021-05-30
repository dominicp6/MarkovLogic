class Community(object):
    """
    A object which wraps the sets of node clusterings in a hypergraph.
    (Output object from the run_random_walks method of RandomWalker)
    """

    def __init__(self, single_nodes=None, node_clusters=None, source_node=None):
        self.source_node = source_node

        if single_nodes is not None:
            self.single_nodes = single_nodes
        else:
            self.single_nodes = []
        if node_clusters is not None:
            self.node_clusters = node_clusters
        else:
            self.node_clusters = []

    def __str__(self):
        return """Community(single_nodes: {}, node_clusters: {})""".format(self.single_nodes, self.node_clusters)

    def get_number_of_single_nodes(self):
        return len(self.single_nodes)

    def get_number_of_clusters(self):
        return len(self.node_clusters)

    def get_number_of_nodes(self):
        return sum([len(cluster) for cluster in self.node_clusters]) + self.get_number_of_clusters()
