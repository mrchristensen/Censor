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
from .type_helpers import get_type, _is_integral, _is_ptr, _is_array
from .sizeof import get_size_ast

class ChangeToVoidPointer(LiftNode):
    """LiftToCompoundBlock Transform"""

    def visit_BinaryOp(self, node):
        self.generic_visit(node)
        
        if node.op == '+':
            self.toVoidPointer(node)
        elif node.op == '-':
            left_type, right_type = self.toVoidPointer(node)
            if (_is_ptr(left_type) or _is_array(left_type)) and (_is_ptr(right_type) or _is_array(right_type)):
                #This should only be allowed when they are both pointing to the same type of object
                #The result should equal the difference in index values of the two pointers
                #left_type.type must be equivalent to right_type.type
                node.right = AST.Cast(AST.Typename(None,[],AST.PtrDecl([],AST.TypeDecl(None,[],AST.IdentifierType(['void'])))),
                                      node.right)
                node.left = AST.Cast(AST.Typename(None,[],AST.PtrDecl([],AST.TypeDecl(None,[],AST.IdentifierType(['void'])))),
                                     node.left)
                ptr_size = get_size_ast(left_type.type)
                node = AST.BinaryOp('/',node,ptr_size)

        return node      
        
    def toVoidPointer(self, node):
        left_type = get_type(node.left,self.envr)
        right_type = get_type(node.right,self.envr)
        if _is_integral(left_type) and (_is_ptr(right_type) or _is_array(right_type)):
            right_type.show()
            ptr_size = get_size_ast(right_type.type)
            node.left = AST.BinaryOp('*',node.left,ptr_size)
            node.right = AST.Cast(AST.Typename(None,[],AST.PtrDecl([],AST.TypeDecl(None,[],AST.IdentifierType(['void'])))),
                                  node.right)
        if _is_integral(right_type) and (_is_ptr(left_type) or _is_array(left_type)):
            left_type.show()
            ptr_size = get_size_ast(left_type.type)
            node.right = AST.BinaryOp('*',node.right,ptr_size)
            node.left = AST.Cast(AST.Typename(None,[],AST.PtrDecl([],AST.TypeDecl(None,[],AST.IdentifierType(['void'])))),
                                 node.left)

        return left_type, right_type

