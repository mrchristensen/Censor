"""
Helpers for working with information about types during AST transformations.
All references to the c specification refer to the version here:
    http://www.open-std.org/jtc1/sc22/WG14/www/docs/n1256.pdf
"""
# pylint: disable=useless-import-alias
from copy import deepcopy
import io
from enum import Enum
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
import cesk.limits as limits

class Side(Enum):
    """Return type of function asking which type of a binary operand that
    both sides should be cast to."""
    LEFT = 1
    RIGHT = 2
    NOCAST = 3

def get_type(expr, env):
    """Takes in an expression and a type environment (map of identifiers to
    types) and returns a new node representing the type of the given expression.
    NOTE: testing for this method is largely done through the test cases
    for remove_compound_assignment, which cover needing to calculate the type
    of many different kinds of expressions."""
    return deepcopy(_get_type_helper(expr, env))

def make_temp_ptr(lvalue_expr, id_generator, env):
    """Given an lvalue, this function will return a Decl node representing a
    declaration of a new unique identifier, and assigning the address of the
    given lvalue to that unique idenitfier. This is very useful when you need
    a temp variable while simplifying complicated expressions in the AST."""
    temp_name = id_generator.get_unique_id()
    lvalue_addr = UnaryOp('&', lvalue_expr)
    lvalue_type = get_type(lvalue_expr, env)
    ptr_to_lvalue = PtrDecl([], add_identifier(lvalue_type, temp_name))
    return Decl(temp_name, [], [], [], ptr_to_lvalue, lvalue_addr, None)

def make_temp_value(expr, id_generator, env):
    """Given an expression, this function will return a Decl node representing
    a declaration of a new unique identifier, and assigning the expression
    to that unique idenitfier. This is very useful when you need
    a temp variable while simplifying complicated expressions in the AST."""
    name = id_generator.get_unique_id()
    typ = get_type(expr, env)
    return Decl(name, [], [], [], add_identifier(typ, name), expr, None)

def cast_if_needed(type_node, expr, env):
    """Decides if it is necessary to cast the given expr to the given type,
    or if the types are already unified."""
    # TODO: currently, this function can only decide if two types are unified
    # if they are integral or floating types. If we ever have a deep compare
    # method than can decide equality of any arbitrary ast nodes, we should
    # use that to decide type unification over all types
    expr_type = get_type(expr, env)
    expr_str = io.StringIO()
    type_str = io.StringIO()
    type_node.show(buf=type_str)
    expr_type.show(buf=expr_str)
    if type_str.getvalue() == expr_str.getvalue():
        return expr

    if _is_integral(type_node) or _is_float(type_node):
        if resolve_types(type_node, expr_type) == Side.NOCAST:
            return expr
    elif isinstance(type_node, ArrayDecl):
        # Cannot cast to array type
        return expr
    return Cast(type_node, expr)

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
        node.show()
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

def resolve_types(left, right): # pylint: disable=too-many-return-statements
    """Given two types, figure out what types they should be cast to when
    a binary operation is performed on two objects with the given types
    The rules implemented here come directly from the c spec,
    section, 6.3.1.8 Usual arithmetic conversions, p. 44.
    """
    if _is_ptr(left) and _is_integral(right):
        return Side.NOCAST
    elif _is_integral(left) and _is_ptr(right):
        return Side.NOCAST
    elif _is_ptr(left) and _is_ptr(right):
        return Side.NOCAST
    elif _is_float(left) and _is_integral(right):
        return Side.LEFT
    elif _is_integral(left) and _is_float(right):
        return Side.RIGHT
    elif _is_float(left) and _is_float(right):
        return _resolve_floating_types(left, right)
    elif _is_integral(left) and _is_integral(right):
        return _resolve_integral_types(left, right)
    if _is_array(left) and _is_integral(right):
        return Side.NOCAST
    elif _is_integral(left) and _is_array(right):
        return Side.NOCAST
    print("---left:")
    left.show()
    print("---right:")
    right.show()
    raise NotImplementedError()

def get_no_op():
    """Returns node representina a no-op. Makes a deep copy because we con't
    have any node duplication in the tree because parent links are used
    for interpreting."""
    return deepcopy(_NO_OP)

## Private helper functions that shouldn't be called from outside this file ##

# statement representing a no-op in C. See
# https://stackoverflow.com/questions/7978620/whats-a-portable-way-to-implement-no-op-statement-in-c
_NO_OP = Cast(Typename(None, [], IdentifierType(['void'])),
              Constant('int', '0'))

