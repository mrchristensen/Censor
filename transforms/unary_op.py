""" AST transform: unary ops in expressions such as:

    sizeof is replaced by its constant equivalent
    int x = sizeof(long long)
    -->
    int x = 8;

"""

from copy import deepcopy
from .lift_node import LiftNode
from .type_helpers import get_type, make_temp_value
from .sizeof import get_size_ast
import pycparser.c_ast as AST
# from .type_helpers import get_no_op
# from .helpers import ensure_compound

class LiftUnaryOp(LiftNode):
    """ Tranforms unary operators into another equivalent AST"""

    def visit_UnaryOp(self, node): #pylint: disable=invalid-name
        """ Special parsing of UnaryOp AST nodes """
        #  Recursively remove Unary Ops
        if node.op == 'sizeof':
            type_node = get_type(node.expr, self.envr)
            #type_node = node.expr
            return get_size_ast(type_node, self.envr)

        node.expr = self.generic_visit(node.expr)
        if node.op == '!':
            raise NotImplementedError()
        elif node.op in ['++', '--', 'p--', 'p++']:
            return self.inc_and_dec(node)
        elif node.op in ['+', '-', '~']:
            raise NotImplementedError()
        elif node.op in ['&', '*']:
            node.expr = self.visit(node.expr)
            return node
        else:
            raise NotImplementedError()

    def inc_and_dec(self, node):
        """ handles transforming pre and post increment and decrement op """
        if node.op == 'p++':
            decl = make_temp_value(node.expr, self.id_generator, self.envr)
            binop = AST.BinaryOp('+', deepcopy(node.expr), constant_one())
            inc = AST.Assignment('=', deepcopy(node.expr), binop)
            self.insert_into_scope(decl, inc)
            self.envr.add(decl.name, decl.type)
            node = AST.ID(decl.name)
        elif node.op == 'p--':
            decl = make_temp_value(node.expr, self.id_generator, self.envr)
            binop = AST.BinaryOp('-', deepcopy(node.expr), constant_one())
            inc = AST.Assignment('=', deepcopy(node.expr), binop)
            self.insert_into_scope(decl, inc)
            self.envr.add(decl.name, decl.type)
            node = AST.ID(decl.name)
        elif node.op == '++':
            binop = AST.BinaryOp('+', deepcopy(node.expr), constant_one())
            inc = AST.Assignment('=', deepcopy(node.expr), binop)
            self.insert_into_scope(inc)
            node = node.expr
        elif node.op == '--':
            binop = AST.BinaryOp('-', deepcopy(node.expr), constant_one())
            inc = AST.Assignment('=', deepcopy(node.expr), binop)
            self.insert_into_scope(inc)
            node = node.expr
        return node

def constant_one():
    """ return the number 1 as an ast constant """
    return AST.Constant('int', '1')
