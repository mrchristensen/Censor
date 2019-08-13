'''Pragma to OMP CancellationPoint Node transform'''

import re
from omp.omp_ast import OmpCancellationPoint
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "parallel": OmpClause.Parallel,
    "for": OmpClause.For,
    "sections": OmpClause.Sections,
    "taskgroup": OmpClause.Taskgroup,
    }

class PragmaToOmpCancellationPoint(PragmaToOmp):
    '''Pragma to OmpCancellationPoint Node transform'''

    def __init__(self):
        super().__init__(
            OmpCancellationPoint,
            re.compile(r'omp +cancellation point.*'),
            STR_TO_CLAUSE_TYPE,
            False
        )
