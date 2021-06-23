from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter
import cProfile

if __name__ == "__main__":
    config = {
        'clustering_params': {
            'min_cluster_size': 10,
            'max_lambda2': 0.8,
        },
        'random_walk_params': {
            'epsilon': 0.05,
            'num_top': 3,
            'theta_hit': 4.9,
            'theta_sym': 0.1,
            'theta_js': 0.0005,
            'max_js_div': 0.003,
            'pca_dim': 2,
            'pca_threshold': 40,
            'k': 1.25,
            'max_path_length': 5,
            'multiprocessing': False,
        }
    }

    original_hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')

    #cProfile.run("Hypergraph(database_file='./Databases/kinship.db', info_file='./Databases/kinship.info')")

    hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
    hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

    # hypergraph_communities = [Communities(hypergraph, config=config['random_walk_params'])
    #                           for hypergraph in hypergraph_clusters]

    cProfile.run("[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]")

    # for communities in hypergraph_communities:
    #     print(communities)
    # communities = Communities(original_hypergraph, config=config['random_walk_params'])
    # community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
    #                                      original_hypergraph=original_hypergraph)
    # print(communities)
    # community_printer.write_files(file_name='imdb')


