from collections import defaultdict, Counter
import numpy as np
import operator


def _kulback_lieber_div(p,q):
    return sum(p * np.log(p / q) for p, q in zip(p, q) if p != 0)

def _jenson_shannon_divergence(p, q):
    m = 0.5 * (p + q)
    return 0.5 * _kulback_lieber_div(p, m) + 0.5 * _kulback_lieber_div(q,m)

def compute_jenson_shannon_divergence(path_probs_1, path_probs_2):
    path_set_1 = [path_and_prob[0] for path_and_prob in path_probs_1]
    path_set_2 = [path_and_prob[0] for path_and_prob in path_probs_2]
    paths_of_2_not_in_1 = np.setdiff1d(path_set_2, path_set_1)

    p = np.array([path_and_prob[1] for path_and_prob in path_probs_1] + [0]*len(paths_of_2_not_in_1))
    q = np.array([path_and_prob[1] if path_and_prob[0] in path_set_2 else 0 for path_and_prob in path_probs_1] + [path_and_prob[1] for path_and_prob in path_probs_2 if path_and_prob[0] in paths_of_2_not_in_1])

    assert len(p) == len(q)

    return _jenson_shannon_divergence(p,q)

def merge_node_paths(path_probs_1, path_probs_2):
    path_sums = dict(Counter(path_probs_1) + Counter(path_probs_2))
    return {path_string : path_sums[path_string] / 2 for path_string in path_sums.keys()}

class Node(object):
    """
    Defines a node object, a constituent of a hypergraph.

    :param: node_name (str) - the name of thr node 
    :param: node_type (str) - the type of the node
    """

    def __init__(self, node_name : str, node_type : str):
        assert isinstance(node_name, str), "Arg Error: node_name must be of type str"
        assert isinstance(node_type, str), "Arg Error: node_type must be of type str"
        self.name = node_name
        self.type = node_type
        self.first_visit = True
        self.ave_hitting_time = float('inf')
        self.sample_paths = defaultdict(int)

    def __str__(self):
        return self.name
        
    def reset(self):
        """
        Resets node properties to their default value.
        """
        self.ave_hitting_time = float('inf')
        self.sample_paths = dict()
        self.first_visit = True

    def update(self, max_length : int, walk_number : int):
        """
        Updates node properties after a random walk is complete.
        """
        if self.first_visit == False: 
            if self.ave_hitting_time != float('inf'):
                self.ave_hitting_time += 1/(walk_number) * (max_length - self.ave_hitting_time)
            else:
                #Tuncated average hitting time:
                #set the average hitting time to max_length if the node wasn't visited during the walk
                self.ave_hitting_time = max_length
        
        self.first_visit = True

    def update_ave_hitting_time(self, hitting_time : float, walk_number : int):
        """
        Updates the average hitting time of the node using the most recent 
        hitting time.
        """
        if self.ave_hitting_time == float('inf'):
            self.ave_hitting_time = hitting_time
        else:
            self.ave_hitting_time += 1/(walk_number) * (hitting_time - self.ave_hitting_time)

    def update_sample_paths(self, path : list):
        """
        Updates the sample paths of the node with the most recent path.
        """
        path_string = ','.join(path)
        self.sample_paths[path_string] += 1

    def get_Ntop_paths(self, Ntop : int):
        num_paths = sum(self.sample_paths.values())
        sample_paths_probabilities = {key : value/num_paths for key, value in self.sample_paths.items()}
        sorted_paths = sorted(sample_paths_probabilities.items(), key=operator.itemgetter(1), reverse=True)

        if len(sorted_paths) >= Ntop:
            return sorted_paths[0:Ntop]
        else:
            return sorted_paths
