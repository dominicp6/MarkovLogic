import numpy as np
import warnings
import math
import networkx as nx
from scipy import sparse
from sklearn.cluster import KMeans
from collections import OrderedDict
import halp.utilities.undirected_matrices as umat
from halp.algorithms.undirected_partitioning import _compute_normalized_laplacian as compute_normalized_laplacian
import graph_utils as graph_util
from Hypergraph import Hypergraph


class HierarchicalClusterer(object):
    """
    A class to perform hierarchical clustering on either a weighted, undirected graph
    or a weighted, undirected hypergraph.

    -------------------------------------------------------------------------------------------------
    If clustering on a graph we use the MakeTree algorithm and spectral bi-partitioning based
    on the eigenvalues of the random walk Laplacian matrix:

    [1] MakeTree Algorithm              - "A Cost Function For Similarity-Based Hierarchical Clustering", Dashupta S. (2015) arXiv:1510.05043
    [2] Spectral Partitioning Algorithm - "Normalized Cuts and Image Segmentation", Malik J. and Shi J. (2000), IEEE
    
    For a comprehensive introduction to the topic of spectral clustering see:
    [3] A Tutorial On Spectral Clustering, von Luxburg U. (2007) arXiv:0711.0189
    -------------------------------------------------------------------------------------------------
    If clustering on a hypergraph we use the MakeTree algorithm and the Normalized Hypergraph
    Cut algorithm for hypergraphs, a generalization of the graph-based spectral bi-partitioning
    algorithm:

    [4] Normalized Hypergraph Cut       - “Learning with hypergraphs: Clustering, classification, and embedding.” Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.  Advances in neural information processing systems. (2006)
    -------------------------------------------------------------------------------------------------

    GENERIC PARAMETERS:
    :param stop_criterion: specifies the stop criterion for when to stop clustering. The options are:  
                           'eigenvalue' - stop partitioning a cluster when the value of the second 
                                          smallest eigenvalue of the cluster's Laplace matrix falls
                                          below a specified value
                           'tree_height' - run the full hierarchical clustering down to singleton
                                          leaf nodes and then output graph clusters from a specified
                                          height in the hierarchical clustering tree
                           'cluster_size' - stop partitioning a cluster when the number of nodes in
                                          the partitioned cluster would below a specified size
    :param min_ssev (float): [Only if stop criteiron is 'eigenvalue'] The minimum value of the second 
                        smallest eigenvalue of the Laplace matrix for when to stop partitioning
    :param tree_output_height (int): [Only if stop criterion is 'tree_height'] The height in the hierarchical
                               clustering tree from which to output the final node clusters, e.g. height of 0 
                               would output only leaf nodes.
    :param min_cluster_size (int): [Only if stop criterion is 'cluster_size'] The minimum cluster size
                             of the final output node clusters

    PARAMETERS FOR HIERARCHICAL CLUSTERING OF GRAPHS
    :param n_init (int): [K-means hyperparameter] The number of times the k-means algorithn will be run
                    with different centroid seeds. The final result will be the best output of 
                    n_init consecutive runs in terms of inertia (default 10)
    :param max_iter (int): [K-means hyperparameter] The maximum number of iterations of the k-means algorithm
                    for a single run (default 300)

    PARAMETERS FOR HIERARCHICAL CLUSTERING OF HYPERGRAPHS
    :param threshold (float): The second smallest eigenvalue threshold value for the Normalized Hypergraph Cut 
                              algorithm. 
    :param max_fractional_size (float): Hypergraph splitting stops either either of the partitioned hypergraphs
    have more than max_fractional_size number of nodes compared to the original input hypergraph
    """

    def __init__(self, config):

        #Suggested default parameter values
        #----------------------------------
        # stop_criterion = 'eigenvalue', 
        # min_ssev = 0.01, 
        # tree_output_depth = 1,
        # min_cluster_size = 1, 
        # n_init = 10, 
        # max_iter = 300, 
        # threshold = 0.01, 
        # max_fractional_size = 0.9

        self.stop_criterion = config['stop_criterion']
        self.min_ssev = config['min_ssev']
        self.tree_output_depth = config['tree_output_depth']
        self.min_cluster_size = config['min_cluster_size']
        self.n_init = config['n_init']
        self.max_iter = config['max_iter']
        self.threshold = config['threshold']
        self.max_fractional_size = config['max_fractional_size']
        
        assert self.stop_criterion in ['eigenvalue', 'cluster_size', 'tree_depth'], "Arg Error: stop_criterion must be one of 'eigenvalue', 'cluster_size', 'tree_depth'"
        assert self.min_ssev > 0, "Arg Error: min_ssev must be a positive real number"
        assert isinstance(self.tree_output_depth, int) and self.tree_output_depth >= 1, "Arg Error: tree_output_depth must be a positive integer"
        assert isinstance(self.min_cluster_size, int) and self.min_cluster_size >= 1, "Arg Error: min_cluster size must be a positive integer"
        assert isinstance(self.n_init, int) and self.n_init > 0, "Arg Error: n_init must be a positive integer"
        assert isinstance(self.max_iter, int) and self.max_iter > 0, "Arg Error: max_iter must be a positive integer"
        assert isinstance(self.threshold, (int, float)), "Arg Error: threshold must be a real number"
        assert isinstance(self.max_fractional_size, float) and self.max_fractional_size < 1 and self.max_fractional_size > 0, "Arg Error: max_fractional_size must be a number between 0 and 1"

        self._original_hypergraph = None
        self._hierarchical_clustering_tree = OrderedDict()
        self._banned_positions = set()
        self._most_recent_ssev = 0
        self._most_recent_cluster_sizes = []
        self._most_recent_graph_size = 0
        self._clusters_too_big = False

    def diagnose_no_partition_error(self):
        """
        Determines plausible reasons why the hierarchical clustering 
        terminated prematurely and suggest how the user should change
        hyperparameters accordingly.
        """
        if self._clusters_too_big == True:
            self._clusters_too_big = False
            print('max_fractional_size = {} but after one split the two hypergraphs were fractional size {} and {} of the original'.format(self.max_fractional_size, round(self._most_recent_cluster_sizes[0]/self._most_recent_graph_size,2), round(self._most_recent_cluster_sizes[1]/self._most_recent_graph_size,2)))
        elif self.stop_criterion == 'eigenvalue':
            print('min_ssev = {} but the parent graph had second smallest eigenvalue ssev = {}'.format(self.min_ssev,round(self._most_recent_ssev,3)))
        elif self.stop_criterion == 'cluster_size':
            print('min_cluster_size = {} but after one split the clusters are size {} and {}'.format(self.min_cluster_size, *self._most_recent_cluster_sizes))
        elif self.stop_criterion == 'tree_depth':
            raise NotImplementedError
        else:
            raise NotImplementedError

        raise RuntimeError('Stop criterion automatically satisfied for the original hypergraph: no splitting occurred')
    
    def normalized_hypergraph_cut(self, H):
        """Executes the min-cut algorithm described in the paper:
        Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
        "Learning with hypergraphs: Clustering, classification, and embedding."
        Advances in neural information processing systems. 2006.
        (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

        This algorithm uses the normalized Laplacian to partition the hypergraph
        into two disjoint components.

        :param H: the hypergraph to perform the hypergraph-cut algorithm on.
        :returns: H1 -- the hypergraph derived from the nodes of the first partition
                  H2 -- the hypergraph derived from the nodes of the second partition
                  split_again (bool) -- whether or not to continue splitting the 
                  hypergraph based on the second smallest eigenvalue criterion 
                  (always 'True' for this algorithm)
        """
        split_again = True
        self._most_recent_graph_size = H.number_of_nodes()

        # Get index<->node mappings and index<->hyperedge_id mappings for matrices
        _, nodes_to_indices = umat.get_node_mapping(H)
        _, hyperedge_ids_to_indices = umat.get_hyperedge_id_mapping(H)

        delta = compute_normalized_laplacian(H,
                                            nodes_to_indices,
                                            hyperedge_ids_to_indices)

        eigenvalues, eigenvectors = np.linalg.eig(delta.todense())

        second_min_index = np.argsort(eigenvalues)[1]
        self._most_recent_ssev = np.real(eigenvalues[second_min_index])
        
        #If stopping based on eigenvalue, don't split if the second smallest 
        #eigenvalue is below the minimum threshold
        if self.stop_criterion == 'eigenvalue' and self._most_recent_ssev < self.min_ssev:
            split_again = False
            return H, None, split_again

        second_eigenvector = eigenvectors[:, second_min_index]
        partition_index = [i for i in range(len(second_eigenvector))
                        if second_eigenvector[i] >= self.threshold]

        S1, S2 = set(), set()
        for key, value in nodes_to_indices.items():
            if value in partition_index:
                S1.add(key)
            else:
                S2.add(key)

        H1 = self._original_hypergraph.convert_to_hypergraph(S1)
        H2 = self._original_hypergraph.convert_to_hypergraph(S2)

        self._most_recent_cluster_sizes = [H1.number_of_nodes(), H2.number_of_nodes()]
        
        #Don't split again if either of the resulting hypergraphs have more than
        #self.max_fractional_size of the number of nodes of the original
        if H1.number_of_nodes() >= self.max_fractional_size * H.number_of_nodes() or H2.number_of_nodes() >= self.max_fractional_size * H.number_of_nodes():
            split_again = False
            self._clusters_too_big = True

        return H1, H2, split_again

    def normalized_graph_cut(self, G):
        """
        Implements the spectral bipartitioning algorithm from:
        "Normalized Cuts and Image Segmentation", Malik J. and Shi J. (2000), IEEE
        (https://people.eecs.berkeley.edu/~malik/papers/SM-ncut.pdf)

        The algorithm uses the normalized Laplacian to partition a graph into
        two disjoint components.

        :param G: graph to perform the spectral bipartitioning on
        :returns: G1 -- the graph derived from the nodes of the first partition
                  G2 -- the graph derived from the nodes of the second partition
                  split_again (bool) -- whether or not to continue splitting the 
                  graph based on the second smallest eigenvalue criterion 
        """
        split_again = True
        self._most_recent_graph_size = G.number_of_nodes()

        #get the L_{RW} spectrum of G by solving the generalised eigenvalue problem
        #NB: number of graph nodes = number of eigenvectors
        w,U = graph_util.laplace_RW_spectrum(G)

        #update most recent second smallest eigenvalue
        self._most_recent_ssev = w[1]
        
        #If stopping based on eigenvalue, don't split if the second smallest 
        #eigenvalue is below the minimum threshold
        if self.stop_criterion == 'eigenvalue' and self._most_recent_ssev < self.min_ssev:
            split_again = False
            return G, None, split_again

        #k means cluster the ordered eigenvectors 
        #it is this stage of the algorithm that makes it stochastic
        kmeans = KMeans(init="random", n_clusters=2, n_init=self.n_init, max_iter=self.max_iter).fit(U)
        labels = kmeans.labels_
        
        #find the indices of the nodes in each cluster
        C1 = np.where(labels == 1)[0]
        C2 = np.where(labels == 0)[0]

        #get the node labels from the indices
        nodes = np.array(G.nodes())
        S1 = [nodes[i] for i in C1]
        S2 = [nodes[i] for i in C2]
        self._most_recent_cluster_sizes = [len(S1), len(S2)]

        #create subgraphs from the node sets
        G1 = graph_util.create_subgraph(G, S1)
        G2 = graph_util.create_subgraph(G, S2)

        return G1, G2, split_again

    def _partition(self, G):
        """
        Takes a graph/hypergraph G as input and splits it into two clusters using 
        a spectral partitioning algorithm / Normalized Hypergraph Cut respectively.

        :param G: input graph/hypergraph
        :returns: G1, G2 - the two graphs/hypergraphs resulting from the partitioning
                  split_again (bool) - whether or not to continue splitting again 
                  based on the cluster size of second smallest eigenvalue criterion.
        """
        number_of_nodes = G.number_of_nodes()
        #If stopping based on cluster size, don't split if the number of 
        #nodes in the graph/hypergraph is smaller than min_cluster_size
        if self.stop_criterion == 'cluster_size' and number_of_nodes < self.min_cluster_size:
            split_again = False
            return G, None, split_again
        
        if isinstance(G, nx.Graph):
            G1, G2, split_again = self.normalized_graph_cut(G)
        elif isinstance(G, Hypergraph):
            G1, G2, split_again = self.normalized_hypergraph_cut(G)
        else:
            raise ValueError('Input must be either of type Graph or EnhancedUndirectedGraph')

        return G1, G2, split_again        

    def _remove_from_tree(self, position):
        """
        Removes a graph/hypergraph and its sibling from the hierarchical 
        clustering tree if it did not satisfy the criterion to be split further.

        :param position: the position of the graph/hypergraph in the tree to be removed.
        """
        #if it was a right-split graph then we can remove its left-split sibling which is already in the clusters dict
        if position[-1] == '1':
            banned_sibling = position[:-1] + '0'
            #print('Deleting banned sibling {}'.format(banned_sibling))
            del self._hierarchical_clustering_tree[banned_sibling]
        #if it was a left-split graph then add the right-split position to the banned siblings list
        else:
            banned_sibling = position[:-1] + '1'
            #print('Adding banned sibling {}'.format(banned_sibling))

        self._banned_positions.add(banned_sibling)
        #delete the graph from the clusters dict
        del self._hierarchical_clustering_tree[position]

    def _make_tree(self, G, depth=0, position = ''):
        """
        A recursive function which constructs the hierarchical clustering tree
        of a graph or hypergraph.

        :param depth (int): the previous depth reached in the hierarchical 
                            clustering tree
        :param position (str): the position of the cluster just added to the
                            (binary) tree (encoded as a binary string).
        """

        if G.number_of_nodes() == 0 or G.number_of_nodes() == 1:
            #if the graph has no nodes / one node then no need to F
            #proceed further with hierarchical clustering
            pass
        else:
            #partition the graph
            G1, G2, split_again = self._partition(G)
            #if split again then recursively call the make_tree algorithm
            if split_again:
                #only further split if the graphs are not already singleton node sets
                if G1.number_of_nodes() > 1 and G2.number_of_nodes() > 1:
                    #increment the depth of the hierarhcial clustering tree
                    depth += 1
                    #If stop criterion is 'tree_depth', then only continue splitting if we have not exceeded tree_output_depth
                    if self.stop_criterion in ['eigenvalue', 'cluster_size'] or self.stop_criterion == 'tree_depth' and depth <= self.tree_output_depth:
                        #Add the left-split graph to the tree and split again
                        new_position = position + '0'
                        self._hierarchical_clustering_tree[new_position] = G1
                        self._make_tree(G1, depth = depth, position = new_position)
                        #If the right-split graph is not in banned positions, then add the right-split graph to the tree and split again
                        if position + '1' not in self._banned_positions:
                            new_position = position + '1'
                            self._hierarchical_clustering_tree[new_position] = G2
                            self._make_tree(G2, depth = depth, position = new_position)
            elif depth != 0:
                self._remove_from_tree(position)
            else:
                #Hyperparameters are such that we have no splitting of the original graph
                #output an appropriate error message
                self.diagnose_no_partition_error()

    def _get_leaf_nodes(self):
        """
        Extracts just the leaf nodes from the hierarchical clustering tree.

        These leaf nodes constitue the final clusterings.
        """
        if len(self._hierarchical_clustering_tree) == 0:
            raise RuntimeError('Empty hierarchical clustering tree. Try again with different stop criteria.')
        
        leaf_nodes = dict()
        for position, cluster in self._hierarchical_clustering_tree.items():
            #if the position is not a descendent of a banned position then add it to the leaf nodes
            if not any(position.startswith(banned_position) for banned_position in self._banned_positions):
                leaf_nodes[position] = cluster
                #if a parent was in the leaf node set then remove it as it was not infact a leaf node
                if position[:-1] in leaf_nodes.keys():
                    del leaf_nodes[position[:-1]]

        return leaf_nodes

    def hierarchical_clustering(self, G):
        """
        Hierarchical cluster a graph/hypergraph G.

        :param: G (either Graph or EnhancedUndirectedGraph)
                - the object to run hierarchical clustering on
        :returns: list of leaf node graph/hypergraph objects obtained
                  after hierarchical clustering
        """
        if isinstance(G, nx.Graph):
            pass
        elif isinstance(G, Hypergraph):
            self._original_hypergraph = G
        else:
            raise ValueError('Input must be either of type Graph or EnhancedUndirectedGraph')

        #Get the number of nodes in the graph/hypergraph
        num_nodes = G.number_of_nodes()
        
        assert self.min_cluster_size < num_nodes, "Arg Error: min_cluster_size ({}) must be an integer smaller than the number of nodes in the graph/hypergraph ({})".format(self.min_cluster_size, num_nodes)

        if self.stop_criterion == 'tree_depth' and self.tree_output_depth > math.log(num_nodes, 2):
            warnings.warn("Arg Warning: tree_output_depth is likey larger than the maximum possible for this graph/hypergraph")
        
        #Construct the hierarchical clustering tree
        self._make_tree(G)

        #Extarct the leaf nodes from the hierachical clustering tree
        leaf_nodes = self._get_leaf_nodes()

        #Reset properties
        self._hierarchical_clustering_tree = OrderedDict()
        self._banned_positions = set()
        self._original_hypergraph = None

        return leaf_nodes.values()
