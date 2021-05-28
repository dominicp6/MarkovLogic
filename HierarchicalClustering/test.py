import hypernetx as hnx
import matplotlib.pyplot as plt
from hypernetx import Entity
from networkx.drawing.nx_pylab import draw
from GraphObjects import EnhancedHypergraph
from NewHC import HierarchicalClusterer

H = EnhancedHypergraph(database_file='Databases/smoking.db', info_file='Databases/smoking.info')
#G = H.convert_to_graph(True)
config = {
    'randomwalk_params': {'num_walks': 1000,
                          'max_length': 7,
                          'walk_scaling_param': 5,
                          'theta_hit': 6.9,
                          'theta_sym': 0.1,
                          'theta_js': 1,
                          'num_top': 3},
    'clustering_params': {'min_cluster_size': 3,
                          'max_lambda2': .7},
    'terminal_params': {
        'verbose': False,
    }
}
#clusterer = HierarchicalClusterer(H, config=config['clustering_params'])
#hypergraph_clusters = clusterer.hierarchical_clustering()

#for i, hypergraph in enumerate(hypergraph_clusters):
    #print(f'Running random walks on hypergraph {i+1}/{len(hypergraph_clusters)}'

H.generate_communities(config['randomwalk_params'])

# for hg in hypergraph_clusters:
#     plt.figure()
#     hnx.draw(hg)
# plt.show()
