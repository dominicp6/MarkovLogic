from hypernetx.classes import Entity


class Edge(Entity):

    def __init__(self, edge_id, nodes, predicate):
        super().__init__(uid=edge_id, elements=nodes)
        self.predicate = predicate
