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
            epsilon      -  The maximum fractional error for the mean truncated hitting time.
                            Used to determine the number of random walks that need to be run from each source node.
            theta_hit    -  Threshold for the average truncated hitting time (ATHT). Nodes with larger ATHT are excluded
                            from the community.
            theta_sym    -  Threshold difference in ATHT for nodes to be considered as potentially symmetric.
            theta_js     -  Threshold difference in Jensen-Shannon divergence of path distributions for potentially
                            symmetric nodes to be clustered together.
            num_top      -  The num_top most frequent paths to consider when calculating the Jensen-Shannon divergence
                            between path distributions.
        """

        assert type(config['epsilon']) is float and 1 > config['epsilon'] > 0, "epsilon must be a positive float " \
                                                                               "between 0 and 1"
        assert type(config['theta_hit']) is float and config['theta_hit'] > 0, "theta_hit must be a positive float"
        assert type(config['theta_sym']) is float and config['theta_sym'] > 0, "theta_sym must be a positive float"
        assert type(config['theta_js']) is float and config['theta_js'] > 0, "theta_js must be a positive float"
        assert type(config['num_top']) is int and config['num_top'] > 0, "num_top must be a positive int"

        assert len(hypergraph.node_types) > 0, "Cannot generate communities for Hypergraph without typed nodes." \
                                               "To specify typing, regenerate the Hypergraph using a .info file."

        self.hypergraph = hypergraph
        if hypergraph.estimated_graph_diameter is None:
            print(f"Warning: Graph diameter of the hypergraph not known. Resulting to using default length of random "
                  f"walks.")

        self.communities = {}

        self.communities = {node.name: self.get_community(source_node=node, config=config) for node in
                            hypergraph.nodes() if node.is_source_node}

    def __str__(self):
        output_string = ''
        for community_id, community in enumerate(self.communities.values()):
            output_string += f'COMMUNITY {community_id + 1} \n' + community.__str__()

        return output_string

    def get_community(self, source_node: Node, config: dict):
        random_walk_data = generate_node_random_walk_data(self.hypergraph,
                                                          source_node=source_node,
                                                          epsilon=config['epsilon'])

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
