import undirected_matrices as umat

class Community(object):
    """
    TODO: add description
    """
    def __init__(self, clustered_nodes):
        self.single_nodes, self.clusters = self.get_single_nodes_and_clusters(clustered_nodes)
        self.num_single_nodes = len(self.single_nodes)
        self.num_clusters = len(self.clusters)
    
    def get_single_nodes_and_clusters(self, clustered_nodes):
        """
        :param: clustered_nodes - a list of lists
        """
        single_nodes = []
        clusters = []
        for array in clustered_nodes:
            if len(array) == 1:
                single_nodes.append(array)
            else:
                clusters.append(array)
        
        return single_nodes, clusters


def _populate_node_to_name_map(communities, node_to_node_ids):
    """
    TODO: write description
    """
    node_to_name_map = dict()
    for community in communities:
        for single_node in community.single_nodes:
            node_to_name_map[single_node.name] = 'NODE_'+node_to_node_ids[single_node.name]
        
        for idx, cluster in enumerate(community.clusters):
            for cluster_node in cluster:
                node_to_name_map[cluster_node.name] = 'CLUST_'+idx

    return node_to_name_map

def _get_output_string(hyperedge_id, node_to_name_map, original_hypergraph):
    predicate = original_hypergraph.get_predicate_of_hyperedge(hyperedge_id)
    hyperedge_nodes = original_hypergraph.get_hyperedge_nodes(hyperedge_id)
    number_nodes_in_hyperedge = len(hyperedge_nodes)
    output_string = predicate + '('
    for idx, hyperedge_node in enumerate(hyperedge_nodes):
        name = node_to_name_map[hyperedge_node]
        if idx < (number_nodes_in_hyperedge - 1): 
            output_string += name+',' 
        else: 
            output_string += name+')'

    return output_string

def write_communities_file(original_hypergraph, communities, file_name : str):
    """
    TODO: Add description

    :param: communities - a list of type community
    """
    
    #TODO: check input argument types

    num_of_communities = len(communities)
    _, node_to_node_ids = umat.get_node_mapping(original_hypergraph)
    node_to_hyperedge_ids = original_hypergraph.get_node_to_hyperedge_id_dict()
    node_to_name_map = _populate_node_to_name_map(communities, node_to_node_ids)

    out_file = open(file_name, 'w')

    out_file.write('#START_GRAPH #COMS {}'.format(num_of_communities))

    for idx, community in enumerate(communities):
        atom_strings = set()
        for single_node in community.single_nodes:
            for hyperedge_id in node_to_hyperedge_ids[single_node.name]:
                atom_strings.add(_get_output_string(hyperedge_id, node_to_name_map, original_hypergraph))

        for cluster in community.clusters:
            for cluster_node in cluster:
                for hyperedge_id in node_to_hyperedge_ids[cluster_node.name]:
                    atom_strings.add(_get_output_string(hyperedge_id, node_to_name_map, original_hypergraph))
        out_file.write('#START_DB  {}  #COMS  1  #NUM_ATOMS {}'.format(idx, len(atom_strings)))
        for atom_string in atom_strings:
            out_file.write(atom_string)

    out_file.write('#END DB')
    out_file.write('#END GRAPH')

    out_file.close()
                    


