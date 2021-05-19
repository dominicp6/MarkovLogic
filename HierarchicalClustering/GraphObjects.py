import warnings
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from networkx import Graph

import hypernetx as hnx
from hypernetx import Hypergraph
from hypernetx import Entity
from hypernetx import EntitySet
from itertools import combinations

class EnhancedGraph(Graph):
    def __init__(self):
        super().__init__()

    def convert_to_hypergraph_from_template(self, template_hypergraph):
        hypergraph = EnhancedHypergraph()

        for node in self.nodes():
            # for each node in the graph, find the sets of hyperedge nodes from the
            # template hypergraph which contain that node
            hyperedges_of_node = template_hypergraph.nodes[node].memberships
            for hyperedge_id, edge in hyperedges_of_node.items():
                # add the corresponding hyperedges to the new hypergraph instance
                hypergraph.add_edge(edge)

        return hypergraph

class EnhancedHypergraph(Hypergraph):

    def __init__(self, database_file=None):
        super().__init__()

        # self._hyperedges_of_node = defaultdict(lambda: set())  # node_id: set(h_edge1, h_edge2,...)

        if database_file:
            self.generate_from_database(path_to_db_file=database_file, path_to_info_file=None)

    #
    # def get_hyperedges_of_node(self, node):
    #     return self._hyperedges_of_node[node]
    #
    # def get_node_to_hyperedges_dict(self):
    #     return dict(self._hyperedges_of_node)
    #
    # def number_of_nodes(self):
    #     return len(self.get_node_set())
    #
    # def number_of_edges(self):
    #     return len(self.get_hyperedge_id_set())
    #
    # def _add_nodes_to_hyperedge(self, nodes, hyperedge_id):
    #     for node in nodes:
    #         self._hyperedges_of_node[node].add(hyperedge_id)
    #
    # def _remove_nodes_from_hyperedge(self, nodes, hyperedge_id):
    #     for node in nodes:
    #         self._hyperedges_of_node[node].remove(hyperedge_id)
    #
    # def add_hyperedge(self, nodes, predicate=None, node_name_to_node_type=None):
    #     """
    #     Adds a hyperedge to the hypergraph. If the hyperedge contains nodes not
    #     already present in the hypergraph then these nodes are also added to the
    #     hypergraph.
    #
    #     :param nodes: the node set of the hyperedge to add
    #     :param predicate (str): the predicate name of the hyperedge [optional]
    #     """
    #     hyperedge_id = super().add_hyperedge(nodes, {'predicate': predicate})
    #
    #     self._add_nodes_to_hyperedge(nodes, hyperedge_id)
    #
    #     return hyperedge_id
    #
    # def add_hyperedges(self, hyperedges, predicate=None, node_name_to_node_type=None):
    #     """
    #     Adds a hyperedges to the hypergraph. If the hyperedges contain nodes not
    #     already present in the hypergraph then these nodes are also added to the
    #     hypergraph.
    #
    #     :param hyperedges: a list of node sets of the hyperedges to add
    #     :param predicate (str): the predicate name of the hyperedges (same for each) [optional]
    #     """
    #     hyperedge_ids = []
    #     for nodes in hyperedges:
    #         hyperedge_id = self.add_hyperedge(nodes, predicate)
    #         hyperedge_ids.append(hyperedge_id)
    #
    #     return hyperedge_ids
    #
    # def remove_hyperedge(self, hyperedge_id):
    #     nodes = self.get_hyperedge_nodes(hyperedge_id)
    #     self._remove_nodes_from_hyperedge(nodes, hyperedge_id)
    #     super().remove_hyperedge(hyperedge_id)
    #
    # def remove_hyperedges(self, hyperedge_ids):
    #     for hyperedge_id in hyperedge_ids:
    #         self.remove_hyperedge(hyperedge_id)
    #
    def convert_to_graph(self, sum_weights_for_multi_edges):
        # graph = nx.Graph()
        graph = EnhancedGraph()

        for hyperedge in self.edges():
            nodes = hyperedge.elements

            # from the hyperedge node set construct a complete subgraph (clique)
            for edge in combinations(nodes, 2):
                if sum_weights_for_multi_edges == True:
                    # increment edge weight if edge already exists
                    if graph.has_edge(*edge):
                        graph[edge[0]][edge[1]]['weight'] += 1
                    # else add the new edge
                    else:
                        graph.add_edge(*edge, weight=1)
                else:
                    graph.add_edge(*edge, weight=1)

        # Check that the graph is connected
        assert nx.is_connected(graph)

        return graph

    def _correct_line_syntax(self, line_fragments):
        argument_string = line_fragments[1][0:1]
        # check that open and closed parentheses are correctly used
        # check that the argument string does not contain duplicate closing braces
        if (len(line_fragments) == 2) and (line_fragments[1][-1] == ")") and (")" not in argument_string):
            return True
        else:
            return False

    def _parse_line(self, file_name: str, line: str, line_number: int):
        """
        Parses a line from a .db or .info file.

        :param file_name: name of the file which is currently being parsed
        :param line: the line to be parsed
        :param line_number: the line number of the line to parse
        :returns: predicate - the predicate defined in that line of the file
                  predicate_arguments - the arguments of that predicate

        e.g. Friends(Anna, Bob) gets parsed as:
        predicate:           Friends
        predicate_arguments: [Anna,Bob]
        """
        line = line.strip()

        line_fragments = line.split('(')
        if not self._correct_line_syntax(line_fragments):
            raise IOError("Line {} [{}]".format(line_number, line)
                          + "of {} has incorrect syntax \n".format(file_name) +
                          "Make sure that each predicate is correctly" +
                          " formatted with braces and commas e.g. " +
                          " Friends(Anna, Bob)")

        predicate = line_fragments[0]
        predicate_argument_string = line_fragments[1][0:-1]
        predicate_arguments = [predicate_argument.strip() for predicate_argument in
                               predicate_argument_string.split(',')]
        return predicate, predicate_arguments

    def generate_from_database(self, path_to_db_file: str, path_to_info_file=None):
        """
        Generates an undirected hypergraph representation of a relational database
        that is defined in an Alchemy .db file

        If path_to_info_file is provided, then also reads in a .info file which
        specifies the types of each predicate_argument, allowing nodes of the
        hypergraph to be annotated by their type.
        """

        db_file = open(path_to_db_file, 'r')
        for line_idx, line in enumerate(db_file.readlines()):
            # Skip empty lines
            if not line:
                continue

            predicate, nodes_of_predicate = self._parse_line(file_name=path_to_db_file, line=line, line_number=line_idx)

            node_set = set(nodes_of_predicate)
            edge = Entity(uid=line_idx, elements=node_set)
            self.add_edge(edge)

        db_file.close()

