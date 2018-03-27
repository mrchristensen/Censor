"""Helper functions for node transformers"""

from pycparser.c_ast import Compound

def ensure_compound(node):
    """Wrap an AST node in a compound block if necessary"""
    if node is None:
        return Compound([])
    if isinstance(node, Compound):
        if node.block_items is None:
            node.block_items = []
        return node
    return Compound([node])

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

class IncorrectTransformOrder(Exception):
    """If an AST transform ever realizes it is being called in the wrong
    order (for example, if it encounters a kind of node that should have
    already been removed), it raises this exception."""

    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node
