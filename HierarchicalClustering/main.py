from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter
import cProfile
import numpy as np

if __name__ == "__main__":
    config = {
        'clustering_params': {
            'min_cluster_size': 10,
            'max_lambda2': 0.8,
        },
        'random_walk_params': {
            'epsilon': 0.05,
            'max_num_paths': 3,
            'pca_dim': 2,
            'clustering_method_threshold': 50,
            'max_path_length': 5,
            'theta_p': 0.01,
            'pruning_value': 10,
            'multiprocessing': False
        }
    }

    sm_config = {
        "num_walks": 10000,
        "max_length": 5,
        "theta_hit": 4.9,
        "theta_sym": 0.1,
        "theta_js": 100,
        "num_top": 3,
    }

    original_hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')

    # cProfile.run("Hypergraph(database_file='./Databases/kinship.db', info_file='./Databases/kinship.info')")

    hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
    hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()
    hypergraph_communities = [Communities(hypergraph, config=config['random_walk_params'])
                              for hypergraph in hypergraph_clusters]

    # hypergraph_communities = [Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]
    # cProfile.run("Communities(hypergraph_clusters[0], config=config['random_walk_params'])")
    # cProfile.run("[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]")
    # for communities in hypergraph_communities:
    #     print(communities)

    # for communities in hypergraph_communities:
    #     print(communities)
    # communities = Communities(original_hypergraph, config=config['random_walk_params'])
    # list_of_communities = [Communities(hypergraph, config=config['random_walk_params'])
    #                        for hypergraph in hypergraph_clusters]
    list_of_communities = [Communities(original_hypergraph,
                                        config=config['random_walk_params'],
                                        )]

    community_printer = CommunityPrinter(
        list_of_communities=hypergraph_communities,
        original_hypergraph=original_hypergraph)
    for communities in list_of_communities:
        print(communities)
    #community_printer.write_files(file_name='imdb')

    # print('Average number of single nodes')
    # single_nodes = [[community.number_of_single_nodes for community in hypergraph_communities[i].communities.values()]
    #               for i in range(len(hypergraph_communities))]
    #
    # print('Average number of clusters')
    # clusters = [[community.number_of_clusters for community in hypergraph_communities[i].communities.values()]
    #               for i in range(len(hypergraph_communities))]
    #
    # single_nodes_flat = [node for sublist in single_nodes for node in sublist]
    # clusters_flat = [node for sublist in clusters for node in sublist]
    # print(single_nodes_flat)
    # print(np.mean(single_nodes_flat))
    # print(np.mean(clusters_flat))

