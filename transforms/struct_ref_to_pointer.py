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
from .change_void_pointer import make_void_pointer
from .sizeof import get_struct_offset

class StructRefToPointerArith(LiftNode):
    """ Transform all StructRef accessess to void* arithmetic """

    def visit_StructRef(self, node): # pylint: disable=invalid-name
        """ Remove by changing to pointer arithmetic """
        self.generic_visit(node)
        if node.type == '.':
            reference = AST.UnaryOp('&', node.name)
            struct_type = get_type(node.name, self.envr).type
        else: #node.type == '->'
            reference = node.name
            struct_type = get_type(node.name, self.envr).type.type
        void_ptr_cast = make_void_pointer(reference)
        offset, result_type = get_struct_offset(struct_type,
                                                node.field,
                                                self.envr)
        arithmetic = AST.BinaryOp('+', void_ptr_cast, offset)

        ptr_to_result = AST.Cast(make_ptr_of_type(result_type), arithmetic)
        result = AST.UnaryOp('*', ptr_to_result)

        return deepcopy(result)

def make_ptr_of_type(node):
    """ Nests a type in a PtrDecl """
    if isinstance(node, AST.TypeDecl):
        node.declname = None
    elif isinstance(node, AST.ArrayDecl):
        node.type.declname = None
    return AST.PtrDecl([], node)
