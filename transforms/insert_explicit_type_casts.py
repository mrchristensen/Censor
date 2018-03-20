"""Makes all typecasts explicit"""
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
from pycparser.c_ast import InitList, Constant, Struct, ID
# from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer
from .type_helpers import Side, get_type, resolve_types, is_float, is_integral

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
        type_node = get_type(ID(node.name), self.env)

        if node.init is None:
            return node

        node.init = self.generic_visit(node.init)

        if isinstance(type_node, TypeDecl) and isinstance(type_node.type, Struct):
            if node.init:
                # TODO: uncomment once RemoveInitLists is implemented
                # raise IncorrectTransformOrder("RemoveInitLists must be done first.", node)
                pass
        elif isinstance(type_node, (TypeDecl, PtrDecl)):
            node.init = Cast(type_node, self.visit(node.init))
        elif isinstance(type_node, ArrayDecl):
            if node.init and isinstance(node.init, InitList):
                # TODO: uncomment once RemoveInitLists is implemented
                # raise IncorrectTransformOrder("RemoveInitLists must be done first.", node)
                pass
            elif node.init and isinstance(node.init, Constant):
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

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Add a type cast based on type info about the lvalue stored in
        the Environment."""
        self.generic_visit(node)
        lvalue_type = get_type(node.lvalue, self.env)

        # figure out if cast is necessary and do it if it is
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
