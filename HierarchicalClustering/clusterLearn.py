from EnhancedHypergraph import EnhancedUndirectedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
from RandomWalker import RandomWalker
from CommunityPrinter import CommunityPrinter
import itertools
import cProfile
import os
import time


# TODO: check how node typing should affect the RW routine

def run_hierarchical_clustering(database_file, config):
    output_file_name = database_file.rstrip('.db')

    rw_config = config['randomwalk_params'] # Is it necessary to unpack all these parameters?
    hc_config = config['clustering_params']
    dir_config = config['directory_params']
    terminal_config = config['terminal_params']

    start = time.time()
    hypergraph = EnhancedUndirectedHypergraph(verbose=terminal_config['verbose'])
    rw = RandomWalker(number_of_walks=rw_config['number_of_walks'],
                      max_length=rw_config['max_length'],
                      use_sample_paths=rw_config['use_sample_paths'],
                      HT_merge_threshold=rw_config['HT_merge_threshold'],
                      JS_merge_threshold=rw_config['JS_merge_threshold'],
                      N_top=rw_config['N_top']) # Why not RandomWalker(rw_config),
                                                # also either instantiate all at top or all when you need them

    # Generate a hypergraph from a database file
    # cProfile.run('hypergraph.generate_from_database(db_file_name="ani.db")')
    path_to_database_file = os.path.join(dir_config['data_dir'], database_file)
    hypergraph.generate_from_database(path_to_db_file=path_to_database_file) # This should happen right in instantiation
    end1 = time.time()

    # Convert the hypergraph to a graph
    # cProfile.run('hypergraph.convert_to_graph(verbose=True)')
    graph = hypergraph.convert_to_graph()
    end2 = time.time()

    # Perform hierarchical clustering on the graph
    clusterer = HierarchicalClusterer(stop_criterion=hc_config['stop_criterion'], min_ssev=hc_config['min_ssev'],
                                      tree_output_depth=hc_config['tree_output_depth'],
                                      min_cluster_size=hc_config['min_cluster_size'], n_init=hc_config['n_init'],
                                      max_iter=hc_config['max_iter'], threshold=hc_config['threshold'],
                                      max_fractional_size=hc_config['max_fractional_size']) # Again, why not HC(hc_config)
    # cProfile.run('clusterer.hierarchical_clustering(graph)')
    graph_clusters = clusterer.hierarchical_clustering(graph)
    end3 = time.time()
    # print(graph_clusters)
    # Find the communities in each cluster
    communities = []
    community_hypergraphs = [] # What are communities? also how similar ar communities and community_hypergraphs?
    for cluster in graph_clusters:
        cluster_hypergraph = hypergraph.convert_to_hypergraph(cluster) # This should be of the form graph.convert_to_hypergraph
        community_hypergraphs.append(cluster_hypergraph)
        # cProfile.run('rw.run_random_walks(cluster_hypergraph)')
        communities.append(rw.run_random_walks(cluster_hypergraph))
    end4 = time.time()
    # Save the communities to disk
    com_printer = CommunityPrinter(output_directory=dir_config['data_dir'], original_hypergraph=hypergraph,
                                   communities=communities, community_hypergraphs=community_hypergraphs) # Not everything needs to be an object
                                                                                                        # If anything, then the object needs to be community, and it should have a function print
    com_printer.write_communities_files(file_name=output_file_name, verbose=terminal_config['verbose'])
    end5 = time.time()

    if terminal_config['verbose']:
        print('Read file:            {}'.format(str(end1 - start)))
        print('Convert to Graph:     {}'.format(str(end2 - end1)))
        print('Hierarchical Cluster: {}'.format(str(end3 - end2)))
        print('Random Walks:         {}'.format(str(end4 - end3)))
        print('Saving Files:         {}'.format(str(end5 - end4)))
