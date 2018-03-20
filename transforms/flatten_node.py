"""
FlattenNode AST transform
"""

from .node_transformer import NodeTransformer

class FlattenNode(NodeTransformer):
    """
    Generic node transformer for taking one node and replacing
    it with a many nodes. It works by defining 'visit_Compound' method
    to visit each scope and an 'insert_into_scope'
    method that you can call during any visit and the nodes will
    be inserted into the current scope above the node you are visiting.
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
