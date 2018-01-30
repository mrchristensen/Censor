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
