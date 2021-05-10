#Adapted and expanded from code in the HALP package (http://murali-group.github.io/halp/)

"""
.. module:: graph_utils
   :synopsis: Provides various methods for tranforming a graph/hypergraph
            (or its components) into useful corresponding matrix
            representations.
"""
import numpy as np
from scipy import sparse
import networkx as nx
from scipy.linalg import eigh
from EnhancedHypergraph import EnhancedUndirectedHypergraph


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
        SG.add_node(subgraph_nodes[0])
    SG.graph.update(G.graph)
    return SG


def get_node_mapping(H):
    """Generates mappings between the set of nodes and integer indices (where
    every node corresponds to exactly 1 integer index).

    :param H: the hypergraph to find the node mapping on.
    :returns: dict -- for each integer index, maps the index to the node.
              dict -- for each node, maps the node to the integer index.

    """
    node_set = H.get_node_set()
    nodes_to_indices, indices_to_nodes = {}, {}

    node_index = 0
    for node in node_set:
        nodes_to_indices.update({node: node_index})
        indices_to_nodes.update({node_index: node})
        node_index += 1

    return indices_to_nodes, nodes_to_indices


def get_hyperedge_id_mapping(H):
    """Generates mappings between the set of hyperedge IDs and integer indices
    (where every hyperedge ID corresponds to exactly 1 integer index).

    :param H: the hypergraph to find the hyperedge ID mapping on.
    :returns: dict -- for each integer index, maps the index to the hyperedge
                ID.
              dict -- for each hyperedge ID, maps the hyperedge ID to the
                integer index.
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, EnhancedUndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    indices_to_hyperedge_ids, hyperedge_ids_to_indices = {}, {}
    hyperedge_index = 0
    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_ids_to_indices.update({hyperedge_id: hyperedge_index})
        indices_to_hyperedge_ids.update({hyperedge_index: hyperedge_id})
        hyperedge_index += 1

    return indices_to_hyperedge_ids, hyperedge_ids_to_indices


def get_incidence_matrix(H, nodes_to_indices, hyperedge_ids_to_indices):
    """Creates the incidence matrix of the given hypergraph as a sparse matrix.

    :param H: the hypergraph for which to create the incidence matrix of.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the incidence matrix as a sparse matrix.
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, EnhancedUndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    rows, cols = [], []
    for hyperedge_id, hyperedge_index in hyperedge_ids_to_indices.items():
        for node in H.get_hyperedge_nodes(hyperedge_id):
            # get the mapping between the node and its ID
            rows.append(nodes_to_indices.get(node))
            cols.append(hyperedge_index)

    values = np.ones(len(rows), dtype=int)
    node_count = len(H.get_node_set())
    hyperedge_count = len(H.get_hyperedge_id_set())

    return sparse.csr_matrix((values, (rows, cols)),
                             shape=(node_count, hyperedge_count))


def get_vertex_degree_matrix(M, W):
    """Creates the diagonal maxtrix D_v of vertex degrees as a sparse matrix,
    where a vertex degree is the sum of the weights of all hyperedges
    in the vertex's star.

    :param M: the incidence matrix of the hypergraph to find the D_v matrix on.
    :param W: the diagonal hyperedge weight matrix of the hypergraph.
    :returns: sparse.csc_matrix -- the diagonal vertex degree matrix as a
            sparse matrix.

    """
    return sparse.diags([M * W.diagonal()], [0], format="csr")


def get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices):
    """Creates the diagonal matrix W of hyperedge weights as a sparse matrix.

    :param H: the hypergraph to find the weights.
    :param hyperedge_weights: the mapping from the indices of hyperedge IDs to
                            the corresponding hyperedge weights.
    :returns: sparse.csc_matrix -- the diagonal edge weight matrix as a
            sparse matrix.

    """
    # Combined 2 methods into 1; this could be written better
    hyperedge_weights = {}
    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_weights.update({hyperedge_ids_to_indices[hyperedge_id]:
                                 H.get_hyperedge_weight(hyperedge_id)})

    hyperedge_weight_vector = []
    for i in range(len(hyperedge_weights.keys())):
        hyperedge_weight_vector.append(hyperedge_weights.get(i))

    return sparse.diags([hyperedge_weight_vector], [0], format="csr")


