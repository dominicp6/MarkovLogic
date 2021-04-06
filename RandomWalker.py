from EnhancedHypergraph import EnhancedUndirectedHypergraph
from Community import Community
import graph_utils as graph_util
import numpy as np
from collections import defaultdict
from scipy import sparse

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

    def __init__(self, number_of_walks = 100, max_length = 100, merge_criterion = 'truncated_hitting_time', source_node = None, merge_threshold = 2):
        assert isinstance(number_of_walks, int), "Arg Error: number_of_walks must be of type int"
        assert isinstance(max_length, int), "Arg Error: max_length must be of type int"
        assert merge_criterion in ['JS_divergence', 'truncated_hitting_time'], "Arg Error: merge criterion must be either JS_divergence of truncated_hitting_time"
        assert isinstance(merge_threshold, (int,float)) and merge_threshold > 0, "Arg Error: merge_threshold must be a positive real number"
        
        self.number_of_walks = number_of_walks
        self.max_length = max_length
        self.merge_criterion = merge_criterion
        self.merge_threshold = merge_threshold
        
    def _setup_params(self, H):
        self._indices_to_nodes, self._nodes_to_indices = graph_util.get_node_mapping(H)
        _, self._hyperedge_ids_to_indices = graph_util.get_hyperedge_id_mapping(H)

        #self.transition_matrix = self._compute_transition_matrix(H)

        #self.sample_paths = defaultdict(lambda: [])
        
        return 

    def _compute_transition_matrix(self, H):
        """Computes the transition matrix for a random walk on the given
        hypergraph as described in the paper:
        Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
        "Learning with hypergraphs: Clustering, classification, and embedding."
        Advances in neural information processing systems. 2006.
        (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

        :param H: the hypergraph to find the transition matrix of.
        :returns: sparse.csr_matrix -- the transition matrix as a sparse matrix.

        """
        M = graph_util.get_incidence_matrix(H,
                                    self._nodes_to_indices, self._hyperedge_ids_to_indices)
        W = graph_util.get_hyperedge_weight_matrix(H, self._hyperedge_ids_to_indices)
        D_v = graph_util.get_vertex_degree_matrix(M, W)
        D_e = graph_util.get_hyperedge_degree_matrix(M)

        D_v_inv = graph_util.fast_inverse(D_v)
        D_e_inv = graph_util.fast_inverse(D_e)
        M_trans = M.transpose()

        #construct the transition matrix
        P = D_v_inv * M * W * D_e_inv * M_trans

        return P

    def _get_source_node(self):
        """
        Gets a source node from a hypergraph from which to start running random walks
        by randomly selecting a node from the hypergraph.

        :param H: the hypergraph to get the source node from
        :returns: the ID of the source node
        """
        #TODO: change this so that it uses a more sensible criterion than a random selection?
        return np.random.choice(list(self._nodes_to_indices.keys()))

    def _cluster_nodes(self, node_list):
        """
        Clusters a list of nodes into groups based on the truncated hitting
        criterion as follows:

        Let h_{j} be the average truncated hitting time of node v_{j}.
        Nodes v_{j} are grouped into disjoint sets A_{k} such that:
        for all v_{j} in A_{k} there exists a node v_{j'} in A_{k}
        such that |h_{j} - h_{j'}| <= merge_threshold.
        Ref: https://alchemy.cs.washington.edu/papers/kok10/kok10.pdf
        """

        #sort the nodes in the hypergraph in increasing order of average hitting time
        sorted_node_list = sorted(node_list, key = lambda n: n.ave_hitting_time)

        node_clusters = []
        cluster = []
        for idx, node in enumerate(sorted_node_list):
            if idx == 0:
                cluster.append(node)
                t_old = node.ave_hitting_time
                continue
            
            t_new = node.ave_hitting_time
            cluster.append(node)

            if (t_new - t_old) <= self.merge_threshold:
                t_old = t_new
            else:
                #append the cluster A_{k} to the list of clusters
                node_clusters.append(cluster)
                cluster = []
        
        if len(cluster) > 0:
            node_clusters.append(cluster)
            
        
        return node_clusters

    def _get_next_node_idx(self, H, current_node):
        """
        Uses the transition matrix of the hypergraph to sample the next node 
        index in a random walk given the current node idx.

        :param H: The hypergraph on which to perform the random walk
        :param current_node_idx: The index of the currently selected node

        :returns next_node_idx: The index of the next node in the random walk
        """

        #An option which uses the transition matrix
        #row = self.transition_matrix.getrow(current_node_idx)
        #nodes_to_transition_to = row.nonzero()[1]
        #transition_probs = row.data
        #return np.random.choice(nodes_to_transition_to, p=transition_probs)

        #1) Find hyperedges that the node is a member of
        node_hyperedge_ids = H.get_star(current_node)
        #2) Select a hyperedge uniformly at random
        hyperedge_id = np.random.choice(tuple(node_hyperedge_ids))
        hyperedge = H.get_hyperedge_nodes(hyperedge_id)
        hyperedge.remove(current_node)
        #3) Select a node at random from that hyperedge
        if len(hyperedge) == 0:
            return current_node
            
        next_node = np.random.choice(tuple(hyperedge))

        return next_node

    def run_random_walks(self, H):
        """
        Runs random walks on the hypergraph H to cluster nodes based on 
        a merge criterion (either 'truncated_hitting_time' or 'JS_divergence').

        :param: H (EnhancedUndirectedHypergraph) - the hypergraph to run random walks on
        :returns: Community object of the hypergraph's node clusters
        """
        self._setup_params(H)

        #get the source node for the random walk
        source_node = self._get_source_node()

        #sample_path = []

        #use transition matix to run random walks
        for walk in range(1, self.number_of_walks + 1):
            for step in range(self.max_length):
                if step == 0:
                    current_node = source_node
                    #sample_path.append(current_node_idx)
            
                #make a random step using the transition matrix
                next_node = self._get_next_node_idx(H, current_node)

                node_obj = H.node_name_to_node_object[next_node]
                
                current_node = next_node
                #sample_path.append(current_node_idx)

                #update node properties if its a first visit
                if node_obj.first_visit:
                    node_obj.update_ave_hitting_time(hitting_time = step, walk_number = walk)
                    #node_obj.update_sample_paths(path = sample_path, walk_number = walk)
                    node_obj.first_visit = False

            H.update_nodes(max_length = self.max_length, walk_number = walk)

        #cluster nodes based on their symmetry properties
        if self.merge_criterion == 'truncated_hitting_time':
            node_list = H.node_name_to_node_object.values()
            clusters = self._cluster_nodes(node_list)

        elif self.merge_criterion == 'JS_divergence':
            #TODO: Implement JS divergence clustering
            raise NotImplementedError

        return Community(clustered_nodes = clusters, source_node = source_node)
       
        



        
        




        