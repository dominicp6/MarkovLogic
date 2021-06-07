import networkx as nx
import scipy as sp

def get_second_eigenpair(graph):

    laplacian_matrix = nx.normalized_laplacian_matrix(graph)
    # Compute the second smallest eigenvalue of the laplacian matrix
    eig_vals, eig_vecs = sp.sparse.linalg.eigsh(laplacian_matrix, which="SM", k=2)
    v_2 = eig_vecs[:, 1]
    lambda2 = eig_vals[1]
    return v_2, lambda2

def create_subgraph(G, subgraph_nodes):
    """
    Constructs a subgraph (SG) from a graph (G), where the nodes
    of the subgraph are subgraph_nodes (a subset of the nodes 
    of G)
    """
    SG = G.__class__()
    if len(subgraph_nodes) > 1:
        SG.add_edges_from((n, nbr, d)
            for n, nbrs in G.adj.items() if n in subgraph_nodes
            for nbr, d in nbrs.items() if nbr in subgraph_nodes)
    else:
        #subgraph_nodes is a singleton set(), next line retrieves the element
        (subgraph_node,) = subgraph_nodes
        SG.add_node(subgraph_node)
    SG.graph.update(G.graph)
    return SG

