"""
Transform to remove all compound assignments such as "a += 4.5;" from the
input program. It is useful to have these removed because it is impossible to
annotate explicitly the type casts in a program such as.

int a = 1;
a += 4.5;

However, if the program is transformed to

int a = 1;
{
    int* $1 = &a;
    *$1 = *$1 + 4.5;
}

then it can be annotated with explicit type casts as follow:

int a = 1;
{
    int* $1 = &a;
    *$1 = (int) ((float)*$1 + (float)4.5);
}

We can do this because any lvalue in C can be resolved to an address except
for two cases: variables marked as register, which we can, as an
implementation, safely ignore, and bit-fields, which we do not support.
TODO: see if bit-fields can be ignored by an implementation that is still
standard-compliant.
"""
from copy import deepcopy
from pycparser.c_ast import Decl, UnaryOp, BinaryOp, Assignment, Compound, ID, PtrDecl
from .helpers import IDGenerator
from .type_helpers import get_type, Envr, remove_identifier, add_identifier
from .node_transformer import NodeTransformer

class RemoveCompoundAssignment(NodeTransformer):
    """Transform to remove all compound assignments from the input program."""

    def __init__(self):
        self.envr = Envr()

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Create a new environment with the current environment as its
        parent so that scoping is handled properly."""
        # print("visiting compound")
        self.envr = Envr(self.envr)
        retval = self.generic_visit(node)
        self.envr = self.envr.parent
        return retval

    def visit_Decl(self, node): #pylint: disable=invalid-name
        """Visit Decl nodes so that we can save type information about
        identifiers in the environment."""
        # print("visiting decl")
        type_node = deepcopy(node.type)
        ident = remove_identifier(type_node)

        if self.envr.is_locally_defined(ident):
            raise Exception("Error: redefinition of " + ident)

        self.envr.add(ident, type_node)
        # self.envr.show()
        return self.generic_visit(node)

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Visit all Assignment nodes and get rid of the compound ones."""
        if node.op == '=':
            return self.generic_visit(node)

        temp_name = IDGenerator.get_unique_id()
        lvalue_addr = UnaryOp('&', node.lvalue)

        lvalue_type = get_type(node.lvalue, self.envr)

        ptr_to_lvalue = PtrDecl([], add_identifier(lvalue_type, temp_name))
        first_line = Decl(temp_name, [], [], [], ptr_to_lvalue, lvalue_addr, None)

        dereferenced_temp_name = UnaryOp('*', ID(temp_name))
        operation = BinaryOp(node.op[:-1], dereferenced_temp_name, node.rvalue)
        second_line = Assignment('=', dereferenced_temp_name, operation)

        return Compound([first_line, second_line])
