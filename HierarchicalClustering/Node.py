from hypernetx.classes import Entity
from HierarchicalClustering.Community import Community
from collections import defaultdict


def reset(node):
    node.path_counts = defaultdict(lambda: 0)
    node.accumulated_hitting_time = 0
    node.number_of_hits = 0
    node.average_hitting_time = 0


def add_path(node, path):
    node.path_counts[path] += 1


def update_accumulated_hitting_time(node, hitting_time):
    node.accumulated_hitting_time += hitting_time


def update_average_hitting_time(node, number_of_walks, max_length):
    # asset self.average_hitting_time == 0, else this method was called more than once before
    # resetting node properties, which is unintended behaviour
    assert node.average_hitting_time == 0
    node.average_hitting_time = (node.accumulated_hitting_time + (number_of_walks - node.number_of_hits)
                                 * max_length) / number_of_walks

class Node(Entity):

    def __init__(self, name, node_type):
        super().__init__(uid=name)
        self.name = name
        self.node_type = node_type
        self.path_counts = defaultdict(lambda: 0)
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0
        self.average_hitting_time = 0
        self.community = Community()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

