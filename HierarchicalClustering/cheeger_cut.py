import numpy as np
import scipy as sp
import scipy.sparse
import networkx as nx
from graph_utils import create_subgraph
from GraphObjects import Graph


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


def cheeger_cut(graph: Graph, v_2):
    """
    Given a graph G and the second eigenvector of the laplacian matrix, find the cheeger cut.
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
