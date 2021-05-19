import hypernetx as hnx
import matplotlib.pyplot as plt
from hypernetx import Entity
from networkx.drawing.nx_pylab import draw
from GraphObjects import EnhancedHypergraph
from HierarchicalClusterer import HierarchicalClusterer

H = EnhancedHypergraph(database_file='smoking.db')
hnx.draw(H)
G = H.convert_to_graph(True)
config = {
    'randomwalk_params': {'number_of_walks': 100,
                          'max_length': 100,
                          'use_sample_paths': False,
                          'HT_merge_threshold': 2,
                          'JS_merge_threshold': 2,
                          'N_top': 5, },
    'clustering_params': {'stop_criterion': 'cluster_size',
                          'min_ssev': 0.01,
                          'tree_output_depth': 1,
                          'min_cluster_size': 2,
                          'n_init': 10,
                          'max_iter': 300,
                          'threshold': 0.01,
                          'max_fractional_size': 0.9},
    'terminal_params': {
        'verbose': False,
    }
}
clusterer = HierarchicalClusterer(config=config['clustering_params'])
graph_clusters = clusterer.hierarchical_clustering(G)
print(graph_clusters)
for g in graph_clusters:
    print(g.nodes())
hypergraph_clusters = [graph.convert_to_hypergraph_from_template(H) for graph in graph_clusters]
#for i in graph_clusters:
#    draw(i)
for hg in hypergraph_clusters:
    plt.figure()
    hnx.draw(hg)
plt.show()
