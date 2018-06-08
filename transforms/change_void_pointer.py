"""
int * k = &m;
k = k + 1;

int * k = &m;
k = (int*) (((void*)k) + (1 * sizeof(int)))

sizeof will be replace with a constant
"""

from copy import deepcopy
import pycparser.c_ast as AST
from .lift_node import LiftNode
from .type_helpers import make_temp_ptr, make_temp_value

class Change_to_void_pointer(LiftNode):
    """LiftToCompoundBlock Transform"""

    def visit_BinaryOp(self, node):
        if node.op = '+':
            print('add')
        elif node.op = '-':
            print('subtract')

        self.generic_visit(node)        
        

