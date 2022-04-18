from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from HierarchicalClustering.HierarchicalClusterer import HierarchicalClusterer
from tqdm import tqdm

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


