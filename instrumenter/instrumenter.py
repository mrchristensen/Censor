"""Instrumenter class for traversing anc instrumenting an AST"""
from ast import NodeTransformer


class Instrumenter(NodeTransformer):
    """Instrumenter class"""
    def __init__(self):
        pass

    def generic_visit(self, node):
        """Performs a generic visit for nodes that aren't explicitly visited"""
        print(node)

    def visit_While(self, node): #pylint: disable=invalid-name
        """Visit a while loop"""
        self.generic_visit(node)
        print('Visiting a While')
