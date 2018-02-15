"""Pragma to OMP Barrier Node transform"""

import re
from omp.omp_ast import OmpBarrier
from .pragma_to_omp import PragmaToOmp

class PragmaToOmpBarrier(PragmaToOmp):
    """Pragma to OMP Barrier Node transform"""

    def __init__(self):
        super().__init__()
        self.str_to_clause_type = {}
        self.pattern = re.compile(r'omp +barrier\s*')

    def visit_Pragma(self, node): #pylint: disable=invalid-name
        """Visit each Pragma node and change it if it matches our pattern"""
        if self.pragma_matches(node.string):
            return OmpBarrier(node.string)
        return node
