"""
Creates a map from compound blocks in the AST to type environments.
To use this for a transform that needs type information about Unions,
Structs, Typedefs, and identifiers, have

def __init__(self, environments):
    self.environments = environments
    self.env = environments["GLOBAL"]
    .
    .
    .
in your __init__, and

def visit_Compound(self, node):
    parent = self.env
    self.env = self.environments[node]
    # DO whatever you want to visit the children of the compound
    .
    .
    .
    self.env = parent
    return retval

in your visit_Compound, and then self.envr will always be the environment
of your current scope.
"""

from copy import deepcopy
from pycparser.c_ast import ID
from .node_transformer import NodeTransformer
from .type_helpers import remove_identifier

class Envr:
    """Holds the enviorment (a mapping of identifiers to types)"""
    parent = None

    def __init__(self, parent=None):
        self.parent = parent
        self.map_to_type = {}

    def get_type(self, ident):
        """Returns the type currently associated with the given
        identifier"""
        if isinstance(ident, ID):
            ident = ident.name

        if ident in self.map_to_type:
            return self.map_to_type[ident]
        elif self.parent is not None:
            return self.parent.get_type(ident)
        else:
            raise Exception("Undefined Identifier " + ident)

    def add(self, ident, type_node):
        """Add a new identifier to the mapping"""
        if isinstance(ident, ID):
            ident = ident.name
        if ident in self.map_to_type:
            raise Exception("Redefinition of " + ident)

        self.map_to_type[ident] = type_node

    def show(self):
        """Prints to the console all the identifiers being kept in the
        environment."""
        out = "Current:\n"
        for ident in self.map_to_type:
            out += "\n\t" + ident
        current = self.parent
        while current != None:
            out += "\nParent:\n"
            for ident in current.map_to_type:
                out += "\n\t" + ident
            current = current.parent
        print(out)

class TypeEnvironmentCalculator(NodeTransformer):
    """Aggregate type information for all of the scopes in the AST,
    return a dictionary mapping Compound nodes to the environment
    representing their scope.
    NOTE: It would make more technical sense for TypeEnvironmentCalculator to
    inherit directly from NodeVisitor (instead of NodeTransformer), because
    it is not actually changing any nodes. However, it inherits from
    NodeTranformer for now because it needs to be able to handle both
    pycparser.c_ast.Node and omp.omp_ast.Node. If we ever figure out a way
    for all the nodes to be the same type, this should inherit from
    NodeVisitor.
    """
    def __init__(self):
        self.envr = None
        self.environemnts = None

    def get_environments(self, ast):
        """Aggregate type information for all of the scopes in the AST,
        return a dictionary mapping Compound nodes to the environment
        representing their scope."""
        self.envr = Envr()
        self.environemnts = {"GLOBAL": self.envr}
        self.visit(ast)
        return self.environemnts

    def visit_Typedef(self, node): # pylint: disable=invalid-name
        """Add typedefs to the type environment."""
        self.envr.add(node.name, node.type)
        return node

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Create a new environment with the current environment as its
        parent so that scoping is handled properly."""
        self.envr = Envr(self.envr)
        retval = self.generic_visit(node)
        self.environemnts[node] = self.envr
        self.envr = self.envr.parent
        return retval

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        """Add Create a new environment for the scope of the function. Add the
        function parameters to this scope, then handle the body."""
        node.decl = self.visit(node.decl)
        self.envr = Envr(self.envr)

        func_decl = node.decl.type
        if func_decl.args != None:
            func_decl.args = self.visit(func_decl.args)
        node.body = self.generic_visit(node.body)

        self.environemnts[node.body] = self.envr
        self.envr = self.envr.parent
        return node


    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Visit Decl nodes so that we can save type information about
        identifiers in the environment."""
        type_node = deepcopy(node.type)
        ident = remove_identifier(type_node)

        self.envr.add(ident, type_node)
        return node
