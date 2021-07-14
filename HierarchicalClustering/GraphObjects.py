import random
import networkx as nx
import multiprocessing
from itertools import combinations
from collections import defaultdict
from networkx.algorithms.distance_measures import diameter as calculate_diameter
from HierarchicalClustering.database import parse_line, is_empty_or_comment
from typing import List

class Graph(nx.Graph):
    """
    Extends the networkx Graph object, allowing it to be converted to a hypergraph if a template is provided.
    """

    def __init__(self):
        super().__init__()

    def diameter(self):
        return calculate_diameter(self)

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
            hyperedges_of_node = template_hypergraph.memberships[node]
            for edge in hyperedges_of_node:
                # only add a hyperedge if a strict majority of vertices in the edge are part of the cluster
                predicate = template_hypergraph.predicates[edge]
                edge_nodes = template_hypergraph.edges[edge]
                number_of_edge_nodes_in_graph = len(set(self.nodes()).intersection(set(edge_nodes)))

                if number_of_edge_nodes_in_graph > len(edge_nodes) / 2:
                    hypergraph.add_edge(edge_id=edge,
                                        predicate=predicate,
                                        nodes=edge_nodes)

                hypergraph.node_types.update(template_hypergraph.predicate_argument_types[predicate])

            hypergraph.is_source_node[node] = True

            # add singleton edges to the hypergraph
            singleton_edges = template_hypergraph.singleton_edges[node]
            for predicate in singleton_edges:
                hypergraph.add_edge(predicate=predicate, nodes=[node])

        hypergraph.diameter = self.diameter()

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
        self.singleton_edges = defaultdict(set)  # dict(node_name: set(predicate)), all edges with one node
        self.edges = {}                          # dict(edge_id: list(node_name)), all edges joining two or more nodes
        self.predicates = {}                     # dict(edge_id: predicate_name), the predicate name of each edge
        self.nodes = {}                          # dict(node_name: node_type), each node and their type
        self.memberships = defaultdict(set)      # dict(node_name: set(edge_id)), the edges each node is a member of
        self.predicate_argument_types = {}       # dict(predicate_name: list(node_type)), the node types that go into
                                                 # arguments of the predicate
        self.node_types = set()                  # set(node_types), all unique node types in the hypergraph
        self.is_source_node = defaultdict(bool)  # dict(node_name: bool), whether each node is a source node for
                                                 # random walks
        self.is_source_node.setdefault(False)
        self.diameter = None

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
            lines_in_db = database_file.readlines()
            # for large databases, use multiprocessing to speed-up line imports
            if len(lines_in_db) > 5000:
                pool = multiprocessing.Pool()
                predicates_and_node_names = pool.starmap_async(parse_line,
                                                               [(line, line_idx, path_to_db_file)
                                                                for line_idx, line in enumerate(lines_in_db)
                                                                if not is_empty_or_comment(line)]).get()
            else:
                predicates_and_node_names = [parse_line(line, line_idx, path_to_db_file)
                                             for line_idx, line in enumerate(lines_in_db)
                                             if not is_empty_or_comment(line)]

        [self.add_edge(edge_id=edge_idx, predicate=predicate, nodes=node_names)
         for edge_idx, (predicate, node_names) in enumerate(predicates_and_node_names)]

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

                predicate, types = parse_line(line=line, line_idx=line_idx, file_name=path_to_info_file)

                predicate_argument_types[predicate] = types
                self.node_types.update(types)

        return predicate_argument_types

    def add_edge(self, predicate: str, nodes: List[str], edge_id=None):
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
        number_of_singleton_edges = sum(len(predicate_set) for predicate_set in self.singleton_edges.values())
        number_of_non_singleton_edges = len(self.edges)
        return number_of_non_singleton_edges + number_of_singleton_edges

    def number_of_predicates(self):
        return len(set(self.predicates.values()))

    def get_random_edge_and_neighbor_of_node(self, node: str):
        """
        Given a node, gets a random non-single-vertex hyperedge that the node belongs to. Then gets a random node
        from the other nodes in that hyperedge (neighbor). Returns the hyperedge and the neighbor.
        """
        edges = self.memberships[node]
        edge = random.choice(list(edges))
        nodes_of_edge = self.edges[edge].copy()
        nodes_of_edge.remove(node)
        neighbor = random.choice(nodes_of_edge)

        return edge, neighbor

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
