from MarkovLogicProject.HierarchicalClustering.Depricated.Community import Community
import Node as node_utils
import halp.utilities.undirected_matrices as umat
import numpy as np
from collections import defaultdict


def get_single_nodes_and_node_clusters(clustered_nodes):
    """
    Separates a list of lists of node clusters into clusters
    of single nodes and clusters of more the one node.

    :param: clustered_nodes - a list of lists
    :returns: single_nodes - the list of single node clusters
                clusters - a list of list of multi-node clusters
    """
    single_nodes = []
    node_clusters = []
    for array in clustered_nodes:
        if len(array) == 1:
            single_nodes.append(array[0])
        else:
            node_clusters.append(array)
    
    return single_nodes, node_clusters

class RandomWalker(object):
    """
    Runs random walks on a hypergraph and merges nodes based
    on truncated hitting time + Jason-Shanon divergence in 
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

    def __init__(self, config):
        
        #Suggested default parameter values
        #----------------------------------
        # number_of_walks = 100, 
        # max_length = 100, 
        # use_sample_paths = False, 
        # source_node = None, 
        # HT_merge_threshold = 2, 
        # JS_merge_threshold = 2, 
        # N_top = 5

        self.number_of_walks = config['number_of_walks']
        self.max_length = config['max_length']
        self.use_sample_paths = config['use_sample_paths']
        self.N_top = config['N_top']
        self.HT_merge_threshold = config['HT_merge_threshold']
        self.JS_merge_threshold = config['JS_merge_threshold']
        
        assert isinstance(self.number_of_walks, int), "Arg Error: number_of_walks must be of type int"
        assert isinstance(self.max_length, int), "Arg Error: max_length must be of type int"
        assert isinstance(self.use_sample_paths, bool), "Arg Error: use_sample_paths must be of type bool"
        assert isinstance(self.N_top, int), "Arg Error: N_top must be of type int"
        assert isinstance(self.HT_merge_threshold, (int,float)) and self.HT_merge_threshold > 0, "Arg Error: HT_merge_threshold must be a positive real number"
        
        
    def _setup_params(self, H):
        self._indices_to_nodes, self._nodes_to_indices = umat.get_node_mapping(H)
        self.sample_paths = defaultdict(lambda: [])
        
        return 

    def _get_source_node(self):
        """
        Gets a source node from a hypergraph from which to start running random walks
        by randomly selecting a node from the hypergraph.

        :param H: the hypergraph to get the source node from
        :returns: the ID of the source node
        """
        #TODO: change this so that it uses a more sensible criterion than a random selection?
        return np.random.choice(list(self._nodes_to_indices.keys()))
    
    def _get_next_node(self, H, current_node, call=0):
        """
        Give the current node, v_{i}, randomly chooses the next node in the
        random walk by first randomly choosing a hyperedge e from the set
        E_{i} of hyperedges that are incident to i, and then randomly choosing
        j from among the nodes that are connected to e (excluding i)

        :param H: The hypergraph on which to perform the random walk
        :param current_node_idx: The index of the currently selected node

        :returns next_node_idx: The index of the next node in the random walk
        """

        #1) Find hyperedges that the node is a member of
        node_hyperedge_ids = H.get_star(current_node)
        #2) Select a hyperedge uniformly at random
        hyperedge_id = np.random.choice(tuple(node_hyperedge_ids))
        hyperedge = H.get_hyperedge_nodes(hyperedge_id)
        #to guarantee transitioning to a different node we remove the current node from the possibilities
        hyperedge.remove(current_node) 
        #3) Select a node at random from that hyperedge
        if len(hyperedge) == 0:
            #If the hyperedge is a singleton set of just the current node, then try again
            call += 1
            if call <= 10:
                return self._get_next_node(H, current_node, call = call)
            else:
                raise RuntimeError('Got stuck at node {} when trying to run random walk.'.format(current_node))
        else:
            #else select the next node at random
            next_node = np.random.choice(tuple(hyperedge))

        return next_node, hyperedge_id

    def _cluster_nodes_by_truncated_hitting_times(self, node_list):
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

            if (t_new - t_old) <= self.HT_merge_threshold:
                t_old = t_new
            else:
                #append the cluster A_{k} to the list of clusters
                node_clusters.append(cluster)
                cluster = []
        
        if len(cluster) > 0:
            node_clusters.append(cluster)
            
        
        return node_clusters

    def _cluster_nodes_by_path_symmetry(self, node_list):
        """
        Clusters a list of nodes into groups based on the path symmetries using 
        greedy agglomerative clustering as follows:

        Two nodes are approximated as symmetrical if their distributions of stored
        paths are similar. Since the most frequently appearing paths are more repre-
        sentative of a distribution, we only use the top Ntop paths in each node. 
        Path similarity is measured using Jensen-Shannon divergence. 
        Each node starts in its own cluster. At each step, we merge the pair of 
        clusters whose path distributions are most similar. When there is more than
        one node in a cluster, its path distribution is the average over those of its nodes. 
        The clustering stops when no pair of clusters have divergence less than θjs.
        """

        node_clusters = [[node] for node in node_list]
        node_paths = [node.get_Ntop_paths(self.N_top) for node in node_list]
        mergeOccurred = True
        max_div = float('inf')
        
        while mergeOccurred:
            mergeOccurred = False
            best_pair = [-1,-1]
            smallestDiv = max_div
            for i in range(len(node_paths)):
                for j in range(i + 1, len(node_paths)):
                    JSdiv = node_utils.compute_jenson_shannon_divergence(node_paths[i],node_paths[j])
                    if JSdiv < smallestDiv and JSdiv < self.JS_merge_threshold:
                        smallestDiv = JSdiv
                        best_pair[0] = i
                        best_pair[1] = j

            if smallestDiv < max_div:
                mergeOccurred = True
                i = best_pair[0]
                j = best_pair[1]
                node_clusters[i].extend(node_clusters[j])
                del node_clusters[j]
                node_paths[i] = node_utils.merge_node_paths(node_paths[i], node_paths[j])
                del node_paths[j]

        return node_clusters

    def _cluster_nodes(self, H):
        node_list = H.node_name_to_node_object.values()
        truncated_hitting_time_clusters = self._cluster_nodes_by_truncated_hitting_times(node_list)

        if self.use_sample_paths:
            final_clusters = []
            for node_cluster in truncated_hitting_time_clusters:
                final_clusters.extend(self._cluster_nodes_by_path_symmetry(node_cluster))
            
        else:
            final_clusters = truncated_hitting_time_clusters
        
        single_nodes, node_clusters = get_single_nodes_and_node_clusters(final_clusters)

        return single_nodes, node_clusters

    def _run_walk_from_source_node(self, H, walk, source_node):
        if self.use_sample_paths: sample_path = []
        for step in range(self.max_length):
            if step == 0:
                current_node = source_node
        
            #make a random step using the transition matrix
            next_node, next_hyperedge_id = self._get_next_node(H, current_node)
            
            if self.use_sample_paths:
                #update the sample paths
                sample_path.append(str(step))
                sample_path.append(next_hyperedge_id)

            node_obj = H.node_name_to_node_object[next_node]
            
            current_node = next_node

            #update node properties if its a first visit
            if node_obj.first_visit:
                node_obj.update_ave_hitting_time(hitting_time = step, walk_number = walk)
                if self.use_sample_paths:
                    node_obj.update_sample_paths(path = sample_path.copy())
                node_obj.first_visit = False

        H.update_nodes(max_length = self.max_length, walk_number = walk)

    def run_random_walks(self, H):
        """
        Runs random walks on the hypergraph H to cluster nodes based on 
        a merge criterion (either truncated_hitting_time (if use_sample_paths = False) 
        or truncated_hitting_time combined with path JS_divergence (if use_sample_paths = True)).

        :param: H (Hypergraph) - the hypergraph to run random walks on
        :returns: Community object of the hypergraph's node clusters
        """
        self._setup_params(H)

        #get the source node for the random walk
        source_node = self._get_source_node()

        #use transition matix to run random walks
        for walk in range(1, self.number_of_walks + 1):
            self._run_walk_from_source_node(H, walk, source_node)

        #cluster nodes based on their symmetry properties
        single_nodes, node_clusters = self._cluster_nodes(H)

        return Community(single_nodes=single_nodes, node_clusters=node_clusters, source_node=source_node, hypergraph=H)
       
        



        
        




        