import networkx as nx
from collections import defaultdict
import numpy as np
from networkx import Graph
from hypernetx import Hypergraph
import random

from HierarchicalClustering.Community import Community
from HierarchicalClustering.Edge import Edge
from HierarchicalClustering.Node import Node
import HierarchicalClustering.Node as node_utls
from HierarchicalClustering.NodeCluster import NodeCluster
from itertools import combinations
from HierarchicalClustering.merge_utilities import compute_js_divergence


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
            # for each node in the graph, find the sets of hyperedges from the
            # template hypergraph which contain that node
            hyperedges_of_node = template_hypergraph.nodes[node].memberships
            for hyperedge_id, edge in hyperedges_of_node.items():
                # add the corresponding hyperedge to the new hypergraph instance
                hypergraph.add_edge(edge)

        for edge in hypergraph.edges():
            hypergraph.node_objects.update([node for node in template_hypergraph.node_objects if node.name
                                            in [node.name for node in edge.elements.values()]])

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


    def _reset_nodes(self):
        # resets the sample path and truncated hitting time data for every node in the hypergraph
        for node in self.nodes():
            node_utls.reset(node)

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
                # for i in range(len(node_names)):
                #     self.type_to_nodes_map[node_types[i]].append(node_names[i])

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

    def _run_random_walk(self, source_node, max_path_length):
        current_node = source_node
        encountered_nodes = set()
        path = ''
        for step in range(max_path_length):

            next_node, next_edge = self._get_random_neighbor_and_edge_of_node(current_node)
            test_set.add(next_node.name)
            path += str(next_edge.predicate)+','

            if next_node.name not in encountered_nodes:
                next_node.number_of_hits += 1
                #next_node.add_path(path)
                node_utls.add_path(next_node, path)
                hitting_time = step + 1
                #next_node.update_accumulated_hitting_time(hitting_time)
                node_utls.update_accumulated_hitting_time(next_node, hitting_time)
                encountered_nodes.add(next_node.name)

            current_node = next_node

    def _run_random_walks(self, source_node, number_of_walks, max_path_length):
        for walk in range(number_of_walks):
            self._run_random_walk(source_node, max_path_length)

        for node in self.nodes():
            #print(f"#hits {node.number_of_hits} accTime {node.accumulated_hitting_time}")
            #node.update_average_hitting_time(number_of_walks, max_path_length)
            node_utls.update_average_hitting_time(node, number_of_walks, max_path_length)
            #print(f"exptHT {(node.accumulated_hitting_time + (10000-node.number_of_hits)*5)/10000} actualHT {node.average_hitting_time}")


    def _get_close_nodes(self, threshold_hitting_time):
        return [node for node in self.nodes() if node.average_hitting_time < threshold_hitting_time]

    @staticmethod
    def _cluster_nodes_by_truncated_hitting_times(nodes, threshold_hitting_time_difference):
        """
        Clusters a list of nodes into groups based on the truncated hitting
        criterion as follows:

        Let h_{j} be the average truncated hitting time of node v_{j}.
        Nodes v_{j} are grouped into disjoint sets A_{k} such that:
        for all v_{j} in A_{k} there exists a node v_{j'} in A_{k}
        such that |h_{j} - h_{j'}| <= merge_threshold.
        Ref: https://alchemy.cs.washington.edu/papers/kok10/kok10.pdf
        """

        # sort the nodes in the hypergraph in increasing order of average hitting time
        nodes = sorted(nodes, key=lambda n: n.average_hitting_time)
        current_hitting_time = nodes[0].average_hitting_time
        distance_symmetric_clusters = []
        distance_symmetric_cluster = []
        for node in nodes:
            if (node.average_hitting_time - current_hitting_time) < threshold_hitting_time_difference:
                distance_symmetric_cluster.append(node)
            else:
                distance_symmetric_clusters.append(distance_symmetric_cluster.copy())
                distance_symmetric_cluster.clear()
                distance_symmetric_cluster.append(node)
            current_hitting_time = node.average_hitting_time

        # append the last cluster to the list if it is not empty
        if distance_symmetric_cluster is not None:
            distance_symmetric_clusters.append(distance_symmetric_cluster)

        return distance_symmetric_clusters

    @staticmethod
    def _get_single_nodes_and_node_clusters_from_js_clusters(js_clusters):
        single_nodes = []
        node_clusters = []
        for js_cluster in js_clusters:
            if js_cluster.number_of_nodes() == 1:
                single_nodes.append(js_cluster.nodes[0])
            else:
                node_clusters.append(js_cluster.nodes)

        return single_nodes, node_clusters

    @staticmethod
    def _cluster_nodes_by_js_divergence(nodes, threshold_js_divergence, max_frequent_paths):

        js_clusters = [NodeCluster([node]) for node in nodes]

        max_divergence = float('inf')
        cluster_to_merge1 = None
        cluster_to_merge2 = None

        while True:
            smallest_divergence = max_divergence
            for i in range(len(js_clusters)):
                for j in range(i + 1, len(js_clusters)):
                    js_divergence = compute_js_divergence(js_clusters[i], js_clusters[j], max_frequent_paths)

                    if js_divergence < smallest_divergence and js_divergence < threshold_js_divergence:
                        smallest_divergence = js_divergence
                        cluster_to_merge1 = i
                        cluster_to_merge2 = j

                    if js_divergence > threshold_js_divergence: #TODO: to remove - for debugging only
                        print('Exceeded threshold')

            # if we've found a pair of clusters to merge, merge the two clusters and continue
            if smallest_divergence < max_divergence:
                js_clusters[cluster_to_merge1].merge(js_clusters[cluster_to_merge2])
                del js_clusters[cluster_to_merge2]
            # otherwise, stop merging
            else:
                break

        js_cluster_numbers.append(len(js_clusters))

        return js_clusters

    def _cluster_nodes(self, nodes, config):
        single_nodes = []
        node_clusters = []

        for node_type in self.node_types:
            nodes_of_type = [node for node in nodes if node.node_type == node_type]
            if nodes_of_type:
                distance_symmetric_clusters = self._cluster_nodes_by_truncated_hitting_times(
                    nodes_of_type, threshold_hitting_time_difference=config['theta_sym'])

                distance_symmetric_clusters_numbers.append(len(distance_symmetric_clusters))

                for distance_symmetric_cluster in distance_symmetric_clusters:
                    if len(distance_symmetric_cluster) == 1:
                        single_nodes.append(distance_symmetric_cluster[0])
                    else:
                        js_clusters = self._cluster_nodes_by_js_divergence(distance_symmetric_cluster,
                                                                           threshold_js_divergence=config['theta_js'],
                                                                           max_frequent_paths=config['num_top'])
                        js_single_nodes, js_node_clusters = self._get_single_nodes_and_node_clusters_from_js_clusters(
                            js_clusters)
                        single_nodes.extend(js_single_nodes)
                        node_clusters.extend(js_node_clusters)

        return single_nodes, node_clusters

    def generate_communities(self, config):
        """
        Config parameters:
        num_walks : the maximum number of random walks to run per node
        max_length: the maximum length of a random walk
        walk_scaling_param: the number of random walks to run is min(num_walks, walk_scaling_param|V||E|) where
                            |V| and |E| are the number of nodes and hyperedges in the hypergraph respectively
        theta_hit : after running walks, nodes whose truncated hitting times are larger theta_hit are discarded
        theta_sym : of the remaining nodes, those whose truncated hitting times are less than theta_sym apart are considered
                    as potentially symmetric
        theta_js  : agglomerative clustering of symmetric nodes stops when no pairs of clusters have a path-distribution
                    Jenson-Shannon divergence less than theta_js
        num_top   : the number of most frequent paths to consider when computing the Jenson-Shannon divergence between
                        two path sets
        """

        # TODO: check that the config parameters are valid

        source_nodes = []
        communities = []
        for node in self.nodes():
            # Get number of samples from criterion (explain)
            num_samples = min(config['num_walks'],
                              config[
                                  'walk_scaling_param'] * self.number_of_nodes() * self.number_of_edges())

            self._run_random_walks(source_node=node, number_of_walks=num_samples, max_path_length=config['max_length'])
            close_nodes = self._get_close_nodes(threshold_hitting_time=config['theta_hit'])
            print(node.name)
            print(f"Close nodes: {len(close_nodes)}")
            close_node_numbers.append(len(close_nodes))

            if close_nodes:
                single_nodes, node_clusters = self._cluster_nodes(close_nodes, config)
                print(Community(single_nodes=single_nodes, node_clusters=node_clusters, source_node=node))
                communities.append(Community(single_nodes=single_nodes, node_clusters=node_clusters, source_node=node))
            else:
                communities.append(Community(single_nodes=[], node_clusters=[], source_node=node))

            self._reset_nodes()

            # unmerged_community = Community() - TODO: figure out how this would work

        # return communities, unmerged communities, source nodes
        print(close_node_numbers)
        print(distance_symmetric_clusters_numbers)
        print(np.mean(distance_symmetric_clusters_numbers))
        return communities
