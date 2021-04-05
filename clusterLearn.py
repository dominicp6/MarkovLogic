from EnhancedHypergraph import EnhancedUndirectedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
from RandomWalker import RandomWalker
from print_utils import write_communities_files
import itertools

 #TODO: check how node typing should affect the RW routine
 #TODO: check the reading type setting when importing a .info file
 #TODO: remove the need for an EnhancedGraph class

if __name__ == "__main__":
    H = EnhancedUndirectedHypergraph()
    rw = RandomWalker(number_of_walks=10)

    #Generate a hypergraph from a database file
    H.read_from_alchemy_db(db_file_name="ani.db")

    #Convert the hypergraph to a graph
    G = H.convert_to_graph(verbose=True)

    #Perform hierarchical clustering on the graph
    clusterer = HierarchicalClusterer(stop_criterion='cluster_size', min_cluster_size=2)
    graph_clusters = clusterer.hierarchical_clustering(G)
    print(graph_clusters)
    #Find the communities in each cluster
    communities = []
    community_hypergraphs = []
    for graph in graph_clusters:
        cluster_hypergraph = H.convert_to_hypergraph(graph)
        community_hypergraphs.append(cluster_hypergraph)
        communities.append(rw.run_random_walks(cluster_hypergraph))
    #Save the communities to disk
    write_communities_files(H,community_hypergraphs,communities,'test_file')
    