"""Ternary to If transform"""

from pycparser.c_ast import If, Assignment, ID
from .lift_node import LiftNode
from .type_helpers import make_temp_value

class TernaryToIf(LiftNode):
    """
    Transform to do two things.
    Lift ternary operators out of inline locations.
    Transform them into if statements
    """

    def visit_TernaryOp(self, node): # pylint: disable=invalid-name
        """Transform Ternary to If"""
        # TODO currently not supporting the use of unitialized ids in the ternary operator
        # gcc only throws a warning if you write something like this
        # char* str = expr ? expr : str;
        # even though the 'str' id might be used unitialized.
        node = self.generic_visit(node)
        decl = make_temp_value(node, self.id_generator, self.envr)
        decl.init = None
        ident = decl.name
        self.envr.add(ident, decl.type)
        iftrue = Assignment('=', ID(ident), node.iftrue)
        iffalse = Assignment('=', ID(ident), node.iffalse)
        if_node = If(node.cond, iftrue, iffalse)
        self.insert_into_scope(decl, if_node)
        return ID(ident)
