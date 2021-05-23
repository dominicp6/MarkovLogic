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
from math import floor


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


class GraphCluster:
    def __init__(self, list_of_graphs):
        if not all([issubclass(graph.__class__, Graph) for graph in list_of_graphs]) and isinstance(list_of_graphs, list):
            print(type(list_of_graphs))
            raise ValueError("GraphCluster object must be initialised from a list of Graph or EnhancedGraph objects")
        self.graphs = list_of_graphs

    def __getitem__(self, index):
        return self.graphs[index]

    def _find_candidate_hypergraph_ids_to_add_hyperedge_to(self, hyperedge):
        """
        Find candidate hypergraph ids for adding a hyperedge to. Candidates correspond to those
        graphs in the graph cluster that share the most nodes with the nodes of the hyperedge.
        """

        hyperedge_nodes = set(hyperedge.elements.keys())
        number_of_hyperedge_nodes = len(hyperedge_nodes)
        max_nodes_in_graph = 0
        candidate_hypergraphs_to_add_hyperedge_to = []
        for graph_id, graph in enumerate(self.graphs):
            # stop searching if either
            #   1) we find a graph for the first time containing more than half of the hyperedge nodes
            #   2) the total number of matched nodes in our candidate graphs equals the number of hyperedge nodes
            if max_nodes_in_graph <= floor(number_of_hyperedge_nodes / 2) \
                    and len(candidate_hypergraphs_to_add_hyperedge_to) * max_nodes_in_graph < number_of_hyperedge_nodes:
                num_edge_nodes_in_graph = len(hyperedge_nodes.intersection(set(graph.nodes())))
                if num_edge_nodes_in_graph > max_nodes_in_graph:
                    candidate_hypergraphs_to_add_hyperedge_to = [graph_id]
                    max_nodes_in_graph = num_edge_nodes_in_graph
                elif num_edge_nodes_in_graph == max_nodes_in_graph:
                    candidate_hypergraphs_to_add_hyperedge_to.append(graph_id)
                else:
                    pass
            else:
                break

        return candidate_hypergraphs_to_add_hyperedge_to

    @staticmethod
    def _find_optimal_id_from_candidates_using_clusters(candidate_hypergraph_ids, hypergraph_cluster):
        if len(candidate_hypergraph_ids):
            hypergraph_to_add_hyperedge_to = candidate_hypergraph_ids[0]
        else:
            lowest = float('inf')
            hypergraph_to_add_hyperedge_to = 0
            for candidate_id in candidate_hypergraph_ids:
                num_nodes = hypergraph_cluster[candidate_id].number_of_nodes()
                if num_nodes < lowest:
                    lowest = num_nodes
                    hypergraph_to_add_hyperedge_to = candidate_id

        return hypergraph_to_add_hyperedge_to

    def _find_hypergraph_id_to_add_hyperedge_to(self, hyperedge, hypergraph_cluster):

        candidate_hypergraph_ids = self._find_candidate_hypergraph_ids_to_add_hyperedge_to(hyperedge)
        hyperedge_id = self._find_optimal_id_from_candidates_using_clusters(candidate_hypergraph_ids,
                                                                            hypergraph_cluster)

        return hyperedge_id

    def convert_to_hypergraph_cluster_from_template(self, template_hypergraph):
        hypergraph_cluster = [EnhancedHypergraph() for idx in range(len(self.graphs))]

        for hyperedge in template_hypergraph.edges():
            hypergraph_id = self._find_hypergraph_id_to_add_hyperedge_to(hyperedge, hypergraph_cluster)
            hypergraph_cluster[hypergraph_id].add_edge(hyperedge)

        # remove empty hypergraphs
        hypergraph_cluster = [hypergraph for hypergraph in hypergraph_cluster if hypergraph.number_of_nodes() > 0]

        return hypergraph_cluster


class EnhancedHypergraph(Hypergraph):

    def __init__(self, database_file=None):
        super().__init__()

        # self._hyperedges_of_node = defaultdict(lambda: set())  # node_id: set(h_edge1, h_edge2,...)

        if database_file:
            self.generate_from_database(path_to_db_file=database_file, path_to_info_file=None)

    def convert_to_graph(self, sum_weights_for_multi_edges=True):
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
