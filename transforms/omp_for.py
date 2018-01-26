"""Pragma to OMP For Node transform"""

import re
from omp_ast import OmpFor
from pycparser.c_ast import Pragma, For
from .node_transformer import NodeTransformer

class PragmaToOmpFor(NodeTransformer):
    """Pragma to OMP For Node transform"""

    def __init__(self):
        self.pattern = re.compile(r'omp +for( +[a-zA-Z]+(\([0-9]+\))?)*')

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """ Visit each compound node and check it's children for the Pragma
            nodes we want to change. Recursively alter, if found.
        """
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if isinstance(child, Pragma) and isinstance(node.block_items[index+1], For):
                node.block_items[index] = self.alter_pragma(child, node.block_items[index+1])
                node.block_items.pop(index+1)
                self.visit(node.block_items[index])
        return node

    def alter_pragma(self, node, for_):
        """ Return an OmpFor Node with the following for nested underneath
            if it is an omp for pragma
        """
        matches = self.pattern.match(node.string)
        if matches:
            return OmpFor(node.string.split()[2:], [for_], node.coord)
