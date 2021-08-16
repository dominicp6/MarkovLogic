import numpy as np
from HierarchicalClustering.GraphObjects import Hypergraph
from HierarchicalClustering.NodeRandomWalkData import NodeClusterRandomWalkData
from HierarchicalClustering.RandomWalker import RandomWalker
from collections import defaultdict

from HierarchicalClustering.cluster_by_path_similarity import get_close_nodes_based_on_truncated_hitting_time, \
    get_close_nodes_based_on_path_count
from HierarchicalClustering.errors import check_argument
from HierarchicalClustering.probability_distance_metrics import sk_divergence, compute_average_distribution


def compute_divergence(node_cluster1: NodeClusterRandomWalkData,
                       node_cluster2: NodeClusterRandomWalkData,
                       number_of_walks=1000,
                       number_of_top_paths=None,
                       ):
    p = node_cluster1.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    q = node_cluster2.get_top_n_path_probabilities(number_of_top_paths, number_of_walks=number_of_walks)
    m = compute_average_distribution(p, q)

    div = sk_divergence(p, q)

    mu_SK, sigma_SK = compute_mu_and_sigma_SK(number_of_walks=number_of_walks,
                                              average_path_probabilities=m,
                                              number_of_top_paths=number_of_top_paths
                                              )

    if len(m) == len(p):
        # print('Length p ', len(p))
        # print(p)
        # print('Length q ', len(q))
        # print(q)
        # print('Number of top paths ', number_of_top_paths)
        #
        # print('Length m ', len(m))
        # print(m)
        #
        # print('Mu_J ', mu_J)
        # print('Sigma_J ', sigma_J)
        # print('JS_div ', js_div)
        # input()

        return div, mu_SK, sigma_SK

    else:
        return None, None, None


def compute_mu_and_sigma_SK(number_of_walks: int,
                            average_path_probabilities: dict,
                            number_of_top_paths: int,
                            ):
    average_probability = list(average_path_probabilities.values())
    average_probability.sort(reverse=True)
    k = min(len(average_probability), number_of_top_paths)
    sigma_sk_squared = (1 / number_of_walks) * sum([average_probability[i] * (2 - average_probability[i])
                                                          for i in range(k)])
    sigma_sk = 0.1 * np.sqrt(sigma_sk_squared)

    # calculate expected mean if the null-hypothesis is true
    mu_sk = 0.474 * (2 / number_of_walks) * sum([(1 - average_probability[i] / 2) for i in range(k)])

    return mu_sk, sigma_sk


class DivergenceTester(object):

    def __init__(self,
                 hypergraph: Hypergraph,
                 config: dict,
                 theta_hit=None):

        self._check_arguments(config)

        self.config = config

        self.theta_hit = theta_hit

        self.hypergraph = hypergraph

        self.communities = {}

    def run_tests(self, number_of_repeats, number_of_walks, length_of_walk, number_of_top_paths):

        assert number_of_repeats % 2 == 0

        self.random_walker = RandomWalker(hypergraph=self.hypergraph,
                                          config=self.config,
                                          num_walks=number_of_walks,
                                          walk_length=length_of_walk)

        # initialise dict node to node path distribution
        path_distributions_of_nodes = defaultdict(lambda: [])
        source_node = list(self.hypergraph.nodes.keys())[0]
        for exp_number in range(number_of_repeats):
            random_walk_data = self.random_walker.generate_node_random_walk_data(source_node=source_node)
            length_of_random_walks = self.random_walker.length_of_walk

            # remove the source node from the random_walk_data and add it to the set of single nodes
            del random_walk_data[source_node]

            close_nodes = self._get_close_nodes(random_walk_data, length_of_random_walks)

            # print(len(close_nodes))

            for node in close_nodes:
                path_distributions_of_nodes[node.name].append(NodeClusterRandomWalkData([node]))

        divergences_of_nodes = defaultdict(lambda: defaultdict(lambda: []))
        for node in path_distributions_of_nodes.keys():
            for pair_number in range(int(number_of_repeats / 2)):
                try:
                    cluster_1 = path_distributions_of_nodes[node][pair_number * 2]
                    cluster_2 = path_distributions_of_nodes[node][pair_number * 2 + 1]
                    div, mu_SK, sigma_SK = compute_divergence(cluster_1,
                                                              cluster_2,
                                                              number_of_walks=number_of_walks,
                                                              number_of_top_paths=number_of_top_paths)

                    if div is not None:
                        divergences_of_nodes[node]['div'].append(div)
                        divergences_of_nodes[node]['mu_SK'].append(mu_SK)
                        divergences_of_nodes[node]['sigma_SK'].append(sigma_SK)
                        print(div, mu_SK, sigma_SK)
                except:
                    pass

        expected_mean_div = []
        actual_mean_div = []
        expected_std_div = []
        actual_std_div = []
        for node in divergences_of_nodes.keys():
            if len(divergences_of_nodes[node]["mu_SK"]) > 0.8 * (number_of_repeats / 2):
                expected_mean_div.append(np.mean(divergences_of_nodes[node]["mu_SK"]))
                actual_mean_div.append(np.mean(divergences_of_nodes[node]["div"]))
                expected_std_div.append(np.mean(divergences_of_nodes[node]["sigma_SK"]))
                actual_std_div.append(np.std(divergences_of_nodes[node]["div"]))

                print(f'Node name: {node}')
                print(f'Number of pairs: {len(divergences_of_nodes[node]["mu_SK"])}')
                print(f'Mean SK Div. Expected: {np.mean(divergences_of_nodes[node]["mu_SK"])} '
                      f'Actual: {np.mean(divergences_of_nodes[node]["div"])}')
                print(f'STD SK Div. Expected: {np.mean(divergences_of_nodes[node]["sigma_SK"])} '
                      f'Actual: {np.std(divergences_of_nodes[node]["div"])}')
                print('----------')

        mean_expected_mean = np.mean(expected_mean_div)
        mean_actual_mean = np.mean(actual_mean_div)
        mean_expected_std = np.mean(expected_std_div)
        mean_actual_std = np.mean(actual_std_div)

        print('Mean expected mean', mean_expected_mean)
        print('Mean actual mean', mean_actual_mean)
        print('Mean expected std', mean_expected_std)
        print('Mean actual std', mean_actual_std)

    def _get_close_nodes(self, random_walk_data, length_of_random_walks):
        if self.theta_hit:
            close_nodes = get_close_nodes_based_on_truncated_hitting_time(random_walk_data,
                                                                          self.theta_hit,
                                                                          length_of_random_walks)
        else:
            close_nodes = get_close_nodes_based_on_path_count(random_walk_data)

        return close_nodes

    @staticmethod
    def _check_arguments(config):
        check_argument('epsilon', config['epsilon'], float, 0, 1)
        check_argument('max_num_paths', config['max_num_paths'], int, 0)
        check_argument('max_path_length', config['max_path_length'], int, 0)


if __name__ == "__main__":
    config = {
        'epsilon': 0.05,
        'max_num_paths': 3,
        'max_path_length': 5
    }

    hypergraph = Hypergraph(database_file='../Databases/imdb4.db', info_file='../Databases/imdb.info')

    tester = DivergenceTester(hypergraph, config, theta_hit=None)
    tester.run_tests(number_of_repeats=500,
                     number_of_walks=2500,
                     length_of_walk=5,
                     number_of_top_paths=3
                     )


