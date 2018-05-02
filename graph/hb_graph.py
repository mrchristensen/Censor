"""Happens Before version of computation graph"""

from graph.graph import Graph

class HBGraph(Graph):
    """Happens Before version of computation graph"""

    def process_post(self, task_id, parent_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_isolated(self, task_id, parent_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_await(self):
        """Process one line from log file"""
        raise NotImplementedError

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
        raise NotImplementedError

    def process_write(self, addr, task_id):
        """Process one line from log file"""
        raise NotImplementedError
