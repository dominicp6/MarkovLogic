class Community(object):
    """
    A object which wraps the sets of node clusterings in a hypergraph.
    (Output object from the run_random_walks method of RandomWalker)
    """
    def __init__(self, clustered_nodes, source_node):
        self.single_nodes, self.clusters = self.get_single_nodes_and_clusters(clustered_nodes)
        self.num_single_nodes = len(self.single_nodes)
        self.num_clusters = len(self.clusters)
        self.num_nodes = sum([len(cluster) for cluster in self.clusters])+self.num_single_nodes
        self.source_node = source_node
    
    def all_nodes(self):
        cluster_nodes = [cluster_node for cluster in self.clusters for cluster_node in cluster]
        return self.single_nodes + cluster_nodes
    
    def get_single_nodes_and_clusters(self, clustered_nodes):
        """
        Separates a list of lists of node clusters into clusters
        of single nodes and clusters of more the one node.

        :param: clustered_nodes - a list of lists
        :returns: single_nodes - the list of single node clusters
                  clusters - a list of list of multi-node clusters
        """
        single_nodes = []
        clusters = []
        for array in clustered_nodes:
            if len(array) == 1:
                single_nodes.append(array[0])
            else:
                clusters.append(array)
        
        return single_nodes, clusters

    def __str__(self):
        return """Community(single_nodes: {}, clusters: {}, source_node: {})""".format(self.single_nodes, self.clusters, self.source_node)





