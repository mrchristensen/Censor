""" AST transform: unary ops in expressions such as:

    sizeof is replaced by its constant equivalent
    int x = sizeof(long long)
    -->
    int x = 8;

"""

from .lift_node import LiftNode
from .type_helpers import get_type
from .sizeof import get_size_ast
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
        elif node.op in ['++', '--', '+', '-', '~', 'p--', 'p++']:
            raise NotImplementedError()
        elif node.op == '&':
            return node #do nothing
        elif node.op == '*':
            return node #do nothing
        else:
            raise NotImplementedError()
