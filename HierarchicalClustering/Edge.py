from hypernetx.classes import Entity
from Node import Node


class Edge(Entity):

    def __init__(self, uid: int, nodes: list[Node], predicate: str):
        super().__init__(uid=uid, elements=nodes)
        self.predicate = predicate
