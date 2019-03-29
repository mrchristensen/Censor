"""Pragma to OMP Parallel Node transform"""

import pycparser.c_ast as AST
from .node_transformer import NodeTransformer

class CorrectPragmaPlacement(NodeTransformer):
    """ Put compound blocks where needed in order to have
        pragma's properly be before what they were meant to"""

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Search compound for pragma nodes to transform"""
        if node.block_items is None:
            return node
        self.remove_list = [] #pylint: disable=attribute-defined-outside-init
        for index, child in enumerate(node.block_items):
            if isinstance(child, (AST.For, AST.While, AST.DoWhile)):
                child.stmt = self.ensure_compound(node, index, child.stmt)
            elif isinstance(child, AST.If):
                #do not need the true side because pycparser would throw an
                #error on finding else with out a if, keep to make compound
                child.iftrue = self.ensure_compound(node, index, child.iftrue)
                if child.iffalse is not None:
                    child.iffalse = self.ensure_compound(node,
                                                         index,
                                                         child.iffalse)
        for index in reversed(self.remove_list):
            del node.block_items[index]
        self.remove_list = [] #pylint: disable=attribute-defined-outside-init
        node = self.generic_visit(node)
        return node

    def ensure_compound(self, compound, index, item):
        """ If pragma grap next and make compound,
            if compound do nothing alse make compound """
        if isinstance(item, AST.Pragma):
            block = [item]
            index += 1
            while isinstance(compound.block_items[index], AST.Pragma):
                index += 1
                self.remove_list.append(index)
                block.append(compound.block_items[index])

            self.remove_list.append(index)
            block.append(compound.block_items[index])

            return AST.Compound(block, item.coord)
        elif isinstance(item, AST.Compound):
            return item
        else:
            return AST.Compound([item], item.coord)
