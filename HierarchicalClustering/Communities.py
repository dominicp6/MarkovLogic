from random_walks import generate_node_random_walk_data
from clustering_nodes_by_path_similarity import get_close_nodes, cluster_nodes_by_path_similarity
from GraphObjects import Hypergraph
from Node import Node


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
            num_walks    -  The number of random walks to run from each node.
            max_length   -  The maximum length of the random walks.
            theta_hit    -  Threshold for the average truncated hitting time (ATHT). Nodes with larger ATHT are excluded
                            from the community.
            theta_sym    -  Threshold difference in ATHT for nodes to be considered as potentially symmetric.
            theta_js     -  Threshold difference in Jensen-Shannon divergence of path distributions for potentially
                            symmetric nodes to be clustered together.
            num_top      -  The num_top most frequent paths to consider when calculating the Jensen-Shannon divergence
                            between path distributions.
        """

        assert type(config['num_walks']) is int and config['num_walks'] > 0, "num_walks must be a positive integer"
        assert type(config['max_length']) is int and config['max_length'] > 0, "max_length must be a positive integer"
        assert type(config['theta_hit']) is float and config['theta_hit'] > 0, "theta_hit must be a positive float"
        assert type(config['theta_sym']) is float and config['theta_sym'] > 0, "theta_sym must be a positive float"
        assert type(config['theta_js']) is float and config['theta_js'] > 0, "theta_js must be a positive float"
        assert type(config['num_top']) is int and config['num_top'] > 0, "num_top must be a positive int"

        self.hypergraph = hypergraph
        self.communities = {}

        for node in self.hypergraph.nodes():
            community = self.get_community(source_node=node, config=config)
            self.communities[node.name] = community

    def __str__(self):
        for community in self.communities.values():
            print(community)

    def get_community(self, source_node: Node, config: dict):

        random_walk_data = generate_node_random_walk_data(self.hypergraph, source_node=source_node,
                                                          number_of_walks=config['num_walks'],
                                                          max_path_length=config['max_length'])

        # remove the source node from the random_walk_data and add it to the set of single nodes
        del random_walk_data[source_node.name]
        single_nodes = {source_node.name}
        clusters = []

        close_nodes = get_close_nodes(random_walk_data, threshold_hitting_time=config['theta_hit'])

        for node_type in self.hypergraph.node_types:
            nodes_of_type = [node for node in close_nodes if node.node_type == node_type]
            if nodes_of_type:
                single_nodes_of_type, clusters_of_type = cluster_nodes_by_path_similarity(nodes_of_type, config)

                single_nodes.update(single_nodes_of_type)
                clusters.extend(clusters_of_type)

        community = Community(source_node.name, single_nodes, clusters)

        return community


class Community(object):

    def __init__(self, source_node: str, single_nodes: set[str], clusters: list[set[str]]):
        self.source_node = source_node
        self.single_nodes = single_nodes
        self.clusters = clusters
        self.number_of_single_nodes = len(single_nodes)
        self.number_of_cluster_nodes = sum([len(cluster) for cluster in clusters])
        self.number_of_clusters = len(clusters)
        self.number_of_nodes = self.number_of_single_nodes + self.number_of_cluster_nodes

    def __str__(self):
        output_str = ''
        source_str = f"SOURCE: {self.source_node}\n ---------------------------- \n"
        single_nodes_str = "".join([f"SINGLE: {node}\n" for node in self.single_nodes])
        clusters_str = ""
        for cluster_number, cluster in enumerate(self.clusters):
            clusters_str += f"CLUSTER {cluster_number}: \n"
            clusters_str += "".join([f"        {node}\n" for node in cluster])

        output_str += source_str + single_nodes_str + clusters_str + "\n"

        return output_str



