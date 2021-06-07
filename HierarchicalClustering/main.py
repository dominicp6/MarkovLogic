from GraphObjects import EnhancedHypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities


config = {
    'clustering_params' : {
        'min_cluster_size' : 10,
        'max_lambda2' : 0.8,
    },
    'random_walk_params' : {
        'num_walks': 100,
        'max_length': 5,
        'walk_scaling_param': 5,
        'theta_hit': 4.9,
        'theta_sym': 0.1,
        'theta_js': 1,
        'num_top': 3
    }
}

hypergraph = EnhancedHypergraph(database_file='imdb1.db', info_file='imdb.info')

HC = HierarchicalClusterer(hypergraph, config['clustering_params'])
hypergraph_clusters = HC.hierarchical_clustering()

hgs_communities = []
for hypergraph in hypergraph_clusters:
    hgs_communities.append(Communities(hypergraph, config['random_walk_params']))

for hg_number, communities in enumerate(hgs_communities):
    print(f'Hypergraph {hg_number}')
    for node, cluster_dict in communities.communities.items():
        print(f'Source Node {node}')
        print(cluster_dict)
        for single_node in cluster_dict['single_nodes']:
            print(f'SINGLE NODE: {single_node.name}')

        for cluster_number, cluster in enumerate(cluster_dict['clusters']):
            print(f'CLUSTER {cluster_number}:')
            for node in cluster:
                print('     '+node)



