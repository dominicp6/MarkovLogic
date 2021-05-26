import warnings
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from networkx import Graph

import hypernetx as hnx
from hypernetx import Hypergraph
from Edge import Edge
from Node import Node, run_random_walks
from hypernetx import EntitySet
from itertools import combinations


class EnhancedGraph(Graph):
    def __init__(self):
        super().__init__()

    def convert_to_hypergraph_from_template(self, template_hypergraph):
        # TODO: include the copying of node-type information from the template
        hypergraph = EnhancedHypergraph()

        for node in self.nodes():
            # for each node in the graph, find the sets of hyperedges from the
            # template hypergraph which contain that node
            hyperedges_of_node = template_hypergraph.nodes[node].memberships
            for hyperedge_id, edge in hyperedges_of_node.items():
                # add the corresponding hyperedge to the new hypergraph instance
                hypergraph.add_edge(edge)

        return hypergraph


class EnhancedHypergraph(Hypergraph):

    def __init__(self, database_file=None, info_file=None):
        super().__init__()
        self.type_to_nodes_map = defaultdict(list)
        self.node_types = set()

        if database_file and not info_file:
            raise ValueError("Cannot generate hypergraph. Database file provided but no info file provided.")
        elif info_file and not database_file:
            raise ValueError("Cannot generate hypergraph. Info file provided but no database file provided.")
        elif info_file and database_file:
            self.generate_from_database(path_to_db_file=database_file, path_to_info_file=info_file)
        else:
            pass

    def generate_communities(self, config):
        generate_communities(hypergraph=self, config=config)

    def reset_nodes(self):
        # resets the sample path and truncated hitting time data for every node in the hypergraph
        pass

    def convert_to_graph(self, sum_weights_for_multi_edges=True):
        graph = EnhancedGraph()

        for hyperedge in self.edges():
            nodes = hyperedge.elements

            # from the hyperedge node set construct a complete subgraph (clique)
            for edge in combinations(nodes, 2):
                if sum_weights_for_multi_edges:
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

    @staticmethod
    def _good_line_syntax(line_fragments):
        argument_string = line_fragments[1][0:1]
        # check that open and closed parentheses are correctly used
        # check that the argument string does not contain duplicate closing braces
        if (len(line_fragments) == 2) and (line_fragments[1][-1] == ")") and (")" not in argument_string):
            return True
        else:
            return False

    def _get_predicate_argument_types_from_info_file(self, path_to_info_file: str):
        predicate_argument_types = {}
        with open(path_to_info_file, 'r') as info_file:
            for line_idx, line in enumerate(info_file.readlines()):
                # Skip empty lines
                if not line:
                    continue

                predicate, types = self._parse_line(file_name=path_to_info_file, line=line, line_number=line_idx)
                predicate_argument_types[predicate] = types
                self.node_types.update(types)

        return predicate_argument_types

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
        if not self._good_line_syntax(line_fragments):
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

    def generate_from_database(self, path_to_db_file: str, path_to_info_file: str):
        """
        Generates an undirected hypergraph representation of a relational database
        that is defined in an Alchemy .db file

        If path_to_info_file is provided, then also reads in a .info file which
        specifies the types of each predicate_argument, allowing nodes of the
        hypergraph to be annotated by their type.
        """

        predicate_argument_types = self._get_predicate_argument_types_from_info_file(path_to_info_file)

        with open(path_to_db_file, 'r') as database_file:
            for line_idx, line in enumerate(database_file.readlines()):
                # Skip empty lines
                if not line:
                    continue

                predicate, node_names = self._parse_line(file_name=path_to_db_file, line=line,
                                                         line_number=line_idx)
                node_types = predicate_argument_types[predicate]
                for i in range(len(node_names)):
                    self.type_to_nodes_map[node_types[i]].append(node_names[i])

                nodes = [Node(name=nodes[i], node_type=node_types[i]) for i in range(len(node_names))]
                edge = Edge(edge_id=line_idx, nodes=nodes, predicate=predicate)

                self.add_edge(edge)
