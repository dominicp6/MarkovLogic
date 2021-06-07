import pytest
import random
import numpy as np
import math

from HierarchicalClustering.GraphObjects import EnhancedHypergraph
from HierarchicalClustering.merge_utilities import _kl_divergence, _js_divergence

H = EnhancedHypergraph(database_file='../Databases/smoking.db', info_file='../Databases/smoking.info')
config = {'num_walks': 1000,
          'max_length': 7,
          'walk_scaling_param': 5,
          'theta_hit': 6.9,
          'theta_sym': 0.1,
          'theta_js': 1,
          'num_top': 3}

communities = H.generate_communities(config)

H2 = EnhancedHypergraph(database_file='../Databases/imdb1.db', info_file='../Databases/imdb.info')
config2 = {'num_walks': 10000,
           'max_length': 5,
           'walk_scaling_param': 5,
           'theta_hit': 4.9,
           'theta_sym': 0.1,
           'theta_js': 1,
           'num_top': 3}


def test_non_empty_communities():
    assert all(community.single_nodes is not None or community.node_clusters is not None for community in communities)


def test_no_empty_clusters():
    for community in communities:
        single_nodes = community.single_nodes
        node_clusters = community.node_clusters
        assert len(single_nodes) >= 0
        assert len(node_clusters) >= 0


def test_no_nodes_lost_in_clustering():
    for node in H.nodes():
        H._run_random_walks(source_node=node, number_of_walks=500, max_path_length=5)
        close_nodes = H._get_close_nodes(threshold_hitting_time=4.9)
        single_nodes, node_clusters = H._cluster_nodes(close_nodes, config)
        total_nodes = len(single_nodes) + sum([len(node_cluster) for node_cluster in node_clusters])
        H._reset_nodes()
        assert total_nodes == len(close_nodes)


def test_correct_computation_of_kl_divergence():
    p1 = {'a': 0.5, 'b': 0.3, 'c': 0.2}
    q1 = {'a': 0.7, 'b': 0.2, 'c': 0.1}
    q2 = {'a': 0.7, 'b': 0.2, 'd': 0.0, 'c': 0.1}
    q3 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}

    p2 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}
    q4 = {'a': 0.6, 'b': 0.2, 'c': 0.15, 'd': 0.05}

    assert math.isclose(_kl_divergence(p1, q1), 0.09203285023)
    assert math.isclose(_kl_divergence(p1, q2), 0.09203285023)
    assert math.isclose(_kl_divergence(q2, q3), 0.13862943611)
    assert math.isclose(_kl_divergence(q1, q3), 0.13862943611)
    assert math.isclose(_kl_divergence(p2, q4), 0.06735896506)


def test_correct_computation_of_js_divergence():
    p1 = {'a': 0.5, 'b': 0.3, 'c': 0.2}
    q1 = {'d': 0.1, 'a': 0.7, 'b': 0.1, 'c': 0.1}

    assert math.isclose(_js_divergence(p1, q1), 0.0776870668)


def test_always_some_nearby_nodes():
    for node in H.nodes():
        H._run_random_walks(source_node=node, number_of_walks=500, max_path_length=5)
        close_nodes = H._get_close_nodes(threshold_hitting_time=4.9)
        H._reset_nodes()
        assert len(close_nodes) > 0


def test_check_correct_average_hitting_time_calculation():
    for node in H.nodes():
        H._run_random_walks(source_node=node, number_of_walks=500, max_path_length=5)
        for node in H.node_objects:
            assert node.average_hitting_time == ((500 - node.number_of_hits) * 5 + node.accumulated_hitting_time) / 500
        H._reset_nodes()
        break


def test_path_dictionaries_not_empty_if_hit():
    for node in H.nodes():
        H._run_random_walks(source_node=node, number_of_walks=500, max_path_length=5)
        for node in H.node_objects:
            if node.number_of_hits > 0:
                assert sum(node.path_counts.values()) > 0
        H._reset_nodes()
        break


def test_number_close_nodes_same_as_SOTA():
    len_of_close_nodes = []
    for node in H2.nodes():
        H2._run_random_walks(source_node=node, number_of_walks=config2['num_walks'], max_path_length=config2['max_length'])
        close_nodes = H2._get_close_nodes(threshold_hitting_time=config2['theta_hit'])
        len_of_close_nodes.append(len(close_nodes))
        H2._reset_nodes()

    assert np.abs(np.mean(len_of_close_nodes) - 21.56338028) < 0.615929519

def test_number_distance_symmetric_clusters_same_as_SOTA():
    num_dist_sym_clusters = []
    for node in H2.nodes():
        H2._run_random_walks(source_node=node, number_of_walks=config2['num_walks'],
                             max_path_length=config2['max_length'])
        close_nodes = H2._get_close_nodes(threshold_hitting_time=config2['theta_hit'])
        for node_type in H2.node_types:
            nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
            if nodes_of_type:
                distance_symmetric_clusters = H2._cluster_nodes_by_truncated_hitting_times(
                    nodes_of_type, threshold_hitting_time_difference=config['theta_sym'])

                num_dist_sym_clusters.append(len(distance_symmetric_clusters))
        H2._reset_nodes()

    assert np.abs(np.mean(num_dist_sym_clusters) - 1.699) < 0.033
