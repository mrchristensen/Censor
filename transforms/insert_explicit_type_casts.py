"""Makes all typecasts explicit"""
from copy import deepcopy
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
from pycparser.c_ast import InitList, Constant, Struct, ID
# from pycparser.c_ast import  BinaryOp, UnaryOp, InitList,  Compound,  Decl,
from .node_transformer import NodeTransformer
from .type_helpers import Side, get_type, resolve_types, is_float, is_integral
from .type_helpers import remove_identifier

# TODO: take care of storage qualifiers correctly
# const extern volatile static register

class InsertExplicitTypeCasts(NodeTransformer):
    """NodeTransformer to make all typecasts in the program explicit."""
    def __init__(self, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.env
        self.env = self.environments[node]
        retval = self.generic_visit(node)
        self.env = parent
        return retval

    def visit_Decl(self, node): #pylint: disable=invalid-name
        """Add necessary type casts when the Decl involves an assignment."""
        # print("Decl:\n"); node.show()
        # print("node type:\n"); node.type.show()
        type_node = get_type(ID(node.name), self.env)

        if node.init is None:
            return node

        node.init = self.generic_visit(node.init)

        if isinstance(type_node, TypeDecl) and isinstance(type_node.type, Struct):
            if isinstance(node.init, InitList):
                annotate_struct_initlist(node.init, type_node.type)
        elif isinstance(type_node, (TypeDecl, PtrDecl)):
            node.init = Cast(type_node, self.visit(node.init))
        elif isinstance(type_node, ArrayDecl):
            if isinstance(node.init, InitList):
                annotate_array_initlist(node.init, type_node.type)
            elif isinstance(node.init, Constant):
                # TODO: figure out what to do with cases like
                # char wow[100] = "wow"; where an array is initialized
                # from a string
                raise NotImplementedError()
            else:
                raise NotImplementedError()
        elif isinstance(type_node, FuncDecl):
            # don't do any cast, casting to a function type doesn't compile,
            # casting to a function pointer type is undefined behavior
            pass
        else:
            raise NotImplementedError()

        node.type = self.generic_visit(node.type)
        return node

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        """Add all necessary typecasts to aribitrary arithmetic expressions."""
        # NOTE: the only time we need to deal with UnaryOp nodes is when they are
        # recursively nested inside a binaryOp node. Or a decl.

        # recursively visit children and perform needed type annotations
        node = self.generic_visit(node)

        # resolve types for the given operation
        left_type = get_type(node.left, self.env)
        right_type = get_type(node.right, self.env)
        cast_to = resolve_types(left_type, right_type)

        if cast_to == Side.LEFT:
            node.right = Cast(left_type, node.right)
        elif cast_to == Side.RIGHT:
            node.left = Cast(right_type, node.left)

        return node

    def visit_InitList(self, node): #pylint: disable=invalid-name
        """Add necessary typecasts to expressions inside of an initializer list
        for arrays and structs."""
        # make sure you take care of any expressions, as well as namedinitializers,
        # that could occur inside of here
        return self.generic_visit(node)

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Add a type cast based on type info about the lvalue stored in
        the Environment."""
        # print("---------"); node.show()
        self.generic_visit(node)
        lvalue_type = get_type(node.lvalue, self.env)
        # TODO: annotate inside of initializer list if used here
        # TODO: if we ever implement a method to do a full comparison as node
        # equality, don't do the cast if get_type(lvalue) == get_type(rvalue)
        if is_integral(lvalue_type) or is_float(lvalue_type):
            rvalue_type = get_type(node.rvalue, self.env)
            if resolve_types(lvalue_type, rvalue_type) == Side.NOCAST:
                return node
        node.rvalue = Cast(lvalue_type, node.rvalue)
        return node

    def visit_FuncCall(self, node): #pylint: disable=invalid-name
        """Put explicit type casts in front of each parameter in the call."""
        # TODO uh...actually implement it
        return self.generic_visit(node)

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
    return initlist


def annotate_struct_initlist(initlist, type_node):
    """Takes an initializer list and a TypeDecl node members are cast to the
    types of the corresponding fields of the struct."""
    # TODO: implement for named initializers
    # TODO: implement recursively if the elements of the list are also
    # initializer lists, whether they are for structs, more arrays,
    # unions, or anything else
    for i in range(len(initlist.exprs)):
        cast_to = deepcopy(type_node.decls[i].type)
        remove_identifier(cast_to)
        initlist.exprs[i] = Cast(cast_to, initlist.exprs[i])
    return initlist, type_node
