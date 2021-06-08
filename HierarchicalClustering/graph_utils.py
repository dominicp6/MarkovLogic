import networkx as nx
from scipy.sparse.linalg import eigsh


def get_second_eigenpair(graph):
    """
    Returns the second smallest eigenvalue and eigenvector of the laplacian matrix of a graph.
    """
    assert isinstance(graph, nx.Graph)

    laplacian_matrix = nx.normalized_laplacian_matrix(graph)

    # Compute the second smallest eigenvalue of the laplacian matrix
    eigen_values, eigen_vectors = eigsh(laplacian_matrix, which="SM", k=2)

    vector2 = eigen_vectors[:, 1]
    lambda2 = eigen_values[1]

    return vector2, lambda2


def create_subgraph(graph, subgraph_nodes):
    """
    Constructs a subgraph from a graph, where the nodes of the subgraph are subgraph_nodes (a subset of the nodes
    of the graph)
    """
    assert isinstance(graph, nx.Graph)

    subgraph = graph.__class__()
    if len(subgraph_nodes) > 1:
        subgraph.add_edges_from((node, neighbor, degree)
                                for node, neighbors in graph.adj.items() if node in subgraph_nodes
                                for neighbor, degree in neighbors.items() if neighbor in subgraph_nodes)
    else:
        # subgraph_nodes is a singleton set(), next line retrieves the element
        (subgraph_node,) = subgraph_nodes
        subgraph.add_node(subgraph_node)
    subgraph.graph.update(graph.graph)

    return subgraph
