"""Pragma to OMP Parallel Node transform"""

import re
from pycparser.c_ast import Pragma
from omp.omp_ast import OmpParallel, OmpFor
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp
from .helpers import ensure_compound

PARALLEL_STR_TO_CLAUSE_TYPE = {
    "if": OmpClause.If,
    "num_threads": OmpClause.NumThreads,
    "default": OmpClause.Default,
    "private": OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "shared": OmpClause.Shared,
    "copyin": OmpClause.CopyIn,
    "reduction": OmpClause.Reduction,
    }

FOR_STR_TO_CLAUSE_TYPE = {
    "private":	    OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate": OmpClause.LastPrivate,
    "reduction": OmpClause.Reduction,
    "schedule": OmpClause.Schedule,
    "collapse": OmpClause.Collapse,
    "ordered": OmpClause.Ordered,
    }

class PragmaToOmpParallelFor(PragmaToOmp):
    """Pragma to OMP Parallel Node transform"""

    def __init__(self):
        super().__init__(
            None, # We override the default transform
            re.compile(r'omp +parallel +for.*'),
            {} # We have to toggle between two mappings for clauses
        )

    def visit_Compound(self, node):
        """Search compound for pragma nodes to transform"""
        node = self.generic_visit(node)
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if isinstance(child, Pragma) \
               and self.pragma_matches(child.string) \
               and index + 1 < len(node.block_items):
                # We wrap the children in a compound block because
                # then we can easily visit scopes by only visiting
                # Compound nodes
                next_sibling = ensure_compound(node.block_items[index+1])
                self.str_to_clause_type = FOR_STR_TO_CLAUSE_TYPE
                for_node = ensure_compound(
                    OmpFor(
                        child.string,
                        self.clause_nodes_from_pragma_string(child.string),
                        next_sibling,
                        child.coord
                        )
                    )
                self.str_to_clause_type = PARALLEL_STR_TO_CLAUSE_TYPE
                node.block_items[index] = OmpParallel(
                    child.string,
                    self.clause_nodes_from_pragma_string(child.string),
                    for_node,
                    child.coord
                )
                node.block_items.pop(index+1)
        return node
