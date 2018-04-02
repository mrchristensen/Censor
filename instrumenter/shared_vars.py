"""SharedVars helpers"""

from pycparser.c_ast import ID, Compound, NodeVisitor, DeclList, Assignment, For
from omp.omp_ast import OmpParallel
from omp.clause import Private, FirstPrivate, LastPrivate
from transforms.node_transformer import NodeTransformer
from transforms.helpers import WithParent

def private_ids(omp):
    """Return list of identifiers made private by parent Omp node"""
    ids = []
    klass = omp.__class__.__name__
    if 'Omp' in klass and hasattr(omp, 'clauses'):
        #TODO verify that I am handling all the right clauses
        for clause in omp.clauses:
            for clause_klass in [Private, FirstPrivate, LastPrivate]:
                if isinstance(clause, clause_klass):
                    ids.extend(clause.ids)
    return ids

class SharedVars():
    """Holds the environment of shared variables"""

    def __init__(self, parent=None):
        self.parent = parent
        self.vars = set()

    def update(self, ids):
        """Add a set of ids as shared variables to the current scope"""
        self.vars.update(ids)

    def contains(self, ident):
        """Return true if ident resolves to a shared variable in the current
        scope"""
        if isinstance(ident, ID):
            ident = ident.name
        return ident in self.vars

class DeclVisitor(NodeVisitor):
    """Used to update state: locals, aliases"""
    def __init__(self):
        self.locals = set()
        self.aliases = set()

    def skip(self, node): # pylint: disable=no-self-use
        """Only visit current scope"""
        return node is None or isinstance(node, (For, Compound))

    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Update state: locals, aliases"""
        #TODO: update aliases
        self.locals.add(node.name)

class IDVisitor(NodeVisitor):
    """Used to update state: scope"""
    def __init__(self, whitelist):
        self.whitelist = whitelist
        self.shared = set()

    def skip(self, node): # pylint: disable=no-self-use
        """Only visit current scope"""
        return node is None or isinstance(node, (For, Compound))

    def visit_ID(self, node): # pylint: disable=invalid-name
        """Update state: shared"""
        if node.name not in self.whitelist:
            self.shared.add(node.name)

class SharedVarsVisitor(WithParent):
    """
    Returns a SharedVars for the AST.

    This transform should be a visitor but inherits from node transformer
    because it needs to support Omp* nodes.

    It assumes that the AST has been transformed to the point that every scope
    we need to visit is a Compound node. For nodes are always wrapped by a
    Compound It works by visiting each scope and updating some state along the
    way:

    locals:         A set of locally defined identifiers
    aliases:        A set of ids that alias shared variables
    scopes:         The result. A map from Compound nodes to sets of shared
                    variables
    made_private:   A set of identifiers that have been made private by OpenMP
                    data sharing attribute clauses. This is wiped clean when a
                    new thread team is spawned. (OmpParallel)

    If an identifier in the scope references a variable that is not locally
    defined and has not been made private then it is shared.
    If a variable is locally defined but it is an alias of a shared variable
    then it is shared as well.
    If a variable is not locally defined but is a function parameter and is
    being referenced in the outermost scope of the function body then it is
    shared if it was shared in the caller's scope and is passed as a pointer.

    We don't have to worry about whether we are in a parallel region or not
    because the information we gather will only be used later by an
    Instrumenter class that takes care of that logic.
    """
    #TODO: handle function arguments
    #TODO: collect information about which functions are called in parallel
    #regions

    def __init__(self):
        super().__init__()
        self.decl_visitor = DeclVisitor()
        self.scope = SharedVars()
        self.scopes = {"GLOBAL": self.scope}
        self.made_private = set()
        self.aliases = set()
        self.locals = set()

    def visit_For(self, node): # pylint: disable=invalid-name
        """Separate scope for for loops. Iteration variable is private.
        Parent will always be a OmpFor node.
        """
        #TODO: reduce duplicated code
        self.scope = SharedVars(self.scope)
        self.made_private.update(private_ids(self.parent))
        self.decl_visitor.visit(node)
        self.decl_visitor.visit(node.stmt)
        self.locals.update(self.decl_visitor.locals)
        if isinstance(node.init, DeclList):
            self.made_private.add(node.init.decls[0].name)
        elif isinstance(node.init, Assignment):
            self.made_private.add(node.init.lvalue.name)
        else:
            raise NotImplementedError

        whitelist = (self.locals - self.aliases) | self.made_private
        id_visitor = IDVisitor(whitelist)
        id_visitor.visit(node)
        self.scope.update(id_visitor.shared)
        self.scopes[node] = self.scope
        return node

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Visit each scope and add to the environment"""
        # Set up
        self.scope = SharedVars(self.scope)
        if isinstance(self.parent, OmpParallel):
            self.made_private.clear()
        self.made_private.update(private_ids(self.parent))
        self.decl_visitor.visit(node)
        self.locals.update(self.decl_visitor.locals)

        whitelist = (self.locals - self.aliases) | self.made_private
        id_visitor = IDVisitor(whitelist)
        id_visitor.visit(node)
        self.scope.update(id_visitor.shared)
        self.scopes[node] = self.scope

        # Recover old values
        self.decl_visitor.locals.clear()
        self.locals.clear()
        node = self.generic_visit(node)
        self.scope = self.scope.parent
        return node

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
