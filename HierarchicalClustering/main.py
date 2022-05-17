from GraphObjects import Hypergraph
from HierarchicalClustering import HierarchicalClusterer
from HierarchicalClustering.diagnostics import hierarchical_clustering_diagnostics, hypergraph_diagnostics, \
    random_walk_diagnostics

if __name__ == "__main__":
    config = {
        'clustering_params': {
            'min_cluster_size': 3,
            'max_lambda2': 0.7,
        },
        'random_walk_params': {
            'epsilon': 0.1,
            'max_num_paths': 3,
            'alpha_sym': 0.1,
            'pca_dim': 2,
            'clustering_method_threshold': 50,
            'max_path_length': 7,
            'theta_p': 0.5,
            'multiprocessing': False
        }
    }

    print('Original Hypergraph')
    original_hypergraph = Hypergraph(database_file='./Databases/MovieLensMini.db',
                                     info_file='./Databases/MovieLensMini.info')

    hc = HierarchicalClusterer(original_hypergraph, config=config['clustering_params'])

    # hypergraph_diagnostics(original_hypergraph)
    # hierarchical_clustering_diagnostics(original_hypergraph)
    # random_walk_diagnostics(original_hypergraph)


    # cProfile.run("Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb1.info')")
    #
    # hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
    # hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()
    #
    # hypergraph_communities = [Communities(hypergraph, config=config['random_walk_params'])
    #                           for hypergraph in hypergraph_clusters]
    #
    #[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]
    #
    # #cProfile.run("Communities(hypergraph_clusters[0], config=config['random_walk_params'])")
    # cProfile.run("[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]")
    #
    # for communities in hypergraph_communities:
    #     print(communities)

    # communities = Communities(original_hypergraph, config=config['random_walk_params'])
    # community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
    #                                      original_hypergraph=original_hypergraph)
    # print(communities)
    # community_printer.write_files(file_name='imdb')