def _get_type_helper(expr, env): # pylint: disable=too-many-return-statements,too-many-branches
    """Does all of the actual work for get_type, but returns a reference to
    a node that is currently in the AST."""
    if isinstance(expr, (TypeDecl, PtrDecl, ArrayDecl, Typename)):
        return expr
    elif isinstance(expr, str):
        return _get_type_helper(ID(expr), env)
    elif isinstance(expr, ID):
        return _get_id_type(expr, env)
    elif isinstance(expr, Constant):
        # TODO: if the int is over a certain size, change to long?
        if expr.type == 'string':
            return PtrDecl([], TypeDecl(None, [], IdentifierType(['char'])))
        elif expr.type == 'float':
            if expr.value[-1] in "fF":
                return TypeDecl(None, [], IdentifierType(['float']))
            elif expr.value[-1] in "lL":
                return TypeDecl(None, [], IdentifierType(['long', 'double']))
            else:
                return TypeDecl(None, [], IdentifierType(['double']))
        else:
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
        return _get_unop_type(expr, env)
    elif isinstance(expr, BinaryOp):
        return _get_binop_type(expr, env)
    elif isinstance(expr, TernaryOp):
        return _get_ternary_type(expr, env)
    elif isinstance(expr, StructRef):
        return _get_structref_type(expr, env)
    elif isinstance(expr, ArrayRef):
        return _get_type_helper(expr.name, env).type
    elif isinstance(expr, FuncCall):
        func_decl = env.get_type(expr.name)
        return func_decl.type
    elif isinstance(expr, ExprList): # is type of last expression
        return _get_type_helper(expr.exprs[-1], env)
    elif isinstance(expr, Assignment):
        return _get_type_helper(expr.lvalue, env)
    else:
        raise NotImplementedError("Have not implemented get_type " +
                                  "for node type: " + type(expr).__name__)
    return expr.type

def _get_id_type(expr, env):
    # TODO: make it actually work for typedefs
    type_node = env.get_type(expr.name)
    if type_node and isinstance(type_node.type, (Struct, Union)):
        struct_type = type_node.type
        # if you have the name of the struct but not its field declarations,
        # go find them
        if struct_type.decls is None:
            struct_type_string = type(struct_type).__name__  \
                                + " " + struct_type.name
            type_node.type = env.get_type(struct_type_string)
    return type_node

def _is_integral(type_node):
    """Returns if the given type node describes an integral type."""
    # TODO: Add support for user-defined integral types that are
    # defined through typedef's or enums
    if _is_float(type_node):
        return False
    integral_ids = ['int', 'char', 'short', 'long',
                    'long long', 'unsigned', 'signed']
    if isinstance(type_node, TypeDecl):
        if isinstance(type_node.type, IdentifierType):
            return bool([i for i in integral_ids if i in type_node.type.names])
        return False
    elif isinstance(type_node, IdentifierType):
        return bool([i for i in integral_ids if i in type_node.names])
    return False

def _is_float(type_node):
    """Returns if the given type node describes an integral type."""
    # TODO: Add support for user-defined floating types that are
    # defined through typedef's
    if isinstance(type_node, TypeDecl):
        if isinstance(type_node.type, IdentifierType):
            return 'float' in type_node.type.names or \
                    'double' in type_node.type.names
        return False
    elif isinstance(type_node, IdentifierType):
        return 'float' in type_node.names or \
                'double' in type_node.names
    return False

def _is_arithmetic_type(typ):
    """Returns true if the type node is an arithmetic type"""
    return _is_float(typ) or _is_integral(typ)

def _is_ptr(type_node):
    """Returns true if the given type node describes a pointer type."""
    return isinstance(type_node, PtrDecl)

def _is_array(type_node):
    """Returns true is the given type node describes an array type."""
    return isinstance(type_node, ArrayDecl)

def _get_integral_range(type_node):
    """Takes in a type_node describing an integral type and returns the range
    of integers that the given integral type can represent, e.g.
    _get_integral_range(TypeDecl(None, [],
                    IdentifierType(['char'])) == Range(-128,127)"""
    # TODO: Add support for user-defined integral types that are
    # defined through typedef's or enums
    type_string = " ".join(type_node.type.names)
    return limits.RANGES[type_string]

def _is_signed(int_range):
    """Takes a Range, says if that Range represents a signed integral type."""
    return int_range.min != 0

