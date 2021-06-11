from graph_utils import get_second_eigenpair
from cheeger_cut import cheeger_cut


class HierarchicalClusterer(object):
    """
    To perform hierarchical clustering of a hypergraph.

    Example usage:
        HC = HierarchicalClusterer(hypergraph, config = {'min_cluster_size' : 5, 'max_lambda2' : 0.8})
        hypergraph_clusters = HC.hierarchical_clustering()

    The steps are:
    1. Convert the hypergraph into a graph by replacing each n-hyperedge with an n-clique.
    2. Recursively bi-partition the graph into smaller graphs using the Cheeger-Cut algorithm. Stop partitioning when
       a terminating condition is met (either because graph is split too small, or because the size of the second
       smallest Laplacian eigenvalue exceeds a threshold). This produces a hierarchical binary tree of graph objects.
    3. Convert the graphs from the leaf nodes of the tree into hypergraphs using the original hypergraph as a template.
       Return the list of hypergraphs.

    Configuration parameters (to specify stop criteria):
        min_cluster_size (int) - the smallest size (number of nodes) of the final graphs that are permitted.
        max_lambda2 (float in interval 0-2)    - the largest value of the second smallest eigenvalue of the graph's
                                 laplacian matrix permitted (due to the Cheeger-inequality, larger values of lambda2
                                  signify that it is more challenging to find a sparse-cut for the graph)
    """

    def __init__(self, hypergraph, config):
        self.min_cluster_size = config['min_cluster_size']
        self.max_lambda2 = config['max_lambda2']
        self.hypergraph = hypergraph
        self.graph_clusters = []
        self.hypergraph_clusters = []

        assert self.min_cluster_size > 2, "Argument Error: min_cluster_size must be greater than 2"
        assert 0 < self.max_lambda2 < 2, "Argument Error: max_lambda2 needs to be greater than 0 and less than 2"
        assert self.hypergraph.number_of_nodes() > self.min_cluster_size, \
            "Argument Error: min_cluster_size needs to be smaller than the number of nodes in the hypergraph"

    def hierarchical_clustering(self):

        # 1. Convert hypergraph to graph
        original_graph = self.hypergraph.convert_to_graph()

        # 2. Hierarchical cluster the graph
        self.get_clusters(original_graph)

        # 3. Convert the graph clusters into hypergraphs
        self.hypergraph_clusters = [graph.convert_to_hypergraph_from_template(self.hypergraph) for graph in
                                    self.graph_clusters]

        return self.hypergraph_clusters

    def get_clusters(self, graph):
        v_2, lambda2 = get_second_eigenpair(graph)

        # stop splitting if lambda2 stop criterion met
        if lambda2 > self.max_lambda2:
            self.graph_clusters.append(graph)
            return None
        else:
            subgraph1, subgraph2 = cheeger_cut(graph, v_2)

            # stop splitting if cluster size stop criterion met
            if (self.min_cluster_size and
                    (subgraph1.number_of_nodes() < self.min_cluster_size or
                     subgraph2.number_of_nodes() < self.min_cluster_size)):

                self.graph_clusters.append(graph)
                return None

            else:
                return self.get_clusters(subgraph1), self.get_clusters(subgraph2)
