"""AST transform that transforms a break to goto"""

from pycparser.c_ast import Goto, Label, EmptyStatement
from .node_transformer import NodeTransformer
from .lift_node import LiftNode

class BreakToGoto(LiftNode):
    """Transform to change break statements to goto code"""

    def visit_DoWhile(self, node): #pylint: disable=invalid-name
        """for each DoWhile, look for break statements"""
        return self.visit_loop(node)

    def visit_While(self, node): #pylint: disable=invalid-name
        """ While breaks """
        return self.visit_loop(node)

    def visit_loop(self, node):
        """ general function for removing breaks """
        node = self.generic_visit(node)
        break_placer = BreakPlacer(self.id_generator)
        node = break_placer.generic_visit(node)
        if break_placer.label is not None:
            self.append_to_scope(Label(break_placer.label,
                                       EmptyStatement(coord=node.coord),
                                       coord=node.coord))
        return node

class BreakPlacer(NodeTransformer):
    """NodeTransformer to change break statements to goto statements"""

    def __init__(self, id_generator):
        self.id_generator = id_generator
        self.label = None

    def visit_Break(self, node): #pylint: disable=invalid-name
        """Replace continue with goto statement"""
        if self.label is None:
            self.label = self.id_generator.get_unique_id()
        return Goto(self.label, coord=node.coord)

    def visit_DoWhile(self, node): #pylint: disable=invalid-name, no-self-use
        """Prevents visiting more loops"""
        return node # don't visit more loops
