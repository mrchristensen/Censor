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

    This is useful for cases where lists cannot be returned from the visit
    method because there is no way to make all nodes direct children of a
    compound block.
    """

    def __init__(self, id_generator, environments):
        self.index = 0
        self.block_items = []
        self.environments = environments
        self.envr = environments["GLOBAL"]
        self.id_generator = id_generator

    def insert_into_scope(self, *nodes):
        """Insert nodes into scope above current index"""
        self.block_items.insert(0, (self.index, nodes))

    def append_to_scope(self, *nodes):
        """Append nodes to scope below current index"""
        self.block_items.insert(0, (self.index + 1, nodes))

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        """Visit file level scope"""
        block_items = self.block_items
        index = self.index
        self.block_items = []
        self.index = 0
        if node.ext is not None:
            for i, item in enumerate(node.ext):
                self.index = i
                item = self.visit(item)
        for i, items in self.block_items:
            if i < len(node.ext):
                node.ext[i:i] = items
            else:
                node.ext.extend(items)
        self.block_items = block_items
        self.index = index
        return node

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Visit scope"""
        block_items = self.block_items
        envr = self.envr
        index = self.index
        self.block_items = []
        self.envr = self.environments[node]
        self.index = 0
        if node.block_items is not None:
            for i, item in enumerate(node.block_items):
                self.index = i
                node.block_items[i] = self.visit(item)
        for i, items in self.block_items:
            if i < len(node.block_items):
                node.block_items[i:i] = items
            else:
                node.block_items.extend(items)
        self.block_items = block_items
        self.index = index
        self.envr = envr
        return node
