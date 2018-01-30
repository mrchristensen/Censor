"""AST transform that transforms a do-while loop to goto code"""

from pycparser.c_ast import If, Goto, Label
from .node_transformer import NodeTransformer
from .helpers import append_statement

class DoWhileToGoto(NodeTransformer):
    """NodeTransformer to change do-while loops to goto code"""

    def __init__(self):
        self.index = 0

    def visit_DoWhile(self, node): #pylint: disable=invalid-name
        """Transform a do-while loop to goto code"""
        node = self.generic_visit(node)
        label = 'censor' + str(self.index)
        if_node = If(node.cond, Goto(label), None)
        body = append_statement(node.stmt, if_node)
        continue_transformer = ContinueToGoto(label)
        body = continue_transformer.visit(body)
        return Label(label, body)

class ContinueToGoto(NodeTransformer):
    """NodeTransformer to change continue statements to goto statements"""

    def __init__(self, label):
        self.label = label

    def visit_Continue(self, _): #pylint: disable=invalid-name
        """Replace continue with goto statment"""
        return Goto(self.label)
