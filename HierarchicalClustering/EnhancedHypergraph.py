import warnings
import networkx as nx
from collections import defaultdict
from Hypergraph import UndirectedHypergraph
from Node import Node

class Hypergraph(UndirectedHypergraph):
    """
    The Hypergraph class extends the UndirectedHypergraph class
    from the Hypergraphs Algorithm Package (http://murali-group.github.io/halp/)
    to have additional functionality relevant to facilitate working with 
    Alchemy-formatted database files (Alchemy software: http://alchemy.cs.washington.edu/).
    """
    def __init__(self, database_file=None, info_file=None):
        super().__init__()

        self._predicates = set()
        self._predicate_counts = defaultdict(lambda: 0)
        self._node_to_hyperedge_ids = defaultdict(lambda: set())
        self._predicate_to_types = defaultdict(lambda: [])
        self._node_name_to_node_type = defaultdict(lambda: 'default_type')
        self.node_name_to_node_object = defaultdict(lambda: Node)
        self.community = None

        if database_file != None:
            self.generate_from_database(path_to_db_file=database_file, path_to_info_file=info_file)

    def __str__(self): 
        output = '''Hypergraph
--------------------------------
#nodes     : {} 
#hyperedges: {}
#predicates: {} 
--------------------------------'''.format(str(self.number_of_nodes()),
str(self.number_of_edges()),
str(self.number_of_predicates()))

        return output

    def get_predicates(self):
        return self._predicates

    def get_predicate_of_hyperedge(self, hyperedge_id):
        try:
            predicate = self.get_hyperedge_attribute(hyperedge_id, "predicate")
        except:
            predicate = None
        return predicate

    def number_of_predicates(self):
        return len(self.get_predicates())

    def get_predicate_counts(self):
        return dict(self._predicate_counts)

    def get_hyperedge_ids_of_node(self, node):
        return self._node_to_hyperedge_ids[node]

    def get_node_to_hyperedge_id_dict(self):
        return dict(self._node_to_hyperedge_ids)

    def number_of_nodes(self):
        return len(self.get_node_set())

    def number_of_edges(self):
        return len(self.get_hyperedge_id_set())

    def reset_nodes(self):
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

    def _add_predicate(self, predicate : str):
        self._predicates.add(predicate)
        self._predicate_counts[predicate] += 1

    def _remove_predicate(self, predicate : str):
        self._predicate_counts[predicate] -= 1
        if self._predicate_counts[predicate] == 0:
            self._predicates.remove(predicate)

    def _add_nodes(self, nodes, node_name_to_node_type=None):
        for node in nodes:
            #retrieve the node's type, if it has been specified
            if node_name_to_node_type is not None:
                node_type = node_name_to_node_type[node]
            else:
                node_type = 'default_type'
            #create a new node only if it isn't already in the node set
            if not self.has_node(node):
                self.node_name_to_node_object[node] = Node(node_name = node, node_type = node_type)

    def _remove_node(self, node):
        del self.node_name_to_node_object[node]

    #TODO: somehow merge these with the other add/remove node methods we have?
    def _add_nodes_to_hyperedge(self, nodes, hyperedge_id):
        for node in nodes:
            self._node_to_hyperedge_ids[node].add(hyperedge_id)

    def _remove_nodes_from_hyperedge(self, nodes, hyperedge_id):
        for node in nodes:
            self._node_to_hyperedge_ids[node].remove(hyperedge_id)
            #also remove the node if it has no associated hyperedges remaining
            if len(self._node_to_hyperedge_ids[node]) == 0:
                self._remove_node(node)

    #TODO: consistent comments for these functions
    def add_hyperedge(self, nodes, attr_dict=None, node_name_to_node_type = None, **attr):
        #update predicate dict
        if attr_dict["predicate"] is not None:
            self._add_predicate(attr_dict["predicate"])
        #call parent method
        hyperedge_id = super().add_hyperedge(nodes, attr_dict, **attr)
        #update node and hyperedge dict
        self._add_nodes(nodes, node_name_to_node_type)
        self._add_nodes_to_hyperedge(nodes, hyperedge_id)
        
        return hyperedge_id

    def add_hyperedges(self, hyperedges, attr_dict=None, node_name_to_node_type = None, **attr):
        #call parent method
        hyperedge_ids = super().add_hyperedges(hyperedges, attr_dict, **attr) 
        #update node to hyperedge dict
        for nodes, hyperedge_id in zip(hyperedges, hyperedge_ids):
            if attr_dict["predicate"] is not None:
                self._add_predicate(attr_dict["predicate"])
            self._add_nodes_to_hyperedge(nodes, hyperedge_id)
            self._add_nodes(nodes, node_name_to_node_type)
        
        return hyperedge_ids

    def remove_hyperedge(self, hyperedge_id):
        #update predicate dict
        predicate = self.get_predicate_of_hyperedge(hyperedge_id)
        if predicate is not None:
            self._remove_predicate(predicate)
        #update node to hyperedge dict
        nodes = self.get_hyperedge_nodes(hyperedge_id)
        self._remove_nodes_from_hyperedge(nodes, hyperedge_id)
        #call parent method
        super().remove_hyperedge(hyperedge_id)

    def remove_hyperedges(self, hyperedge_ids):
        for hyperedge_id in hyperedge_ids:
            predicate = self.get_predicate_of_hyperedge(hyperedge_id)
            if predicate is not None:
                self._remove_predicate(predicate)
            nodes = self.get_hyperedge_nodes(hyperedge_id)
            self._remove_nodes_from_hyperedge(nodes, hyperedge_id)
        #call parent method
        super().remove_hyperedges(hyperedge_ids)

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

    def _read_info_file(self, info_file_name):
        info_file = open(info_file_name, 'r')
        for line_idx, line in enumerate(info_file.readlines()):
            #Skip empty lines
            if not line:
                continue
            
            predicate, types = self._parse_line(file_name=info_file_name, line = line, line_idx = line_idx)
            self._predicate_to_types[predicate] = types

        info_file.close()

    def _label_nodes_with_predicate(self, node_list, predicate):
        if len(self._predicate_to_types) > 0:
            for idx, node in enumerate(node_list):
                self._node_name_to_node_type[node] = self._predicate_to_types[predicate][idx]

    def _read_db_file(self, db_file_name):
        db_file = open(db_file_name, 'r')

        for line_idx, line in enumerate(db_file.readlines()):
            #Skip empty lines
            if not line:
                continue

            predicate, node_list = self._parse_line(file_name=db_file_name, line = line, line_idx = line_idx)
            self._label_nodes_with_predicate(node_list, predicate)
            node_set = set(node_list)

            self.add_hyperedge(node_set, weight=1, attr_dict = {"predicate": str(predicate)})

        db_file.close()

    def generate_from_database(self, path_to_db_file: str, path_to_info_file = None):
        """
        Generates an undirected hypergraph representation of a relational database 
        that is defined in an Alchemy .db file

        If path_to_info_file is provided, then also reads in a .info file which 
        specifies the types of each predicate_argument, allowing nodes of the 
        hypergraph to be annotated by their type.
        """
        if path_to_info_file is not None:
            self._read_info_file(path_to_info_file)

        self._read_db_file(path_to_db_file)
        
    


    
        