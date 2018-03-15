"""Helpers for working with information about types during AST transformations."""
from copy import deepcopy
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import


# TODO: support Enum declarations

class Envr:
    """Holds the enviorment (a mapping of identifiers to types)"""
    parent = None

    def __init__(self, parent=None):
        self.parent = parent
        self.map_to_type = {}

    def get_type(self, ident):
        """Returns the type currently associated with the given
        identifier"""
        if isinstance(ident, ID):
            ident = ident.name

        if ident in self.map_to_type: # pylint: disable=no-else-return
            return self.map_to_type[ident]
        elif self.parent is not None:
            return self.parent.get_type(ident)
        else:
            return None

    def add(self, ident, type_node):
        """Add a new identifier to the mapping"""
        if isinstance(ident, ID):
            ident = ident.name

        # # if the type is actually a typedef for another type, map the
        # # identifier directly to the other type
        # # CANT do this because if the originial type is declared incline,
        # if isinstance(type_node, TypeDecl) and isinstance(type_node.type, IdentifierType):
        #     if len(type_node.type.names) == 1:
        #         type_name = type_node.type.names[0]
        #         if self.is_defined(type_name):
        #             self.map_to_type[ident] = self.get_type(type_name)
        #             return

        self.map_to_type[ident] = type_node

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        if isinstance(ident, ID):
            ident = ident.name
        return self.get_type(ident) is not None

    def is_locally_defined(self, ident):
        """returns if a given identifier is defined in the local scope"""
        if isinstance(ident, ID):
            ident = ident.name
        return ident in self.map_to_type

    def show(self):
        """Prints to the console all the identifiers being kept in the
        environment."""
        out = "Current:\n"
        for ident in self.map_to_type:
            out += "\n\t" + ident
        current = self.parent
        while current != None:
            out += "\nParent:\n"
            for ident in current.map_to_type:
                out += "\n\t" + ident
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
    elif isinstance(node, (Struct, Union)):
        # remove the identifier, end recursion
        ident = node.name
        node.name = None
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
        # add the identifier, end recursion
        node.declname = ident
        return node
    elif isinstance(node, (Struct, Union)):
        # add the identifier, end recursion
        node.name = ident
        return node
    elif isinstance(node, (PtrDecl, ArrayDecl, FuncDecl)):
        # recur
        node.type = add_identifier(node.type, ident)
        return node
    else:
        raise NotImplementedError()

def is_integral(type_node):
    """Returns if the given type node describes an integral type."""
    # TODO: Add support for user-defined integral types that are
    # defined through typedef's or enums
    integral_ids = ['int', 'char', 'short']
    if isinstance(type_node, TypeDecl):
        if isinstance(type_node.type, IdentifierType):
            return bool([i for i in integral_ids if i in type_node.type.names])
        return False
    elif isinstance(type_node, IdentifierType):
        return bool([i for i in integral_ids if i in type_node.names])
    return False

def is_float(type_node):
    """Returns if the given type node describes an integral type."""
    # TODO: Add support for user-defined floating types that are
    # defined through typedef's
    if isinstance(type_node, TypeDecl):
        if isinstance(type_node.type, IdentifierType):
            return 'float' in type_node.type.names or 'double' in type_node.type.names
        return False
    elif isinstance(type_node, IdentifierType):
        return 'float' in type_node.type.names or 'double' in type_node.type.names
    return False

def is_ptr(type_node):
    """Returns if the given type node describes a pointer type."""
    return isinstance(type_node, PtrDecl)

def resolve_integral_types(left, right):
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types"""
    # TODO
    left = right
    return left

def resolve_floating_types(left, right):
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types"""
    # TODO
    left = right
    return left

def resolve_types(left, right): # pylint: disable=too-many-return-statements
    """Given two types, figure out what types they should be cast to when
    a binary operation is performed on two objects with the given types
    The rules implemented here come directly from the c spec:
    http://www.open-std.org/jtc1/sc22/WG14/www/docs/n1256.pdf
    section, 6.3.1.8 Usual arithmetic conversions, p. 44.
    """
    if is_ptr(left) and is_integral(right):
        return left
    elif is_integral(left) and is_ptr(right):
        return right
    elif is_ptr(left) and is_ptr(right):
        return TypeDecl(None, [], IdentifierType(['int']))
    elif is_float(left) and is_integral(right):
        return left
    elif is_integral(left) and is_float(right):
        return right
    elif is_float(left) and is_float(right):
        return resolve_floating_types(left, right)
    elif is_integral(left) and is_integral(right):
        return resolve_integral_types(left, right)
    print("---left:")
    left.show()
    print("---right:")
    right.show()
    raise NotImplementedError()

def get_binop_type(expr, env):
    """Takes in a BinaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op in ['<', '<=', '==', '>', '>=', '!=', '&&', '||']:
        return TypeDecl(None, [], IdentifierType(['int']))
    elif expr.op in ['%', '*', '+', '-', '/', '^', '|', '&', '<<', '>>']:
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
        return PtrDecl([], get_type_helper(expr.expr, env))
    elif expr.op == '*':
        type_of_operand = get_type(expr.expr, env)
        if not isinstance(type_of_operand, PtrDecl):
            raise Exception("Attempting to dereference a non-pointer.")
        return type_of_operand.type
    else:
        raise NotImplementedError()

def get_structref_type(expr, env):
    """Resolve the type of a StructRef node."""
    # find the type of whatever is on the left of the . or ->
    type_decl = get_type_helper(expr.name, env)

    # go look up the type, see what the type of the given field is
    if isinstance(type_decl, PtrDecl):
        type_decl = type_decl.type

    struct_type = type_decl.type
    if isinstance(struct_type, IdentifierType):
        struct_type = env.get_type(struct_type.names[0]).type

    # if you have the name of the struct but not its field declarations, go find them
    if struct_type.decls is None:
        struct_type_string = struct_type.name
        struct_type = env.get_type(struct_type_string)

    for decl in struct_type.decls:
        if decl.name == expr.field.name:
            return decl.type
    raise Exception("Struct " + struct_type_string +
                    "doesn't have field " + expr.field.name)

def get_type(expr, env):
    """Takes in an expression and a type environment (map of identifiers to
    types) and returns a new node representing the type of the given expression.
    NOTE: testing for this method is largely done through the test cases
    for remove_compound_assignment, which cover needing to calculate the type
    of many different kinds of expressions."""
    return deepcopy(get_type_helper(expr, env))

def get_type_helper(expr, env): # pylint: disable=too-many-return-statements
    """Does all of the actual work for get_type, but returns a reference to
    a node that is currently in the AST."""
    if isinstance(expr, TypeDecl):
        return expr
    elif isinstance(expr, ID):
        # TODO: make it actually work for typedefs
        return env.get_type(expr.name)
    elif isinstance(expr, Constant):
        # TODO: if the int is over a certain size, change to long?
        return TypeDecl(None, [], IdentifierType([expr.type]))
    elif isinstance(expr, Cast):
        return expr.to_type
    elif isinstance(expr, UnaryOp):
        return get_unop_type(expr, env)
    elif isinstance(expr, BinaryOp):
        return get_binop_type(expr, env)
    elif isinstance(expr, StructRef):
        return get_structref_type(expr, env)
    elif isinstance(expr, ArrayRef):
        return get_type_helper(expr.name, env).type
    elif isinstance(expr, FuncCall):
        func_decl = env.get_type(expr.name)
        return func_decl.type
    else:
        raise NotImplementedError()
    return expr.type
