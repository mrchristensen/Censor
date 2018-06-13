"""
int * k = &m;
k = k + 1;

int * k = &m;
k = (int*) (((void*)k) + (1 * sizeof(int)))

sizeof will be replace with a constant
"""
import pycparser.c_ast as AST
from .lift_node import LiftNode
from .type_helpers import get_type, _is_integral, _is_ptr, _is_array
from .sizeof import get_size_ast

class ChangeToVoidPointer(LiftNode):
    """ Transforms all pointer arithmetic to void* arithmetic """

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        """ Looks for pointer arithmetic within BinaryOp ast """
        self.generic_visit(node)

        if node.op == '+':
            left_type, right_type, node = self.arithmetic_to_void_pointer(node)
            if (_is_integral(left_type) and
                    (_is_ptr(right_type) or _is_array(right_type))):
                ptr_size = get_size_ast(right_type.type, self.envr)
                node.left = AST.BinaryOp('*', node.left, ptr_size)
                node.right = make_void_pointer(node.right)
                node = AST.Cast(AST.PtrDecl([], right_type.type), node)
        elif node.op == '-':
            left_type, right_type, node = self.arithmetic_to_void_pointer(node)
            if ((_is_ptr(left_type) or _is_array(left_type)) and
                    (_is_ptr(right_type) or _is_array(right_type))):
                #This should only be allowed when they are both pointing to the
                # same type of object. The result should equal the difference
                # in index values of the two pointers
                # left_type.type must be equivalent to right_type.type
                node.left = make_void_pointer(node.left)
                node.right = make_void_pointer(node.right)
                ptr_size = get_size_ast(left_type.type, self.envr)
                node = AST.BinaryOp('/', node, ptr_size)

        return node

    def arithmetic_to_void_pointer(self, node):
        """ transforms binops of the from ptr + 8 or ptr - 10 """
        left_type = get_type(node.left, self.envr)
        right_type = get_type(node.right, self.envr)
        if (_is_integral(right_type) and
                (_is_ptr(left_type) or _is_array(left_type))):
            ptr_size = get_size_ast(left_type.type, self.envr)
            node.right = AST.BinaryOp('*', node.right, ptr_size)
            node.left = make_void_pointer(node.left)
            node = AST.Cast(AST.PtrDecl([], left_type.type), node)

        return left_type, right_type, node

def make_void_pointer(node):
    """ helper function to nest a pointer in a void* cast """
    void_id = AST.IdentifierType(['void'])
    void_ptr_type = AST.PtrDecl([], AST.TypeDecl(None, [], void_id))
    return AST.Cast(AST.Typename(None, [], void_ptr_type), node)
