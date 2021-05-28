import pytest
import os

from HierarchicalClustering.GraphObjects import EnhancedHypergraph

smoking_db = '../Databases/smoking.db'
predicate_db = '../Databases/predicate_testing.db'
smoking_info = '../Databases/smoking.info'
predicate_info = '../Databases/predicate_testing.info'


def test_correct_hypergraph_size_from_database():
    H = EnhancedHypergraph(database_file=smoking_db, info_file=smoking_info)
    assert H.number_of_nodes() == 8, f"Expected #nodes: {8}, Actual {H.number_of_nodes()}"
    assert H.number_of_edges() == 22, f"Expected #edges: {22}, Actual {H.number_of_edges()}"


def test_correct_graph_size_when_converting_hypergraph_to_graph():
    H = EnhancedHypergraph(database_file=smoking_db, info_file=smoking_info)
    G = H.convert_to_graph()
    assert G.number_of_nodes() == 8, f"Expected #nodes: {8}, Actual {G.number_of_nodes()}"
    assert G.number_of_edges() == 8, f"Expected #nodes: {8}, Actual {G.number_of_nodes()}"


def test_correct_hypergraph_predicate_types():
    H = EnhancedHypergraph(database_file=predicate_db, info_file=predicate_info)
    assert all(node_type in H.node_types for node_type in ['person', 'motive', 'location', 'item']), \
        f"Unexpected node types: {H.node_types}"
    assert len(H.node_types) == 4, f"Expected #types: {4}, Actual: {len(H.node_types)}"
    assert H.nodes['MsScarlet'].node_type == 'person'
    assert H.nodes['CandleStick'].node_type == 'item'
    assert H.nodes['Kitchen'].node_type == 'location'
    assert H.nodes['Money'].node_type == 'motive'


def test_correct_number_of_node_objects():
    H = EnhancedHypergraph(database_file=smoking_db, info_file=smoking_info)
    assert len(H.node_objects) == H.number_of_nodes()
