from hypernetx.classes import Entity

class Edge(Entity):

    def __init__(self, id, nodes, predicate):
        super().__init__(uid=id, elements=nodes)
        self.id = id
        self.predicate = predicate
