from EnhancedHypergraph import EnhancedUndirectedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
from RandomWalker import RandomWalker
from CommunityPrinter import CommunityPrinter
import itertools
import cProfile
import time

 #TODO: check how node typing should affect the RW routine

if __name__ == "__main__":
    start = time.time()
    H = EnhancedUndirectedHypergraph()
    rw = RandomWalker(number_of_walks=10, use_sample_paths=True)

    #Generate a hypergraph from a database file
    #cProfile.run('H.read_from_alchemy_db(db_file_name="ani.db")')
    H.read_from_alchemy_db(db_file_name="ani.db")
    end1 = time.time()

    #Convert the hypergraph to a graph
    #cProfile.run('H.convert_to_graph(verbose=True)')
    G = H.convert_to_graph(verbose=True)
    end2 = time.time()

    #Perform hierarchical clustering on the graph
    clusterer = HierarchicalClusterer(stop_criterion='eigenvalue', min_cluster_size=3, max_fractional_size=0.95)
    #cProfile.run('clusterer.hierarchical_clustering(G)')
    graph_clusters = clusterer.hierarchical_clustering(G)
    end3 = time.time()
    #print(graph_clusters)
    #Find the communities in each cluster
    communities = []
    community_hypergraphs = []
    for graph in graph_clusters:
        cluster_hypergraph = H.convert_to_hypergraph(graph)
        community_hypergraphs.append(cluster_hypergraph)
        #cProfile.run('rw.run_random_walks(cluster_hypergraph)')
        communities.append(rw.run_random_walks(cluster_hypergraph))
    end4 = time.time()
    #Save the communities to disk
    com_printer = CommunityPrinter(original_hypergraph=H, communities=communities, community_hypergraphs=community_hypergraphs) 
    com_printer.write_communities_files(file_name='test_file')
    end5 = time.time()


    print('Read file:            {}'.format(str(end1-start)))
    print('Convert to Graph:     {}'.format(str(end2-end1)))
    print('Hierarchical Cluster: {}'.format(str(end3-end2)))
    print('Random Walks:         {}'.format(str(end4-end3)))
    print('Saving Files:         {}'.format(str(end5-end4)))
    
    