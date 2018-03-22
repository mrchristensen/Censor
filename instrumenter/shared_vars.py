"""SharedVars helpers"""

from pycparser.c_ast import ID
from transforms.node_transformer import NodeTransformer

class WithSharedVars(NodeTransformer):
    """
    NodeTransformer base class that has helper methods defined
    for dealing with shared variables
    """
    def __init__(self, ast):
        self.scopes = SharedVarsVisitor().visit(ast)
        self.shared_vars = self.scopes["GLOBAL"]

    def is_shared(self, ident):
        """Return true if variable is shared in scope"""
        return self.shared_vars.contains(ident)

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Set environment for shared variables"""
        old_shared_vars = self.shared_vars
        self.shared_vars = self.scopes[node]
        retval = self.generic_visit(node)
        self.shared_vars = old_shared_vars
        return retval

class SharedVars():
    """Holds the environment of shared variables"""

    def __init__(self, parent=None):
        self.parent = parent
        self.vars = set()

    def add(self, ident):
        """Add an identifier as a shared variable to the current scope"""
        if not isinstance(ident, ID):
            raise ValueError
        self.vars.add(ident.name)

    def contains(self, ident):
        """Return true if ident resolves to a shared variable in the current scope"""
        if not isinstance(ident, ID):
            raise ValueError
        return ident in self.vars

class WithParent(NodeTransformer):
    """Node transformer that keeps track of parent nodes"""
    def __init__(self):
        self.parent = None

    def generic_visit(self, node):
        """Visit each child and set parent"""
        old_parent = self.parent
        self.parent = node
        node = super().generic_visit(node)
        self.parent = old_parent
        return node

def private_ids(omp):
    """Return list of identifiers made private by parent Omp node"""
    ids = []
    klass = omp.__class__.__name__
    if 'Omp' in klass and hasattr(omp, 'clauses'):
        for key in ['private']:
            if key in omp.clauses:
                ids.extend(omp.clauses[key])
    return ids

class SharedVarsVisitor(WithParent):
    """
    Returns a SharedVars for the AST.

    This transform should be a visitor but inherits from node transformer
    because it needs to support Omp* nodes.

    It works by visiting each scope in a depth first fashion and finding
    ID nodes that don't have a matching Decl node in the same scope.
    If there isn't a clause on a parent Omp node then that variable is shared
    in the scope.

    TODO: implement visit method(s).
    TODO: handle functions in a smart way
    TODO: only visit parallel regions
    """
    def __init__(self):
        super().__init__()
        self.scope = SharedVars()
        self.scopes = {"GLOBAL": self.scope}

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Visit each scope and add to the environment"""
        self.scope = SharedVars(self.scope)
        retval = self.generic_visit(node)
        self.scopes[node] = self.scope
        self.scope = self.scope.parent
        return retval
