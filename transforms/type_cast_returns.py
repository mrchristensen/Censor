"""
Adds explicit type casts to all return statements
"""
from copy import deepcopy
from pycparser.c_ast import Return, Cast
from .type_helpers import remove_identifier
from .node_transformer import NodeTransformer

class TypeCastReturns(NodeTransformer):
    """Transform to remove all compound assignments from the input program."""

    def __init__(self):
        self.return_type = None

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        """Keep track of the return type of the function definition we
        are currently parsing."""
        self.return_type = deepcopy(node.decl.type.type)
        remove_identifier(self.return_type)
        return self.generic_visit(node)

    def visit_Return(self, node): # pylint: disable=invalid-name
        """Wrap return in appropriate type cast."""
        return Return(Cast(self.return_type, node.expr))
