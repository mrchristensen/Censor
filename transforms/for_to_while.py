"""AST transform that transforms a for loop to a while loop"""

from pycparser.c_ast import While, Compound, ID
from .node_transformer import NodeTransformer

class ForToWhile(NodeTransformer): #pylint: disable=too-few-public-methods
    """NodeTransformer to change for loops to while loops"""

    def visit_For(self, node): #pylint: disable=invalid-name
        """Transform a for loop to a while loop"""
        node = self.generic_visit(node)
        cond = transform_loop_condition(node.cond)
        stmt = transform_loop_statement(node.stmt, node.next)
        if node.init is None:
            return While(cond, stmt, node.coord)
        return Compound([
            node.init,
            While(cond, stmt, node.coord)
            ])

def transform_loop_condition(cond):
    """Transform empty for loop condition to a truthy value for while loop"""
    if cond is None:
        return ID("true")
    return cond

def transform_loop_statement(stmt, inc):
    """Transform for loop statement by incorporating for loop's increment statement"""
    if stmt is None:
        return Compound([inc])
    elif not isinstance(stmt, Compound):
        return do_transform_loop_statement([stmt], inc)
    return do_transform_loop_statement(stmt.block_items, inc)

def do_transform_loop_statement(items, inc):
    """Embed increment statement into list of statements"""
    if items is None:
        items = []
    compound = Compound(items)
    if inc is None:
        return compound
    continue_transformer = PrefixContinueWithNext(inc)
    compound = continue_transformer.visit(compound)
    compound.block_items.append(inc)
    return compound

class PrefixContinueWithNext(NodeTransformer):
    """NodeTransformer to prefix continue nodes with a statement"""
    # TODO: replace continues with goto statement?
    def __init__(self, prefix):
        self.prefix = prefix

    def skip(self, node): #pylint: disable=no-self-use
        """Don't visit child While loops"""
        return isinstance(node, While)

    def visit_Continue(self, node): #pylint: disable=invalid-name
        """Prefix continue with prefix node"""
        return Compound([self.prefix, node])
