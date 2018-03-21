"""Helpers for working with information about types during AST transformations."""
from copy import deepcopy
from enum import Enum
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
from cesk.limits import RANGES

class Side(Enum):
    """Return type of function asking which type of a binary operand that
    both sides should be cast to."""
    LEFT = 1
    RIGHT = 2
    NOCAST = 3

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
    elif isinstance(node, (Struct, Union, Enum)):
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
    elif isinstance(node, (Struct, Union, Enum)):
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

def get_integral_range(type_node):
    """Takes in a type_node describing an integral type and returns the range
    of integers that the given integral type can represent, e.g.
    get_integral_range(TypeDecl(None, [],
                    IdentifierType(['char'])) == Range(-127,127)"""
    # TODO: Add support for user-defined integral types that are
    # defined through typedef's or enums
    type_string = " ".join(type_node.type.names)
    return RANGES[type_string]

def is_signed(int_range):
    """Takes a Range, says if that Range represents a signed integral type."""
    return not int_range.min == 0

def resolve_integral_types(left, right): # pylint: disable=too-many-return-statements
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types"""
    # TODO Add support for user-defined integral types that are
    # defined through typedef's or enums
    l_range = get_integral_range(left)
    r_range = get_integral_range(right)

    if l_range == r_range:
        return Side.NOCAST
    elif is_signed(l_range) == is_signed(r_range):
        if l_range.max > r_range.max:
            return Side.LEFT
        else:
            return Side.RIGHT
    elif not is_signed(l_range) and l_range.max >= (r_range.max - r_range.min):
        return Side.LEFT
    elif not is_signed(r_range) and r_range.max >= (l_range.max - l_range.min):
        return Side.RIGHT
    elif is_signed(l_range) and l_range.max >= r_range.max:
        return Side.LEFT
    elif is_signed(r_range) and r_range.max >= l_range.max:
        return Side.RIGHT
    else:
        # Technically, there is an extra case in the C spec here:
        # "Otherwise, both operands are converted to the unsigned integer type
        # corresponding to the type of the operand with signed integer type."
        # As an implementation, we don't want to have to deal with that, so
        # cesk.limits.py should be set up so that this case is never reached.
        raise Exception("Incorrect integer Limits!")

    left = right
    return Side.LEFT

def resolve_floating_types(left, right):
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types"""
    # TODO support for typedef defined floating types
    # TODO support for complex floating types
    if left.type.names == right.type.names:
        return Side.NOCAST
    elif 'long' in left.type.names:
        return Side.LEFT
    elif 'long' in right.type.names:
        return Side.RIGHT
    elif 'double' in left.type.names:
        return Side.LEFT
    return Side.RIGHT

def resolve_types(left, right): # pylint: disable=too-many-return-statements
    """Given two types, figure out what types they should be cast to when
    a binary operation is performed on two objects with the given types
    The rules implemented here come directly from the c spec:
    http://www.open-std.org/jtc1/sc22/WG14/www/docs/n1256.pdf
    section, 6.3.1.8 Usual arithmetic conversions, p. 44.
    """
    if is_ptr(left) and is_integral(right):
        return Side.LEFT
    elif is_integral(left) and is_ptr(right):
        return Side.RIGHT
    elif is_ptr(left) and is_ptr(right):
        return TypeDecl(None, [], IdentifierType(['int']))
    elif is_float(left) and is_integral(right):
        return Side.LEFT
    elif is_integral(left) and is_float(right):
        return Side.RIGHT
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
        if resolve_types(left_type, right_type) == Side.LEFT:
            return left_type
        else:
            return right_type
    else:
        raise NotImplementedError()

def get_unop_type(expr, env):
    """Takes in a UnaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op == 'sizeof' or expr.op == '!':
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

    if isinstance(type_decl, PtrDecl):
        type_decl = type_decl.type

    struct_type = type_decl.type
    if isinstance(struct_type, IdentifierType):
        struct_type = env.get_type(struct_type.names[0]).type

    # if you have the name of the struct but not its field declarations, go find them
    if struct_type.decls is None:
        struct_type_string = struct_type.name
        struct_type = env.get_type(struct_type_string)

    if isinstance(struct_type, TypeDecl):
        struct_type = struct_type.type

    for decl in struct_type.decls:
        if decl.name == expr.field.name:
            ret = deepcopy(decl.type)
            remove_identifier(ret)
            return ret
    raise Exception("Struct doesn't have field " + expr.field.name)

def get_type(expr, env):
    """Takes in an expression and a type environment (map of identifiers to
    types) and returns a new node representing the type of the given expression.
    NOTE: testing for this method is largely done through the test cases
    for remove_compound_assignment, which cover needing to calculate the type
    of many different kinds of expressions."""
    return deepcopy(get_type_helper(expr, env))

def get_type_helper(expr, env): # pylint: disable=too-many-return-statements,too-many-branches
    """Does all of the actual work for get_type, but returns a reference to
    a node that is currently in the AST."""
    # print("---getting type of node of type", type(expr))
    if isinstance(expr, TypeDecl):
        return expr
    elif isinstance(expr, ID):
        # TODO: make it actually work for typedefs
        type_node = env.get_type(expr.name)
        if type_node and isinstance(type_node.type, Struct):
            struct_type = type_node.type
            # if you have the name of the struct but not its field declarations,
            # go find them
            if struct_type.decls is None:
                struct_type_string = struct_type.name
                type_node.type = env.get_type(struct_type_string)
        return type_node
    elif isinstance(expr, Constant):
        # TODO: if the int is over a certain size, change to long?
        return TypeDecl(None, [], IdentifierType([expr.type]))
    elif isinstance(expr, Cast):
        if isinstance(expr.to_type, Typename):
            # TODO: the Typename node has a quals attribute for extra
            # qualifiers. Are these ever important? I don't even know
            # why the Typename node exists in the first place...
            return expr.to_type.type
        else:
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
