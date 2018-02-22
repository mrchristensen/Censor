"""Makes all typecasts explicit"""

from copy import deepcopy
from cesk.structures import Envr
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
# from pycparser.c_ast import  BinaryOp, UnaryOp, InitList,  Compound,  Decl,
# from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer

# TODO: take care of modifiers and storage qualifiers correctly
# modifiers: signed unsigned long short
# const extern volatile static register

# it already puts the type cast in for structs and unions!!!


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

        # if self.envr.is_localy_defined(ident):
        #     raise Exception("Error: redefinition of " + ident)

        # TODO: put type information into the environment

        if node.init is None:
            return node

        if isinstance(node.type, TypeDecl):
            node.init = Cast(node.type.type, self.generic_visit(node.init))
        elif isinstance(node.type, PtrDecl):
            type_node = deepcopy(node.type)
            try:
                type_node = remove_identifier(type_node)
                node.init = Cast(type_node, self.generic_visit(node.init))
            except NoCastNeeded:
                node.init = self.generic_visit(node.init)
        elif isinstance(node.type, ArrayDecl):
            # don't do any cast, casting to an array type doesn't compile
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
    """Takes in a PtrDecl and removes the identifier, so it can be used
    for type casting."""
    if isinstance(node.type, TypeDecl):
        # remove the identifier, end recursion
        node.type.declname = None
        return node
    elif isinstance(node.type, PtrDecl):
        # recur
        return PtrDecl(node.quals, remove_identifier(node.type))
    elif isinstance(node.type, ArrayDecl):
        raise NoCastNeeded("Array Pointer")
    elif isinstance(node.type, FuncDecl):
        raise NoCastNeeded("Function Pointer")
    else:
        raise NotImplementedError()

def handle_constant(node):
    """Takes a node for a constant expression, returns an appropriately type
    casted version of the same node"""
    return node
