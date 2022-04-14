import numpy as np
from HierarchicalClustering.HierarchicalClusterer import *
from HierarchicalClustering.GraphObjects import *

def P_star(n, L):
    return 1 + (n * (n**L -1 )/(n-1))


def N(P_star, epsilon=0.05, k=3):
    return ((k+1)*(0.577 + np.log(P_star)) - 1)/epsilon**2


def compute_execution_cost(L, n, nodes):
    computation_cost = 0
    for (length, predicate, node_number) in zip(L,n,nodes):
        computation_cost += N(P_star(predicate, length)) * node_number

    return computation_cost


def compute_speed_up(original_hypergraph, hypergraph_clusters):
    original_cost = compute_execution_cost(L=original_hypergraph.diameter(),
                                           n=original_hypergraph.number_of_predicates(),
                                           nodes=original_hypergraph.number_of_nodes())
    final_cost = sum([compute_execution_cost(L=hypergraph.diameter(),
                                            n=hypergraph.number_of_predicates(),
                                            nodes=hypergraph.number_of_nodes())
                      for hypergraph in hypergraph_clusters])

    print(f"Speed up: {round(original_cost / final_cost, 2)}")



# Concrete example
# before
L = [8]
n = [3]
nodes = [25]

original_cost = compute_execution_cost(L, n, nodes)
print(original_cost)

# after
L = [1, 2]
n = [3, 3]
nodes = [21, 4]

new_cost = compute_execution_cost(L, n, nodes)
print(new_cost)

print(f"Speed up: {round(original_cost/new_cost, 2)}")

# IMDB
imdb_hypergraph = Hypergraph(database_file='./Databases/imdb1.db',
                             info_file='./Databases/imdb1.info')
print(imdb_hypergraph)
HierarchicalClusterer()



