"""Computation Graph"""

import csv
from collections import OrderedDict

def task_ids(line):
    """Parse out arguments for processing isolated and post"""
    task_id = line[1].strip()
    parent_id = line[2].strip()
    return (task_id, parent_id)

def read_write_args(line):
    """Parse out arguments for processing reads and writes"""
    addr = line[1].strip()
    task_id = int(line[2].strip())
    return (addr, task_id)

class Node():
    """Computation Graph Node"""

    def __init__(self):
        self.reads = []
        self.writes = []

    def __str__(self):
        len_reads = len(self.reads)
        len_writes = len(self.writes)
        return 'N(%s,%s)' % (len_reads, len_writes)

    def add_read(self, addr, task_id):
        """Adds memory access to reads array"""
        self.reads.append((addr, task_id))

    def add_write(self, addr, task_id):
        """Adds memory access to writes array"""
        self.writes.append((addr, task_id))

class Graph():
    """Computation Graph Base class"""

    def __init__(self):
        self.nodes = OrderedDict()
        self.task_to_node = OrderedDict()

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
        self.nodes[node] = []

    def add_edge(self, from_node, to_node):
        """Adds directed edge between nodes"""
        if from_node not in self.nodes or to_node not in self.nodes:
            raise KeyError('Node not in graph')
        self.nodes[from_node].append(to_node)

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
        if line[0] == 'post':
            self.process_post(*task_ids(line))
        elif line[0] == 'isolated':
            self.process_isolated(*task_ids(line))
        elif line[0] == 'await':
            self.process_await()
        elif line[0] == 'ewait':
            self.process_ewait()
        elif line[0] == 'clause read':
            self.process_omp_clause_read(*read_write_args(line))
        elif line[0] == 'clause write':
            self.process_omp_clause_write(*read_write_args(line))
        elif line[0] == 'read':
            self.process_read(*read_write_args(line))
        elif line[0] == 'write':
            self.process_write(*read_write_args(line))

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
        raise NotImplementedError

    def process_omp_clause_write(self, addr, task_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_read(self, addr, task_id):
        """Process one line from log file"""
        raise NotImplementedError

    def process_write(self, addr, task_id):
        """Process one line from log file"""
        raise NotImplementedError
