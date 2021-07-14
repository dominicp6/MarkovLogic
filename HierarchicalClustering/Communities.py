from multiprocessing import Pool, cpu_count
from RandomWalker import RandomWalker
from clustering_nodes_by_path_similarity import *
from GraphObjects import Hypergraph
from errors import check_argument


class Communities(object):

    def __init__(self, hypergraph: Hypergraph,
                 config: dict,
                 num_walks=None,
                 walk_length=None,
                 theta_hit=None,
                 theta_sym=None,
                 theta_js=None,
                 num_top_paths=None):

        """
        Generates the communities associated with a hypergraph.

        Each node of a hypergraph has a community associated with it. A community is a collection
        of 'single nodes' and 'node clusters'. Node clusters are groups of nodes which have similar symmetry
        properties with respect to the source node (i.e. similar truncated hitting times and similar distributions
         of paths). A node is called a 'single node' if its node cluster contains only itself. Nodes can only be in
        the same cluster if they are of the same type.

        Config parameters:
            epsilon, number_of_paths, max_num_paths, max_path_length, k, alpha_sym (see RandomWalker.py for details)
            theta_p: the desired significance level for testing the null hypothesis of nodes being path symmetric
                     when clustering by JS divergence of by birch clustering on PCA path-count features. Smaller values
                     of theta_p give fewer clusters.
            pca_dim: the desired dimension of the path-count feature vectors after dimensionality reduction with PCA
            clustering_method_threshold: the threshold cluster size at which birch clustering on PCA path-count features
                     is used instead of clustering based on JS divergence (slower for large clusters)

        """

        self._check_arguments(config)

        self.theta_hit = theta_hit
        self.theta_sym = theta_sym
        self.theta_js = theta_js
        self.num_top_paths = num_top_paths

        self.hypergraph = hypergraph
        if hypergraph.diameter is None:
            print(f"Warning: Graph of the hypergraph not known. Reverting to using default length of random "
                  f"walks.")

        self.random_walker = RandomWalker(hypergraph=hypergraph,
                                          config=config,
                                          num_walks=num_walks,
                                          walk_length=walk_length)

        self.communities = {}

        if config['multiprocessing']:
            pool = Pool(processes=cpu_count())
            communities = pool.starmap_async(self.get_community, [(node, config) for node in hypergraph.nodes.keys()
                                                                  if hypergraph.is_source_node[node]]).get()
            self.communities = {community.source_node: community for community in communities}
        else:
            self.communities = {node: self.get_community(source_node=node, config=config) for node in
                                hypergraph.nodes.keys() if hypergraph.is_source_node[node]}

    def __str__(self):
        output_string = ''
        for community_id, community in enumerate(self.communities.values()):
            output_string += f'COMMUNITY {community_id + 1} \n' + community.__str__()

        return output_string

    def get_community(self, source_node: str, config: dict):
        random_walk_data = self.random_walker.generate_node_random_walk_data(source_node=source_node)

        # remove the source node from the random_walk_data and add it to the set of single nodes
        del random_walk_data[source_node]
        single_nodes = {source_node}
        clusters = []

        theta_sym = self._get_theta_sym(config)

        close_nodes = self._get_close_nodes(random_walk_data)

        single_nodes_of_node_type = dict()
        for node_type in self.hypergraph.node_types:
            nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
            if nodes_of_type:
                single_nodes_of_type, clusters_of_type = \
                    cluster_nodes_by_path_similarity(nodes=nodes_of_type,
                                                     number_of_walks=self.random_walker.number_of_walks_ran,
                                                     theta_sym=theta_sym,
                                                     config=config,
                                                     theta_js=self.theta_js,
                                                     num_top_paths=self.num_top_paths)
                single_nodes_of_node_type[node_type] = single_nodes_of_type
                clusters.extend(clusters_of_type)

        single_nodes_remaining_after_pruning = prune_nodes(single_nodes_of_node_type, config['pruning_value'])
        single_nodes.update(single_nodes_remaining_after_pruning)

        community = Community(source_node, single_nodes, clusters)

        return community

    def _get_close_nodes(self, random_walk_data):
        if self.theta_hit is None:
            close_nodes = get_close_nodes_based_on_path_count(random_walk_data)
        else:
            close_nodes = get_close_nodes_based_on_truncated_hitting_time(random_walk_data, self.theta_hit)
        return close_nodes

    def _get_theta_sym(self, config):
        if self.theta_sym is None:
            theta_sym = compute_theta_sym(config['theta_p'],
                                          self.random_walker.number_of_walks_ran,
                                          self.random_walker.length_of_walk)
        else:
            theta_sym = self.theta_sym

        return theta_sym

    @staticmethod
    def _check_arguments(config):
        check_argument('epsilon', config['epsilon'], float, 0, 1)
        check_argument('max_num_paths', config['max_num_paths'], int, 0)
        check_argument('pca_dim', config['pca_dim'], int, 2, strict_inequalities=False)
        check_argument('clustering_method_threshold', config['clustering_method_threshold'], int, 4,
                       strict_inequalities=False)
        check_argument('max_path_length', config['max_path_length'], int, 0)
        check_argument('theta_p', config['theta_p'], float, 0, 1)
        check_argument('multiprocessing', config['multiprocessing'], bool)
        if config['pruning_value'] is not None:
            check_argument('pruning_value', config['pruning_value'], int, 0)


class Community(object):

    def __init__(self, source_node: str, single_nodes: set[str], clusters: list[set[str]]):
        self.source_node = source_node
        self.single_nodes = single_nodes
        self.clusters = clusters
        self.nodes_in_clusters = set().union(*self.clusters)
        self.nodes = self.single_nodes.union(self.nodes_in_clusters)

        self.number_of_clusters = len(clusters)
        self.number_of_single_nodes = len(self.single_nodes)
        self.number_of_nodes_in_clusters = len(self.nodes_in_clusters)
        self.number_of_nodes = len(self.nodes)

    def __len__(self):
        return self.number_of_nodes

    def __str__(self):
        output_str = ''
        source_str = f"SOURCE: {self.source_node}\n ---------------------------- \n"
        single_nodes_str = "".join([f"SINGLE: {node}\n" for node in self.single_nodes])
        clusters_str = ""
        for cluster_id, cluster in enumerate(self.clusters):
            clusters_str += f"CLUSTER {cluster_id}: \n"
            clusters_str += "".join([f"        {node}\n" for node in cluster])

        output_str += source_str + single_nodes_str + clusters_str + "\n"

        return output_str
