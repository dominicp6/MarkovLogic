import graph_utils as graph_util
from EnhancedHypergraph import EnhancedUndirectedHypergraph
from Community import Community

def _populate_node_to_name_map(communities, node_to_node_ids):
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
    for community in communities:
        for single_node in community.single_nodes:
            ldb_node_to_name_map[single_node.name] = 'NODE_'+str(node_to_node_ids[single_node.name])
            uldb_node_to_name_map[single_node.name] = 'NODE_'+str(node_to_node_ids[single_node.name])
        
        for idx, cluster in enumerate(community.clusters):
            for cluster_node in cluster:
                ldb_node_to_name_map[cluster_node.name] = 'CLUST_'+str(idx)
                uldb_node_to_name_map[cluster_node.name] = 'NODE_'+str(node_to_node_ids[cluster_node.name])


    return ldb_node_to_name_map, uldb_node_to_name_map

def _get_output_string(hyperedge_id, node_to_name_map, hypergraph):
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
    number_nodes_in_hyperedge = len(hyperedge_nodes)
    output_string = predicate + '('
    for idx, hyperedge_node in enumerate(hyperedge_nodes):
        try:
            name = node_to_name_map[hyperedge_node]
        except:
            print('Node {} from hyperedge {} not in community'.format(hyperedge_node, hyperedge_id))
        if idx < (number_nodes_in_hyperedge - 1): 
            output_string += name+',' 
        else: 
            output_string += name+')\n'

    return output_string

def write_communities_files(original_hypergraph, community_hypergraphs, communities, file_name : str):
    """
    Writes the communities .ldb, .uldb, and .srcnclust files to disk

    :param original_hypergraph: the hypergraph representation of the relational database
    :param community_hypergraphs: a list of hypergraphs obtained after performing hierarchical clustering 
                                  on the original hypergraph
    :param communities: a list of communities corresponding to each of the community_hypergraphs
    :param file_name: the name of the output file (before .ldb/.uldb/.srcnclust suffix)
    """
    
    assert isinstance(original_hypergraph, EnhancedUndirectedHypergraph), "Arg Error: original_hypergraph must be of type EnhancedUndirectedHypergraph"
    assert isinstance(community_hypergraphs[0], EnhancedUndirectedHypergraph), "Arg Error: community_hypergraphs must be of type List<EnhancedUndirectedHypergraph>"
    assert isinstance(communities[0], Community), "Arg Error: communities must be of type List<Community>"

    #Set up preliminary variables and dictionary mappings
    num_of_communities = len(communities)
    _, node_to_node_ids = graph_util.get_node_mapping(original_hypergraph)
    ldb_node_to_name_map, uldb_node_to_name_map = _populate_node_to_name_map(communities, node_to_node_ids)

    #Open the files
    ldb_out_file = open(file_name+'.ldb', 'w')
    uldb_out_file = open(file_name+'.uldb', 'w')
    srcnclust_out_file = open(file_name+'.srcnclust', 'w')

    #Write header line
    ldb_out_file.write('#START_GRAPH  #COMS {}\n\n'.format(num_of_communities))
    uldb_out_file.write('#START_GRAPH  #COMS {}\n\n'.format(num_of_communities))
    srcnclust_out_file.write('#START_GRAPH #COMS {}\n\n'.format(num_of_communities))

    #For each community
    for idx, (community_hypergraph, community) in enumerate(zip(community_hypergraphs,communities)):
        #Output the community's source node to the srcnclust file
        srcnclust_out_file.write("#START_DB {} #NUM_SINGLES {} #NUM_CLUSTS {} #NUM_NODES {}\n".format(idx, community.num_single_nodes, community.num_clusters, community.num_nodes))
        srcnclust_out_file.write("SRC {}\n".format(node_to_node_ids[community.source_node]))
        ldb_atom_strings = set()
        uldb_atom_strings = set()
        single_node_ids = []
        #For each single node
        for single_node in community.single_nodes:
            single_node_ids.append(str(node_to_node_ids[single_node.name]))
            node_to_hyperedge_ids = community_hypergraph.get_node_to_hyperedge_id_dict()
            #For each hyperedge associated with each single node
            for hyperedge_id in node_to_hyperedge_ids[single_node.name]:
                #Get the hyperedge strings to be output to the .ldb and .uldb files
                ldb_atom_strings.add(_get_output_string(hyperedge_id, ldb_node_to_name_map, community_hypergraph))
                uldb_atom_strings.add(_get_output_string(hyperedge_id, uldb_node_to_name_map, community_hypergraph))

        #Output single node ids to srcnclust file
        single_node_ids.sort(key=int)
        for single_node_id in single_node_ids:
            srcnclust_out_file.write(single_node_id+'\n')

        cluster_node_ids = []
        #For each multi-node cluster
        for idx, cluster in enumerate(community.clusters):
            #For each cluster node
            node_ids = []
            for cluster_node in cluster:
                node_ids.append(str(node_to_node_ids[cluster_node.name]))
                node_to_hyperedge_ids = community_hypergraph.get_node_to_hyperedge_id_dict()
                #For each hyperedge associated with each cluster node
                for hyperedge_id in node_to_hyperedge_ids[cluster_node.name]:
                    #Get the hyperedge strings to be output to the .ldb and .uldb files
                    ldb_atom_strings.add(_get_output_string(hyperedge_id, ldb_node_to_name_map, community_hypergraph))
                    uldb_atom_strings.add(_get_output_string(hyperedge_id, uldb_node_to_name_map, community_hypergraph))
            #Output the string of node ids in the cluster to the .srcnclust file
            node_ids.sort(key=int)
            string_of_node_ids = ' '.join(node_ids)
            srcnclust_out_file.write('CLUST {}  {}\n'.format(idx, string_of_node_ids))
            cluster_node_ids.extend(node_ids)

        #Output the node id list of the community to the .srcnclust file
        all_node_ids = single_node_ids  + cluster_node_ids
        all_node_ids.sort(key=int)
        string_of_all_node_ids = ' '.join(all_node_ids)
        srcnclust_out_file.write("NODES {}\n".format(string_of_all_node_ids)) 
        srcnclust_out_file.write("#END_DB\n\n")

        ldb_out_file.write('#START_DB  {}  #COMS  1  #NUM_ATOMS {}\n'.format(idx, len(ldb_atom_strings)))
        uldb_out_file.write('#START_DB  {}  #COMS  1  #NUM_ATOMS {}\n'.format(idx, len(uldb_atom_strings)))

        #Output the hyperedge strings to the .ldb and .uldb files
        for atom_string in ldb_atom_strings:
            ldb_out_file.write(atom_string)

        for atom_string in uldb_atom_strings:
            uldb_out_file.write(atom_string)

        ldb_out_file.write("#END_DB\n")
        ldb_out_file.write('\n')

        uldb_out_file.write("#END_DB\n")
        uldb_out_file.write('\n')

    #Output the footer and close the files
    ldb_out_file.write('#END_GRAPH\n')
    ldb_out_file.close()
    uldb_out_file.write('#END_GRAPH\n')
    uldb_out_file.close()
    srcnclust_out_file.write('#END_GRAPH\n')
    srcnclust_out_file.close()
