import unittest

import numpy as np
import math

from GraphObjects import Hypergraph
from NodeRandomWalkData import NodeClusterRandomWalkData
from js_divergence_utils import kl_divergence, js_divergence, compute_js_divergence_of_top_n_paths
from Communities import Communities
from random_walks import generate_node_random_walk_data
from clustering_nodes_by_path_similarity import get_close_nodes

H = Hypergraph(database_file='./Databases/smoking.db', info_file='./Databases/smoking.info')
config = {'epsilon': 0.01,
          'k': 1.25,
          'max_path_length': 5,
          'theta_hit': 6.9,
          'theta_sym': 0.1,
          'theta_js': 1.0,
          'num_top': 3}

communities = Communities(H, config).communities

H2 = Hypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')
config2 = {'epsilon': 0.01,
           'k': 1.25,
           'max_path_length': 5,
           'theta_hit': 4.9,
           'theta_sym': 0.1,
           'theta_js': 1.0,
           'num_top': 3}


class TestRandomWalks(unittest.TestCase):

    def test_correct_node_cluster_merging(self):
        for node in H.nodes.keys():
            nodes_rw_data = generate_node_random_walk_data(H, source_node=node, epsilon=0.01)
            close_nodes = get_close_nodes(nodes_rw_data, threshold_hitting_time=5)

            # MERGE SOME CLUSTERS ------------------------------------------------------------------------------
            js_clusters = [NodeClusterRandomWalkData([node]) for node in close_nodes]

            max_divergence = float('inf')
            cluster_to_merge1 = None
            cluster_to_merge2 = None

            while True:
                smallest_divergence = max_divergence
                for i in range(len(js_clusters)):
                    for j in range(i + 1, len(js_clusters)):
                        js_div = compute_js_divergence_of_top_n_paths(js_clusters[i], js_clusters[j],
                                                                      3)

                        if js_div < smallest_divergence and js_div < 0.25:
                            smallest_divergence = js_div
                            cluster_to_merge1 = i
                            cluster_to_merge2 = j

                # if we've found a pair of clusters to merge, merge the two clusters and continue
                if smallest_divergence < max_divergence:
                    js_clusters[cluster_to_merge1].merge(js_clusters[cluster_to_merge2])
                    del js_clusters[cluster_to_merge2]
                # otherwise, stop merging
                else:
                    break
            # --------------------------------------------------------------------------------------------------

            for node_cluster in js_clusters:
                # verify that path counts have been correctly added
                assert sum(node_cluster.path_counts.values()) == node_cluster.total_count

                # verify that the probability distribution of path counts is correctly normalised
                assert math.isclose(
                    sum(node_cluster.get_top_n_path_probabilities(len(node_cluster.path_counts)).values()), 1)

    def test_valid_average_hitting_time(self):
        max_path_length = 5
        for node in H.nodes.keys():
            nodes_rw_data = generate_node_random_walk_data(H, source_node=node, epsilon=0.01)
            for node_data in nodes_rw_data.values():
                if node_data.number_of_hits == 0:
                    assert node_data.average_hitting_time == max_path_length
                else:
                    assert node_data.average_hitting_time <= max_path_length
                    assert node_data.average_hitting_time > 0

    def test_no_empty_communities(self):
        for node_name, community in communities.items():
            all_nodes = []
            all_nodes.extend(community.single_nodes)
            for cluster in community.clusters:
                all_nodes.extend(cluster)
            assert len(all_nodes) > 0

    def test_fewer_nodes_in_communities_than_in_original_hypergraph(self):
        for node_name, community in communities.items():
            total_nodes = len(community.single_nodes) + sum([len(node_cluster) for node_cluster in
                                                             community.clusters])
            assert total_nodes <= H.number_of_nodes()

    def test_no_duplicate_nodes_in_communities(self):
        for node_name, community in communities.items():
            all_nodes = []
            all_nodes.extend(community.single_nodes)
            for cluster in community.clusters:
                all_nodes.extend(cluster)
            assert len(all_nodes) == len(set(all_nodes))

    def test_correct_computation_of_kl_divergence(self):
        p1 = {'a': 0.5, 'b': 0.3, 'c': 0.2}
        q1 = {'a': 0.7, 'b': 0.2, 'c': 0.1}
        q2 = {'a': 0.7, 'b': 0.2, 'd': 0.0, 'c': 0.1}
        q3 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}

        p2 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}
        q4 = {'a': 0.6, 'b': 0.2, 'c': 0.15, 'd': 0.05}

        assert math.isclose(kl_divergence(p1, q1), 0.09203285023)
        assert math.isclose(kl_divergence(p1, q2), 0.09203285023)
        assert math.isclose(kl_divergence(q2, q3), 0.13862943611)
        assert math.isclose(kl_divergence(q1, q3), 0.13862943611)
        assert math.isclose(kl_divergence(p2, q4), 0.06735896506)

    def test_correct_computation_of_js_divergence(self):
        p1 = {'a': 0.5, 'b': 0.3, 'c': 0.2}
        q1 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}

        assert math.isclose(js_divergence(p1, q1), 0.0776870668)

    def test_number_of_close_nodes_same_as_SOTA(self):
        len_of_close_nodes = []
        for node in H2.nodes.keys():
            nodes_rw_data = generate_node_random_walk_data(H2, source_node=node, epsilon=config2['epsilon'])
            close_nodes_rw_data = get_close_nodes(nodes_rw_data, threshold_hitting_time=config2['theta_hit'])
            len_of_close_nodes.append(len(close_nodes_rw_data))

        print("Average # close nodes")
        print("---------------------")
        print(f"This implementation {np.mean(len_of_close_nodes)}, SOTA {21.56338028}")
        assert np.abs(np.mean(len_of_close_nodes) - 21.56338028) < 0.615929519

    def test_average_number_of_clusters_and_single_nodes_same_as_SOTA(self):
        clusters_and_single_nodes = []
        nodes = []
        communities2 = Communities(H2, config2).communities
        for node_name, community in communities2.items():
            num_c_and_sn = community.number_of_single_nodes + community.number_of_clusters
            num_nodes = community.number_of_nodes
            clusters_and_single_nodes.append(num_c_and_sn)
            nodes.append(num_nodes)

        print("Average # clusters and single nodes")
        print("-------------------------------------")
        print(f"This implementation {np.mean(clusters_and_single_nodes)}, SOTA {6.290141}")
        print("Average # nodes")
        print("-------------------------------------")
        print(f"This implementation {np.mean(nodes)}, SOTA {21.53662}")
        assert np.abs(np.mean(clusters_and_single_nodes) - 6.290141) < 0.035258
        assert np.abs(np.mean(nodes) - 21.53662) < 0.097241
