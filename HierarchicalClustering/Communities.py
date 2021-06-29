from multiprocessing import Pool, cpu_count
from RandomWalker import RandomWalker
from clustering_nodes_by_path_similarity import get_close_nodes, cluster_nodes_by_path_similarity
from GraphObjects import Hypergraph
import cProfile


class Communities(object):

    def __init__(self, hypergraph: Hypergraph, config: dict):

        """
        Generates the communities associated with a hypergraph.

        Each node of a hypergraph has a community associated with it. A community is a collection
        of 'single nodes' and 'node clusters'. Node clusters are groups of nodes which have similar symmetry
        properties with respect to the source node (i.e. similar truncated hitting times and similar distributions
         of paths). A node is called a 'single node' if its node cluster contains only itself. Nodes can only be in
        the same cluster if they are of the same type.

        Config parameters:
            epsilon      -  The maximum fractional error for the mean truncated hitting time.
                            Used to determine the number of random walks that need to be run from each source node.
            theta_hit    -  Threshold for the average truncated hitting time (ATHT). Nodes with larger ATHT are excluded
                            from the community.
            theta_sym    -  Threshold difference in ATHT for nodes to be considered as potentially symmetric.
            theta_js     -  Threshold difference in Jensen-Shannon divergence of path distributions for potentially
                            symmetric nodes to be clustered together.
            num_top      -  The num_top most frequent paths to consider when calculating the Jensen-Shannon divergence
                            between path distributions.
            TODO: write the other parameters
        """

        assert type(config['epsilon']) is float and 1 > config['epsilon'] > 0, "epsilon must be a positive float " \
                                                                               "between 0 and 1"
        assert type(config['max_num_paths']) is int and config[
            'max_num_paths'] > 0, "max_num_paths must be a positive integer"
        assert type(config['theta_hit']) is float and config['theta_hit'] > 0, "theta_hit must be a positive float"
        assert type(config['theta_sym']) is float and config['theta_sym'] > 0, "theta_sym must be a positive float"
        assert type(config['theta_js']) is float and config['theta_js'] > 0, "theta_js must be a positive float"
        assert type(config['pca_dim']) is int and config['pca_dim'] >= 2, "pca_dim must be an integer " \
                                                                          "greater than or equal to 2"
        assert type(config['k_means_cluster_size_threshold']) is int and config['k_means_cluster_size_threshold'] >= 4,\
            "k_means_cluster_size_threshold must be an integer greater than or equal to 4"
        assert type(config['k']) is float and config['k'] >= 1, "k must be a float greater than or equal to 1"
        assert type(config['max_path_length']) is int and config['max_path_length'] > 0, "max_path_length must be a" \
                                                                                         "positive integer"
        assert type(config['p_value']) is float and config['p_value'] > 0, "p_value must be a positive float"
        assert type(config['multiprocessing']) is bool

        self.hypergraph = hypergraph
        if hypergraph.estimated_graph_diameter is None:
            print(f"Warning: Graph diameter of the hypergraph not known. Reverting to using default length of random "
                  f"walks.")

        self.random_walker = RandomWalker(hypergraph=hypergraph, epsilon=config['epsilon'],
                                          k=config['k'], max_path_length=config['max_path_length'],
                                          number_of_paths=config['max_num_paths'])

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

        close_nodes = get_close_nodes(random_walk_data, threshold_hitting_time=config['theta_hit'])

        for node_type in self.hypergraph.node_types:
            nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
            if nodes_of_type:
                single_nodes_of_type, clusters_of_type = \
                    cluster_nodes_by_path_similarity(nodes=nodes_of_type,
                                                     number_of_walks=self.random_walker.number_of_walks_ran,
                                                     config=config)

                single_nodes.update(single_nodes_of_type)
                clusters.extend(clusters_of_type)

        community = Community(source_node, single_nodes, clusters)

        return community


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
