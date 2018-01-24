"""Helper classes and functions for testing"""

from pycparser.c_ast import NodeVisitor

class ForVisitor(NodeVisitor):
    """Basic For loop visitor"""
    def __init__(self):
        self.nodes = []
    def visit_For(self, node): #pylint: disable=invalid-name
        """Gather For nodes"""
        self.nodes.append(node)

class WhileVisitor(NodeVisitor):
    """Basic While loop visitor"""
    def __init__(self):
        self.nodes = []
    def visit_While(self, node): #pylint: disable=invalid-name
        """Gather While nodes"""
        self.nodes.append(node)
