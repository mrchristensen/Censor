"""
Transforms struct access to equivalent pointer arithmetic

struct a{
    int a;
    int b;
}

int main(){
    struct a tester;
    tester.a;
    tester.b;
}

-->
*((int*)((void*)&tester + 0))
*((int*)((void*)&tester + 2))

"""

from copy import deepcopy
import pycparser.c_ast as AST
from .lift_node import LiftNode
from .type_helpers import get_type
from .helpers import make_unit_pointer, remove_identifier
from .sizeof import get_struct_offset

class StructRefToPointerArith(LiftNode):
    """ Transform all StructRef accessess to void* arithmetic """

    def visit_StructRef(self, node): # pylint: disable=invalid-name
        """ Remove by changing to pointer arithmetic """
        self.generic_visit(node)
        if node.type == '.':
            reference = AST.UnaryOp('&', node.name, node.coord)
            struct_type = get_type(node.name, self.envr).type
        else: #node.type == '->'
            reference = node.name
            struct_type = get_type(node.name, self.envr).type.type
        void_ptr_cast = make_unit_pointer(reference)
        offset, result_type = get_struct_offset(struct_type,
                                                node.field,
                                                self.envr)
        arithmetic = AST.BinaryOp('+', void_ptr_cast, offset, node.coord)

        ptr_to_result = AST.Cast(make_ptr_of_type(deepcopy(result_type)),
                                 arithmetic,
                                 coord=node.coord)
        result = AST.UnaryOp('*', ptr_to_result, coord=node.coord)

        return deepcopy(result)

def make_ptr_of_type(node):
    """ Nests a type in a PtrDecl """
    remove_identifier(node)
    return AST.PtrDecl([], node, coord=node.coord)
