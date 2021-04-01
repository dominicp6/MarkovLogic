from EnhancedHypergraph import EnhancedUndirectedHypergraph
from Community import Community
import undirected_matrices as umat
import numpy as np
from collections import defaultdict

class RandomWalker(object):
    """
    Runs random walks on a hypergraph and merges nodes based
    on either their truncated hitting time of Jason-Shanon divergence in 
    the distribution of paths.

    param: number_of_walks (int): the number of random walks to run from the
    cluster's source node
    param: merge_criterion: specifies the criterion used to merge nodes based
                            on their symmetry properties. The options are:
                            'JSDiv' - merge based on the Jason-Shanon divergence 
                            between the distributions of the paths
                            'hitting_time' - merge based on the differences in
                            truncated hitting times of arriving at the nodes 
                            when starting from the source node
    """

    def __init__(self,H, number_of_walks = 100, max_length = 100, merge_criterion = 'JS_divergence', source_node = None, merge_threshold = 2):
        assert isinstance(H, EnhancedUndirectedHypergraph), "Arg Error: H must be of type EnhancedUndirectedHypergraph"
        assert isinstance(number_of_walks, int), "Arg Error: number_of_walks must be of type int"
        assert isinstance(max_length, int), "Arg Error: max_length must be of type int"
        assert merge_criterion in ['JS_divergence', 'truncated_hitting_times'], "Arg Error: merge criterion must be either JS_divergence of truncated_hitting_times"
        assert isinstance(merge_threshold, float), "Arg Error: merge_threshold must be of type float"
        
        self.H = H
        self.number_of_walks = number_of_walks
        self.max_length = max_length
        self.merge_criterion = merge_criterion
        self.source_node = source_node
        self.merge_threshold = merge_threshold

        #populate dictionary mappings
        #TODO: change this so that it differentiates between nodes of different types?
        self._indices_to_nodes, self._nodes_to_indices = umat.get_node_mapping(self.H)
        _, self._hyperedge_ids_to_indices = umat.get_hyperedge_id_mapping(self.H)

        self.transition_matrix = self._compute_transition_matrix()

        self.sample_paths = defaultdict(lambda: [])

    def _compute_transition_matrix(self):
        """Computes the transition matrix for a random walk on the given
        hypergraph as described in the paper:
        Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
        "Learning with hypergraphs: Clustering, classification, and embedding."
        Advances in neural information processing systems. 2006.
        (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

        :param H: the hypergraph to find the transition matrix of.
        :returns: sparse.csc_matrix -- the transition matrix as a sparse matrix.

        """
        M = umat.get_incidence_matrix(self.H,
                                    self._nodes_to_indices, self._hyperedge_ids_to_indices)
        W = umat.get_hyperedge_weight_matrix(self.H, self._hyperedge_ids_to_indices)
        D_v = umat.get_vertex_degree_matrix(M, W)
        D_e = umat.get_hyperedge_degree_matrix(M)

        D_v_inv = umat.fast_inverse(D_v)
        D_e_inv = umat.fast_inverse(D_e)
        M_trans = M.transpose()

        #construct the transition matrix
        P = D_v_inv * M * W * D_e_inv * M_trans

        return P

    def _get_source_node(self):
        """
        Gets a source node from a hypergraph from which to start running random walks

        :param H: the hypergraph to get the source node from
        :returns: the ID of the source node
        """
        #TODO: change this so that it uses a more sensible criterion than a random selection
        if self.source_node == None:
            self.source_node = np.random.choice(self._nodes_to_indices.values())
        else:
            pass

    def _cluster_nodes(self, node_list):
        """
        Clusters a list of nodes into groups based on the truncated hitting
        criterion.

        #TODO: explain the criterion
        """

        #sort the nodes in the hypergraph in increasing order of average hitting time
        sorted_node_list = sorted(node_list, key = lambda n: n.ave_hitting_time)

        node_clusters = []
        cluster = []
        for idx, node in enumerate(sorted_node_list):
            if idx == 0:
                cluster.append(node)
                t_old = node.ave_hitting_time
            
            t_new = node.ave_hitting_time
            if (t_new - t_old) <= self.merge_threshold:
                cluster.append(node)
                t_old = t_new
            else:
                node_clusters.append(cluster)
                cluster = []
        
        return node_clusters


    def run_random_walks(self):
        #get the source node for the random walk
        self._get_source_node()

        node_idx_array = [idx for idx in range(self.transition_matrix.shape[0])]
        sample_path = []

        #use transition matix to run random walks
        for walk in range(1, self.number_of_walks + 1):
            for step in range(self.max_length):
                if step == 0:
                    current_node_idx = self.source_node
                    sample_path.append(current_node_idx)
                
                #make a random step using the transition matrix
                next_node_idx = np.random.choice(node_idx_array, p=self.transition_matrix[current_node_idx][:])

                node_obj = self.H.node_name_to_node_object[self._indices_to_nodes[next_node_idx]]
                
                current_node_idx = next_node_idx
                sample_path.append(current_node_idx)

                #update node properties if its a first visit
                if node_obj.first_visit:
                    node_obj.update_ave_hitting_time(hitting_time = step, walk_number = walk)
                    node_obj.update_sample_paths(sample_path = sample_path, walk_number = walk)
                    node_obj.first_visit = False

            self.H.reset_nodes(max_length = self.max_length, walk_number = walk)

        #cluster nodes based on their symmetry properties
        if self.merge_criterion == 'truncated_hitting_time':
            node_list = self.H.node_name_to_node_object.values()
            clusters = self._cluster_nodes(node_list)

        elif self.merge_criterion == 'JS_divergence':
            #TODO: Implement JS divergence clustering
            raise NotImplementedError

        return Community(clusters)
       
        



        
        




        