"""
This transform flattens out deep references to structs and multi
dimensional arrays into a line of simple references.

It visits each compound and puts the intermediate references for each
struct and array ref immediately above the original reference in the compound
block.
"""

from pycparser.c_ast import StructRef, ArrayRef, PtrDecl, ID, UnaryOp, Decl
from .node_transformer import NodeTransformer
from .type_helpers import get_type, add_identifier

class FlattenRefs(NodeTransformer):
    """Transform: flatten nested struct references"""

    def __init__(self, id_generator, environments):
        super().__init__()
        self.environments = environments
        self.envr = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.envr
        self.envr = self.environments[node]
        retval = self.generic_visit(node)
        self.envr = parent
        return retval

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """
        Flatten struct and array references in Assignment nodes
        """
        (node.lvalue, ldecls) = self.flatten_ref(node.lvalue)
        (node.rvalue, rdecls) = self.flatten_ref(node.rvalue)
        return ldecls + rdecls + [node]

    def flatten_ref(self, node):
        """
        Flatten out reference into several declarations and return a tuple
        of an ID to the last declared variable and the list of declarations
        """
        decls = []
        if isinstance(node, (StructRef, ArrayRef)):
            (node.name, decls) = self.flatten_ref(node.name)
            name = self.id_generator.get_unique_id()
            addr = UnaryOp('&', node)
            typ = get_type(node, self.envr)
            ptr = PtrDecl([], add_identifier(typ, name))
            decl = Decl(name, [], [], [], ptr, addr, None)
            decls.append(decl)
            self.envr.add(name, ptr)
            node = UnaryOp('*', ID(name))
        return (node, decls)
