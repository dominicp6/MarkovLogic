class Node(object):
    """
    Defines a node object, a constituent of a hypergraph.

    :param: node_type (str) - the type of the node
    """

    def __init__(self, node_name : str, node_type : str):
        #TODO: enforce node_type non null
        self.name = node_name
        self.type = node_type
        self.first_visit = True
        self.ave_hitting_time = float('inf')
        self.sample_paths = dict()

    def reset(self, max_length : int, walk_number : int, hard_reset : bool):
        if hard_reset == False:
            if self.first_visit == False: 
                if self.ave_hitting_time != float('inf'):
                    self.ave_hitting_time += 1/(walk_number) * (max_length - self.ave_hitting_time)
                else:
                    self.ave_hitting_time = max_length
        else:
            self.ave_hitting_time = float('inf')
            self.sample_paths = dict()
        
        self.first_visit = True

    def update_ave_hitting_time(self, hitting_time : float, walk_number : int):
        #TODO: enforce typing
        self.ave_hitting_time += 1/(walk_number) * (hitting_time - self.ave_hitting_time)

    def update_sample_paths(self, path : list, walk_number : int):
        #TODO: enforce typing
        self.sample_paths[walk_number] = path
