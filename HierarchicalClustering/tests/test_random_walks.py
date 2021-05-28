import pytest
import random
import math

from HierarchicalClustering.GraphObjects import EnhancedHypergraph
from HierarchicalClustering.merge_utilities import _kl_divergence

H = EnhancedHypergraph(database_file='../Databases/smoking.db', info_file='../Databases/smoking.info')
config = {'num_walks': 1000,
          'max_length': 7,
          'walk_scaling_param': 5,
          'theta_hit': 6.9,
          'theta_sym': 0.1,
          'theta_js': 1,
          'num_top': 3}

communities = H.generate_communities(config)


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

    assert math.isclose(_kl_divergence(p1, q1), 0.09203285023)
    assert math.isclose(_kl_divergence(p1, q2), 0.09203285023)
    assert math.isclose(_kl_divergence(q2, q3), 0.13862943611)
    assert math.isclose(_kl_divergence(q1, q3), 0.13862943611)


def test_correct_computation_of_js_divergence():
    pass


def test_always_some_nearby_nodes():
    for node in H.nodes():
        H._run_random_walks(source_node=node, number_of_walks=500, max_path_length=5)
        close_nodes = H._get_close_nodes(threshold_hitting_time=4.9)
        H._reset_nodes()
        assert len(close_nodes) > 0


def test_no_unit_sized_clusters_input_to_js_clustering():
    pass


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
