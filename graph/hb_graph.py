"""Happens Before version of computation graph"""

from graph.graph import Graph

class HBGraph(Graph):
    """Happens Before version of computation graph"""

    def process_log_line(self, line):
        """Processes one line from log file"""
        if line[0] == 'enter':
            self.process_omp_enter(line)
        elif line[0] == 'exit':
            self.process_omp_exit(line)
        elif line[0] == 'clause read':
            self.process_omp_clause_read(line)
        elif line[0] == 'clause write':
            self.process_omp_clause_write(line)
        elif line[0] == 'read':
            self.process_read(line)
        elif line[0] == 'write':
            self.process_write(line)

    def process_omp_enter(self, line):
        """Process one line from log file"""
        pass

    def process_omp_exit(self, line):
        """Process one line from log file"""
        pass

    def process_omp_clause_read(self, line):
        """Process one line from log file"""
        pass

    def process_omp_clause_write(self, line):
        """Process one line from log file"""
        pass

    def process_read(self, line):
        """Process one line from log file"""
        pass

    def process_write(self, line):
        """Process one line from log file"""
        pass
