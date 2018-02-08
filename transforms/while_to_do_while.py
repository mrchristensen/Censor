"""AST transform that transforms a while loop to a do-while loop"""

from pycparser.c_ast import DoWhile, If
from .node_transformer import NodeTransformer

class WhileToDoWhile(NodeTransformer):
    """NodeTransformer to change while loops to do-while loops"""

    def __init__(self):
        pass

    def visit_While(self, node): #pylint: disable=invalid-name
        """Transform a while loop to a do-while loop"""
        node = self.generic_visit(node)
        cond = node.cond
        stmt = node.stmt
        return If(node.cond, DoWhile(cond, stmt, node.coord), None)
