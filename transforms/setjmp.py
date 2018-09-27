'''
    setjmp(lvalue);

    is changed to:

    setjmp(&lvalue);
 '''
from pycparser.c_ast import UnaryOp
from .node_transformer import NodeTransformer

class Setjmp(NodeTransformer):
    """ Adds & to setjmp parameters"""

    def visit_FuncCall(self, node): # pylint: disable=invalid-name
        """Adds & to setjmp parameters"""
        if node.name.name == 'setjmp':
            node.args.exprs[0] = UnaryOp('&', node.args.exprs[0])
        return node
