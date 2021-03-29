from EnhancedHypergraph import EnhancedUndirectedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
import itertools

if __name__ == "__main__":
    H = EnhancedUndirectedHypergraph()
    H.read_from_alchemy_db(file_name="ani.db")
    print(H)
    G = H.convert_to_graph()

    clusterer = HierarchicalClusterer()
    graph_clusters = clusterer.hierarchical_clustering(G)
    print(graph_clusters)
    total_order = 0
    for graph in graph_clusters:
        total_order += graph.order()
        hypergraph = H.convert_graph_to_hypergraph(graph)
        print(hypergraph)
    print(total_order)