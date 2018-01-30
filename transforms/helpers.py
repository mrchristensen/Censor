"""Helper functions for node transformers"""

from pycparser.c_ast import Compound

def append_statement(compound, stmt):
    """
    Given a compound node and a node to append, returns a new compound
    with the node to append as the last block item
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
