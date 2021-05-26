import warnings
import networkx as nx
from collections import defaultdict
from halp.undirected_hypergraph import UndirectedHypergraph
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
        self._hyperedges_of_node = defaultdict(lambda: set())              
        self.predicate_argument_types = defaultdict(lambda: [])                
        self.node_name_to_node_type = defaultdict(lambda: 'default_type') 
        self.node_name_to_node_object = defaultdict(lambda: Node) 

        if database_file:
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

    def get_hyperedges_of_node(self, node):
        return self._hyperedges_of_node[node]

    def get_node_to_hyperedges_dict(self):
        return dict(self._hyperedges_of_node)

    def get_type_of_node(self, node):
        return self.node_name_to_node_type[node]

    def number_of_nodes(self):
        return len(self.get_node_set())

    def number_of_edges(self):
        return len(self.get_hyperedge_id_set())

    def reset_nodes(self):
        for node_obj in self.node_name_to_node_object.values():
            node_obj.reset()

    def update_node_random_walk_parameters(self, max_length : int, walk_number: int):
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

    def _add_node(self, node, node_type):
        self.node_name_to_node_object[node] = Node(node_name = node, node_type = node_type)

    def _add_nodes(self, nodes, node_name_to_node_type):
        for node in nodes:
            #retrieve the node's type, if it has been specified
            try:
                node_type = node_name_to_node_type[node]
            except:
                node_type = 'default_type'
            #create a new node only if it isn't already in the node set
            if not self.has_node(node):
                self._add_node(node, node_type)

    def _add_nodes_to_hyperedge(self, nodes, hyperedge_id):
        for node in nodes:
            self._hyperedges_of_node[node].add(hyperedge_id)

    def _remove_node(self, node):
        del self.node_name_to_node_type[node]
        del self.node_name_to_node_object[node]

    def _remove_nodes(self, nodes):
        for node in nodes:
            #only remove a node if it has no associated hyperedges remaining
            if len(self._hyperedges_of_node[node]) == 0:
                self._remove_node(node)

    def _remove_nodes_from_hyperedge(self, nodes, hyperedge_id):
        for node in nodes:
            self._hyperedges_of_node[node].remove(hyperedge_id)

    def add_hyperedge(self, nodes, predicate=None, node_name_to_node_type = None):  
        """
        Adds a hyperedge to the hypergraph. If the hyperedge contains nodes not 
        already present in the hypergraph then these nodes are also added to the
        hypergraph.

        :param nodes: the node set of the hyperedge to add
        :param predicate (str): the predicate name of the hyperedge [optional]
        """
        hyperedge_id = super().add_hyperedge(nodes, {'predicate' : predicate})
        if predicate:
            self._add_predicate(predicate)
        self._add_nodes(nodes, node_name_to_node_type)
        self._add_nodes_to_hyperedge(nodes, hyperedge_id)
        
        return hyperedge_id

    def add_hyperedges(self, hyperedges, predicate=None, node_name_to_node_type = None):
        """
        Adds a hyperedges to the hypergraph. If the hyperedges contain nodes not 
        already present in the hypergraph then these nodes are also added to the
        hypergraph.

        :param hyperedges: a list of node sets of the hyperedges to add
        :param predicate (str): the predicate name of the hyperedges (same for each) [optional] 
        """
        hyperedge_ids = []
        for nodes in hyperedges:
            hyperedge_id = self.add_hyperedge(nodes, predicate)
            hyperedge_ids.append(hyperedge_id)
        
        return hyperedge_ids

    def remove_hyperedge(self, hyperedge_id):
        predicate = self.get_predicate_of_hyperedge(hyperedge_id)
        if predicate:
            self._remove_predicate(predicate)
        nodes = self.get_hyperedge_nodes(hyperedge_id)
        self._remove_nodes_from_hyperedge(nodes, hyperedge_id)
        self._remove_nodes(nodes)
        super().remove_hyperedge(hyperedge_id)

    def remove_hyperedges(self, hyperedge_ids):
        for hyperedge_id in hyperedge_ids:
            self.remove_hyperedge(hyperedge_id)

    def _correct_line_syntax(self, line_fragments):
        argument_string = line_fragments[1][0:1]
        #check that open and closed parentheses are correctly used
        #check that the argument string does not contain duplicate closing braces
        if (len(line_fragments) == 2) and (line_fragments[1][-1] == ")") and (")" not in argument_string):
            return True
        else:
            return False

    def _parse_line(self, file_name : str, line : str, line_number : int):
        """
        Parses a line from a .db or .info file.

        :param file_name: name of the file which is currently being parsed
        :param line: the line to be parsed
        :param line_number: the line number of the line to parse
        :returns: predicate - the predicate defined in that line of the file
                  predicate_arguments - the arguments of that predicate

        e.g. Friends(Anna, Bob) gets parsed as:
        predicate:           Friends
        predicate_arguments: [Anna,Bob]
        """
        line = line.strip()

        line_fragments = line.split('(')
        if not self._correct_line_syntax(line_fragments):
            raise IOError("Line {} [{}]".format(line_number, line)
                            +"of {} has incorrect syntax \n".format(file_name)+
                            "Make sure that each predicate is correctly"+
                            " formatted with braces and commas e.g. "+
                            " Friends(Anna, Bob)")

        predicate = line_fragments[0]
        predicate_argument_string = line_fragments[1][0:-1]
        predicate_arguments = [predicate_argument.strip() for predicate_argument in predicate_argument_string.split(',')]
        return predicate, predicate_arguments

    def _generate_predicate_to_type_from_info_file(self, info_file_name):
        info_file = open(info_file_name, 'r')
        for line_idx, line in enumerate(info_file.readlines()):
            #skip empty lines
            if not line:
                continue
            
            #line_number = line_idx + 1 since enumerate starts from 0 but file line numbering starts from one
            predicate, types = self._parse_line(file_name=info_file_name, line = line, line_number = line_idx+1)
            self.predicate_argument_types[predicate] = types

        info_file.close()

    def _label_nodes_with_types(self, node_list, predicate):
        for idx, node in enumerate(node_list):
            self.node_name_to_node_type[node] = self.predicate_argument_types[predicate][idx]

    def generate_from_database(self, path_to_db_file: str, path_to_info_file = None):
        """
        Generates an undirected hypergraph representation of a relational database 
        that is defined in an Alchemy .db file

        If path_to_info_file is provided, then also reads in a .info file which 
        specifies the types of each predicate_argument, allowing nodes of the 
        hypergraph to be annotated by their type.
        """
        if path_to_info_file is not None:
            self._generate_predicate_to_type_from_info_file(path_to_info_file)

        db_file = open(path_to_db_file, 'r')
        for line_idx, line in enumerate(db_file.readlines()):
            #Skip empty lines
            if not line:
                continue

            predicate, node_list = self._parse_line(file_name=path_to_db_file, line = line, line_number = line_idx)
            
            #If the argument types of the predicate are known then label nodes with their type
            if self.predicate_argument_types[predicate]:
                self._label_nodes_with_types(node_list, predicate)

            node_set = set(node_list)
            self.add_hyperedge(node_set, predicate = predicate)

        db_file.close()
        
    


    
        