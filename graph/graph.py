"""Computation Graph"""

import csv

class Node():
    """Computation Graph Node"""

    def __init__(self):
        self.reads = []
        self.writes = []

    def add_read(self, addr, thread_num):
        """Adds memory access to reads array"""
        self.reads.append((addr, thread_num))

    def add_write(self, addr, thread_num):
        """Adds memory access to writes array"""
        self.writes.append((addr, thread_num))

class Graph():
    """Computation Graph Base class"""

    def __init__(self):
        self.nodes = {}

    def from_log_file(self, log_path):
        """Builds graph from log file"""
        with open(log_path) as log_file:
            log = csv.reader(log_file)
            for line in log:
                self.process_log_line(line)

    def process_log_line(self, line):
        """Processes one line from log file"""
        raise NotImplementedError('Abstract method')

    def add_node(self, node):
        """Adds node to graph"""
        self.nodes[node] = set()

    def add_edge(self, from_node, to_node):
        """Adds directed edge between nodes"""
        if from_node not in self.nodes or to_node not in self.nodes:
            raise KeyError('Node not in graph')
        self.nodes[from_node].add(to_node)
