from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from printing_communities import write_communities_to_file

config = {
    'clustering_params': {
        'min_cluster_size': 10,
        'max_lambda2': 0.8,
    },
    'random_walk_params': {
        'num_walks': 1000,
        'max_length': 5,
        'walk_scaling_param': 5,
        'theta_hit': 4.9,
        'theta_sym': 0.1,
        'theta_js': 1.0,
        'num_top': 3
    }
}

original_hypergraph = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')

hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=config['clustering_params'])
hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

hypergraph_communities = []
for hypergraph in hypergraph_clusters:
    hypergraph_communities.append(Communities(hypergraph, config=config['random_walk_params']))

write_communities_to_file(list_of_communities=hypergraph_communities, original_hypergraph=original_hypergraph,
                          file_name='imdb')
