"""AST transform that transforms a for loop to a while loop"""

from pycparser.c_ast import While
from .node_transformer import NodeTransformer

class ForToWhile(NodeTransformer): #pylint: disable=too-few-public-methods
    """ASTTransform to change for loops to while loops"""

    def visit_For(self, node): #pylint: disable=invalid-name,no-self-use
        """Transform a for loop to a while loop"""
        #TODO: handle node.init field
        #need to put it in an outer scope without conflicts
        node = self.generic_visit(node)
        return While(node.cond, node.stmt, node.coord)
