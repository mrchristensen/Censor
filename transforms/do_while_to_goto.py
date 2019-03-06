"""AST transform that transforms a do-while loop to goto code"""

from pycparser.c_ast import If, Goto, Label
from .node_transformer import NodeTransformer
from .helpers import append_statement

class DoWhileToGoto(NodeTransformer):
    """NodeTransformer to change do-while loops to goto code"""

    def __init__(self, id_generator):
        self.index = 0
        self.id_generator = id_generator

    def visit_DoWhile(self, node): #pylint: disable=invalid-name
        """Transform a do-while loop to goto code"""
        label = self.id_generator.get_unique_id()
        self.index += 1
        node = self.generic_visit(node)
        if_node = If(node.cond, Goto(label, coord=node.coord), None,
                     coord=node.coord)
        body = append_statement(node.stmt, if_node)
        continue_transformer = ContinueToGoto(label)
        body = continue_transformer.visit(body)
        return Label(label, body, coord=node.coord)

class ContinueToGoto(NodeTransformer):
    """NodeTransformer to change continue statements to goto statements"""

    def __init__(self, label):
        self.label = label

    def visit_Continue(self, node): #pylint: disable=invalid-name
        """Replace continue with goto statment"""
        return Goto(self.label, coord=node.coord)
