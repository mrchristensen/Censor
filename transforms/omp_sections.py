'''Pragma to OMP Sections Node transform'''

import re
from omp.omp_ast import OmpSections
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "private": OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate": OmpClause.LastPrivate,
    "reduction": OmpClause.Reduction,
    "nowait": OmpClause.NoWait,
    }

class PragmaToOmpSections(PragmaToOmp):
    '''Pragma to OMP Sections Node transform'''

    def __init__(self):
        super().__init__(
            OmpSections,
            re.compile(r'omp +sections.*'),
            STR_TO_CLAUSE_TYPE
        )
