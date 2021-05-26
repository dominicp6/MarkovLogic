class Community(object):
    """
    A object which wraps the sets of node clusterings in a hypergraph.
    (Output object from the run_random_walks method of RandomWalker)
    """
    def __init__(self, single_nodes, node_clusters, source_node, hypergraph, node_to_node_ids=None):
        self.single_nodes = single_nodes
        self.node_clusters = node_clusters
        self.source_node = source_node

        self.num_single_nodes = len(self.single_nodes)
        self.num_clusters = len(self.node_clusters)
        self.num_nodes = sum([len(cluster) for cluster in self.node_clusters])+self.num_single_nodes

    #     if node_to_node_ids is not None:
    #         self.set_node_ids(node_to_node_ids)

    # def set_node_ids(self, node_to_node_ids):
    #     self.node_to_node_ids = node_to_node_ids
    #     self.single_node_ids = [self.node_to_node_ids[single_node.name] for single_node in self.single_nodes]
    #     self.cluster_node_ids = [self.node_to_node_ids[cluster_node.name] for cluster in self.node_clusters for cluster_node in cluster]
    #     self.single_node_hyperedges = [self.node_to_hyperedges[single_node.name] for single_node in self.single_nodes]
    #     self.cluster_node_hyperedges = [self.node_to_hyperedges[cluster_node.name] for cluster in self.node_clusters for cluster_node in cluster]
    

    def __str__(self):
        return """Community(single_nodes: {}, node_clusters: {}, source_node: {})""".format(self.single_nodes, self.node_clusters, self.source_node)





