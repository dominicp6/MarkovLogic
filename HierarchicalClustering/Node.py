from hypernetx.classes import Entity
from HierarchicalClustering.Community import Community
from collections import defaultdict


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

    def reset(self):
        self.path_counts = defaultdict(lambda: 0)
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0
        self.average_hitting_time = 0

    def add_path(self, path):
        self.path_counts[path] += 1

    def update_accumulated_hitting_time(self, hitting_time):
        self.accumulated_hitting_time += hitting_time

    def update_average_hitting_time(self, number_of_walks, max_length):
        # asset self.average_hitting_time == 0, else this method was called more than once before
        # resetting node properties, which is unintended behaviour
        assert self.average_hitting_time == 0
        self.average_hitting_time = (self.accumulated_hitting_time + (number_of_walks - self.number_of_hits)
                                     * max_length)/number_of_walks
