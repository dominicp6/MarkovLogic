import hypernetx as hnx
import matplotlib.pyplot as plt
from hypernetx import Entity
from networkx.drawing.nx_pylab import draw
from GraphObjects import EnhancedHypergraph
from NewHC import HierarchicalClusterer

H = EnhancedHypergraph(database_file='ani.db')
hnx.draw(H)
G = H.convert_to_graph(True)
config = {
    'randomwalk_params': {'number_of_walks': 100,
                          'max_length': 100,
                          'use_sample_paths': False,
                          'HT_merge_threshold': 2,
                          'JS_merge_threshold': 2,
                          'N_top': 5, },
    'clustering_params': {'min_cluster_size': 20,
                          'max_lambda2': .7},
    'terminal_params': {
        'verbose': False,
    }
}
clusterer = HierarchicalClusterer(H, config=config['clustering_params'])
hypergraph_clusters = clusterer.hierarchical_clustering()

for hg in hypergraph_clusters:
    plt.figure()
    hnx.draw(hg)
plt.show()
