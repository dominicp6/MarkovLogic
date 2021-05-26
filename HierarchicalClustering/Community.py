class Community(object):
    """
    A object which wraps the sets of node clusterings in a hypergraph.
    (Output object from the run_random_walks method of RandomWalker)
    """

    def __init__(self, single_nodes, node_clusters, source_node):
        self.single_nodes = single_nodes
        self.node_clusters = node_clusters
        self.source_node = source_node

        self.num_single_nodes = len(self.single_nodes)
        self.num_clusters = len(self.node_clusters)
        self.num_nodes = sum([len(cluster) for cluster in self.node_clusters]) + self.num_single_nodes

    def __str__(self):
        return """Community(single_nodes: {}, node_clusters: {}, source_node: {})""".format(self.single_nodes,
                                                                                            self.node_clusters,
                                                                                            self.source_node)
