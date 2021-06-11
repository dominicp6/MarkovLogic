import unittest

from GraphObjects import Hypergraph

smoking_db = './Databases/smoking.db'
predicate_db = './Databases/predicate_testing.db'
smoking_info = './Databases/smoking.info'
predicate_info = './Databases/predicate_testing.info'

H1 = Hypergraph(database_file=smoking_db, info_file=smoking_info)
H2 = Hypergraph(database_file=predicate_db, info_file=predicate_info)


class TestHypergraph(unittest.TestCase):

    def test_correct_hypergraph_size_from_database(self):
        assert H1.number_of_nodes() == 8, f"Expected #nodes: {8}, Actual {H1.number_of_nodes()}"
        assert H1.number_of_edges() == 22, f"Expected #edges: {22}, Actual {H1.number_of_edges()}"

    def test_correct_graph_size_when_converting_hypergraph_to_graph(self):
        G = H1.convert_to_graph()
        assert G.number_of_nodes() == 8, f"Expected #nodes: {8}, Actual {G.number_of_nodes()}"
        assert G.number_of_edges() == 8, f"Expected #nodes: {8}, Actual {G.number_of_nodes()}"

    def test_correct_hypergraph_predicate_types(self):
        assert all(node_type in H2.node_types for node_type in ['person', 'motive', 'location', 'item']), \
            f"Unexpected node types: {H2.node_types}"
        assert len(H2.node_types) == 4, f"Expected #types: {4}, Actual: {len(H2.node_types)}"
        assert H2.nodes['MsScarlet'].node_type == 'person'
        assert H2.nodes['CandleStick'].node_type == 'item'
        assert H2.nodes['Kitchen'].node_type == 'location'
        assert H2.nodes['Money'].node_type == 'motive'
