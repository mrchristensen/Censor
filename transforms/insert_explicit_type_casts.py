"""Makes all typecasts explicit"""
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl
from pycparser.c_ast import InitList, Constant, Struct, ID
# from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer
from .type_helpers import Side, get_type, resolve_types, is_float, is_integral
from .type_helpers import remove_identifier

# NOTE: return statements are note type casted because

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

        node.init = self.handle_assignment(type_node, node.init)
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
        node.lvalue = self.generic_visit(node.lvalue)
        lvalue_type = get_type(node.lvalue, self.env)
        node.rvalue = self.handle_assignment(lvalue_type, node.rvalue)
        return node

    def visit_FuncCall(self, node): #pylint: disable=invalid-name
        """Put explicit type casts in front of each parameter in the call."""
        func_type = get_type(node.name, self.env)
        formal_args = func_type.args.params
        args = node.args.exprs
        for i, arg in enumerate(args):
            arg_type = get_type(formal_args[i].type, self.env)
            remove_identifier(arg_type)
            args[i] = self.cast_if_needed(arg_type, arg)

        return self.generic_visit(node)

    def handle_assignment(self, type_node, rvalue):
        """Handle type cast upon assignment whether part of a Decl or not."""
        if rvalue is None:
            return rvalue

        rvalue = self.generic_visit(rvalue)

        if isinstance(type_node, TypeDecl) and isinstance(type_node.type, Struct):
            # TODO: uncomment once RemoveInitLists is implemented
            # raise IncorrectTransformOrder("RemoveInitLists must be done first.", node)
            pass
        elif isinstance(type_node, (TypeDecl, PtrDecl)):
            rvalue = self.cast_if_needed(type_node, self.visit(rvalue))
        elif isinstance(type_node, ArrayDecl):
            if isinstance(rvalue, InitList):
                # TODO: uncomment once RemoveInitLists is implemented
                # raise IncorrectTransformOrder("RemoveInitLists must be done first.", node)
                pass
            elif isinstance(rvalue, Constant):
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
        return rvalue

    def cast_if_needed(self, type_node, expr):
        """Decides if it is necessary to cast the given expr to the given type,
        or if the types are already unified."""
        # TODO: currently, this function can only decide if two types are unified
        # if they are integral or floating types. If we ever have a deep compare
        # method than can decide equality of any arbitrary ast nodes, we should
        # use that to decide type unification over all types
        if is_integral(type_node) or is_float(type_node):
            expr_type = get_type(expr, self.env)
            if resolve_types(type_node, expr_type) == Side.NOCAST:
                return expr
        return Cast(type_node, expr)
