"""Makes all typecasts explicit"""
from pycparser.c_ast import Cast, TypeDecl, PtrDecl, ArrayDecl, FuncDecl, UnaryOp
from pycparser.c_ast import InitList, Constant, Struct, Union, ID, EllipsisParam
from .helpers import IncorrectTransformOrder
from .node_transformer import NodeTransformer
from .type_helpers import Side, get_type, resolve_types, cast_if_needed
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
        if node.init:
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
        if node.args is None or func_type.args is None:
            return self.generic_visit(node)

        formal_args = func_type.args.params
        args = node.args.exprs
        rest_args = False
        for i, arg in enumerate(args):
            if rest_args or isinstance(formal_args[i], EllipsisParam):
                rest_args = True
            else:
                arg_type = get_type(formal_args[i].type, self.env)
                if isinstance(arg_type, ArrayDecl):
                    arg_type = PtrDecl(None, arg_type.type)
                remove_identifier(arg_type)
                args[i] = cast_if_needed(arg_type, arg, self.env)
            if isinstance(args[i], UnaryOp) and args[i].op == '*':
                args[i] = Cast(get_type(args[i], self.env), args[i])

        return self.generic_visit(node)

    def handle_assignment(self, type_node, rvalue):
        """Handle type cast upon assignment whether part of a Decl or not."""
        ril_error_message = "RemoveInitLists must be done first."

        rvalue = self.visit(rvalue)

        if isinstance(type_node, TypeDecl) and \
            isinstance(type_node.type, Struct):
            return rvalue
            #raise IncorrectTransformOrder(ril_error_message, rvalue)
        elif isinstance(type_node, TypeDecl) and \
            isinstance(type_node.type, Union):
            return rvalue
        elif isinstance(type_node, (TypeDecl, PtrDecl)):
            rvalue = cast_if_needed(type_node, rvalue, self.env)
        elif isinstance(type_node, ArrayDecl):
            if isinstance(rvalue, InitList):
                raise IncorrectTransformOrder(ril_error_message, rvalue)
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

        if isinstance(rvalue, UnaryOp) and rvalue.op == '*':
            rvalue = Cast(get_type(rvalue, self.env), rvalue)
        return rvalue
