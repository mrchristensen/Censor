"""Makes all typecasts explicit"""
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
from pycparser.c_ast import InitList, Constant
# from pycparser.c_ast import  BinaryOp, UnaryOp, InitList,  Compound,  Decl,
# from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer

# TODO: take care of modifiers and storage qualifiers correctly
# modifiers: signed unsigned long short
# const extern volatile static register

# it already puts the type cast in for structs and unions!!!

# TODO: in function calls, the arguments need to be cast to the correct type,
# as does the return value. So the Environment DEFINITELY needs to store info on
# types of functions.

class InsertExplicitTypeCasts(NodeTransformer):
    """NodeTransformer to make all typecasts in the program explicit."""
    def __init__(self, environments):
        self.environments = environments
        self.envr = environments["GLOBAL"]

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.envr
        self.envr = self.environments[node]
        retval = self.generic_visit(node)
        self.envr = parent
        return retval

    def visit_Decl(self, node): #pylint: disable=invalid-name
        """Add necessary type casts when the Decl involves an assignment."""
        # print("Decl:\n"); node.show()
        # print("node type:\n"); node.type.show()
        ident = node.name
        type_node = self.envr.get_type(ident)

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
            # TODO: add type information of the function to the environment
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

# def handle_assignment(init, type_node):
#     """Handle type cast upon assignment whether part of a Decl or not."""
#     pass

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
