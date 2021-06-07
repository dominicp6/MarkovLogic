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
        source_str = f"SOURCE: {self.source_node.name}\n ---------------------------- \n"
        single_nodes_str = "".join([f"SINGLE: {node.name}\n" for node in self.single_nodes])
        clusters_str = ""
        for cluster in self.node_clusters:
            clusters_str += "CLUST: \n"
            clusters_str += "".join([f"        {node.name}\n" for node in cluster])

        output_str = source_str + single_nodes_str + clusters_str

        return output_str

    def get_number_of_single_nodes(self):
        return len(self.single_nodes)

    def get_number_of_clusters(self):
        return len(self.node_clusters)

    def get_number_of_nodes(self):
        return sum([len(cluster) for cluster in self.node_clusters]) + self.get_number_of_clusters()
