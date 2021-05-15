import networkx as nx
from EnhancedHypergraph import EnhancedUndirectedHypergraph
from itertools import combinations

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
    
    if hypergraph._verbose:
        print("New graph object")
        print("--------------------------------")
        print("#nodes               : {}".format(graph.order()))
        print("#edges               : {}".format(graph.size()))
        print("#connected components: {}".format(nx.number_connected_components(graph)))
        print("--------------------------------")

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
    #initialise a new hypergraph
    hypergraph = EnhancedUndirectedHypergraph()
    
    if isinstance(graph, nx.Graph):
        nodes = graph.nodes()
    elif isinstance(graph, set):
        nodes = graph
    else:
        raise ValueError('Input must be either of type Graph or Set, but is of type {}'.format(type(graph)))

    for node in nodes:
        #for each node in the graph, find the sets of hyperedge nodes from the
        #template hypergraph which contain that node
        for hyperedge_id in template_hypergraph._node_to_hyperedge_ids[node]:
            #add the corresponding hyperedges to the new hypergraph instance
            hypergraph.add_hyperedge(template_hypergraph.get_hyperedge_nodes(hyperedge_id), 
                                    weight=1, 
                                    attr_dict = {"predicate": template_hypergraph.get_hyperedge_attribute(hyperedge_id, "predicate")}, 
                                    node_name_to_node_type=template_hypergraph._node_name_to_node_type)
    
    return hypergraph