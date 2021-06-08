from hypernetx.classes import Entity


class Node(Entity):

    def __init__(self, name, node_type):
        super().__init__(uid=name)
        self.name = name
        self.node_type = node_type
