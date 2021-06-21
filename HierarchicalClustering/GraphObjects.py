import random
import networkx as nx
import re
from itertools import combinations
from collections import defaultdict
from networkx.algorithms.approximation.distance_measures import diameter as estimate_diameter


class InvalidLineSyntaxError(Exception):
    def __init__(self, line, line_number, file_name):
        self.line = line
        self.line_number = line_number
        self.file_name = file_name

    def __str__(self):
        return f'Line {self.line_number} "{self.line}" of {self.file_name} has incorrect syntax. Make sure that each ' \
               f'predicate is correctly formatted with braces and commas e.g. Friends(person, person)'


def parse_line(line: str):
    """
    Parses a correctly-formatted predicate. e.g. Friends(Alice, Bob) returns 'Friends', ['Alice', 'Bob'].
    Returns None, None if the predicate is incorrectly formatted.
    """
    line = line.strip()

    if not is_good_line_syntax(line):
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


def is_good_line_syntax(line: str):
    """
    Checks for correct line syntax, returning either True or False.

    For the database and info files, examples of correct line syntax are e.g. Friends(Alice, Bob),
    Family(Jane, Edward, Steve), Smokes(John) - i.e. alpha-numeric characters followed by an open parenthesis
    followed by comma-separated alpha-numeric characters followed by a closed parenthesis.
    """
    correct_syntax = re.match("(\w|-|')+\(((\w|-|')+|((\w|-|')+,\s*)+(\w|-|')+)\)$", line)
    is_correct_syntax = bool(correct_syntax)

    return is_correct_syntax


def is_empty_or_comment(line: str):
    if line is None or line.isspace() or line.lstrip()[0:2] == '//':
        return True
    else:
        return False



class Graph(nx.Graph):
    """
    Extends the networkx Graph object, allowing it to be converted to a hypergraph if a template is provided.
    """

    def __init__(self):
        super().__init__()

    def get_estimated_diameter(self):
        """
        Uses the 2-sweep algorithm to find a lower bound for the diameter of the graph in O(|V|) time.
        """
        return estimate_diameter(self)

    def convert_to_hypergraph_from_template(self, template_hypergraph):
        """
        Convert to a hypergraph by looping over the nodes in the graph and adding all hyperedges that the node is a
        member of in the template.
        """

        assert isinstance(template_hypergraph, Hypergraph)

        hypergraph = Hypergraph()
        hypergraph.predicate_argument_types = template_hypergraph.predicate_argument_types

        for node in self.nodes():
            # add non-singleton edges to the hypergraph
            hyperedge_ids_of_node = template_hypergraph.memberships[node]
            for edge_id in hyperedge_ids_of_node:
                # only add a hyperedge if a strict majority of vertices in the edge are part of the cluster
                predicate = template_hypergraph.predicates[edge_id]
                edge_nodes = template_hypergraph.edges[edge_id]
                number_of_edge_nodes_in_graph = len(set(self.nodes()).intersection(set(edge_nodes)))

                if number_of_edge_nodes_in_graph > len(edge_nodes) / 2:
                    hypergraph.add_edge(edge_id=edge_id,
                                        predicate=predicate,
                                        nodes=edge_nodes)

                hypergraph.node_types.update(template_hypergraph.predicate_argument_types[predicate])

            hypergraph.is_source_node[node] = True

            # add singleton edges to the hypergraph
            singleton_edges = template_hypergraph.singleton_edges[node]
            for predicate in singleton_edges:
                hypergraph.add_edge(predicate=predicate, nodes=[node])

        hypergraph.estimated_graph_diameter = self.get_estimated_diameter()

        return hypergraph

