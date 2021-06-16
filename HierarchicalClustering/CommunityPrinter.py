import os

from Communities import *
from collections import defaultdict
import itertools


class CommunityPrinter(object):
    def __init__(self, list_of_communities: list[Communities], original_hypergraph: Hypergraph):

        self.list_of_communities = list_of_communities

        self.num_of_communities = sum(len(communities.communities) for communities in self.list_of_communities)

        # Alchemy requires that each node in the original hypergraph is indexed with a unique id number
        self.node_to_node_id = defaultdict(int)
        for node_id, node in enumerate(original_hypergraph.nodes):
            self.node_to_node_id[node] = node_id

        assert self.num_of_communities <= original_hypergraph.number_of_nodes(), f"Incorrect hypergraph provided for " \
                                                                                 f"original_hypergraph. More " \
                                                                                 f"communities found (" \
                                                                                 f"{self.num_of_communities}) than " \
                                                                                 f"the number of node in " \
                                                                                 f"original_hypergraph (" \
                                                                                 f"{original_hypergraph.number_of_nodes()})."

        # .ldb is a type of file used by Alchemy. This maps each node to its string representation for the ldb file.
        self.node_to_ldb_string = self._get_node_to_ldb_string_map()

        self.hypergraph_number = 0
        self.community_number = 0

    def write_files(self, file_name: str):
        self._write_ldb_file(file_name)
        self._write_uldb_file(file_name)
        self._write_srcnclust_file(file_name)

    def _write_ldb_file(self, file_name: str):
        """
        A type of file required by Alchemy for structure learning.

        To construct the ldb file, consider each community in turn, find all hyperedges from the original
        hypergraph whose nodes are members of the community, then return a list of these hyperedges, but formatted with
        each constant replaced by either a node id (if the constant corresponds to a single node), or a cluster id
        (if the constant corresponds to a node belonging to a cluster).

        Example output (for a single community):

        #START_DB 0 #COM 1 #NUM_ATOMS 5
        movie(NODE_59,NODE_2)
        director(NODE_2)
        actor(CLUST_0)
        movie(NODE_59,CLUST_0)
        workedUnder(CLUST_0,NODE_2)
        #END_DB
        """
        with open(os.path.join(file_name + '.ldb'), 'w') as file:

            self._write_header(file)

            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    ldb_atoms = self._get_atoms_of_community(community, hypergraph_of_community=communities.hypergraph,
                                                             string_type='ldb')
                    self._write_atoms_to_file(ldb_atoms, file)

            self._write_footer(file)

    def _write_uldb_file(self, file_name: str):
        """
        A type of file required by Alchemy for structure learning.

        To construct the uldb file, consider each community in turn, find all hyperedges from the original
        hypergraph whose nodes are members of the community, then return a list of these hyperedges, formatted with
        each constant replaced by its node id.

        Example output (for a single community):

        #START_DB 0 #COM 1 #NUM_ATOMS 7
        workedUnder(NODE_53,NODE_2)
        movie(NODE_59,NODE_41)
        movie(NODE_59,NODE_33)
        actor(NODE_35)
        actor(NODE_40)
        workedUnder(NODE_34,NODE_2)
        actor(NODE_34)
        #END_DB
        """
        with open(os.path.join(file_name + '.uldb'), 'w') as file:

            self._write_header(file)

            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    uldb_atoms = self._get_atoms_of_community(community, hypergraph_of_community=communities.hypergraph,
                                                              string_type='uldb')
                    self._write_atoms_to_file(uldb_atoms, file)

            self._write_footer(file)

    def _write_srcnclust_file(self, file_name: str):
        """
        A type of file required by Alchemy for structure learning.

        To construct the srcnclust file, consider each community and output the node ids of the source nodes,
        single nodes, nodes that are members of clusters, and finally the ids of all nodes in the community.

        Example output (for a single community):

        #START_DB 0 #NUM_SINGLES 2 #NUM_CLUSTS 1 #NUM_NODES 17
        SRC 59
        2
        59
        CLUST 0  14 15 21 23 29 30 33 34 35 39 40 41 45 48 53
        NODES 2 14 15 21 23 29 30 33 34 35 39 40 41 45 48 53 59
        #END_DB
        """
        with open(os.path.join(file_name + '.srcnclusts'), 'w') as file:

            self._write_header(file)

            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    single_node_ids, cluster_node_ids = self._get_node_ids(community)

                    self._write_community_source_node_to_file(community, file)
                    self._write_single_node_ids_to_file(single_node_ids, file)
                    self._write_cluster_node_ids_to_file(cluster_node_ids, file)
                    self._write_all_node_ids_to_file(single_node_ids, cluster_node_ids, file)

            self._write_footer(file)

    def _write_header(self, file):
        header = '#START_GRAPH  #COMS {}\n\n'.format(self.num_of_communities)
        file.write(header)

    def _write_atoms_to_file(self, atoms, file):
        file.write('#START_DB {} #COM 1 #NUM_ATOMS {} \n'.format(self.community_number, len(atoms)))

        for atom in atoms:
            file.write(atom)
        file.write('#END_DB\n\n')

    @staticmethod
    def _write_footer(file):
        file.write('#END_GRAPH\n')

    def _write_community_source_node_to_file(self, community: Community, file):
        file.write("#START_DB {} #NUM_SINGLES {} #NUM_CLUSTS {} #NUM_NODES {}\n".format(self.community_number,
                                                                                        community.number_of_single_nodes
                                                                                        , community.number_of_clusters,
                                                                                        community.number_of_nodes))
        file.write("SRC {}\n".format(self.node_to_node_id[community.source_node]))

    @staticmethod
    def _write_single_node_ids_to_file(node_id_list, file):
        for node_id in node_id_list:
            file.write(node_id + '\n')

    @staticmethod
    def _write_cluster_node_ids_to_file(cluster_node_ids, file):
        for idx, node_id_list in enumerate(cluster_node_ids):
            string_of_node_ids = ' '.join(node_id_list)
            file.write('CLUST {}  {}\n'.format(idx, string_of_node_ids))

    @staticmethod
    def _write_all_node_ids_to_file(single_node_ids, cluster_node_ids, file):
        flattened_cluster_node_ids = list(itertools.chain(*cluster_node_ids))
        all_node_ids = single_node_ids + flattened_cluster_node_ids
        all_node_ids.sort(key=int)
        string_of_all_node_ids = ' '.join(all_node_ids)
        file.write("NODES {}\n".format(string_of_all_node_ids))
        file.write("#END_DB\n\n")

    def _get_atoms_of_community(self, community, hypergraph_of_community, string_type):
        atoms = set()

        for single_node in community.single_nodes:
            edges = hypergraph_of_community.nodes[single_node].memberships.values()
            atoms.update(self._get_atoms_of_edges_for_community(edges, community, string_type))

        for cluster in community.clusters:
            for cluster_node in cluster:
                edges = hypergraph_of_community.nodes[cluster_node].memberships.values()
                atoms.update(self._get_atoms_of_edges_for_community(edges, community, string_type))

        return atoms

    def _get_atoms_of_edges_for_community(self, edges, community, string_type):
        atoms = set()
        for edge in edges:
            nodes_of_edge = set(edge.elements.keys())
            if nodes_of_edge.issubset(community.nodes):
                atoms.add(self._get_atom_for_edge(edge, string_type))
            else:
                continue

        return atoms

    def _get_atom_for_edge(self, edge, string_type):
        atom = edge.predicate + '('
        nodes_of_edge = list(edge.elements.values())
        for node in nodes_of_edge[:-1]:
            atom += self._get_node_name(node, string_type) + ','
        atom += self._get_node_name(nodes_of_edge[-1], string_type) + ')\n'

        return atom

    def _get_node_name(self, node, string_type):
        if string_type == 'ldb':
            return self.node_to_ldb_string[self.hypergraph_number][self.community_number][node.name]

        elif string_type == 'uldb':
            return 'NODE_' + str(self.node_to_node_id[node.name])
        else:
            raise ValueError('String types other than "ldb" or "uldb" are not supported.')

    def _get_node_ids(self, community):
        single_node_ids = []
        for single_node in community.single_nodes:
            single_node_ids.append(str(self.node_to_node_id[single_node]))

        single_node_ids.sort(key=int)

        cluster_node_ids = []
        for cluster in community.clusters:
            node_ids = []
            for cluster_node in cluster:
                node_ids.append(str(self.node_to_node_id[cluster_node]))

            node_ids.sort(key=int)
            cluster_node_ids.append(node_ids)

        return single_node_ids, cluster_node_ids  # list[int], list[list[int]]

    def _get_node_to_ldb_string_map(self):
        """
        Loops over every node in the communities and assigns it an appropriate
        str_name based on whether it is part of a single node cluster or a multi-node
        cluster.
        :returns: node_to_ldb_string - a dictionary mapping from node names to their string
                                        representation for output to the .ldb file
        """
        node_to_ldb_string = defaultdict(lambda: defaultdict(dict))
        for hypergraph_id, communities in enumerate(self.list_of_communities):
            for community_number, community in enumerate(communities.communities.values()):
                for single_node in community.single_nodes:
                    node_to_ldb_string[hypergraph_id][community_number][single_node] = 'NODE_' + str(
                        self.node_to_node_id[single_node])

                for cluster_number, cluster in enumerate(community.clusters):
                    for cluster_node in cluster:
                        node_to_ldb_string[hypergraph_id][community_number][cluster_node] = 'CLUST_' + str(
                            cluster_number)

        return node_to_ldb_string
