"""Happens Before version of computation graph"""

from graph.graph import Graph

class HBGraph(Graph):
    """Happens Before version of computation graph"""

    def process_omp_enter(self, line):
        """Process one line from log file"""
        raise NotImplementedError

    def process_omp_exit(self, line):
        """Process one line from log file"""
        raise NotImplementedError

    def process_omp_clause_read(self, line):
        """Process one line from log file"""
        raise NotImplementedError

    def process_omp_clause_write(self, line):
        """Process one line from log file"""
        raise NotImplementedError

    def process_read(self, line):
        """Process one line from log file"""
        raise NotImplementedError

    def process_write(self, line):
        """Process one line from log file"""
        raise NotImplementedError
