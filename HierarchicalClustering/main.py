from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter
import cProfile
import numpy as np

if __name__ == "__main__":
    config = {
        'clustering_params': {
            'min_cluster_size': 3,
            'max_lambda2': 0.0001,
        },
        'random_walk_params': {
            'epsilon': 0.05,
            'max_num_paths': 3,
            'alpha_sym': 0.1,
            'pca_dim': 2,
            'clustering_method_threshold': 50,
            'k': 1.25,
            'max_path_length': 5,
            'theta_p': 0.5,
            'multiprocessing': False
        }
    }

    def P_star(n, L):
        if n > 1:
            return 1 + (n * (n ** L - 1) / (n - 1))
        else:
            return 1

    def N_paths(P_star, epsilon=0.05, k=3):
        return ((k + 1) * (0.577 + np.log(P_star)) - 1) / epsilon ** 2

    def N_THT(L, epsilon=0.05):
        return (L-1)**2 / (4 * epsilon ** 2)


    def compute_execution_cost(L, n, nodes):
        return max(N_paths(P_star(n, L)), N_THT(L)) * nodes

    def compute_speed_up(original_hypergraph, hypergraph_clusters):
        original_cost = compute_execution_cost(L=original_hypergraph.diameter(),
                                               n=original_hypergraph.number_of_predicates(),
                                               nodes=original_hypergraph.number_of_nodes())
        final_cost = sum([compute_execution_cost(L=hypergraph.diameter(),
                                                 n=hypergraph.number_of_predicates(),
                                                 nodes=hypergraph.number_of_nodes())
                          for hypergraph in hypergraph_clusters])

        print(f"Speed-up: {round(original_cost / final_cost, 2)}")


    print('Original Hypergraph')
    original_hypergraph = Hypergraph(database_file='./Databases/MovieLensMini.db',
                                     info_file='./Databases/MovieLensMini.info')
    print(original_hypergraph)
    hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
    hierarchical_clusterer.run_hierarchical_clustering()

    print('Hypergraph Clusters')
    for hypergraph in hierarchical_clusterer.hypergraph_clusters:
        print(hypergraph)

    compute_speed_up(original_hypergraph, hierarchical_clusterer.hypergraph_clusters)







    #cProfile.run("Hypergraph(database_file='./Databases/kinship.db', info_file='./Databases/kinship.info')")

    #hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
    #hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

    # hypergraph_communities = [Communities(hypergraph, config=config['random_walk_params'])
    #                           for hypergraph in hypergraph_clusters]

    #[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]
    #cProfile.run("Communities(hypergraph_clusters[0], config=config['random_walk_params'])")
    #cProfile.run("[Communities(hypergraph, config=config['random_walk_params']) for hypergraph in hypergraph_clusters]")

    # for communities in hypergraph_communities:
    #     print(communities)
    # communities = Communities(original_hypergraph, config=config['random_walk_params'])
    # community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
    #                                      original_hypergraph=original_hypergraph)
    # print(communities)
    # community_printer.write_files(file_name='imdb')


