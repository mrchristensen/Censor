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

# pylint: disable=no-self-use
class ChangeToVoidPointer(LiftNode):
    """ Transforms all pointer arithmetic to void* arithmetic """

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        """ Looks for pointer arithmetic within BinaryOp ast """
        self.generic_visit(node)
        if node.op == '+':
            left_type, right_type, node = self.arithmetic_to_void_pointer(node)
            if (_is_integral(left_type) and
                    (_is_ptr(right_type) or _is_array(right_type))):
                if _is_array(right_type):
                    node.right = self.add_reference_array(node.right)
                ptr_size = get_size_ast(right_type.type, self.envr)
                if ptr_size.value != '1':
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
        elif node.op == '=':
            if isinstance(node.right, AST.ID):
                right_type = get_type(node.right, self.envr)
                if _is_array(right_type):
                    node.right = self.add_reference_array(node.right)
        return node

    def visit_Cast(self, node): #pylint: disable=invalid-name
        """ Make sure to get the address of the array
            maybe to chummy with the cesk interpreter """
        self.generic_visit(node)
        if isinstance(node.expr, AST.ID):
            expr_type = get_type(node.expr, self.envr)
            if _is_array(expr_type):
                node.expr = self.add_reference_array(node.expr)
        return node

    def visit_FuncCall(self, node): #pylint: disable=invalid-name
        """ To make sure array id's are referenced when passed as a parameter
            This is a nicety for the cesk interpreter """
        node = self.generic_visit(node)
        if node.args is None:
            return node
        for index, param in enumerate(node.args.exprs):
            param_type = get_type(param, self.envr)
            if _is_array(param_type):
                node.args.exprs[index] = self.add_reference_array(param)
        return node

    def add_reference_array(self, node):
        """ Because the interpreter see only an id or memory access at a
            location add the reference to get the location explicity """
        #TODO does not work for arrays that are parametersi
        #b/c arrays are incorrectly typed as arrays when they are pointers
        return AST.UnaryOp('&', node) #cesk interpreter needs
        #return node #more correct for type reasons

    def arithmetic_to_void_pointer(self, node):
        """ transforms binops of the from ptr + 8 or ptr - 10 """
        left_type = get_type(node.left, self.envr)
        right_type = get_type(node.right, self.envr)
        if (_is_integral(right_type) and
                (_is_ptr(left_type) or _is_array(left_type))):
            if _is_array(left_type):
                node.left = self.add_reference_array(node.left)
            ptr_size = get_size_ast(left_type.type, self.envr)
            if not isinstance(ptr_size, AST.Constant) or ptr_size.value != '1':
                node.right = AST.BinaryOp('*', node.right, ptr_size)
                node.left = make_void_pointer(node.left)
                node = AST.Cast(AST.PtrDecl([], left_type.type), node)
        return left_type, right_type, node

def make_void_pointer(node):
    """ helper function to nest a pointer in a void* cast """
    void_id = AST.IdentifierType(['void'])
    void_ptr_type = AST.PtrDecl([], AST.TypeDecl(None, [], void_id))
    return AST.Cast(AST.Typename(None, [], void_ptr_type), node)
