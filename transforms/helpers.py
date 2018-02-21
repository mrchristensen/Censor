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

class IncorrectTransformOrder(Exception):
    """If an AST transform ever realizes it is being called in the wrong
    order (for example, if it encounters a kind of node that should have
    already been removed), it raises this exception."""

    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node

class IDGenerator(object): #pylint:disable=too-few-public-methods
    """Produces identifiers for tranforms to use when they need to declare
    an extra variable as part of a transform. They are guaranteed to be unique
    becuase they use a static counter. They are also guaranteed not to collide
    with any valid identifier in the input program because they begin
    with a $."""
    GLOBAL_ID_COUNT = 0
    @staticmethod
    def get_unique_id():
        """Generates a unique id."""
        IDGenerator.GLOBAL_ID_COUNT += 1
        return "$" + str(IDGenerator.GLOBAL_ID_COUNT)
