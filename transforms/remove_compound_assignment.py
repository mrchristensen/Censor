"""
Transform to remove all compound assignments such as "a += 4.5;" from the
input program. It is useful to have these removed because it is impossible to
annotate explicitly the type casts in a program such as.

int a = 1;
a += 4.5;

However, if the program is transformed to

int a = 1;
int* $1 = &a;
*$1 = *$1 + 4.5;

then it can be annotated with explicit type casts as follows:

int a = 1;
int* $1 = &a;
*$1 = (int) ((float)*$1 + (float)4.5);

We can do this because any lvalue in C can be resolved to an address except
for two cases: variables marked as register, which we can, as an
implementation, safely ignore, and bit-fields, which we do not support.
"""
from copy import deepcopy
from pycparser.c_ast import UnaryOp, BinaryOp, Assignment, ID
from .type_helpers import make_temp_ptr
from .node_transformer import NodeTransformer

class RemoveCompoundAssignment(NodeTransformer):
    """Transform to remove all compound assignments from the input program."""

    def __init__(self, id_generator, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.env
        self.env = self.environments[node]
        retval = self.generic_visit(node)
        self.env = parent
        return retval

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Visit all Assignment nodes and get rid of the compound ones."""
        if node.op == '=':
            return self.generic_visit(node)

        first_line = make_temp_ptr(node.lvalue, self.id_generator, self.env)

        dereferenced_temp_name = UnaryOp('*', ID(first_line.name))
        operation = BinaryOp(node.op[:-1], deepcopy(dereferenced_temp_name), node.rvalue)
        second_line = Assignment('=', dereferenced_temp_name, operation)

        return [first_line, second_line]
