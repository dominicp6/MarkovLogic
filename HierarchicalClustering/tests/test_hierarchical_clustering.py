import unittest

from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from graph_utils import get_second_eigenpair

imdb_db = './Databases/imdb1.db'
imdb_info = './Databases/imdb.info'

H = Hypergraph(database_file=imdb_db, info_file=imdb_info)
clustering_params = {'min_cluster_size': 3, 'max_lambda2': .7}
clusterer = HierarchicalClusterer(H, config=clustering_params)
G = H.convert_to_graph()
clusterer.get_clusters(G)
graph_clusters = clusterer.graph_clusters


class TestHierarchicalClustering(unittest.TestCase):

    def test_min_cluster_size(self):
        assert all(graph.number_of_nodes() > clustering_params['min_cluster_size'] for graph in graph_clusters)

    def test_max_lambda2(self):
        number_exceeding_threshold = sum(
            [get_second_eigenpair(graph)[1] > clustering_params['max_lambda2'] for graph in graph_clusters])
        print(f"{number_exceeding_threshold}/{len(graph_clusters)} hypergraphs have lambda2 > max_lambda2")

    def test_no_nodes_lost(self):
        num_nodes = sum([graph.number_of_nodes() for graph in graph_clusters])
        assert num_nodes == H.number_of_nodes(), f"Expected #nodes: {H.number_of_nodes()}, Actual {num_nodes}"
