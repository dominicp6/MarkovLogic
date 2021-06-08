import unittest

import pytest
import random
import numpy as np
import math

from GraphObjects import EnhancedHypergraph
from js_divergence_utils import kl_divergence, js_divergence
from Communities import Communities, run_random_walks, get_close_nodes, cluster_nodes_by_truncated_hitting_times

H = EnhancedHypergraph(database_file='./Databases/smoking.db', info_file='./Databases/smoking.info')
config = {'num_walks': 1000,
          'max_length': 7,
          'walk_scaling_param': 5,
          'theta_hit': 6.9,
          'theta_sym': 0.1,
          'theta_js': 1,
          'num_top': 3}

communities = Communities(H, config).communities

H2 = EnhancedHypergraph(database_file='./Databases/imdb1.db', info_file='./Databases/imdb.info')
config2 = {'num_walks': 10000,
           'max_length': 5,
           'walk_scaling_param': 5,
           'theta_hit': 4.9,
           'theta_sym': 0.1,
           'theta_js': 1,
           'num_top': 3}


class TestRandomWalks(unittest.TestCase):

    def test_no_empty_communities(self):
        for node_name, node_cluster_dict in communities.items():
            all_nodes = []
            all_nodes.extend(node_cluster_dict['single_nodes'])
            for cluster in node_cluster_dict['clusters']:
                all_nodes.extend(cluster)
            assert len(all_nodes) > 0

    def test_fewer_nodes_in_communities_than_in_original_hypergraph(self):
        for node_name, node_cluster_dict in communities.items():
            total_nodes = len(node_cluster_dict['single_nodes']) + sum([len(node_cluster) for node_cluster in
                                                                        node_cluster_dict['clusters']])
            assert total_nodes <= H.number_of_nodes()

    def test_no_duplicate_nodes_in_communities(self):
        for node_name, node_cluster_dict in communities.items():
            all_nodes = []
            all_nodes.extend(node_cluster_dict['single_nodes'])
            for cluster in node_cluster_dict['clusters']:
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

    def test_number_close_nodes_same_as_SOTA(self):
        len_of_close_nodes = []
        for node in H2.nodes():
            nodes_rw_data = run_random_walks(H2, source_node=node, number_of_walks=config2['num_walks'],
                                             max_path_length=config2['max_length'])
            close_nodes_rw_data = get_close_nodes(nodes_rw_data, threshold_hitting_time=config2['theta_hit'])
            len_of_close_nodes.append(len(close_nodes_rw_data))

        print("Average # close nodes")
        print("---------------------")
        print(f"This implementation {np.mean(len_of_close_nodes)}, SOTA {21.56338028}")
        assert np.abs(np.mean(len_of_close_nodes) - 21.56338028) < 0.615929519

    # def test_number_distance_symmetric_clusters_same_as_SOTA(self):
    #     num_dist_sym_clusters = []
    #     for node in H2.nodes():
    #         nodes_rw_data = run_random_walks(H2, source_node=node, number_of_walks=config2['num_walks'],
    #                                          max_path_length=config2['max_length'])
    #         close_nodes = get_close_nodes(nodes_rw_data, threshold_hitting_time=config2['theta_hit'])
    #         for node_type in H2.node_types:
    #             nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
    #             if nodes_of_type:
    #                 distance_symmetric_single_nodes, distance_symmetric_clusters = cluster_nodes_by_truncated_hitting_times(
    #                     nodes_of_type, threshold_hitting_time_difference=config['theta_sym'])
    #
    #                 num_dist_sym_clusters.append(
    #                     len(distance_symmetric_single_nodes) + len(distance_symmetric_clusters))
    #
    #     print("Average # distance symmetric clusters")
    #     print("-------------------------------------")
    #     print(f"This implementation {np.mean(num_dist_sym_clusters)}, SOTA {1.699}")
    #     assert np.abs(np.mean(num_dist_sym_clusters) - 1.699) < 0.033

    def test_average_number_of_clusters_and_single_nodes_same_as_SOTA(self):
        clusters_and_single_nodes = []
        nodes = []
        communities2 = Communities(H2, config2).communities
        for node_name, node_cluster_dict in communities2.items():
            num_c_and_sn = len(node_cluster_dict['single_nodes']) + len(node_cluster_dict['clusters'])
            num_nodes = len(node_cluster_dict['single_nodes']) + sum([len(node_cluster) for node_cluster in
                                                                      node_cluster_dict['clusters']])
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
