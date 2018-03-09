"""
Creates a map from compound blocks in the AST to type environments.
To use this for a transform that needs type information about Unions,
Structs, Typedefs, and identifiers, have

def __init__(self, environments):
    self.evironments = environments
    self.envr = environments["GLOBAL"]
    .
    .
    .
in your __init__, and

def visit_Compound(self, node):
    parent = self.envr
    self.envr = self.evironments[node]
    # DO whatever you want to visit the children of the compound
    .
    .
    .
    self.envr = parent
    return retval

in your visit_Compound, and then self.envr will always be the environment
of your current scope.
"""
# TODO: support Enum declarations

from copy import deepcopy
from .node_transformer import NodeTransformer
from .type_helpers import Envr, remove_identifier

class TypeEnvironmentCalculator(NodeTransformer):
    """Aggregate type information for all of the scopes in the AST,
    return a dictionary mapping Compound nodes to the environment
    representing their scope.
    NOTE: It would make more technical sense for TypeEnvironmentCalculator to
    inherit directly from NodeVisitor (instead of NodeTransformer), because
    it is not actually changing any nodes. However, it inherits from
    NodeTranformer for now because it needs to be able to handle both
    pycparser.c_ast.Node and omp.omp_ast.Node. If we ever figure out a way
    for all the nodes to be the same type, this should solve the problem.
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
        return self.generic_visit(node)

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Create a new environment with the current environment as its
        parent so that scoping is handled properly."""
        self.envr = Envr(self.envr)
        retval = self.generic_visit(node)
        self.environemnts[node] = self.envr
        self.envr = self.envr.parent
        return retval

    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Visit Decl nodes so that we can save type information about
        identifiers in the environment."""
        # print("visiting decl")
        # node.show()
        type_node = deepcopy(node.type)
        ident = remove_identifier(type_node)

        if self.envr.is_locally_defined(ident):
            raise Exception("Error: redefinition of " + ident)

        self.envr.add(ident, type_node)
        return self.generic_visit(node)
