"""
This transform flattens out deep references to structs and multi
dimensional arrays into a line of simple references.

It visits each compound and puts the intermediate references for each
struct and array ref immediately above the original reference in the compound
block.
"""

from pycparser.c_ast import PtrDecl, ID, UnaryOp, Decl
from .flatten_node import FlattenNode
from .type_helpers import get_type, add_identifier

class FlattenRefs(FlattenNode):
    """Transform: flatten nested struct references"""

    def visit_StructRef(self, node): #pylint: disable=invalid-name
        """
        Flatten out reference into several declarations and return a tuple
        of an ID to the last declared variable and the list of declarations
        """
        node = self.generic_visit(node)
        name = self.id_generator.get_unique_id()
        addr = UnaryOp('&', node)
        typ = get_type(node, self.envr)
        ptr = PtrDecl([], add_identifier(typ, name))
        decl = Decl(name, [], [], [], ptr, addr, None)
        self.insert_into_scope(decl)
        self.envr.add(name, ptr)
        return UnaryOp('*', ID(name))
