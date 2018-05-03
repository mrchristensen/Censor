"""Happens Before version of computation graph"""

from graph.graph import Graph, Node

class HBGraph(Graph):
    """Happens Before version of computation graph"""

    def process_post(self, task_id, parent_id):
        """Process one line from log file"""
        node = Node()
        parent = self.task_to_node[parent_id]
        self.task_to_node[task_id] = node
        self.add_node(node)
        self.add_edge(parent, node)

    def process_isolated(self, task_id, parent_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_await(self):
        """Process one line from log file"""
        # TODO verify this is correct
        # Create new node to join tasks
        # Find all nodes with no outgoing edges
        # Order all those nodes to happen before
        # the joining node
        join_node = Node()
        nodes = [n for n in self.nodes.keys() if not self.nodes[n]]
        self.add_node(join_node)
        for node in nodes:
            self.add_edge(node, join_node)


    def process_ewait(self):
        """Process one line from log file"""
        raise NotImplementedError

    def process_omp_clause_read(self, addr, task_id):
        """Process one line from log file"""
        self.process_read(addr, task_id)

    def process_omp_clause_write(self, addr, task_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_read(self, addr, task_id):
        """Process one line from log file"""
        self.task_to_node[task_id].add_read(addr)

    def process_write(self, addr, task_id):
        """Process one line from log file"""
        self.task_to_node[task_id].add_write(addr)
