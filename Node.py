class Node(object):
    """
    Defines a node object, a constituent of a hypergraph.

    :param: node_name (str) - the name of thr node 
    :param: node_type (str) - the type of the node
    """

    def __init__(self, node_name : str, node_type : str):
        assert isinstance(node_name, str), "Arg Error: node_name must be of type str"
        assert isinstance(node_type, str), "Arg Error: node_type must be of type str"
        self.name = node_name
        self.type = node_type
        self.first_visit = True
        self.ave_hitting_time = float('inf')
        self.sample_paths = dict()

    def __str__(self):
        return self.name

    def reset(self):
        """
        Resets node properties to their default value.
        """
        self.ave_hitting_time = float('inf')
        self.sample_paths = dict()
        self.first_visit = True

    def update(self, max_length : int, walk_number : int):
        """
        Updates node properties after a random walk is complete.
        """
        if self.first_visit == False: 
            if self.ave_hitting_time != float('inf'):
                self.ave_hitting_time += 1/(walk_number) * (max_length - self.ave_hitting_time)
            else:
                #Tuncated average hitting time:
                #set the average hitting time to max_length if the node wasn't visited during the walk
                self.ave_hitting_time = max_length
        
        self.first_visit = True

    def update_ave_hitting_time(self, hitting_time : float, walk_number : int):
        """
        Updates the average hitting time of the node using the most recent 
        hitting time.
        """
        if self.ave_hitting_time == float('inf'):
            self.ave_hitting_time = hitting_time
        else:
            self.ave_hitting_time += 1/(walk_number) * (hitting_time - self.ave_hitting_time)

    def update_sample_paths(self, path : list, walk_number : int):
        """
        Updates the sample paths of the node with the most recent path.
        """
        self.sample_paths[walk_number] = path
