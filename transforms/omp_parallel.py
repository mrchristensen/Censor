"""Pragma to OMP Parallel Node transform"""

import re
from pycparser.c_ast import Pragma
from omp.omp_ast import OmpParallel
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

class PragmaToOmpParallel(PragmaToOmp):
    """Pragma to OMP Parallel Node transform"""

    def __init__(self):
        super().__init__()
        self.str_to_clause_type = {
            "if":	    	OmpClause.If,
            "num_threads": 	OmpClause.NumThreads,
            "default":  	OmpClause.Default,
            "private":    	OmpClause.Private,
            "firstprivate":     OmpClause.FirstPrivate,
            "shared":	    	OmpClause.Shared,
            "copyin":	        OmpClause.CopyIn,
            "reduction":	OmpClause.Reduction,
            }
        self.pattern = re.compile(r'omp +parallel( +[a-zA-Z]+(\([0-9]+\))?)*')

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """ Visit each compound node and check it's children for the Pragma
            nodes we want to change. Recursively alter, if found.
        """
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if len(node.block_items) == index + 1:
                break

            next_sibling = node.block_items[index+1]
            if isinstance(child, Pragma) \
            and self.pragma_matches(child.string):

                node.block_items[index] = OmpParallel(
                    pragma=child.string,
                    clauses=self.clause_nodes_from_pragma_string(child.string),
                    block=next_sibling,
                    coord=child.coord
                    )
                node.block_items.pop(index+1)
                self.visit(node.block_items[index])

        return node
