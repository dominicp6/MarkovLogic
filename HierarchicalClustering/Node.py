from hypernetx.classes import Entity


class Node(Entity):

    def __init__(self, name, node_type):
        super().__init__(uid=name)
        self.type = node_type
        self.paths = []
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0

    def reset_node(self):
        self.paths = []
        self.accumulated_hitting_time = 0
        self.number_of_hits = 0

    def add_sample_path(self, sample_path):
        self.paths.append(sample_path)

    def add_to_accumulated_hitting_time(self, hitting_time):
        self.accumulated_hitting_time += hitting_time

    def increment_number_of_hits(self):
        self.number_of_hits += 1

    def get_average_truncated_hitting_time(self, number_of_walks, max_length):
        return (self.accumulated_hitting_time + (number_of_walks - self.number_of_hits) * max_length)/number_of_walks
