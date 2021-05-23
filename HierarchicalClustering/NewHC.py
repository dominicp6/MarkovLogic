import numpy as np
import scipy as sp
import scipy.sparse
import warnings
import networkx as nx

from HierarchicalClustering.GraphObjects import GraphCluster
from graph_utils import get_second_eigenpair, create_subgraph
import matplotlib.pyplot as plt
from networkx.drawing.nx_pylab import draw
from Hypergraph import Hypergraph


class HierarchicalClusterer(object):
    """
    A class to perform hierarchical clustering on either a weighted, undirected graph
    or a weighted, undirected hypergraph.

    -------------------------------------------------------------------------------------------------
    If clustering on a graph we use the MakeTree algorithm and spectral bi-partitioning based
    on the eigenvalues of the random walk Laplacian matrix:

    [1] MakeTree Algorithm              - "A Cost Function For Similarity-Based Hierarchical Clustering", Dashupta S. (2015) arXiv:1510.05043
    [2] Spectral Partitioning Algorithm - "Normalized Cuts and Image Segmentation", Malik J. and Shi J. (2000), IEEE

    For a comprehensive introduction to the topic of spectral clustering see:
    [3] A Tutorial On Spectral Clustering, von Luxburg U. (2007) arXiv:0711.0189
    -------------------------------------------------------------------------------------------------
    If clustering on a hypergraph we use the MakeTree algorithm and the Normalized Hypergraph
    Cut algorithm for hypergraphs, a generalization of the graph-based spectral bi-partitioning
    algorithm:

    [4] Normalized Hypergraph Cut       - “Learning with hypergraphs: Clustering, classification, and embedding.” Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.  Advances in neural information processing systems. (2006)
    -------------------------------------------------------------------------------------------------

    GENERIC PARAMETERS:
    :param stop_criterion: specifies the stop criterion for when to stop clustering. The options are:
                           'eigenvalue' - stop partitioning a cluster when the value of the second
                                          smallest eigenvalue of the cluster's Laplace matrix falls
                                          below a specified value
                           'tree_height' - run the full hierarchical clustering down to singleton
                                          leaf nodes and then output graph clusters from a specified
                                          height in the hierarchical clustering tree
                           'cluster_size' - stop partitioning a cluster when the number of nodes in
                                          the partitioned cluster would below a specified size
    :param min_ssev (float): [Only if stop criteiron is 'eigenvalue'] The minimum value of the second
                        smallest eigenvalue of the Laplace matrix for when to stop partitioning
    :param tree_output_height (int): [Only if stop criterion is 'tree_height'] The height in the hierarchical
                               clustering tree from which to output the final node clusters, e.g. height of 0
                               would output only leaf nodes.
    :param min_cluster_size (int): [Only if stop criterion is 'cluster_size'] The minimum cluster size
                             of the final output node clusters

    PARAMETERS FOR HIERARCHICAL CLUSTERING OF GRAPHS
    :param n_init (int): [K-means hyperparameter] The number of times the k-means algorithn will be run
                    with different centroid seeds. The final result will be the best output of
                    n_init consecutive runs in terms of inertia (default 10)
    :param max_iter (int): [K-means hyperparameter] The maximum number of iterations of the k-means algorithm
                    for a single run (default 300)

    PARAMETERS FOR HIERARCHICAL CLUSTERING OF HYPERGRAPHS
    :param threshold (float): The second smallest eigenvalue threshold value for the Normalized Hypergraph Cut
                              algorithm.
    :param max_fractional_size (float): Hypergraph splitting stops either either of the partitioned hypergraphs
    have more than max_fractional_size number of nodes compared to the original input hypergraph
    """

    def __init__(self, Hypergraph, config):
        self.min_cluster_size = config['min_cluster_size']
        self.max_lambda2 = config['max_lambda2']
        self.Hypergraph = Hypergraph
        self.graph_cluster = []
        self.hypergraph_cluster = []

        assert self.min_cluster_size > 2, "Argument Error: min_cluster_size must be greater than 2"
        assert 0 < self.max_lambda2 < 2, "Argument Error: max_lambda2 needs to be greater than 0 and less than 2"
        assert self.Hypergraph.number_of_nodes() > self.min_cluster_size, \
            "Argument Error: min_cluster_size needs to be smaller than the number of nodes in the hypergraph"

    def _sweep_set(self, adjacency_matrix, v_2, degrees):
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

    def _cheeger_cut(self, graph, v_2):
        """
        Given a networkx graph G, find the cheeger cut.
        :param graph: The graph on which to operate
        :return: A set containing the vertices on one side of the cheeger cut
        """
        # Compute the key graph matrices
        adjacency_matrix = nx.adjacency_matrix(graph)
        graph_degrees = [t[1] for t in nx.degree(graph)]

        # Perform the sweep set operation to find the sparsest cut
        vertices_indices1 = self._sweep_set(adjacency_matrix, v_2, graph_degrees)
        vertices1 = set([n for i, n in enumerate(graph.nodes()) if i in vertices_indices1])
        Subgraph1 = create_subgraph(graph, vertices1)

        vertices2 = set(graph.nodes()).difference(vertices1)
        Subgraph2 = create_subgraph(graph, vertices2)
        return Subgraph1, Subgraph2

    def get_clusters(self, graph):
        v_2, lambda2 = get_second_eigenpair(graph)
        print(lambda2)
        if lambda2 > self.max_lambda2:
            self.graph_cluster.append(graph)
            print('Met lambda stopping criterion!')
            return None
        else:
            subgraph1, subgraph2 = self._cheeger_cut(graph, v_2)
            print(subgraph1.number_of_nodes())
            print(subgraph2.number_of_nodes())
            if (self.min_cluster_size and
                    (subgraph1.number_of_nodes() < self.min_cluster_size or
                     subgraph2.number_of_nodes() < self.min_cluster_size)):
                self.graph_cluster.append(graph)
                print('Nodes of first subgraph: {}'.format(set(subgraph1.nodes())))
                print('Nodes of second subgraph: {}'.format(set(subgraph2.nodes())))

                return None
            else:
                return self.get_clusters(subgraph1), self.get_clusters(subgraph2)

    def hierarchical_clustering(self):
        """
        Hierarchical cluster a graph/hypergraph G.

        :param: G (either Graph or EnhancedUndirectedGraph)
                - the object to run hierarchical clustering on
        :returns: list of leaf node graph/hypergraph objects obtained
                  after hierarchical clustering
        """
        original_graph = self.Hypergraph.convert_to_graph()
        self.get_clusters(original_graph)
        print(f"Number of clusters: {len(self.graph_cluster)}")
        for idx, graph in enumerate(self.graph_cluster):
            print(f'Graph# {idx}, #nodes {graph.number_of_nodes()}')
            plt.figure()
            draw(graph)
        plt.show()
        graph_cluster = GraphCluster(self.graph_cluster)
        self.hypergraph_cluster = graph_cluster.convert_to_hypergraph_cluster_from_template(self.Hypergraph)
        for idx, hypergraph in enumerate(self.hypergraph_cluster):
            print(f'Hypergraph# {idx}, #nodes {hypergraph.number_of_nodes()}')


        return self.hypergraph_cluster
