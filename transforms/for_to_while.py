'''AST transform that transforms a for loop to a while loop'''

from copy import deepcopy
from pycparser.c_ast import While, Compound, Constant, DoWhile, DeclList
from pycparser.c_ast import Assignment, ExprList
from omp.clause import Collapse, Ordered
from .node_transformer import NodeTransformer
from .helpers import append_statement, ensure_compound

_ERROR_MESSAGE = '''Handling the 'collapse' and 'ordered' clauses is not
yet implemented. These clauses change which for loops are being parallelized
in subtle ways that are not yet understood by us, and are not well documented
by OMP. For a start, see the OMP spec at
http://www.openmp.org/wp-content/uploads/openmp-4.5.pdf,
section 2.7.1 'Loop Construct' '''

class ForToWhile(NodeTransformer):
    '''NodeTransformer to change for loops to while loops'''

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        '''Don't transform the omp for loop, but go inside it to transform any
        loops that may be nested inside it.'''
        if any(isinstance(x, (Collapse, Ordered)) for x in node.clauses):
            raise NotImplementedError(_ERROR_MESSAGE)
        node.loops.stmt = ensure_compound(self.visit(node.loops.stmt))
        return node

    def visit_For(self, node): #pylint: disable=invalid-name
        '''Transform a for loop to a while loop'''
        node = self.generic_visit(node)
        cond = transform_loop_condition(node.cond)
        stmt = transform_loop_statement(node.stmt, node.next)
        if node.init is None:
            return While(cond, stmt, node.coord)
        items = []
        if isinstance(node.init, DeclList):
            items = node.init.decls
        elif isinstance(node.init, Assignment):
            items.append(node.init)
        elif isinstance(node.init, ExprList):
            items = node.init.exprs
        else:
            raise NotImplementedError("Unexpected for initializer.")

        items.append(While(cond, stmt, node.coord))
        return Compound(items, node.coord)

def transform_loop_condition(cond):
    '''Transform empty for loop condition to a truthy value for while loop'''
    if cond is None:
        return Constant('int', '1')
    return cond

def transform_loop_statement(stmt, inc):
    '''Transform loop statement by embedding for loop's increment statement'''
    compound = append_statement(stmt, inc)
    if inc is None:
        return compound
    continue_transformer = PrefixContinueWithNext(inc)
    compound = continue_transformer.visit(compound)
    return compound

class PrefixContinueWithNext(NodeTransformer):
    '''NodeTransformer to prefix continue nodes with a statement'''
    def __init__(self, prefix):
        self.prefix = prefix

    def skip(self, node): #pylint: disable=no-self-use
        '''Don't visit child While loops'''
        return isinstance(node, (DoWhile, While))

    def visit_Continue(self, node): #pylint: disable=invalid-name
        '''Prefix continue with prefix node'''
        return Compound([deepcopy(self.prefix), node], node.coord)
