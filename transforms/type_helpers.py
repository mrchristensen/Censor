"""Helpers for working with information about types during AST transformations."""

from pycparser.c_ast import * #pylint: disable=wildcard-import, unused-wildcard-import


class Envr:
    """Holds the enviorment (a mapping of identifiers to types)"""
    parent = None

    def __init__(self, parent=None):
        self.parent = parent
        self.map_to_type = {}

    def get_type(self, ident):
        """Returns the type currently associated with the given
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

    def show(self):
        """Prints to the console all the identifiers being kept in the
        environment."""
        out = "Current:\n"
        for ident in self.map_to_type:
            out += "\t" + ident
        current = self.parent
        while current != None:
            out += "\nParent:\n"
            for ident in current.map_to_type:
                out += "\t" + ident
            current = current.parent
        print(out)

def remove_identifier(node):
    """Takes in the type attribute of a Decl node and removes the identifier,
    so it can be used for type casting. Returns the identifier"""
    if isinstance(node, TypeDecl):
        # remove the identifier, end recursion
        ident = node.declname
        node.declname = None
        return ident
    elif isinstance(node, (PtrDecl, ArrayDecl, FuncDecl)):
        # recur
        return remove_identifier(node.type)
    else:
        raise NotImplementedError()

def add_identifier(node, ident):
    """Given a node that could be used as the type attribute of a Decl, attach
    the given identifier to it."""
    if isinstance(node, TypeDecl):
        # remove the identifier, end recursion
        node.declname = ident
        return node
    elif isinstance(node, (PtrDecl, ArrayDecl, FuncDecl)):
        # recur
        return remove_identifier(node.type)
    else:
        raise NotImplementedError()

def resolve_types(left, right):
    """Given two types, figure out what types they should be cast to when
    a binary operation is performed on two objects with the given types"""
    # do something pointless so that pylint doesn't complain about
    # unused arguments
    right = left
    return right

def get_binop_type(expr, env):
    """Takes in a BinaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op in ['<', '<=', '==', '>', '>=', '!=', '&&', '||']:
        return TypeDecl(None, [], IdentifierType(['int']))
    elif expr.op in ['%', '*', '+', '–', '/', '^', '|', '&', '<<', '>>']:
        left_type = get_type(expr.left, env)
        right_type = get_type(expr.right, env)
        return resolve_types(left_type, right_type)
    else:
        raise NotImplementedError()

def get_unop_type(expr, env):
    """Takes in a UnaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op == 'sizeof' or expr.op == '!':
        # TODO: type check the expression?
        return TypeDecl(None, [], IdentifierType(['int']))
    elif expr.op in ['++', '--', '+', '-', '~']:
        return get_type(expr.expr, env)
    elif expr.op == '&':
        return PtrDecl([], get_type(expr.expr, env))
    elif expr.op == '*':
        type_of_operand = get_type(expr.expr, env)
        if not isinstance(type_of_operand, PtrDecl):
            raise Exception("Attempting to dereference a non-pointer.")
        return type_of_operand.type
    else:
        raise NotImplementedError()


def get_type(expr, env):
    """Takes in an expression and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if isinstance(expr, ID):
        return env.get_type(expr.name)
    elif isinstance(expr, Constant):
        # TODO: if the int is over a certain size, change to long?
        return TypeDecl(None, [], IdentifierType([expr.type]))
    elif isinstance(expr, Cast):
        # TODO: do any type checking?
        return expr.to_type
    elif isinstance(expr, UnaryOp):
        return get_unop_type(expr, env)
    elif isinstance(expr, BinaryOp):
        return get_binop_type(expr, env)
    elif isinstance(expr, StructRef):
        raise NotImplementedError()
    else:
        raise NotImplementedError()
    return expr.type
