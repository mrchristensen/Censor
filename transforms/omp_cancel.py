'''Pragma to OMP Cancel Node transform'''

import re
from omp.omp_ast import OmpCancel
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "if": OmpClause.If,
    "parallel": OmpClause.Parallel,
    "for": OmpClause.For,
    "sections": OmpClause.Sections,
    "taskgroup": OmpClause.Taskgroup,
    }

class PragmaToOmpCancel(PragmaToOmp):
    '''Pragma to OmpCancel Node transform'''

    def __init__(self):
        super().__init__(
            OmpCancel,
            re.compile(r'omp +cancel.*'),
            STR_TO_CLAUSE_TYPE,
            False
        )
