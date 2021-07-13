import os

from Communities import *
from collections import defaultdict
import itertools


class CommunityPrinter(object):
    """
    Enables community objects to be saved to disk formatted in a way that can be understood by the
    rest of the Alchemy structure learning pipeline.

    Initialised with a list of communities and the original hypergraph that the communities are associated with.

    Calling the write_files() method saves this communities to disk by generating three types of datafiles that
    are required by Alchemy:

    .ldb file       - For each community, contains a list of all hyperedges in a community but with nodes replaced by
                      either node id (if it is a single node) or cluster id (if it is a member of a cluster)
    .uldb file      - As for .ldb file but every node is replaced by its node id, regardless of whether it is a single
                      node or a member of a cluster.
    .srcnclust file - A file that enumerates the node id of every source node, single node and node in each node cluster
                      in a community.
    """
    def __init__(self, list_of_communities: list[Communities], original_hypergraph):

        self.list_of_communities = list_of_communities

        self.num_of_communities = sum(len(communities.communities) for communities in self.list_of_communities)

        # Alchemy requires that each node in the original hypergraph is indexed with a unique id number
        self.node_to_node_id = defaultdict(int)
        for node_id, node in enumerate(original_hypergraph.nodes.keys()):
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

            self.global_community_index = 0
            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    ldb_atoms = self._get_atoms_of_community(community, hypergraph_of_community=communities.hypergraph,
                                                             string_type='ldb')
                    self._write_atoms_to_file(ldb_atoms, file)
                    self.global_community_index += 1

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

            self.global_community_index = 0
            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    uldb_atoms = self._get_atoms_of_community(community, hypergraph_of_community=communities.hypergraph,
                                                              string_type='uldb')
                    self._write_atoms_to_file(uldb_atoms, file)
                    self.global_community_index += 1

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

            self.global_community_index = 0
            for hypergraph_number, communities in enumerate(self.list_of_communities):
                self.hypergraph_number = hypergraph_number
                for community_number, community in enumerate(communities.communities.values()):
                    self.community_number = community_number
                    single_node_ids, cluster_node_ids = self._get_node_ids(community)

                    self._write_community_source_node_to_file(community, file)
                    self._write_single_node_ids_to_file(single_node_ids, file)
                    self._write_cluster_node_ids_to_file(cluster_node_ids, file)
                    self._write_all_node_ids_to_file(single_node_ids, cluster_node_ids, file)
                    self.global_community_index += 1

            self._write_footer(file)

    def _write_header(self, file):
        header = '#START_GRAPH  #COMS {}\n\n'.format(self.num_of_communities)
        file.write(header)

    def _write_atoms_to_file(self, atoms: list[str], file):
        """
        Writes a list of atoms strings to file. These atom strings make up the information content of the .ldb and .uldb
        files.
        """
        file.write('#START_DB {} #COM 1 #NUM_ATOMS {} \n'.format(self.global_community_index, len(atoms)))

        for atom in atoms:
            file.write(atom)
        file.write('#END_DB\n\n')

    @staticmethod
    def _write_footer(file):
        file.write('#END_GRAPH\n')

    def _write_community_source_node_to_file(self, community: Community, file):
        """
        Write the id of the source node of a community to file. Called when creating the .srcnclust file.
        """
        file.write("#START_DB {} #NUM_SINGLES {} #NUM_CLUSTS {} #NUM_NODES {}\n".format(self.global_community_index,
                                                                                        community.number_of_single_nodes
                                                                                        , community.number_of_clusters,
                                                                                        community.number_of_nodes))
        file.write("SRC {}\n".format(self.node_to_node_id[community.source_node]))

    @staticmethod
    def _write_single_node_ids_to_file(node_id_list, file):
        """
        Writes the ids of each single node to file. Called when creating the .srcnclust file.
        """
        for node_id in node_id_list:
            file.write(node_id + '\n')

    @staticmethod
    def _write_cluster_node_ids_to_file(cluster_node_ids, file):
        """
        Writes the node ids of every node in each cluster. Called when creating the .srcnclust file.
        """
        for idx, node_id_list in enumerate(cluster_node_ids):
            string_of_node_ids = ' '.join(node_id_list)
            file.write('CLUST {}  {}\n'.format(idx, string_of_node_ids))

    @staticmethod
    def _write_all_node_ids_to_file(single_node_ids, cluster_node_ids, file):
        """
        Writes a list of node ids of nodes in the community to file. These node ids make up the information content
        of the .srcnclust file.
        """
        flattened_cluster_node_ids = list(itertools.chain(*cluster_node_ids))
        all_node_ids = single_node_ids + flattened_cluster_node_ids
        all_node_ids.sort(key=int)
        string_of_all_node_ids = ' '.join(all_node_ids)
        file.write("NODES {}\n".format(string_of_all_node_ids))
        file.write("#END_DB\n\n")

    def _get_atoms_of_community(self, community, hypergraph_of_community, string_type: str):
        atoms = set()

        for single_node in community.single_nodes:
            atoms.update(self._get_atoms_of_node_in_community(single_node,
                                                              community,
                                                              hypergraph_of_community,
                                                              string_type))

        for cluster in community.clusters:
            for cluster_node in cluster:
                atoms.update(self._get_atoms_of_node_in_community(cluster_node,
                                                                  community,
                                                                  hypergraph_of_community,
                                                                  string_type))

        return atoms

    def _get_atoms_of_node_in_community(self, node, community, hypergraph_of_community, string_type):
        """
        Finds all ground atoms containing a specified node, where all grounding constants are also present in
        the community.
        """
        atoms = set()
        non_singleton_edges = hypergraph_of_community.memberships[node]
        for edge in non_singleton_edges:
            nodes_of_edge = hypergraph_of_community.edges[edge]
            if set(nodes_of_edge).issubset(community.nodes):
                predicate = hypergraph_of_community.predicates[edge]
                atoms.add(self._get_atom_for_edge(edge_predicate=predicate,
                                                  nodes_of_edge=nodes_of_edge,
                                                  string_type=string_type))
            else:
                continue

        for node, singleton_edges in hypergraph_of_community.singleton_edges.items():
            if node in community.nodes:
                for predicate in singleton_edges:
                    atoms.add(self._get_atom_for_edge(edge_predicate=predicate,
                                                      nodes_of_edge=node,
                                                      string_type=string_type))

        return atoms

    def _get_atom_for_edge(self, edge_predicate: str, nodes_of_edge: list[str], string_type: str):
        """
        Constructs and returns the ground atom string representation corresponding to a particular predicate
        and a list of grounded nodes.

        param: string_type: either 'ldb' or 'uldb', depending on whether the ground atom is part of the .ldb file
                            or part of the .uldb file
        """
        if type(nodes_of_edge) == list:
            atom = edge_predicate + '('
            for node in nodes_of_edge[:-1]:
                atom += self._get_node_name(node, string_type) + ','
            atom += self._get_node_name(nodes_of_edge[-1], string_type) + ')\n'
        elif type(nodes_of_edge) == str:
            atom = edge_predicate + '(' + self._get_node_name(nodes_of_edge, string_type) + ')\n'
        else:
            raise TypeError

        return atom

    def _get_node_name(self, node, string_type):
        """
        Finds the appropriate string representation of a node (either NODE_+{node_id} or NODE_{cluster_id}).

        param: string_type: either 'ldb' or 'uldb', in general a different string representation is required for these
                            two different types of files.
        """
        if string_type == 'ldb':
            return self.node_to_ldb_string[self.hypergraph_number][self.community_number][node]

        elif string_type == 'uldb':
            return 'NODE_' + str(self.node_to_node_id[node])
        else:
            raise ValueError('String types other than "ldb" or "uldb" are not supported.')

    def _get_node_ids(self, community):
        """
        Returns a list of all single node ids and cluster node ids in a community.
        """
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
