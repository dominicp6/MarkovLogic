from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from HierarchicalClustering.HierarchicalClusterer import HierarchicalClusterer
from tqdm import tqdm

from HierarchicalClustering.RandomWalker import RandomWalker


def P_star(n, L):
    if n > 1:
        return 1 + (n * (n ** L - 1) / (n - 1))
    else:
        return 1

def N_paths(P_star, epsilon=0.05, k=3):
    return ((k + 1) * (0.577 + np.log(P_star)) - 1) / epsilon ** 2


def N_THT(L, epsilon=0.05):
    return (L - 1) ** 2 / (4 * epsilon ** 2)


def compute_execution_cost(L, n, nodes):
    return max(N_paths(P_star(n, L)), N_THT(L)) * nodes


def compute_speed_up(original_hypergraph, hypergraph_clusters):
    original_cost = compute_execution_cost(L=original_hypergraph.diameter(),
                                           n=original_hypergraph.number_of_predicates(),
                                           nodes=original_hypergraph.number_of_nodes())
    final_cost = sum([compute_execution_cost(L=hypergraph.diameter(),
                                             n=hypergraph.number_of_predicates(),
                                             nodes=hypergraph.number_of_nodes())
                      for hypergraph in hypergraph_clusters])

    return round(original_cost / final_cost, 2)


def hierarchical_clustering_diagnostics(hypergraph):
    speed_up_records = defaultdict(lambda: [])
    lambda2s = np.arange(0.1, 2.0, 0.1)
    for min_cluster_size in tqdm(np.arange(3, min(10, hypergraph.number_of_nodes()), 1)):
        for lambda2 in lambda2s:
            config = {
                'clustering_params': {
                    'min_cluster_size': int(min_cluster_size),
                    'max_lambda2': lambda2,
                }}
            hc = HierarchicalClusterer(hypergraph=hypergraph, config=config['clustering_params'])
            hc.run_hierarchical_clustering()
            speed_up_records[min_cluster_size].append(compute_speed_up(hypergraph,
                                                                       hc.hypergraph_clusters))

    for min_cluster_size, speed_ups in speed_up_records.items():
        plt.plot(lambda2s, speed_ups, label=f'{min_cluster_size}')

    plt.title('Hierarchical Clustering Diagnostics')
    plt.xlabel('max lambda2')
    plt.ylabel('Estimated Speed-up')
    plt.legend()
    plt.show()


def hypergraph_diagnostics(hypergraph):
    degrees = [len(membership_array) for membership_array in hypergraph.memberships.values()]
    plt.xlabel('Degree')
    plt.ylabel('Count')
    plt.title('Degree Distribution')
    plt.hist(degrees, bins=max(degrees) - min(degrees))
    plt.axvline(np.mean(degrees), color='k', linestyle='dashed', linewidth=1)
    plt.show()


def random_walk_diagnostics(hypergraph):
    rsd_dict = dict()
    average_number_of_paths = dict()
    for path_length in tqdm(np.arange(2, 10)):
        config = {
            'random_walk_params': {
                'epsilon': 0.1,
                'max_num_paths': 3,
                'alpha_sym': 0.1,
                'pca_dim': 2,
                'clustering_method_threshold': 50,
                'max_path_length': int(path_length),
                'theta_p': 0.5,
            }
        }
        rw = RandomWalker(hypergraph=hypergraph, config=config['random_walk_params'])
        rw_data = [rw.generate_node_random_walk_data(source_node=node) for node in hypergraph.nodes.keys()]
        rsd_data = []
        num_paths_data = []
        max_number_of_paths = 0
        entries = 0
        for rw_data_from_a_node in rw_data:
            for node_data in rw_data_from_a_node.values():
                entries = len(rw_data)*len(rw_data_from_a_node.values())
                paths = sorted(node_data.path_counts.items(), key=lambda x: x[1], reverse=True)
                path_counts = [path_tuple[1] for path_tuple in paths]
                total_path_count = sum(path_counts)
                path_probabilities = np.array([path_count/total_path_count for path_count in path_counts])
                Z = sum([1/(k+1) for k in range(len(path_counts))])
                ziphian_probabilities = np.array([1/((k+1)*Z) for k in range(len(path_counts))])
                rsd_diff = np.sqrt(np.sum((path_probabilities-ziphian_probabilities)**2))
                rsd_data.append(rsd_diff)
                num_paths_data.append(len(path_counts))
                max_number_of_paths = max(max_number_of_paths, len(path_counts))

        experimental_prob_array = np.zeros((entries, max_number_of_paths))
        ziphian_prob_array = np.zeros((entries, max_number_of_paths))
        entry = 0
        for rw_data_from_a_node in rw_data:
            for node_data in rw_data_from_a_node.values():
                paths = sorted(node_data.path_counts.items(), key=lambda x: x[1], reverse=True)
                path_counts = [path_tuple[1] for path_tuple in paths]
                total_path_count = sum(path_counts)
                path_probabilities = np.array([path_count/total_path_count for path_count in path_counts])
                Z = sum([1/(k+1) for k in range(len(path_counts))])
                ziphian_probabilities = np.array([1/((k+1)*Z) for k in range(len(path_counts))])

                experimental_prob_array[entry][0:len(path_probabilities)] = path_probabilities
                ziphian_prob_array[entry][0:len(ziphian_probabilities)] = ziphian_probabilities
                entry += 1

        rsd_dict[int(path_length)] = np.mean(rsd_data)
        average_number_of_paths[int(path_length)] = np.mean(num_paths_data)
        plt.plot([1/(x+1) for x in np.arange(0, np.shape(experimental_prob_array)[1])], np.mean(experimental_prob_array, axis=0), label='experiment')
        plt.plot([1/(x+1) for x in np.arange(0, np.shape(ziphian_prob_array)[1])], np.mean(ziphian_prob_array, axis=0), label='ziphian')
        plt.xlabel('1 / Path Index')
        plt.ylabel('log(P)')
        plt.title(f'Path Length: {int(path_length)}')
        plt.legend()
        plt.show()

    plt.plot(rsd_dict.keys(), rsd_dict.values())
    plt.xlabel('Path Length')
    plt.ylabel('RSS')
    plt.title('Root-Sum-Square Deviation between Ziphian and Experimental')
    plt.show()
    plt.plot(rsd_dict.keys(), average_number_of_paths.values())
    plt.xlabel('Path Length')
    plt.ylabel('Average Number of Paths')
    plt.title('Number of Path Trends with Path Length')
    plt.show()
