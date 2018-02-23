"""Makes all typecasts explicit"""

from copy import deepcopy
# from cesk.structures import Envr
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
from pycparser.c_ast import InitList, Constant
# from pycparser.c_ast import  BinaryOp, UnaryOp, InitList,  Compound,  Decl,
# from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer

# TODO: take care of modifiers and storage qualifiers correctly
# modifiers: signed unsigned long short
# const extern volatile static register

# it already puts the type cast in for structs and unions!!!

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    parent = None

    def __init__(self, parent=None):
        self.parent = parent
        self.map_to_type = {}

    def get_type(self, ident):
        """returns the type currently associated with the given
        identifier"""
        if ident in self.map_to_type: #pylint: disable=no-else-return
            return self.map_to_type[ident]
        elif self.parent is not None:
            return self.parent.get_type(ident)
        else:
            return None

    def add(self, ident, type_node):
        """Add a new identifier to the mapping"""
        self.map_to_type[ident] = type_node

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        return self.get_type(ident) is not None

    def is_locally_defined(self, ident):
        """returns if a given identifier is defined in the local scope"""
        return ident in self.map_to_type


class NoCastNeeded(Exception):
    """PtrDecl nodes are recursively unwrapped to see if the underlying type
    needs to be given an explicit cast upon assignment. If it turns out to be
    a pointer to a function or an array type, this exception is raised."""
    pass

class InsertExplicitTypeCasts(NodeTransformer):
    """NodeTransformer to make all typecasts in the program explicit."""
    def __init__(self):
        self.envr = Envr()

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Create a new environment with the current environment as its
        parent so that scoping is handled properly."""
        self.envr = Envr(self.envr)
        for i in range(len(node.block_items)):
            node.block_items[i] = self.generic_visit(node.block_items[i])

        self.envr = self.envr.parent
        return node

    def visit_Decl(self, node): #pylint: disable=invalid-name
        """Add necessary type casts when the Decl involves an assignment."""
        # print("Decl:\n"); node.show()
        # print("node type:\n"); node.type.show()
        type_node = deepcopy(node.type)
        try:
            ident = remove_identifier(type_node)
        except NoCastNeeded:
            print("CAUGHT NOCASTNEEDED")
            node.init = self.generic_visit(node.init)

        # if self.envr.is_localy_defined(ident):
        #     raise Exception("Error: redefinition of " + ident)

        self.envr.add(ident, type_node)

        if node.init is None:
            return node

        if isinstance(node.type, (TypeDecl, PtrDecl)):
            node.init = Cast(type_node, self.generic_visit(node.init))
        elif isinstance(node.type, ArrayDecl):
            if isinstance(node.init, InitList):
                annotate_array_initlist(node.init, type_node.type)
            elif isinstance(node.init, Constant):
                # TODO: figure out what to do with cases like
                # char wow[100] = "wow"; where an array is initialized
                # from a string
                raise NotImplementedError()
            else:
                raise NotImplementedError()
            node.init = self.generic_visit(node.init)
        elif isinstance(node.type, FuncDecl):
            # don't do any cast, casting to a function type doesn't compile,
            # casting to a function pointer type is undefined behavior
            node.init = self.generic_visit(node.init)
        else:
            raise NotImplementedError()

        node.type = self.generic_visit(node.type)
        if node.bitsize is not None:
            node.bitsize = self.generic_visit(node.bitsize)
        return node

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        """Add all necessary typecasts to aribitrary arithmetic expressions."""
        # NOTE: the only time we need to deal with UnaryOp nodes is when they are
        # recursively nested inside a binaryOp node. Or a decl.
        return self.generic_visit(node)

    def visit_InitList(self, node): #pylint: disable=invalid-name
        """Add necessary typecasts to expressions inside of an initializer list
        for arrays and structs."""
        # make sure you take care of any expressions, as well as namedinitializers,
        # that could occur inside of here
        return self.generic_visit(node)

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Add a type cast based on type info about the lvalue stored in
        the Environment."""
        pass

def remove_identifier(node):
    """Takes in the type attribute of a Decl node and removes the identifier,
    so it can be used for type casting. Returns the identifier"""
    if isinstance(node, TypeDecl):
        # remove the identifier, end recursion
        ident = node.declname
        node.declname = None
        return ident
    elif isinstance(node, (PtrDecl, ArrayDecl)):
        # recur
        return remove_identifier(node.type)
    elif isinstance(node, FuncDecl):
        # TODO: figure out what the actual correct implementation is...
        raise NoCastNeeded("Function Pointer")
    else:
        raise NotImplementedError()

def annotate_array_initlist(initlist, type_node):
    """Takes an initializer list and a TypeDecl node and casts each element
    of the initializer list to the given type."""
    # TODO: implement for named initializers
    # TODO: implement recursively if the elements of the list are also
    # initializer lists, whether they are for structs, more arrays,
    # unions, or anything else
    for i in range(len(initlist.exprs)):
        initlist.exprs[i] = Cast(type_node, initlist.exprs[i])


def annotate_struct_initlist(initlist, type_node):
    """Takes an initializer list and a TypeDecl node members are cast to the
    types of the corresponding fields of the struct."""
    # TODO: implement for named initializers
    # TODO: implement recursively if the elements of the list are also
    # initializer lists, whether they are for structs, more arrays,
    # unions, or anything else
    return initlist, type_node

def handle_constant(node):
    """Takes a node for a constant expression, returns an appropriately type
    casted version of the same node"""
    return node
