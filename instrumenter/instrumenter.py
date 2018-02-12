"""Instrumenter class for traversing anc instrumenting an AST"""
from transforms.node_transformer import NodeTransformer


class Instrumenter(NodeTransformer):
    """Instrumenter class"""
    def __init__(self):
        pass

    def visit_While(self, node): #pylint: disable=invalid-name
        """Visit a while loop"""
        self.generic_visit(node)
        node.show()
        print('Visiting a While')

    def visit_For(self, node): #pylint: disable=invalid-name
        """Visit a while loop"""
        self.generic_visit(node)
        node.show()
        print('Visiting a For')
