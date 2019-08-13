'''Pragma to OMP Parallel Node transform'''

import re
from pycparser.c_ast import Pragma
from omp.omp_ast import OmpParallel, OmpSections
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp
from .helpers import ensure_compound

PARALLEL_STR_TO_CLAUSE_TYPE = {
    "if": OmpClause.If,
    "num_threads": OmpClause.NumThreads,
    "default": OmpClause.Default,
    "shared": OmpClause.Shared,
    "copyin": OmpClause.CopyIn,
    }

SECTIONS_STR_TO_CLAUSE_TYPE = {
    "private":	    OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate": OmpClause.LastPrivate,
    "reduction": OmpClause.Reduction,
    }

class PragmaToOmpParallelSections(PragmaToOmp):
    '''Pragma to OMP Parallel Node transform'''

    def __init__(self):
        super().__init__(
            None, # We override the default transform
            re.compile(r'omp +parallel +sections.*'),
            {} # We have to toggle between two mappings for clauses
        )

    def visit_Compound(self, node):
        '''Search compound for pragma nodes to transform'''
        node = self.generic_visit(node)
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if isinstance(child, Pragma) \
               and self.pragma_matches(child.string) \
               and index + 1 < len(node.block_items):
                next_sibling = ensure_compound(node.block_items[index+1])
                self.str_to_clause_type = SECTIONS_STR_TO_CLAUSE_TYPE
                sections_node = ensure_compound(
                    OmpSections(
                        'omp sections ' + self.filter_clause_str(child.string),
                        self.clause_nodes_from_pragma_string(child.string),
                        next_sibling,
                        child.coord
                        )
                    )
                self.str_to_clause_type = PARALLEL_STR_TO_CLAUSE_TYPE
                node.block_items[index] = OmpParallel(
                    'omp parallel ' + self.filter_clause_str(child.string),
                    self.clause_nodes_from_pragma_string(child.string),
                    sections_node,
                    child.coord
                )
                node.block_items.pop(index+1)
        return node