class Hypergraph(object):
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
        self.singleton_edges = defaultdict(lambda: set()) # dict(node_name: set(predicate))
        self.edges = {}                                   # dict(edge_id: list(node_name))
        self.predicates = {}                              # dict(edge_id: predicate_name)
        self.nodes = {}                                   # dict(node_name: node_type)
        self.memberships = defaultdict(lambda: set())     # dict(node_name: set(edge_id))
        self.predicate_argument_types = {}                # dict(predicate_name: list(node_type))
        self.node_types = set()                           # set(node_types)
        self.is_source_node = defaultdict(lambda: False)  # dict(node_name: bool)
        self.estimated_graph_diameter = None

        if database_file and not info_file:
            raise ValueError("Cannot generate hypergraph. Database file provided but no info file provided.")
        elif info_file and not database_file:
            raise ValueError("Cannot generate hypergraph. Info file provided but no database file provided.")
        elif info_file and database_file:
            self.construct_from_database(path_to_db_file=database_file, path_to_info_file=info_file)
        # if no .db and .info files provided, create an empty hypergraph object
        else:
            pass

    def is_connected(self):
        is_connected = True
        # the hypergraph is not connected if there exists a node which only belongs to singleton edges
        if len(set(self.singleton_edges.keys()).intersection(self.nodes.keys())) < len(self.singleton_edges):
            is_connected = False

        return is_connected

    def construct_from_database(self, path_to_db_file: str, path_to_info_file=None):

        self.predicate_argument_types = self._get_predicate_argument_types_from_info_file(path_to_info_file)

        with open(path_to_db_file, 'r') as database_file:
            for line_idx, line in enumerate(database_file.readlines()):
                if is_empty_or_comment(line):
                    continue

                predicate, node_names = parse_line(line=line)
                if predicate is None or node_names is None:
                    raise InvalidLineSyntaxError(line, line_idx, file_name=path_to_db_file)

                self.add_edge(edge_id=line_idx, predicate=predicate, nodes=node_names)

        for node_name in self.nodes.keys():
            self.is_source_node[node_name] = True

        assert self.is_connected()

    def _get_predicate_argument_types_from_info_file(self, path_to_info_file: str):
        """
        Parses the info file and returns a dictionary that maps predicate names to a list of strings which specify
        the ordered sequence of constant types that must go into the predicate's argument slots.

        e.g. {'Friends' : ['person', 'person'], 'Family' : ['person', 'person', 'person'], 'Smokes', ['person']}
        """
        predicate_argument_types = {}

        with open(path_to_info_file, 'r') as info_file:
            for line_idx, line in enumerate(info_file.readlines()):
                # Skip empty lines, or lines which are commented out (// symbol)
                if is_empty_or_comment(line):
                    continue

                predicate, types = parse_line(line=line)
                if predicate is None or types is None:
                    raise InvalidLineSyntaxError(line, line_idx, file_name=path_to_info_file)

                predicate_argument_types[predicate] = types
                self.node_types.update(types)

        return predicate_argument_types

    def add_edge(self, predicate: str, nodes: list[str], edge_id=None):
        if len(nodes) == 1:
            node = nodes[0]
            self.singleton_edges[node].add(predicate)
        else:
            self.edges[edge_id] = nodes
            self.predicates[edge_id] = predicate
            [self.memberships[node].add(edge_id) for node in nodes]
            for node_position, node in enumerate(nodes):
                node_type = self.predicate_argument_types[predicate][node_position]
                self.nodes[node] = node_type

    def get_node_set(self):
        return set(self.nodes.keys()).union(set(self.singleton_edges.keys()))

    def number_of_nodes(self):
        return len(set(self.nodes.keys()).union(set(self.singleton_edges.keys())))

    def number_of_edges(self):
        return len(self.edges) + sum(len(predicate_set) for predicate_set in self.singleton_edges.values())

    def get_random_edge_and_neighbor_of_node(self, node: str):
        """
        Given a node, gets a random non-single-vertex hyperedge that the node belongs to. Then gets a random node
        from the other nodes in that hyperedge (neighbor). Returns the hyperedge and the neighbor.
        """
        edge_ids = self.memberships[node]
        edge_id = random.choice(list(edge_ids))
        nodes_of_edge = self.edges[edge_id].copy()
        nodes_of_edge.remove(node)
        neighbor = random.choice(nodes_of_edge)

        return edge_id, neighbor

    def convert_to_graph(self, weighted=True):
        """
        Convert to a weighted graph by replacing each n-ary hyperedge with n-cliques.

        If weighted is True, the edge weight is the number of times the edge was generated when
        replacing all n-hyperedges with n-cliques. If weighted is False, all edges have unit weight.
        """
        graph = Graph()

        for nodes in self.edges.values():
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





