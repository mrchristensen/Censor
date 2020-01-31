""" Helper functions for node transformers

    propagate_constant(binop)
        takes a binop or constant and reduces it to
        a constant if possible

    get_no_op()
        returns an ast node that is a no_op instruction

    ensure_compound(node)
    append_statement(compound, stmt)
    prepend_statement(compound, stmt)

    make_unit_pointer(node)

    remove_identifier(node)
    add_identifier(node, ident)

"""

from copy import deepcopy
from transforms.node_transformer import NodeTransformer
from .type_environment_calculator import Enviornment
import pycparser.c_ast as AST

#Propagate constants
#pylint: disable=too-many-branches
def propagate_constant(binop):
    """ If both sides are a constant combine into a single constant """
    if isinstance(binop, AST.Constant):
        return binop

    if isinstance(binop, AST.UnaryOp):
        return _perform_unary_operation(binop)

    if isinstance(binop.left, AST.BinaryOp):
        left = propagate_constant(binop.left)
    else:
        left = binop.left
    if isinstance(binop.right, AST.BinaryOp):
        right = propagate_constant(binop.right)
    else:
        right = binop.right

    if not (isinstance(left, AST.Constant) and
            isinstance(right, AST.Constant)):
        return binop #not able to propagate to a single constant

    result_type = 'int'
    if left.type == 'int':
        left_value = int(left.value.translate(
            {ord(c):None for c in 'uUlL'}), 0)
    elif left.type == 'float':
        left_value = float(left.value.translate(
            {ord(c):None for c in 'fFlL'}))
        result_type = 'float'
    else:
        return binop
    if right.type == 'int':
        right_value = int(right.value.translate(
            {ord(c):None for c in 'uUlL'}), 0)
    elif right.type == 'float':
        right_value = float(right.value.translate(
            {ord(c):None for c in 'fFlL'}))
        result_type = 'float'
    else:
        return binop

    return _perform_operation(binop, result_type,
                              left_value, right_value)

def get_no_op():
    """Returns node representina a no-op. Makes a deep copy because we con't
    have any node duplication in the tree because parent links are used
    for interpreting."""
    return deepcopy(_NO_OP)

def ensure_compound(node, environments=None, parent_envr=None):
    """Wrap an AST node in a compound block if necessary"""
    if node is None:
        return None
    elif isinstance(node, AST.Compound):
        if node.block_items is None:
            node.block_items = []
        return node
    else:
        new_compound = AST.Compound([node], node.coord)
        if environments and parent_envr:
            new_envr = Enviornment(parent_envr)
            environments[new_compound] = new_envr
        return new_compound

def append_statement(compound, stmt):
    """
    Given two nodes, returns a new Compound node
    with the second node as the last node in the block
    """
    compound = ensure_compound(compound)
    if stmt:
        compound.block_items.append(stmt)
    return compound

def prepend_statement(compound, stmt):
    """
    Given two nodes, returns a new Compound node
    with the second node as the first node in the block
    """
    compound = ensure_compound(compound)
    if stmt:
        compound.block_items.insert(0, stmt)
    return compound

def make_unit_pointer(node):
    """ helper function to nest a pointer in a void* cast """
    void_id = AST.IdentifierType(['char'])
    void_ptr_type = AST.PtrDecl([], AST.TypeDecl(None, [], void_id),
                                coord=node.coord)
    return AST.Cast(AST.Typename(None, [], void_ptr_type), node,
                    coord=node.coord)

def add_identifier(node, ident):
    """Given a node that could be used as the type attribute of a Decl, attach
    the given identifier to it."""
    if isinstance(node, AST.TypeDecl):
        # add the identifier, end recursion
        node.declname = ident
        return node
    elif isinstance(node, (AST.Struct, AST.Union, AST.Enum)):
        # add the identifier, end recursion
        node.name = ident
        return node
    elif isinstance(node, (AST.PtrDecl, AST.ArrayDecl, AST.FuncDecl)):
        # recur
        node.type = add_identifier(node.type, ident)
        return node
    else:
        raise NotImplementedError()

class WithParent(NodeTransformer): # pylint: disable=too-few-public-methods
    """Node transformer that keeps track of parent nodes"""
    def __init__(self):
        self.parent = None

    def generic_visit(self, node):
        """Visit each child and set parent"""
        old_parent = self.parent
        self.parent = node
        node = super().generic_visit(node)
        self.parent = old_parent
        return node

class IncorrectTransformOrder(Exception):
    """If an AST transform ever realizes it is being called in the wrong
    order (for example, if it encounters a kind of node that should have
    already been removed), it raises this exception."""

    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node
## Private helper functions that shouldn't be called from outside this file ##

# statement representing a no-op in C. See
# https://stackoverflow.com/questions/7978620/whats-a-portable-way-to-implement-no-op-statement-in-c
_NO_OP = AST.Cast(AST.Typename(None, [], AST.IdentifierType(['void'])),
                  AST.Constant('int', '0'))

def _perform_operation(binop, result_type, left_value, right_value):
    """ Combines two constants  """
    if binop.op == '+':
        value = AST.Constant(result_type, str(left_value + right_value))
    elif binop.op == '-':
        value = AST.Constant(result_type, str(left_value - right_value))
    elif binop.op == '*':
        value = AST.Constant(result_type, str(left_value * right_value))
    elif binop.op == '%':
        value = AST.Constant(result_type, str(left_value % right_value))
    elif binop.op == '/':
        if result_type == 'int':
            value = AST.Constant(result_type, str(left_value//right_value))
        else:
            value = AST.Constant(result_type, str(left_value / right_value))
    else:
        value = binop

    value.coord = binop.coord
    return value

def  _perform_unary_operation(unop):
    """ perform unary operation if possible """
    if not isinstance(unop.expr, AST.Constant):
        return unop

    if unop.op == '+':
        value = unop.expr
    elif unop.op == '-':
        result_type = 'int'
        if unop.expr.type == 'int':
            expr_value = int(unop.expr.value.translate(
                {ord(c):None for c in 'uUlL'}), 0)
        elif unop.expr.type == 'float':
            expr_value = float(unop.expr.value.translate(
                {ord(c):None for c in 'fFlL'}))
            result_type = 'float'
        value = AST.Constant(result_type, str(-expr_value))
    else:
        value = unop
    return value
