from Hypergraph import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from RandomWalker import RandomWalker
from CommunityPrinter import write_communities_files
from graph_utils import convert_hypergraph_to_graph, convert_graph_to_hypergraph
import itertools
import cProfile
import os
import time

def run_hierarchical_clustering(database_file, config, info_file=None):
    output_file_name = database_file.rstrip('.db')
    rw_config = config['randomwalk_params'] 
    hc_config = config['clustering_params']
    dir_config = config['directory_params']
    terminal_config = config['terminal_params']

    path_to_database_file = os.path.join(dir_config['data_dir'], database_file)
    if info_file:
        path_to_info_file = os.path.join(dir_config['data_dir'], info_file)
    else:
        path_to_info_file = None

    # Construct the original hypergraph and graph objects
    original_hypergraph = Hypergraph(database_file=path_to_database_file, info_file=path_to_info_file)
    original_graph = convert_hypergraph_to_graph(original_hypergraph)

    # Perform hierarchical clustering on the graph
    clusterer = HierarchicalClusterer(config=hc_config) 
    graph_clusters = clusterer.hierarchical_clustering(original_graph)
    hypergraph_clusters = [convert_graph_to_hypergraph(graph, 
                            template_hypergraph=original_hypergraph) for graph in graph_clusters]

    # Find the communities in each hypergraph cluster
    rw = RandomWalker(config=rw_config) 
    communities = [rw.run_random_walks(hypergraph) for hypergraph in hypergraph_clusters]

    # Save the communities to disk
    path_to_output_file = os.path.join(dir_config['data_dir'], output_file_name)
    write_communities_files(output_file=path_to_output_file, 
                            communities=communities, 
                            hypergraph_clusters=hypergraph_clusters, 
                            original_hypergraph=original_hypergraph, 
                            verbose=terminal_config['verbose'])