def _resolve_integral_types(left, right): # pylint: disable=too-many-return-statements
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types.
    For the rationale, see c spec, section, 6.3.1.8 Usual arithmetic
    conversions, p. 44."""
    # TODO Add support for user-defined integral types that are
    # defined through typedef's or enums
    l_range = _get_integral_range(left)
    r_range = _get_integral_range(right)

    if l_range == r_range:
        return Side.NOCAST
    elif _is_signed(l_range) == _is_signed(r_range):
        if l_range.max > r_range.max:
            return Side.LEFT
        else:
            return Side.RIGHT
    elif not _is_signed(l_range) and l_range.max >= (r_range.max - r_range.min):
        return Side.LEFT
    elif not _is_signed(r_range) and r_range.max >= (l_range.max - l_range.min):
        return Side.RIGHT
    elif _is_signed(l_range) and l_range.max >= r_range.max:
        return Side.LEFT
    elif _is_signed(r_range) and r_range.max >= l_range.max:
        return Side.RIGHT
    else:
        # Technically, there is an extra case in the C spec here:
        # "Otherwise, both operands are converted to the unsigned integer type
        # corresponding to the type of the operand with signed integer type."
        # As an implementation, we don't want to have to deal with that, so
        # cesk.limits.py should be set up so that this case is never reached.
        raise Exception("Incorrect integer Limits!")

def _resolve_floating_types(left, right):
    """Given two integral types, figure out what types they should be cast to
    when a binary operation is performed on two objects with the given types.
    For the rationale, see c spec, section, 6.3.1.8 Usual arithmetic
    conversions, p. 44."""
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

def _get_ternary_type(expr, env):
    """Takes a TernaryOp node and a type environment and returns
    a node representing the type of the given expression.
    If the two sides of the ternary operator have arithmetic types
    then the two types are resolved as if there were an operator between them.
    Otherwise the types must be the same so just return the type of one side.
    See the c spec, p. 90. for Ternarys, p. 44 about binary operations"""
    # TODO There might be some corner cases with pointers and type qualifiers
    left_type = get_type(expr.iftrue, env)
    right_type = get_type(expr.iffalse, env)
    if _is_arithmetic_type(left_type) and _is_arithmetic_type(right_type):
        if resolve_types(left_type, right_type) == Side.LEFT:
            return left_type
        else:
            return right_type
    else:
        if _is_nullptr_const(expr.iftrue):
            return get_type(expr.iffalse, env)
        else:
            return get_type(expr.iftrue, env)

def _is_nullptr_const(node):
    """Returns a boolean representing whether or not the given node could be
    interpreted as a nullptr constant."""
    return isinstance(node, Constant) and node.value == 0

def _get_binop_type(expr, env):
    """Takes in a BinaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op in ['<', '<=', '==', '>', '>=', '!=', '&&', '||']:
        return TypeDecl(None, [], IdentifierType(['int']))
    elif expr.op in ['%', '*', '+', '-', '/', '^', '|', '&', '<<', '>>']:
        left_type = get_type(expr.left, env)
        right_type = get_type(expr.right, env)
        if _is_array(left_type):
            left_type = PtrDecl([], left_type.type)
        elif _is_array(right_type):
            right_type = PtrDecl([], right_type.type)
        resolved_type = resolve_types(left_type, right_type)
        if resolved_type == Side.LEFT:
            result_type = left_type
        elif resolved_type == Side.RIGHT:
            result_type = right_type
        elif _is_ptr(left_type) and _is_ptr(right_type):
            result_type = TypeDecl(None, [], IdentifierType(['int']))
        elif _is_ptr(right_type):
            return right_type
        else:
            result_type = left_type
        return result_type
    else:
        raise NotImplementedError()

def _get_unop_type(expr, env):
    """Takes in a UnaryOp node and a type environment (map of identifiers to
    types) and returns a node representing the type of the given expression."""
    if expr.op == 'sizeof':
        return TypeDecl(None, [], IdentifierType(['unsigned', 'long']))
    elif expr.op == '!':
        return TypeDecl(None, [], IdentifierType(['int']))
    elif expr.op in ['++', '--', '+', '-', '~', 'p--', 'p++']:
        return get_type(expr.expr, env)
    elif expr.op == '&':
        type_expr = _get_type_helper(expr.expr, env)
        if _is_array(type_expr):
            type_expr = type_expr.type
        return PtrDecl([], type_expr)
    elif expr.op == '*':
        type_of_operand = get_type(expr.expr, env)
        if not isinstance(type_of_operand, (PtrDecl, ArrayDecl)):
            raise Exception("Attempting to dereference a non-pointer."+
                            str(type_of_operand))
        return type_of_operand.type
    else:
        raise NotImplementedError()

def _get_structref_type(expr, env):
    """Resolve the type of a StructRef node."""
    # find the type of whatever is on the left of the . or ->
    type_decl = _get_type_helper(expr.name, env)
    if isinstance(type_decl, PtrDecl):
        type_decl = type_decl.type

    struct_type = type_decl.type
    if isinstance(struct_type, IdentifierType):
        struct_type = env.get_type(struct_type.names[0]).type

    # if you have the name of the struct but not its field declarations,
    # go find them
    if struct_type.decls is None:
        struct_type_string = type(struct_type).__name__ + " " + struct_type.name
        struct_type = env.get_type(struct_type_string)

    if isinstance(struct_type, TypeDecl):
        struct_type = struct_type.type

    for decl in struct_type.decls:
        if decl.name == expr.field.name:
            ret = deepcopy(decl.type)
            remove_identifier(ret)
            return ret
    raise Exception("Struct doesn't have field " + expr.field.name)
