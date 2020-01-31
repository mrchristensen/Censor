"""Pragma to OMP Parallel Node transform"""

import pycparser.c_ast as AST
from .node_transformer import NodeTransformer
from .type_environment_calculator import Enviornment

class CorrectPragmaPlacement(NodeTransformer):
    """ Put compound blocks where needed in order to have
        pragma's properly be before what they were meant to"""

    def __init__(self, id_gen=None, environments=None):
        self.id_gen = id_gen
        self.environments = environments
        self.cur_env = environments['GLOBAL']

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Search compound for pragma nodes to transform"""
        if node.block_items is None:
            return node
        parent = self.cur_env
        self.cur_env = self.environments[node]
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
        self.cur_env = parent
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
            new_compound = AST.Compound(block, item.coord)
            new_envr = Enviornment(self.cur_env)
            self.environments[new_compound] = new_envr
            return new_compound
        elif isinstance(item, AST.Compound):
            return item
        else:
            new_compound = AST.Compound([item], item.coord)
            new_envr = Enviornment(self.cur_env)
            self.environments[new_compound] = new_envr
            if isinstance(item, AST.If):
                if isinstance(item.iftrue, AST.Compound):
                    self.environments[item.iftrue].parent = new_envr
                if isinstance(item.iffalse, AST.Compound):
                    self.environments[item.iffalse].parent = new_envr
            return new_compound
