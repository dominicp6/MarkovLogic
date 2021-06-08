from hypernetx.classes import Entity


class Edge(Entity):

    def __init__(self, uid, nodes, predicate):
        super().__init__(uid=uid, elements=nodes)
        self.id = uid
        self.predicate = predicate
