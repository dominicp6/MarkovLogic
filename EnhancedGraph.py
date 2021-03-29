import cynetworkx as nx
from cynetworkx.classes.graph import Graph
from graph_hashing import weisfeiler_lehman_graph_hash

class EnhancedGraph(Graph):
    """
    Extends the networkx Graph class to have __hash__ and __eq__ methods
    so that graphs are hashable and equatable
    """

    def __init__(self):
        super().__init__()

    def __hash__(self):
        return weisfeiler_lehman_graph_hash(self)

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return nx.is_isomorphic(self, other)