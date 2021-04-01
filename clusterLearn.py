from EnhancedHypergraph import EnhancedUndirectedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Community import write_communities_file
import itertools

if __name__ == "__main__":
    H = EnhancedUndirectedHypergraph()

    #Generate a hypergraph from a database file
    H.read_from_alchemy_db(file_name="smoking.db")

    #Convert the hypergraph to a graph
    G = H.convert_to_graph(verbose=True)

    #Perform hierarchical clustering on the graph
    clusterer = HierarchicalClusterer(stop_criterion='cluster_size', min_cluster_size=50)
    graph_clusters = clusterer.hierarchical_clustering(G)

    #Find the communities in each cluster
    communities = []
    for graph in graph_clusters:
        cluster_hypergraph = H.convert_to_hypergraph(graph)
        communities.append(cluster_hypergraph.generate_community())
    
    #Save the communities to disk
    write_communities_file(H,communities,'test_file')
    