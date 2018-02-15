"""Pragma to OMP Master Node transform"""

import re
from pycparser.c_ast import Pragma
from omp.omp_ast import OmpMaster
from .pragma_to_omp import PragmaToOmp

class PragmaToOmpMaster(PragmaToOmp):
    """Pragma to OMP Master Node transform"""

    def __init__(self):
        super().__init__()
        self.str_to_clause_type = {}
        self.pattern = re.compile(r'omp +master\s*')

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """ Visit each compound node and check it's children for the Pragma
            nodes we want to change. Recursively alter, if found.
        """
        node = self.generic_visit(node)
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if isinstance(child, Pragma) \
            and self.pragma_matches(child.string) \
            and index + 1 != len(node.block_items):

                next_sibling = node.block_items[index+1]
                node.block_items[index] = OmpMaster(
                    pragma=child.string,
                    block=next_sibling,
                    coord=child.coord,
                    )
                node.block_items.pop(index+1)

        return node
