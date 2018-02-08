"""Pragma to OMP For Node transform"""

import re
from pycparser.c_ast import Pragma, For
from omp.omp_ast import OmpFor
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

class PragmaToOmpFor(PragmaToOmp):
    """Pragma to OMP For Node transform"""

    def __init__(self):
        super().__init__()
        self.str_to_clause_type = {
            "private":	    OmpClause.Private,
            "firstprivate": OmpClause.FirstPrivate,
            "lastprivate":  OmpClause.LastPrivate,
            "reduction":    OmpClause.Reduction,
            "schedule":     OmpClause.Schedule,
            "collapse":	    OmpClause.Collapse,
            "ordered":	    OmpClause.Ordered,
            "nowait":	    OmpClause.NoWait,
            }
        self.pattern = re.compile(r'omp +for( +[a-zA-Z]+(\([0-9]+\))?)*')

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """ Visit each compound node and check it's children for the Pragma
            nodes we want to change. Recursively alter, if found.
        """
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            next_sibling = node.block_items[index+1]
            if isinstance(child, Pragma) \
            and isinstance(next_sibling, For) \
            and self.pragma_matches(child.string):

                node.block_items[index] = OmpFor(
                    pragma=child.string,
                    clauses=self.clause_nodes_from_pragma_string(child.string),
                    loops=next_sibling,
                    coord=child.coord
                    )
                node.block_items.pop(index+1)
                self.visit(node.block_items[index])

        return node