def get_hyperedge_degree_matrix(M):
    """Creates the diagonal matrix of hyperedge degrees D_e as a sparse matrix,
    where a hyperedge degree is the cardinality of the hyperedge.

    :param M: the incidence matrix of the hypergraph to find the D_e matrix on.
    :returns: sparse.csc_matrix -- the diagonal hyperedge degree matrix as a
            sparse matrix.

    """
    degrees = M.sum(0).transpose()
    new_degree = []
    for degree in degrees:
        new_degree.append(int(degree[0:]))

    return sparse.diags([new_degree], [0], format="csr")


def fast_inverse(M):
    """Computes the inverse of a diagonal matrix.

    :param H: the diagonal matrix to find the inverse of.
    :returns: sparse.csc_matrix -- the inverse of the input matrix as a
            sparse matrix.

    """
    diags = M.diagonal()
    new_diag = []
    for value in diags:
        new_diag.append(1.0/value)

    return sparse.diags([new_diag], [0], format="csr")


def compute_normalized_laplacian(H,
                                  nodes_to_indices,
                                  hyperedge_ids_to_indices):
    """Computes the normalized Laplacian as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    :param H: the hypergraph to compute the normalized Laplacian
                    matrix for.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the normalized Laplacian matrix as a sparse
            matrix.

    """
    M = get_incidence_matrix(H,
                                nodes_to_indices, hyperedge_ids_to_indices)
    W = get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices)
    D_v = get_vertex_degree_matrix(M, W)
    D_e = get_hyperedge_degree_matrix(M)

    D_v_sqrt = D_v.sqrt()
    D_v_sqrt_inv = np.real(fast_inverse(D_v_sqrt).todense())
    D_v_sqrt_inv = sparse.csc_matrix(D_v_sqrt_inv)
    D_e_inv = fast_inverse(D_e)
    M_trans = M.transpose()

    theta = D_v_sqrt_inv * M * W * D_e_inv * M_trans * D_v_sqrt_inv

    node_count = len(H.get_node_set())
    I = sparse.eye(node_count)

    delta = I - theta
    return delta

def _compute_transition_matrix(H):
        """Computes the transition matrix for a random walk on the given
        hypergraph as described in the paper:
        Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
        "Learning with hypergraphs: Clustering, classification, and embedding."
        Advances in neural information processing systems. 2006.
        (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

        :param H: the hypergraph to find the transition matrix of.
        :returns: sparse.csr_matrix -- the transition matrix as a sparse matrix.

        """
        _, nodes_to_indices = get_node_mapping(H)
        _, hyperedge_ids_to_indices = get_hyperedge_id_mapping(H)

        M = get_incidence_matrix(H,nodes_to_indices, hyperedge_ids_to_indices)
        W = get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices)
        D_v = get_vertex_degree_matrix(M, W)
        D_e = get_hyperedge_degree_matrix(M)

        D_v_inv = fast_inverse(D_v)
        D_e_inv = fast_inverse(D_e)
        M_trans = M.transpose()

        #construct the transition matrix
        P = D_v_inv * M * W * D_e_inv * M_trans

        return P

def laplace_RW_spectrum(G):
    """
    For a graph G, solves the generalised eigenvalue problem:
    Lu = wDu
    where L = D - W is the Laplacian matrix of the graph,
            D_{ii} = \sum_{j} W_{ij} is a diagonal matrix
            W_{ij} is the weight between the ith and jth node in G
            u is an eigenvector 
            w is an eigenvalue
    
    Note that w, the generalised eigevectors of L, also correspond 
    to the eigenvectors of the so-called random walk Laplacian, L_{RW}
    where L_{RW} = D^{-1}L = I - D^{-1}W 
    
    Part of the Shi and Malik spectral clustering algorithm (refs: [2],[3])

    Ouputs the n smallest eigenvectors and eigenvalues where 
    n is the clusters_per_partition used for the Hierarchcical 
    clustering (=2 by default)
    """

    #compute graph matrices
    W = nx.adjacency_matrix(G).todense()
    D = np.diagflat(np.sum(W, axis=1))
    L = nx.laplacian_matrix(G)
    
    #solve the generalised eigenvalue problem
    w,v = eigh(L.todense(),D, eigvals=(0,1))
    
    return w,v