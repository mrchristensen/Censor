"""AST transform that transforms a for loop to a while loop"""

from pycparser.c_ast import While
from .ast_transform import ASTTransform

class ForToWhile(ASTTransform): #pylint: disable=too-few-public-methods
    """ASTTransform to change for loops to while loops"""

    def transform(self, node):
        """Transform a for loop to a while loop"""
        #TODO implement transform
        #TODO rename iteration variable because it might conflict
        #with other declarations in the outer scope
        return While(node.cond, node.stmt, node.coord)
