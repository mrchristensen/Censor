"""Computation Graph"""

import csv
from collections import OrderedDict

class Node():
    """Computation Graph Node"""

    def __init__(self):
        self.reads = []
        self.writes = []

    def __str__(self):
        len_reads = len(self.reads)
        len_writes = len(self.writes)
        return 'N(%s,%s)' % (len_reads, len_writes)

    def add_read(self, addr, thread_num):
        """Adds memory access to reads array"""
        self.reads.append((addr, thread_num))

    def add_write(self, addr, thread_num):
        """Adds memory access to writes array"""
        self.writes.append((addr, thread_num))

class Graph():
    """Computation Graph Base class"""

    def __init__(self):
        self.nodes = OrderedDict()
        self.current_node = None

    def __str__(self):
        if not self.nodes:
            return 'Empty DAG'
        names = {}
        name = 0
        for node in self.nodes:
            names[node] = name
            name += 1
        graph = ''
        for node in self.nodes:
            graph += str(names[node])
            graph += ": %s => " % (node)
            graph += ', '.join(map(lambda n: str(names[n]), self.nodes[node]))
            graph += "\n"
        return graph

    def add_node(self, node):
        """Adds node to graph"""
        self.nodes[node] = set()

    def add_edge(self, from_node, to_node):
        """Adds directed edge between nodes"""
        if from_node not in self.nodes or to_node not in self.nodes:
            raise KeyError('Node not in graph')
        self.nodes[from_node].add(to_node)

    def has_race(self):
        """Returns true if a race can be proven"""
        raise NotImplementedError

    def from_log_file(self, log_path):
        """Builds graph from log file"""
        with open(log_path) as log_file:
            log = csv.reader(log_file)
            for line in log:
                self.process_log_line(line)

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
