import networkx as nx
from networkx import Graph
from hypernetx import Hypergraph
import random

from Edge import Edge
from Node import Node
from itertools import combinations


test_set = set()
close_node_numbers = []
distance_symmetric_clusters_numbers = []
js_cluster_numbers = []

class EnhancedGraph(Graph):
    def __init__(self):
        super().__init__()

    def convert_to_hypergraph_from_template(self, template_hypergraph):
        hypergraph = EnhancedHypergraph()

        for node in self.nodes():
            hyperedges_of_node = template_hypergraph.nodes[node].memberships
            for hyperedge_id, edge in hyperedges_of_node.items():
                hypergraph.add_edge(edge)

        hypergraph.node_types = template_hypergraph.node_types

        return hypergraph


class EnhancedHypergraph(Hypergraph):

    def __init__(self, database_file=None, info_file=None):
        super().__init__()
        self.node_types = set()

        if database_file and not info_file:
            raise ValueError("Cannot generate hypergraph. Database file provided but no info file provided.")
        elif info_file and not database_file:
            raise ValueError("Cannot generate hypergraph. Info file provided but no database file provided.")
        elif info_file and database_file:
            self.generate_from_database(path_to_db_file=database_file, path_to_info_file=info_file)
        else:
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
    def _is_good_line_syntax(line_fragments):
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

                predicate, types = self._parse_line(line=line)
                predicate_argument_types[predicate] = types
                self.node_types.update(types)

        return predicate_argument_types

    def _parse_line(self, line: str):
        line = line.strip()

        line_fragments = line.split('(')
        if not self._is_good_line_syntax(line_fragments):
            return None, None

        predicate = line_fragments[0]
        predicate_argument_string = line_fragments[1].split(')')[0]
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

                predicate, node_names = self._parse_line(line=line)
                if predicate is None or node_names is None:
                    raise IOError("Line {} [{}]".format(line_idx, line)
                                  + "of {} has incorrect syntax \n".format(path_to_db_file) +
                                  "Make sure that each predicate is correctly" +
                                  " formatted with braces and commas e.g. " +
                                  " Friends(Anna, Bob)")
                node_types = predicate_argument_types[predicate]

                nodes = [Node(name=node_names[i], node_type=node_types[i]) for i in range(len(node_names))]
                edge = Edge(id=line_idx, nodes=nodes, predicate=predicate)

                self.add_edge(edge)

    def _get_random_neighbor_and_edge_of_node(self, node):
        edges = self.nodes[node].memberships.items()
        edges = [edge for edge_id, edge in edges if self.size(edge) >= 2]
        edge = random.choice(edges)
        nodes_of_edge = self.edges[edge].elements.values()
        neighbors = [neighbor for neighbor in nodes_of_edge if neighbor.name != node.name]
        neighbor = random.choice(neighbors)

        return neighbor, edge
