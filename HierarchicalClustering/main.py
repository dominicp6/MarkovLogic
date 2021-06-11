from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities


config = {
    'clustering_params' : {
        'min_cluster_size' : 10,
        'max_lambda2' : 0.8,
    },
    'random_walk_params' : {
        'num_walks': 1000,
        'max_length': 5,
        'walk_scaling_param': 5,
        'theta_hit': 4.9,
        'theta_sym': 0.1,
        'theta_js': 1.0,
        'num_top': 3
    }
}

hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')

communities = Communities(hypergraph, config['random_walk_params'])
print(communities)



