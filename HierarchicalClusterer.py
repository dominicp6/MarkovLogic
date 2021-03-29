import numpy as np
import warnings
import math
import cynetworkx as nx
from scipy.linalg import eigh
from sklearn.cluster import KMeans
from collections import OrderedDict


class HierarchicalClusterer(object):
    """
    A class to perform hierarchical clustering on a weighted, undirected graph
    using the MakeTree algorithm and spectral bi-partitioning based
    on the eigenvalues of the random walk Laplacian matrix.

    [1] MakeTree Algorithm              - A Cost Function For Similarity-Based Hierarchical Clustering, Dashupta S. (2015) arXiv:1510.05043
    [2] Spectral Partitioning Algorithm - Normalized Cuts and Image Segmentation, Malik J. and Shi J. (2000), IEEE
    
    For a comprehensive introduction to the topic of spectral clustering see:
    [3] A Tutorial On Spectral Clustering, von Luxburg U. (2007) arXiv:0711.0189

    :param stop_criterion: specifies the stop criterion for when to stop clustering. The options are:  
                           'eigenvalue' - stop partitioning a cluster when the value of the second 
                                          smallest eigenvalue of the cluster's Laplace matrix falls
                                          below a specified value
                           'tree_height' - run the full hierarchical clustering down to singleton
                                          leaf nodes and then output graph clusters from a specified
                                          height in the hierarchical clustering tree
                           'cluster_size' - stop partitioning a cluster when the number of nodes in
                                          the partitioned cluster would below a specified size
    :param min_eigval2 (float): [Only if stop criteiron is 'eigenvalue'] The minimum value of the second 
                        smallest eigenvalue of the Laplace matrix for when to stop partitioning
    :param tree_output_height (int): [Only if stop criterion is 'tree_height'] The height in the hierarchical
                               clustering tree from which to output the final node clusters, e.g. height of 0 
                               would output only leaf nodes.
    :param min_cluster_size (int): [Only if stop criterion is 'cluster_size'] The minimum cluster size
                             of the final output node clusters
    :param n_init (int): [K-means hyperparameter] The number of times the k-means algorithn will be run
                    with different centroid seeds. The final result will be the best output of 
                    n_init consecutive runs in terms of inertia
    :param max_iter (int): [K-means hyperparameter] The maximum number of iterations of the k-means algorithm
                    for a single run
    TODO:
    :param clusters_per_partition (int): The number of cluster splits to make at each stage of the hierarchical
                    clustering (default is 2, i.e. a bi-partitioning)
    """

    def __init__(self, stop_criterion = 'eigenvalue', min_eigval2 = 0.01, tree_output_depth = 1,
                            min_cluster_size = 1, n_init = 10, max_iter = 300, clusters_per_partition = 2):
        
        assert stop_criterion in ['eigenvalue', 'cluster_size', 'tree_depth'], "Arg Error: stop_criterion must be one of 'eigenvalue', 'cluster_size', 'tree_depth'"
        assert min_eigval2 > 0, "Arg Error: min_eigval2 must be a positive real number"
        assert isinstance(tree_output_depth, int) and tree_output_depth >= 1, "Arg Error: tree_output_depth must be a positive integer"
        assert isinstance(min_cluster_size, int) and min_cluster_size >= 1, "Arg Error: min_cluster size must be a positive integer"
        assert isinstance(n_init, int) and n_init > 0, "Arg Error: n_init must be a positive integer"
        assert isinstance(max_iter, int) and max_iter > 0, "Arg Error: max_iter must be a positive integer"
        assert isinstance(clusters_per_partition, int) and clusters_per_partition >= 2, "Arg Error: clusters_per_partition must be a positive integer bigger than 1"
        
        self.stop_criterion = stop_criterion
        self.min_eigval2 = min_eigval2
        self.tree_output_depth = tree_output_depth
        self.min_cluster_size = min_cluster_size
        self.n_init = n_init
        self.max_iter = max_iter
        self.clusters_per_partition = clusters_per_partition

        self._hierarchical_clustering_tree = OrderedDict()
        self._banned_positions = set()

    def laplace_RW_spectrum(self, G):
        """
        For a graph G, solves the generalised eigenvalue problem:
        Lu = wDu
        where L = D - W is the Laplacian matrix of the graph,
              D_{ii} = \sum_{j} W_{ij} is a diagonal matrix
              W_{ij} is the weight between the ith and jth node in G
              u is an eigenvector 
              w is an eigenvalue
        
        Note that w, the generalised eigevectors of L, also correspond 
        to the eigenvectors of the so-called random walk Laplacian, L_{RW}
        where L_{RW} = D^{-1}L = I - D^{-1}W 
        
        Part of the Shi and Malik spectral clustering algorithm (refs: [2],[3])

        Ouputs the n smallest eigenvectors and eigenvalues where 
        n is the clusters_per_partition used for the Hierarchcical 
        clustering (=2 by default)
        """

        #compute graph matrices
        W = nx.adjacency_matrix(G).todense()
        D = np.diagflat(np.sum(W, axis=1))
        L = nx.laplacian_matrix(G)
        
        #solve the generalised eigenvalue problem
        w,v = eigh(L.todense(),D, eigvals=(0,1))
        return w,v

    def create_subgraph(self, G, subgraph_nodes):
        """
        Constructs a subgraph (SG) from a graph (G), where the nodes
        of the subgraph are subgraph_nodes (a subset of the nodes 
        of G)
        """
        SG = G.__class__()
        if len(subgraph_nodes) > 1:
            SG.add_edges_from((n, nbr, d)
                for n, nbrs in G.adj.items() if n in subgraph_nodes
                for nbr, d in nbrs.items() if nbr in subgraph_nodes)
        else:
            SG.add_node(subgraph_nodes[0])
        SG.graph.update(G.graph)
        return SG

    def bipartition(self, G):
        """
        Takes a graph G as input and splits it into two clusters using 
        a spectral partitioning algorithm
        """
        split_again = True
        
        #get the graph nodes
        nodes = np.array(G.nodes())

        #If stopping based on cluster size, don't split if the number of 
        #nodes in the graph is smaller than min_cluster_size
        if self.stop_criterion == 'cluster_size' and len(nodes) < self.min_cluster_size:
            split_again = False
            return G, None, split_again

        #Shi and Malik clustering, refs: [2],[3]
        #get the L_{RW} spectrum of G by solving the generalised eigenvalue problem
        #NB: number of graph nodes = number of eigenvectors
        w,U = self.laplace_RW_spectrum(G)

        #If stopping based on eigenvalue, don't split if the second smallest 
        #eigenvalue is below the minimum threshold
        if self.stop_criterion == 'eigenvalue' and w[1] < self.min_eigval2:
            split_again = False
            return G, None, split_again

        #k means cluster the ordered eigenvectors 
        kmeans = KMeans(init="random", n_clusters=2, n_init=self.n_init, max_iter=self.max_iter).fit(U)
        labels = kmeans.labels_
        
        #find the indices of the nodes in each cluster
        C1 = np.where(labels == 1)[0]
        C2 = np.where(labels == 0)[0]

        #get the node labels from the indices
        N1 = [nodes[i] for i in C1]
        N2 = [nodes[i] for i in C2]

        #create subgraphs from the node sets
        G1 = self.create_subgraph(G, N1)
        G2 = self.create_subgraph(G, N2)

        return G1, G2, split_again

    def make_tree(self, G, depth=0, position = ''):
        """
        A recursive function with constructs the hierarchical clustering tree 
        """

        if G.order() == 0 or G.order() == 1:
            #if the graph has no nodes / one node then no need to 
            #proceed further with hierarchical clustering
            pass
        else:
            #partition the graph
            G1, G2, split_again = self.bipartition(G)
            #if split again then recursively call the make_tree algorithm
            if split_again:
                #only further split if the graphs are not already singleton node sets
                if G1.order() > 1 and G2.order() > 1:
                    #increment the depth of the hierarhcial clustering tree
                    depth += 1
                    
                    #If stop criterion is 'tree_depth', then only continue splitting if we have not exceeded tree_output_depth
                    if self.stop_criterion in ['eigenvalue', 'cluster_size'] or self.stop_criterion == 'tree_depth' and depth <= self.tree_output_depth:
                        #Add the left-split graph to the clusters dict and split again
                        print('Adding left graph {}'.format(position+'0'))
                        self._hierarchical_clustering_tree[position + '0'] = G1
                        self.make_tree(G1, depth = depth, position = position + '0')
                        #If the right-split graph is not in banned positions, then add the right-split graph to the clusters dict and split again
                        if position + '1' not in self._banned_positions:
                            print('Adding right graph {}'.format(position+'1'))
                            self._hierarchical_clustering_tree[position + '1'] = G2
                            self.make_tree(G2, depth = depth, position = position + '1')
            else:
                #if we are not splitting again then this means that the 
                #graph didn't satisfy our criteria for keeping it in the
                #hierarchical clustering tree, so we remove it and its 
                #sibling from the tree

                #if it was a right-split graph then we can remove its left-split sibling which is already in the clusters dict
                if position[-1] == '1':
                    banned_sibling = position[:-1] + '0'
                    print('Deleting banned sibling {}'.format(banned_sibling))
                    del self._hierarchical_clustering_tree[banned_sibling]
                #if it was a left-split graph then add the right-split position to the banned siblings list
                else:
                    banned_sibling = position[:-1] + '1'
                    print('Adding banned sibling {}'.format(banned_sibling))
                    self._banned_positions.add(banned_sibling)

                #delete the graph from the clusters dict
                print('Deleting graph {}'.format(position))
                del self._hierarchical_clustering_tree[position]


    def get_leaf_nodes(self):
        """
        Extracts the leaf nodes from the Hierarchical clustering tree
        """
        leaf_nodes = dict()
        for position, cluster in self._hierarchical_clustering_tree.items():
            leaf_nodes[position] = cluster
            if position[:-1] in leaf_nodes.keys():
                del leaf_nodes[position[:-1]]

        return leaf_nodes.values()

    def hierarchical_clustering(self, G):
        """
        Hierarchical cluster a graph G
        """

        #Get the number of nodes in the graph
        num_nodes = G.number_of_nodes()
        
        assert self.min_cluster_size < num_nodes, "Arg Error: min_cluster_size ({}) must be an integer smaller than the number of nodes in the graph ({})".format(self.min_cluster_size, num_nodes)

        if self.stop_criterion == 'tree_depth' and self.tree_output_depth > math.log(num_nodes, self.clusters_per_partition):
            warnings.warn("Arg Warning: tree_output_depth is likey larger than the maximum possible for this graph")
        
        #Run hierarchical clustering on the graph
        self.make_tree(G)

        leaf_nodes = self.get_leaf_nodes()

        #Reset properties
        self._hierarchical_clustering_tree = OrderedDict()
        self._banned_positions = set()

        return leaf_nodes