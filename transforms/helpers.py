"""Helper functions for node transformers"""

from pycparser.c_ast import Compound

def append_statement(compound, stmt):
    """
    Given two nodes, returns a new Compound node
    with the second node as the last node in the block
    """
    items = []
    if isinstance(compound, Compound):
        if compound.block_items:
            items = compound.block_items
    elif compound:
        items = [compound]

    if stmt:
        items.append(stmt)
    return Compound(items)

def prepend_statement(compound, stmt):
    """
    Given two nodes, returns a new Compound node
    with the second node as the first node in the block
    """
    items = []
    if isinstance(compound, Compound):
        if compound.block_items:
            items = compound.block_items
    elif compound:
        items = [compound]

    if stmt:
        items.insert(0, stmt)
    return Compound(items)

class IncorrectTransformOrder(Exception):
    """If an AST transform ever realizes it is being called in the wrong
    order (for example, if it encounters a kind of node that should have
    already been removed), it raises this exception."""

    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node
