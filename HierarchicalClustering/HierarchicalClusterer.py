import numpy as np
import scipy as sp
import scipy.sparse
import networkx as nx
from graph_utils import get_second_eigenpair, create_subgraph


def sweep_set(adjacency_matrix, v_2, degrees):
    """
    Given the adjacency matrix of a graph, and the second eigenvalue of the laplacian matrix, use the sweep set
    algorithm to find a sparse cut.
    :param adjacency_matrix: The adjacency matrix of the graph to use.
    :param v_2: The second eigenvector of the laplacian matrix of the graph
    :param degrees: a list with the degrees of each vertex in the graph
    :return: The set of vertices corresponding to the optimal cut
    """
    # Calculate n here once
    n = adjacency_matrix.shape[0]

    # Keep track of the best cut so far
    best_cut_index = None
    best_conductance = None

    # Keep track of the size of the set and the cut weight to make computing the conductance
    # straightforward
    total_volume = np.sum(degrees)
    set_volume = 0
    set_size = 0
    cut_weight = 0

    # Normalise v_2 with the degrees of each vertex
    degree_matrix = sp.sparse.diags(degrees, 0)
    v_2 = degree_matrix.power(-(1 / 2)).dot(v_2)

    # First, sort the vertices based on their value in the second eigenvector
    sorted_vertices = [i for i, v in sorted(enumerate(v_2), key=(lambda y: y[1]))]

    # Keep track of which edges to add/subtract from the cut each time
    x = np.ones(n)

    # Loop through the vertices in the graph
    for (i, v) in enumerate(sorted_vertices[:-1]):
        # Update the set size and cut weight
        set_volume += degrees[v]
        set_size += 1

        # From now on, edges to this vertex will be removed from the cut at each iteration.
        x[v] = -1

        additional_weight = adjacency_matrix[v, :].dot(x)
        cut_weight += additional_weight

        # Calculate the conductance
        this_conductance = cut_weight / min(set_volume, total_volume - set_volume)

        # Check whether this conductance is the best
        if best_conductance is None or this_conductance < best_conductance:
            best_cut_index = i
            best_conductance = this_conductance

    # return best cut
    return sorted_vertices[:best_cut_index + 1]


def cheeger_cut(graph, v_2):
    """
    Given a networkx graph G and the second eigenvector of the laplacian matrix, find the cheeger cut.
    :param graph: The graph on which to operate.
    :param v_2: The second eigenvector of the laplacian matrix of the graph.
    :return: A set containing the vertices on one side of the cheeger cut
    """
    # Compute the key graph matrices
    adjacency_matrix = nx.adjacency_matrix(graph)
    graph_degrees = [t[1] for t in nx.degree(graph)]

    # Perform the sweep set operation to find the sparsest cut
    vertices_indices1 = sweep_set(adjacency_matrix, v_2, graph_degrees)
    vertices1 = set([n for i, n in enumerate(graph.nodes()) if i in vertices_indices1])
    subgraph1 = create_subgraph(graph, vertices1)

    vertices2 = set(graph.nodes()).difference(vertices1)
    subgraph2 = create_subgraph(graph, vertices2)
    return subgraph1, subgraph2


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
