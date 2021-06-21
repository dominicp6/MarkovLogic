import unittest
from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter

H = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')
config = {
    'clustering_params': {
        'min_cluster_size': 10,
        'max_lambda2': 0.8,
    },
    'random_walk_params': {
        'epsilon': 0.05,
        'k': 1.25,
        'max_path_length': 5,
        'theta_hit': 4.9,
        'theta_sym': 0.1,
        'theta_js': 1.0,
        'num_top': 3
    }
}

original_communities = Communities(H, config=config['random_walk_params'])

hierarchical_clusterer = HierarchicalClusterer(hypergraph=H, config=config['clustering_params'])
hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()
hypergraph_communities = []
for hypergraph in hypergraph_clusters:
    hypergraph_communities.append(Communities(hypergraph, config=config['random_walk_params']))


class TestCommunityPrinter(unittest.TestCase):

    def test_similar_to_SOTA_when_not_using_hierarchical_clustering(self):
        community_printer = CommunityPrinter(list_of_communities=[original_communities],
                                             original_hypergraph=H)
        community_printer.write_files('./tests/imdb_no_hc')

        with open("./tests/imdb_no_hc.ldb", "r") as ldb_file:
            lines = [line for line in ldb_file]
            assert abs(len(lines) - 1038) < 80

        with open("./tests/imdb_no_hc.uldb", "r") as uldb_file:
            lines = [line for line in uldb_file]
            assert abs(len(lines) - 5341) < 400

        with open("./tests/imdb_no_hc.srcnclusts", "r") as srcnclusts_file:
            lines = [line for line in srcnclusts_file]
            assert abs(len(lines) - 805) < 70

    def test_similar_to_SOTA_when_using_hierarchical_clustering(self):
        community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
                                             original_hypergraph=H)
        community_printer.write_files('./tests/imdb_hc')
        with open("./tests/imdb_hc.ldb", "r") as ldb_file:
            lines = [line for line in ldb_file]
            assert abs(len(lines) - 1038) < 300

        with open("./tests/imdb_hc.uldb", "r") as uldb_file:
            lines = [line for line in uldb_file]
            assert abs(len(lines) - 5341) < 1800

        with open("./tests/imdb_hc.srcnclusts", "r") as srcnclusts_file:
            lines = [line for line in srcnclusts_file]
            assert abs(len(lines) - 805) < 160
