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
"""
from pycparser.c_ast import Decl, UnaryOp, BinaryOp, Assignment, Compound, ID, PtrDecl
from .type_helpers import get_type, add_identifier
from .node_transformer import NodeTransformer

class RemoveCompoundAssignment(NodeTransformer):
    """Transform to remove all compound assignments from the input program."""

    def __init__(self, id_generator, environments):
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
        """Visit all Assignment nodes and get rid of the compound ones."""
        # print("----------------"); node.show()
        if node.op == '=':
            return self.generic_visit(node)

        temp_name = self.id_generator.get_unique_id()
        lvalue_addr = UnaryOp('&', node.lvalue)

        lvalue_type = get_type(node.lvalue, self.envr)

        ptr_to_lvalue = PtrDecl([], add_identifier(lvalue_type, temp_name))
        # ptr_to_lvalue.show()
        first_line = Decl(temp_name, [], [], [], ptr_to_lvalue, lvalue_addr, None)

        dereferenced_temp_name = UnaryOp('*', ID(temp_name))
        operation = BinaryOp(node.op[:-1], dereferenced_temp_name, node.rvalue)
        second_line = Assignment('=', dereferenced_temp_name, operation)

        return Compound([first_line, second_line])
