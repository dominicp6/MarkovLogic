import networkx as nx
import hypernetx as hnx
import random
import re

from Edge import Edge
from Node import Node
from itertools import combinations


class Graph(nx.Graph):
    """
    Extends the networkx Graph object, allowing it to be converted to a hypergraph if a template is provided.
    """

    def __init__(self):
        super().__init__()

    def convert_to_hypergraph_from_template(self, template_hypergraph):
        """
        Convert to a hypergraph by looping over the nodes in the graph and adding all hyperedges that the node is a
        member of in the template.
        """

        assert isinstance(template_hypergraph, Hypergraph)

        hypergraph = Hypergraph()

        for node in self.nodes():
            hyperedges_of_node = template_hypergraph.nodes[node].memberships
            for hyperedge_id, edge in hyperedges_of_node.items():
                hypergraph.add_edge(edge)

        hypergraph.node_types = template_hypergraph.node_types

        return hypergraph


class Hypergraph(hnx.Hypergraph):
    """
    A hypergraph representation of a relational database constructed from a database file and info file.

    Example usage:
        hypergraph = Hypergraph(database_file = 'my_database.db', info_file = 'my_info_file.info')

    The database file is a list of ground atoms, with a new ground atom on each line.
    e.g.
        Friends(Anna, Bob)
        Friends(Bob, Anna)
        Smokes(Anna)
        Cancer(Bob)

    The info file is a list of the predicates that appear in the database, along with the constant types that
    appear in each of their arguments.
    e.g.
        Friends(person, person)
        Smokes(person)
        Cancer(person)
    """

    def __init__(self, database_file=None, info_file=None):
        super().__init__()
        self.node_types = set()

        if database_file and not info_file:
            raise ValueError("Cannot generate hypergraph. Database file provided but no info file provided.")
        elif info_file and not database_file:
            raise ValueError("Cannot generate hypergraph. Info file provided but no database file provided.")
        elif info_file and database_file:
            self.construct_from_database(path_to_db_file=database_file, path_to_info_file=info_file)

        # if no .db and .info files provided, create an empty hypergraph object
        else:
            pass

    def construct_from_database(self, path_to_db_file: str, path_to_info_file: str):

        predicate_argument_types = self._get_predicate_argument_types_from_info_file(path_to_info_file)

        with open(path_to_db_file, 'r') as database_file:
            for line_idx, line in enumerate(database_file.readlines()):
                # Skip empty lines
                if not line:
                    continue

                predicate, node_names = self._parse_line(line=line)
                if predicate is None or node_names is None:
                    raise IOError(f'Line {line_idx} "{line}" of {path_to_db_file} has incorrect syntax. Make sure '
                                  f'that each predicate is correctly formatted with braces and commas e.g. Friends('
                                  f'Anna, Bob)')
                node_types = predicate_argument_types[predicate]

                nodes = [Node(name=node_names[i], node_type=node_types[i]) for i in range(len(node_names))]
                edge = Edge(uid=line_idx, nodes=nodes, predicate=predicate)

                self.add_edge(edge)

    def convert_to_graph(self, weighted=True):
        """
        Convert to a weighted graph by replacing each n-ary hyperedge with n-cliques.

        If weighted is True, the edge weight is the number of times the edge was generated when
        replacing all n-hyperedges with n-cliques. If weighted is False, all edges have unit weight.
        """
        graph = Graph()

        for hyperedge in self.edges():
            nodes = hyperedge.elements

            # from the hyperedge node set construct a complete subgraph (clique)
            for edge in combinations(nodes, 2):
                if weighted:
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

    def get_random_edge_and_neighbor_of_node(self, node: str):
        """
        Given a node, gets a random non-single-vertex hyperedge that the node belongs to. Then gets a random node
        from the other nodes in that hyperedge (neighbor). Returns the hyperedge and the neighbor.
        """
        edges = self.nodes[node].memberships.items()
        edges = [edge for edge_id, edge in edges if self.size(edge) >= 2]
        edge = random.choice(edges)
        nodes_of_edge = self.edges[edge].elements.values()
        neighbors = [neighbor for neighbor in nodes_of_edge if neighbor.name != node.name]
        neighbor = random.choice(neighbors)

        return edge, neighbor

    def _parse_line(self, line: str):
        """
        Parses a correctly-formatted predicate. e.g. Friends(Alice, Bob) returns 'Friends', ['Alice', 'Bob'].
        Returns None, None if the predicate is incorrectly formatted.
        """
        line = line.strip()

        if not self._is_good_line_syntax(line):
            return None, None

        line_fragments = line.split('(')
        # the predicate name e.g. 'Friends'
        predicate = line_fragments[0]
        # a string of predicate arguments separated by commas e.g. 'Alice, Bob'
        predicate_argument_string = line_fragments[1].split(')')[0]
        # a list of predicate arguments e.g. ['Alice', 'Bob']
        predicate_arguments = [predicate_argument.strip() for predicate_argument in
                               predicate_argument_string.split(',')]

        return predicate, predicate_arguments

    @staticmethod
    def _is_good_line_syntax(line: str):
        """
        Checks for correct line syntax, returning either True or False.

        For the database and info files, examples of correct line syntax are e.g. Friends(Alice, Bob),
        Family(Jane, Edward, Steve), Smokes(John) - i.e. alpha-numeric characters followed by an open parenthesis
        followed by comma-separated alpha-numeric characters followed by a closed parenthesis.
        """
        correct_syntax = re.match("\w+\((\w+|(\w+,\s*)+\w+)\)$", line)
        is_correct_syntax = bool(correct_syntax)

        return is_correct_syntax

    def _get_predicate_argument_types_from_info_file(self, path_to_info_file: str):
        """
        Parses the info file and returns a dictionary that maps predicate names to a list of strings which specify
        the ordered sequence of constant types that must go into the predicate's argument slots.

        e.g. {'Friends' : ['person', 'person'], 'Family' : ['person', 'person', 'person'], 'Smokes', ['person']}
        """
        predicate_argument_types = {}
        with open(path_to_info_file, 'r') as info_file:
            for line_idx, line in enumerate(info_file.readlines()):
                # Skip empty lines
                if not line:
                    continue

                predicate, types = self._parse_line(line=line)
                if predicate is None or types is None:
                    raise IOError(f'Line {line_idx} "{line}" of {path_to_info_file} has incorrect syntax. Make sure '
                                  f'that each predicate is correctly formatted with braces and commas e.g. Friends('
                                  f'person, person)')
                predicate_argument_types[predicate] = types
                self.node_types.update(types)

        return predicate_argument_types
