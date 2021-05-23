from GraphObjects import EnhancedHypergraph
from NewHC import HierarchicalClusterer as NewHierarchicalClusterer
from OldHC import HierarchicalClusterer as OldHierarchicalClusterer
from time import time


config = {
    'randomwalk_params': {'number_of_walks': 100,
                          'max_length': 100,
                          'use_sample_paths': False,
                          'HT_merge_threshold': 2,
                          'JS_merge_threshold': 2,
                          'N_top': 5, },
    'clustering_params': {'min_cluster_size': 3,
                          'max_lambda2': 0.7},
    'terminal_params': {
        'verbose': False,
    }
}

log_file = 'timings_test.log'
databases = ['smoking.db', 'imdb1.db', 'function.db', 'ani.db'] # 'nations.db', 'MovieLensMini.db', 'kinship.db',

file = open('testing', "w")
for database in databases:
    H = EnhancedHypergraph(database_file=database)
    G = H.convert_to_graph(True)

    time0 = time()
    new_clusterer = NewHierarchicalClusterer(H, config=config['clustering_params'])
    new_hypergraph_clusters = new_clusterer.hierarchical_clustering()
    time1 = time()

    old_clusterer = NewHierarchicalClusterer(H, config=config['clustering_params'])
    old_hypergraph_clusters = old_clusterer.hierarchical_clustering()
    time2 = time()

    file.write(f"Database {database}, GroundAtoms {H.number_of_nodes()}, "
               f"NewHC ({len(new_hypergraph_clusters)}){time1-time0}, "
               f"OldHC ({len(old_hypergraph_clusters)}){time2-time1}\n")
    print(f"Database {database}, GroundAtoms {H.number_of_nodes()}, "
               f"NewHC ({len(new_hypergraph_clusters)}){time1 - time0}, "
               f"OldHC ({len(old_hypergraph_clusters)}){time2 - time1}\n")
    print('Done!')
file.close()




