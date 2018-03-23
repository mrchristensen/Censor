"""
LiftNode AST transform
"""

from .node_transformer import NodeTransformer

class LiftNode(NodeTransformer):
    """
    Generic node transformer for inserting nodes into the current scope
    you are visiting while transforming the AST. It works by defining a
    visit method for the Compound blocks and defining an 'insert_into_scope'
    method that you can call at any time to have nodes inserted into the current
    scope above the node you are currently transforming.

    This is useful for cases where lists cannot be returned from the visit method
    because there is no way to make all nodes direct children of a compound block.
    """

    def __init__(self, id_generator, environments):
        self.index = 0
        self.inserts = []
        self.environments = environments
        self.envr = environments["GLOBAL"]
        self.id_generator = id_generator

    def insert_into_scope(self, *nodes):
        """Insert nodes into scope above current index"""
        self.inserts.insert(0, (self.index, nodes))

    def append_to_scope(self, *nodes):
        """Append nodes to scope below current index"""
        self.inserts.insert(0, (self.index + 1, nodes))

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Visit scope"""
        parent_env = self.envr
        self.envr = self.environments[node]
        for i, item in enumerate(node.block_items):
            self.index = i
            item = self.visit(item)
        self.index = 0
        for i, inserts in self.inserts:
            if i < len(node.block_items):
                node.block_items[i:i] = inserts
            else:
                node.block_items.extend(inserts)
        self.inserts = []
        self.envr = parent_env
        return node
