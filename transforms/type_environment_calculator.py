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
import logging
from copy import deepcopy
from pycparser.c_ast import ID, Struct, Union, Enum, FuncDecl
from .node_transformer import NodeTransformer
from .id_generator import IDGenerator
from .helpers import remove_identifier

class Enviornment:
    """Holds the enviornment (a mapping of identifiers to types)"""
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
            logging.error("Redefinition of %s", ident)
            #raise Exception("Redefinition of " + ident)

        self.map_to_type[ident] = type_node

    def show(self):
        """Prints to the console all the identifiers being kept in the
        environment."""
        out = "Current:\n"
        for ident in self.map_to_type:
            out += "\n\t" + ident
        current = self.parent
        while current is not None:
            out += "\nParent:\n"
            for ident in current.map_to_type:
                out += "\n\t" + ident
            current = current.parent
        print(out)

    def is_global(self, ident):
        """ Returns whether or not the indentifieris global """
        if ident in self.map_to_type:
            return self.parent is None
        elif self.parent is None:
            return False
        else:
            return self.parent.is_global(ident)

    def __contains__(self, key):
        if key in self.map_to_type:
            return True
        elif self.parent is None:
            return False
        else:
            return key in self.parent

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
    def __init__(self, id_generator=None):
        self.id_generator = id_generator
        self.envr = None
        self.environemnts = None
        self.declared_not_defined = None
        self.in_func_param = False

    def get_environments(self, ast):
        """Aggregate type information for all of the scopes in the AST,
        return a dictionary mapping Compound nodes to the environment
        representing their scope."""
        self.envr = Enviornment()
        self.environemnts = {"GLOBAL": self.envr}
        self.declared_not_defined = set()
        self.visit(ast)
        return self.environemnts

    def visit_Typedef(self, node): # pylint: disable=invalid-name
        """Add typedefs to the type environment."""
        self.envr.add(node.name, node.type)
        self.generic_visit(node)
        return node

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Create a new environment with the current environment as its
        parent so that scoping is handled properly."""
        self.envr = Enviornment(self.envr)
        retval = self.generic_visit(node)
        self.environemnts[node] = self.envr
        self.envr = self.envr.parent
        return retval

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        """Add Create a new environment for the scope of the function. Add the
        function parameters to this scope, then handle the body."""
        if node.decl.name in self.declared_not_defined:
            self.declared_not_defined.remove(node.decl.name)
        else:
            type_node = deepcopy(node.decl.type)
            ident = remove_identifier(type_node)
            self.envr.add(ident, type_node)

        self.envr = Enviornment(self.envr)

        func_decl = node.decl.type
        if func_decl.args is not None:
            func_decl.args = self.visit(func_decl.args)
        node.body = self.generic_visit(node.body)

        self.environemnts[node.body] = self.envr
        self.envr = self.envr.parent
        return node

    def visit_For(self, node): # pylint: disable=invalid-name
        """The for loop header should have its own scope."""
        self.envr = Enviornment(self.envr)
        node.init = self.visit(node.init)
        # don't need to visit node.cond or node.next because they can't
        # have Declarations in them
        node.stmt = self.visit(node.stmt)
        self.envr = self.envr.parent
        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Visit Decl nodes so that we can save type information about
        identifiers in the environment."""
        #TODO handle extern, static, etc properly

        type_node = deepcopy(node.type)

        ident = remove_identifier(type_node)
        if ident is None:
            if self.id_generator is None:
                self.id_generator = IDGenerator(node)
            ident = self.id_generator.get_unique_id()
        if isinstance(type_node, (Struct, Union, Enum)):
            ident = type(type_node).__name__ + " " + ident

        self.envr.add(ident, type_node)

        if isinstance(type_node, FuncDecl):
            self.declared_not_defined.add(node.name)

        return node

    def visit_TypeDecl(self, node): #pylint: disable=invalid-name
        """ Examine TypeDecl """
        type_node = node.type
        if isinstance(type_node, (Struct, Union)):
            ident = type_node.name
            if ident is not None and type_node.decls is not None:
                ident = type(type_node).__name__ + " " + ident
                if ident not in self.envr:
                    self.envr.add(ident, type_node)
        if isinstance(type_node, Enum):
            ident = type_node.name
            if ident is not None and type_node.values is not None:
                ident = type(type_node).__name__ + " " + ident
                if ident not in self.envr:
                    self.envr.add(ident, type_node)
        node = self.generic_visit(node)
        return node
