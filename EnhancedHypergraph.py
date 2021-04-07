import warnings
import cynetworkx as nx
from itertools import combinations
from collections import defaultdict
from Hypergraph import UndirectedHypergraph
from Node import Node

class EnhancedUndirectedHypergraph(UndirectedHypergraph):
    """
    The EnhancedUndirectedHypergraph class extends the UndirectedHypergraph class
    from the Hypergraphs Algorithm Package (http://murali-group.github.io/halp/)
    to have additional functionality relevant to facilitate working with 
    Alchemy-formatted database files (Alchemy software: http://alchemy.cs.washington.edu/).
    """
    def __init__(self):
        super().__init__()

        self._predicate_set = set()
        self._predicate_counts = defaultdict(lambda: 0)
        self._node_to_hyperedge_ids = defaultdict(lambda: set())
        self._pred_to_types = defaultdict(lambda: [])
        self._node_name_to_node_type = defaultdict(lambda: 'default_type')
        self.node_name_to_node_object = defaultdict(lambda: Node)
        self.community = None

    def __str__(self): 
        output = '''Undirected hypergraph object
--------------------------------
#nodes     : {} 
#hyperedges: {}
#predicates: {} 
--------------------------------'''.format(str(self.order()),
str(self.size()),
str(self.num_predicates()))

        return output

    def _create_nodes(self, nodes,node_name_to_node_type=None):
        """
        Creates a new hypergraph node object for each node in nodes, providing the 
        node isn't already in the hypergraph's node set
        """
        for node in nodes:
            if node_name_to_node_type is not None:
                node_type = node_name_to_node_type[node]
            else:
                node_type = self._node_name_to_node_type[node]
            #only create a new node if it isn't already in the node set
            if node not in self.get_node_set():
                self.node_name_to_node_object[node] = Node(node_name = node, node_type = node_type)

    def _delete_node(self, node):
        """
        Removes a node object from the hypergraph
        """
        del self.node_name_to_node_object[node]

    def _update_node_to_hyperedge_id_dict(self, nodes, hyperedge_id, operation='add'):
        """
        Updates the dictionary mapping from nodes to hyperedge ids.

        Takes as input a set of nodes beloning to a newly added/removed hyperedge
        and updates the _node_to_hyperedge_ids dictionary accordingly.

        :param nodes: the node set of the hyperedge being added/removed
        :param hyperedge_id: the id of the hyperedge being added/removed
        :param operation: 'add' if we are adding hyperedge(s), 'remove' if we are removing
        """
        for node in nodes:
            if operation == 'add':
                self._node_to_hyperedge_ids[node].add(hyperedge_id)

            elif operation == 'remove':
                self._node_to_hyperedge_ids[node].remove(hyperedge_id)
                #also delete the node if it has no associated hyperedges remaining
                if len(self._node_to_hyperedge_ids[node]) == 0:
                    self._delete_node(node)

            else:
                raise ValueError('_update_node_to_hyperedge_id_dict operation parameter must be one of: "add", "remove"')

    def _update_predicate_list(self, predicate: str, operation='add', increment=1):
        """
        Updates the set of predicates and predicate counts of the hypergraph whenever
        hyperedges are added or removed from the hypergraph

        :param predicate: Name of the predicate corresponding to the hyperedge(s) being 
                          added/removed
        :param operation: 'add' if we are adding hyperedge(s), 'remove' if we are removing
        :param incrment: the number of hyperedges to add/remove
        """
        if operation == 'add':
            self._predicate_set.add(predicate)
            self._predicate_counts[predicate] += increment

        elif operation == 'remove':
            self._predicate_counts[predicate] -= increment
            if self._predicate_counts[predicate] <= 0:
                self._predicate_set.remove(predicate)
                self._predicate_counts[predicate] = 0

        else:
            raise ValueError('_update_predicate_list operation parameter must be one of: "add", "remove"')

    def reset_nodes(self):
        """
        Resets the properties of each node to their default values.
        """
        for node_obj in self.node_name_to_node_object.values():
            node_obj.reset()

    def update_nodes(self, max_length : int, walk_number: int):
        """
        Updates the ave_hitting_time property of all nodes in the hypergraph, and
        resets the 'first_visit' property of each node to 'True'. To be called
        every time a random walk is completed on the hypergraph.

        :param: max_length (int)  - the maximum length of the random walk 
        :param: walk_number(int)  - =k if this is the kth random walk on this hypergraph 
        """
        for node_obj in self.node_name_to_node_object.values():
            node_obj.update(max_length = max_length, walk_number = walk_number)

    def get_predicate_of_hyperedge(self, hyperedge_id):
        """
        Returns the predicate corresponding to a given hyperedge_id, if a predicate is 
        defined for that hyperedge. Else returns None.
        """
        try:
            predicate = self.get_hyperedge_attribute(hyperedge_id, "predicate")
        except:
            predicate = None
        return predicate

    def add_hyperedge(self, nodes, attr_dict=None, node_name_to_node_type = None, **attr):
        """
        Extends the add_hyperedge method implementation in UndirectedHypergraph 
        to also update the predicate dict and node to hyperedge dict.
        """
        if attr_dict["predicate"] is not None:
            self._update_predicate_list(attr_dict["predicate"], operation='add')
        self._create_nodes(nodes,node_name_to_node_type)
        hyperedge_id = super().add_hyperedge(nodes, attr_dict, **attr)
        self._update_node_to_hyperedge_id_dict(nodes, hyperedge_id)
        
        return hyperedge_id

    def add_hyperedges(self, hyperedges, attr_dict=None, node_name_to_node_type = None, **attr):
        """
        Extends the add_hyperedges method implementation in UndirectedHypergraph 
        to also update the predicate dict and node to hyperedge dict.
        """
        #update predicate dict
        if attr_dict["predicate"] is not None:
            self._update_predicate_list(attr_dict["predicate"], operation='add', increment=len(hyperedges))
        #call parent method
        hyperedge_ids = super().add_hyperedges(hyperedges, attr_dict, **attr) 
        #update node to hyperedge dict
        for nodes, hyperedge_id in zip(hyperedges, hyperedge_ids):
            self._update_node_to_hyperedge_id_dict(nodes, hyperedge_id)
            self._create_nodes(nodes, node_name_to_node_type)
        
        return hyperedge_ids

    def remove_hyperedge(self, hyperedge_id):
        """
        Extends the remove_hyperedge method implementation in UndirectedHypergraph 
        to also update the predicate dict and node to hyperedge dict.
        """
        #update predicate dict
        predicate = self.get_predicate_of_hyperedge(hyperedge_id)
        if predicate is not None:
            self._update_predicate_list(predicate, operation='remove')
        #update node to hyperedge dict
        nodes = self.get_hyperedge_nodes(hyperedge_id)
        self._update_node_to_hyperedge_id_dict(nodes, hyperedge_id, operation='remove')
        #call parent method
        super().remove_hyperedge(hyperedge_id)

    def remove_hyperedges(self, hyperedge_ids):
        """
        Extends the remove_hyperedges method implementation in UndirectedHypergraph 
        to also update the predicate dict and node to hyperedge dict.
        """
        #update predicate dict
        predicates = []
        for hyperedge_id in hyperedge_ids:
            predicates.append(self.get_predicate_of_hyperedge(hyperedge_id))
        for predicate in predicates:
            if predicate is not None:
                self._update_predicate_list(predicate, operation='remove')
        #update node to hyperedge dict
        for hyperedge_id in hyperedge_ids:
            nodes = self.get_hyperedge_nodes(hyperedge_id)
            self._update_node_to_hyperedge_id_dict(nodes, hyperedge_id, operation='remove')
        #call parent method
        super().remove_hyperedges(hyperedge_ids)

    def get_predicates(self):
        """
        Returns the set of predicates pertaining to the hypergraph.
        """
        return self._predicate_set

    def get_predicate_counts(self):
        """
        Returns the predicate counts dictionary (i.e. number of 
        hyperedges of each predicate type) of the hypergraph.
        """
        return dict(self._predicate_counts)

    def get_hyperedge_ids_of_node(self, node):
        """
        Returns the the hyperedge ids incident on a particular node.
        """
        return self._node_to_hyperedge_ids[node]

    def get_node_to_hyperedge_id_dict(self):
        """
        Returns the the hyperedge ids dictionary of the hypergraph.
        """
        return dict(self._node_to_hyperedge_ids)

    def order(self):
        """
        Returns the number of nodes in the hypergraph.
        """
        return len(self.get_node_set())

    def size(self):
        """
        Returns the number of hyperedges in the hypergraph.
        """
        return len(self.get_hyperedge_id_set())

    def num_predicates(self):
        """
        Returns the number of distinct predicates types of the hypergraph.
        """
        return len(self.get_predicates())

    def _parse_line(self, file_name : str, line : str, line_idx : int):
        """
        Parses a line from a .db or .info file.

        :param file_name: name of the file which is currently being parsed
        :param line: the line to be parsed
        :param line_idx: the idx of the line
        :returns: predicate - the predicate defined in that line of the file
                  predicate_arguments - the arguments of that predicate

        e.g. Friends(Anna, Bob) gets parsed as:
        predicate:           Friends
        predicate_arguments: [Anna,Bob]
        """
        line_number = line_idx + 1
        line = line.strip()

        line_fragments = line.split('(')
        if len(line_fragments) != 2 or line_fragments[1][-1] != ")":
            raise IOError("Line {} [{}]".format(line_number, line)
                            +"of {} has incorrect syntax \n".format(file_name)+
                            "Make sure that each predicate is correctly"+
                            " formatted with braces and commas e.g. "+
                            " Friends(Anna, Bob)")

        predicate = line_fragments[0]
        predicate_argument_string = line_fragments[1][0:-1]
        predicate_arguments = [predicate_argument.strip() for predicate_argument in predicate_argument_string.split(',')]
        return predicate, predicate_arguments


    def read_from_alchemy_db(self, db_file_name: str, info_file_name = None):
        """
        Reads an undirected hypergraph from an Alchemy .db file

        If info_file_name is provided, then also reads in a .info file which 
        specifies the types of each predicate_argument, allowing nodes of the 
        hypergraph to be annotated by their type.
        """
        if info_file_name is not None:
            info_file = open(info_file_name, 'r')
            for line_idx, line in enumerate(info_file.readlines()):
                #Skip empty lines
                if not line:
                    continue
                
                predicate, types = self._parse_line(file_name=info_file_name, line = line, line_idx = line_idx)
                self._pred_to_types[predicate] = types

            info_file.close()

        db_file = open(db_file_name, 'r')

        for line_idx, line in enumerate(db_file.readlines()):
            #Skip empty lines
            if not line:
                continue

            predicate, node_list = self._parse_line(file_name=db_file_name, line = line, line_idx = line_idx)
            if info_file_name is not None:
                for idx, node in enumerate(node_list):
                    self._node_name_to_node_type[node] = self._pred_to_types[predicate][idx]
            nodes = set(node_list)
            #print('1')
            #print(self._node_name_to_node_type)
            self.add_hyperedge(nodes, weight=1, attr_dict = {"predicate": str(predicate)})
            #print(self._node_name_to_node_type)
            #print('2')

        db_file.close()
        print("Successfully imported hypergraph from "+db_file_name)
        


    def convert_to_graph(self, sum_weights_for_multi_edges = True, verbose = True):
        """
        Converts the undirected hypergraph to a graph by replacing all 
        k-hyperedges with k-cliques (a k-clique is a fully connected 
        subgraph with k nodes). This is useful as a pre-processing 
        step for applying graph-based clustering algorithms.

        :param sum_weights_for_multi_edges: if True then replaces any
            multi-edges generated in the hypergraph -> graph conversion
            with a single edge of weight equal to the number of multi
            -edges. If false, give all edges in the graph uniform weight
            regardless of the number of multi-edges.
        """
        G = nx.Graph()

        for hyperedge_id in self.get_hyperedge_id_set():
            nodes = self.get_hyperedge_nodes(hyperedge_id)
            
            #from the hyperedge node set construct a complete subgraph (clique)
            for e in combinations(nodes,2):
                if sum_weights_for_multi_edges == True:
                    #increment edge weight if edge already exists
                    if G.has_edge(*e):
                        G[e[0]][e[1]]['weight'] += 1
                    #else add the new edge
                    else:
                        G.add_edge(*e, weight=1)
                else:
                    G.add_edge(*e, weight=1)
        
        if verbose == True:
            print("New graph object")
            print("--------------------------------")
            print("#nodes               : {}".format(G.order()))
            print("#edges               : {}".format(G.size()))
            print("#connected components: {}".format(nx.number_connected_components(G)))
            print("--------------------------------")

        #Check that the graph is connected
        assert nx.is_connected(G)

        return G

    def convert_to_hypergraph(self, G):
        """
        Converts an undirected graph, or simply a set of graph nodes,
        into a undirected hypergraph using an instance of EnhancedUndirectedHypergraph 
        as a template.

        :param G: The graph (or node set) to be converted to a hypergraph

        """
        #initialise a new hypergraph
        H = EnhancedUndirectedHypergraph()
        
        if isinstance(G, nx.Graph):
            nodes = G.nodes()
        elif isinstance(G, set):
            nodes = G
        else:
            raise ValueError('Input must be either of type Graph or Set, but is of type {}'.format(type(G)))

        for node in nodes:
            #for each node in the graph, find the sets of hyperedge nodes from the
            #template hypergraph which contain that node
            for hyperedge_id in self._node_to_hyperedge_ids[node]:
                #add the corresponding hyperedges to the new hypergraph instance
                H.add_hyperedge(self.get_hyperedge_nodes(hyperedge_id), weight=1, attr_dict = {"predicate": self.get_hyperedge_attribute(hyperedge_id, "predicate")}, node_name_to_node_type=self._node_name_to_node_type)
        
        return H


    
        