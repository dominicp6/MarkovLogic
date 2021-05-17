import networkx as nx
import numpy as np
from scipy.linalg import eigh
from Hypergraph import Hypergraph
from itertools import combinations

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

def convert_hypergraph_to_graph(hypergraph, sum_weights_for_multi_edges = True):
    """
    Converts the undirected hypergraph to a graph by replacing all 
    k-hyperedges with k-cliques (a k-clique is a fully connected 
    subgraph with k nodes). This is useful as a pre-processing 
    step for applying graph-based clustering algorithms.

    :param sum_weights_for_multi_edges: if True then replaces any
        multi-edges generated in the hypergraph -> graph conversion
        with a single edge of weight equal to the number of multi
        -edges. If false, give all edges in the graph uniform weight
        regardless of the number of multi-edges.
    """
    graph = nx.Graph()

    for hyperedge_id in hypergraph.get_hyperedge_id_set():
        nodes = hypergraph.get_hyperedge_nodes(hyperedge_id)
        
        #from the hyperedge node set construct a complete subgraph (clique)
        for e in combinations(nodes,2):
            if sum_weights_for_multi_edges == True:
                #increment edge weight if edge already exists
                if graph.has_edge(*e):
                    graph[e[0]][e[1]]['weight'] += 1
                #else add the new edge
                else:
                    graph.add_edge(*e, weight=1)
            else:
                graph.add_edge(*e, weight=1)

    #Check that the graph is connected
    assert nx.is_connected(graph)

    return graph

def convert_graph_to_hypergraph(graph, template_hypergraph):
    """
    Converts an undirected graph, or simply a set of graph nodes,
    into a undirected hypergraph using an instance of EnhancedUndirectedHypergraph 
    as a template.

    :param graph: The graph (or node set) to be converted to a hypergraph
    :param template_hypergraph: The hypergraph used as a template for the conversion

    """
    hypergraph = Hypergraph()
    
    if isinstance(graph, nx.Graph):
        nodes = graph.nodes()
    elif isinstance(graph, set):
        nodes = graph
    else:
        raise ValueError('Input must be either of type Graph or Set, but is of type {}'.format(type(graph)))

    for node in nodes:
        #for each node in the graph, find the sets of hyperedge nodes from the
        #template hypergraph which contain that node
        for hyperedge_id in template_hypergraph.hyperedges_of_nodes[node]:
            #add the corresponding hyperedges to the new hypergraph instance
            hypergraph.add_hyperedge(template_hypergraph.get_hyperedge_nodes(hyperedge_id), 
                                    predicate = template_hypergraph.get_predicate_of_hyperedge(hyperedge_id), 
                                    node_name_to_node_type=template_hypergraph.node_name_to_node_type)
    
    return hypergraph