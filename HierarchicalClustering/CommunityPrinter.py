import numpy as np
import os
import graph_utils as graph_util
from EnhancedHypergraph import EnhancedUndirectedHypergraph
from Community import Community
import itertools

class CommunityPrinter(object):
    def __init__(self, output_directory, original_hypergraph, communities, community_hypergraphs, verbose=True):

        assert isinstance(original_hypergraph, EnhancedUndirectedHypergraph), "Arg Error: original_hypergraph must be of type EnhancedUndirectedHypergraph"
        assert isinstance(community_hypergraphs[0], EnhancedUndirectedHypergraph), "Arg Error: community_hypergraphs must be of type List<EnhancedUndirectedHypergraph>"
        assert isinstance(communities[0], Community), "Arg Error: communities must be of type List<Community>"
        
        self.output_directory = output_directory
        self.num_of_communities = len(communities)
        self.communities = communities
        self.community_hypergraphs = community_hypergraphs
        _, self.node_to_node_ids = graph_util.get_node_mapping(original_hypergraph)
        self.ldb_node_to_name_map, self.uldb_node_to_name_map = self._populate_node_to_name_map()

    def _populate_node_to_name_map(self):
        """
        Loops over every node in the communities and assigns it an appropriate
        str_name based on whether it is part of a single node cluster or a multi-node
        cluster.

        :param communities: a list of community objects
        :param node_to_node_ids: a dictionary mapping from node names to node ids
        :returns: ldb_node_to_name_map - a dictionary mapping from node names to their string
                                        representation for output to the .ldb file
                uldb_node_to_name_map - a dictionary mapping from node names to their string
                                        representation for output to the .ldb file
        """
        ldb_node_to_name_map = dict()
        uldb_node_to_name_map = dict()
        for community in self.communities:
            for single_node in community.single_nodes:
                ldb_node_to_name_map[single_node.name] = 'NODE_'+str(self.node_to_node_ids[single_node.name])
                uldb_node_to_name_map[single_node.name] = 'NODE_'+str(self.node_to_node_ids[single_node.name])
            
            for idx, cluster in enumerate(community.clusters):
                for cluster_node in cluster:
                    ldb_node_to_name_map[cluster_node.name] = 'CLUST_'+str(idx)
                    uldb_node_to_name_map[cluster_node.name] = 'NODE_'+str(self.node_to_node_ids[cluster_node.name])

        return ldb_node_to_name_map, uldb_node_to_name_map

    def _print_community_diagnostics(self):
        num_nodes = [community_hypergraph.order() for community_hypergraph in self.community_hypergraphs]
        min_nodes = min(num_nodes)
        max_nodes = max(num_nodes)
        num_edges = [community_hypergraph.size() for community_hypergraph in self.community_hypergraphs]
        ave_num_nodes = np.mean(num_nodes)
        ave_num_edges = np.mean(num_edges)
        print('Created {} community hypergraphs with an average of {} nodes and {} edges.'.format(self.num_of_communities, int(ave_num_nodes), int(ave_num_edges)))
        print('The largest community has {} nodes. The smallest has {} nodes.'.format(max_nodes, min_nodes))

    def _get_node_name_from_id_and_map(self, hyperedge_node, hyperedge_id, node_to_name_map):
        try:
            return node_to_name_map[hyperedge_node]
        except:
            raise ValueError('Node {} from hyperedge {} not in community'.format(hyperedge_node, hyperedge_id))

    def _update_hyperedge_string(self, file_type : str, output_string, hyperedge_node, hyperedge_id, num_nodes_in_hyperedge, idx):
        if file_type == 'ldb':
            name = self._get_node_name_from_id_and_map(hyperedge_node, hyperedge_id, self.ldb_node_to_name_map)
        elif file_type == 'uldb':
            name = self._get_node_name_from_id_and_map(hyperedge_node, hyperedge_id, self.ldb_node_to_name_map)

        if idx < (num_nodes_in_hyperedge - 1): 
            output_string += name+',' 
        else: 
            output_string += name+')\n'
        return output_string

    def _get_hyperedge_string_for_file_type(self, file_type : str, predicate, hyperedge_nodes, hyperedge_id):
        assert file_type in ['ldb', 'uldb']
        num_nodes_in_hyperedge = len(hyperedge_nodes)
        output_string = predicate + '('
        for idx, hyperedge_node in enumerate(hyperedge_nodes):
            output_string = self._update_hyperedge_string(file_type, output_string, hyperedge_node, hyperedge_id, num_nodes_in_hyperedge, idx)
        return output_string

    def _get_hyperedge_strings(self, hyperedge_id, hypergraph):
        """
        Outputs a string representation of a given hyperedge in a hypergraph.

        :param hyperedge_id: the ID of the hyperedge to format
        :param node_to_name_map: a dictionary mapping from node names to their string
                                representation for output to file
        :param hypergraph: the hypergraph that the hyperedge belongs to
        :returns: output_string - the string representation of the hyperedge 
        """
        predicate = hypergraph.get_predicate_of_hyperedge(hyperedge_id)
        hyperedge_nodes = hypergraph.get_hyperedge_nodes(hyperedge_id)
        
        ldb_hyperedge_string = self._get_hyperedge_string_for_file_type('ldb', predicate, hyperedge_nodes, hyperedge_id)
        uldb_hyperedge_string = self._get_hyperedge_string_for_file_type('uldb', predicate, hyperedge_nodes, hyperedge_id)
        
        return {'ldb': ldb_hyperedge_string, 'uldb': uldb_hyperedge_string}

    def _create_blank_community_files(self, file_name : str):
        return open(os.path.join(self.output_directory,file_name+'.ldb'), 'w'), open(os.path.join(self.output_directory,file_name+'.uldb'), 'w'), open(os.path.join(self.output_directory,file_name+'.srcnclusts'), 'w')

    def _write_header_to_file(self, header : str, file):
        assert isinstance(header, str)
        file.write(header)

    def _write_community_source_node_to_file(self, community, file, idx):
        file.write("#START_DB {} #NUM_SINGLES {} #NUM_CLUSTS {} #NUM_NODES {}\n".format(idx, community.num_single_nodes, community.num_clusters, community.num_nodes))
        file.write("SRC {}\n".format(self.node_to_node_ids[community.source_node]))

    def _update_atom_strings(self, hyperedge_ids, community_hypergraph):
        for hyperedge_id in hyperedge_ids:
            hyperedge_strings = self._get_hyperedge_strings(hyperedge_id, community_hypergraph)
            self.ldb_atom_strings.add(hyperedge_strings['ldb'])
            self.uldb_atom_strings.add(hyperedge_strings['uldb'])

    def _get_single_node_ids_and_update_single_node_atom_strings(self, community, community_hypergraph):
        single_node_ids = []
        
        node_to_hyperedge_ids = community_hypergraph.get_node_to_hyperedge_id_dict()
        for single_node in community.single_nodes:
            single_node_ids.append(str(self.node_to_node_ids[single_node.name]))
            hyperedge_ids = node_to_hyperedge_ids[single_node.name]
            self._update_atom_strings(hyperedge_ids, community_hypergraph)

        single_node_ids.sort(key=int)
        return single_node_ids

    def _get_cluster_node_ids_and_update_cluster_node_atom_strings(self, community, community_hypergraph):
        cluster_node_ids = []
        
        node_to_hyperedge_ids = community_hypergraph.get_node_to_hyperedge_id_dict()
        for cluster in community.clusters:
            node_ids = []
            for cluster_node in cluster:
                node_ids.append(str(self.node_to_node_ids[cluster_node.name]))
                hyperedge_ids = node_to_hyperedge_ids[cluster_node.name]
                self._update_atom_strings(hyperedge_ids, community_hypergraph)

            #Output the string of node ids in the cluster to the .srcnclust file
            node_ids.sort(key=int)
            cluster_node_ids.append(node_ids)
        
        return cluster_node_ids

    def _write_node_id_list_to_file(self, node_id_list, file):
        for node_id in node_id_list:
            file.write(node_id+'\n')

    def _write_cluster_node_id_list_to_file(self, cluster_node_ids, file):
        for idx, node_id_list in enumerate(cluster_node_ids):
            string_of_node_ids = ' '.join(node_id_list)
            file.write('CLUST {}  {}\n'.format(idx, string_of_node_ids))

    def _write_ordered_string_of_all_node_ids_to_file(self, single_node_ids, cluster_node_ids, file):
        flattened_cluster_node_ids = list(itertools.chain(*cluster_node_ids))
        all_node_ids = single_node_ids  + flattened_cluster_node_ids
        all_node_ids.sort(key=int)
        string_of_all_node_ids = ' '.join(all_node_ids)
        file.write("NODES {}\n".format(string_of_all_node_ids)) 

    def _write_atom_strings_to_file(self, atom_strings, idx, file):
        file.write('#START_DB  {}  #COMS  1  #NUM_ATOMS {}\n'.format(idx, len(atom_strings)))
        for atom_string in atom_strings:
            file.write(atom_string)

    def _write_footer_and_close_file(self, footer, file):
        file.write(footer)
        file.close()

    def _write_body_of_files(self, ldb_file, uldb_file, srcnclust_file):
        for idx, (community_hypergraph, community) in enumerate(zip(self.community_hypergraphs,self.communities)):
            self._write_community_source_node_to_file(community, srcnclust_file, idx)

            self.ldb_atom_strings = set()
            self.uldb_atom_strings = set()

            single_node_ids = self._get_single_node_ids_and_update_single_node_atom_strings(community, community_hypergraph)

            self._write_node_id_list_to_file(single_node_ids, srcnclust_file)

            cluster_node_ids = self._get_cluster_node_ids_and_update_cluster_node_atom_strings(community, community_hypergraph)
            self._write_cluster_node_id_list_to_file(cluster_node_ids, srcnclust_file)

            self._write_ordered_string_of_all_node_ids_to_file(single_node_ids, cluster_node_ids, srcnclust_file)

            self._write_atom_strings_to_file(self.ldb_atom_strings, idx, ldb_file)
            self._write_atom_strings_to_file(self.uldb_atom_strings, idx, uldb_file)

            ldb_file.write("#END_DB\n\n")
            uldb_file.write("#END_DB\n\n")
            srcnclust_file.write("#END_DB\n\n")

    def write_communities_files(self, file_name : str, verbose = True):
        """
        Writes the communities .ldb, .uldb, and .srcnclust files to disk

        :param original_hypergraph: the hypergraph representation of the relational database
        :param community_hypergraphs: a list of hypergraphs obtained after performing hierarchical clustering 
                                    on the original hypergraph
        :param communities: a list of communities corresponding to each of the community_hypergraphs
        :param file_name: the name of the output file (before .ldb/.uldb/.srcnclust suffix)
        :param verbose (bool): whether or not to include a diagnostic output of the size and shape of the communities
        """

        ldb_file, uldb_file, srcnclust_file = self._create_blank_community_files(file_name)

        header = '#START_GRAPH  #COMS {}\n\n'.format(self.num_of_communities)
        self._write_header_to_file(header, ldb_file)
        self._write_header_to_file(header, uldb_file)
        self._write_header_to_file(header, srcnclust_file)

        self._write_body_of_files(ldb_file, uldb_file, srcnclust_file)

        footer = '#END_GRAPH\n'
        self._write_footer_and_close_file(footer, ldb_file)
        self._write_footer_and_close_file(footer, uldb_file)
        self._write_footer_and_close_file(footer, srcnclust_file)

        if verbose == True:
            self._print_community_diagnostics()