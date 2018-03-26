"""AST transform that transforms a for loop to a while loop"""

from pycparser.c_ast import While, Compound, Constant, DoWhile
from .omp_for import PragmaToOmpFor
from .node_transformer import NodeTransformer
from .helpers import append_statement

class ForToWhile(NodeTransformer):
    """NodeTransformer to change for loops to while loops"""

    def skip(self, node):
        return node is None or isinstance(node, PragmaToOmpFor)

    def visit_For(self, node): #pylint: disable=invalid-name
        """Transform a for loop to a while loop"""
        node = self.generic_visit(node)
        cond = transform_loop_condition(node.cond)
        stmt = transform_loop_statement(node.stmt, node.next)
        if node.init is None:
            return While(cond, stmt, node.coord)
        items = node.init.decls
        items.append(While(cond, stmt, node.coord))
        return Compound(items, node.coord)

def transform_loop_condition(cond):
    """Transform empty for loop condition to a truthy value for while loop"""
    if cond is None:
        return Constant('int', '1')
    return cond

def transform_loop_statement(stmt, inc):
    """Transform loop statement by embedding for loop's increment statement"""
    compound = append_statement(stmt, inc)
    if inc is None:
        return compound
    continue_transformer = PrefixContinueWithNext(inc)
    compound = continue_transformer.visit(compound)
    return compound

class PrefixContinueWithNext(NodeTransformer):
    """NodeTransformer to prefix continue nodes with a statement"""
    def __init__(self, prefix):
        self.prefix = prefix

    def skip(self, node): #pylint: disable=no-self-use
        """Don't visit child While loops"""
        return isinstance(node, (DoWhile, While))

    def visit_Continue(self, node): #pylint: disable=invalid-name
        """Prefix continue with prefix node"""
        return Compound([self.prefix, node])
