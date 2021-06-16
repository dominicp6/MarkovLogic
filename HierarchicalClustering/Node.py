from hypernetx.classes import Entity


class Node(Entity):

    def __init__(self, name, node_type, is_source_node=False):
        super().__init__(uid=name)
        self.name = name
        self.node_type = node_type
        self.is_source_node = is_source_node
