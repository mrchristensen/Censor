"""Pragma to OMP Task Node transform"""

import re
from omp.omp_ast import OmpTask
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "if": OmpClause.If,
    "final": OmpClause.Final,
    "untied": OmpClause.Untied,
    "default": OmpClause.Default,
    "mergeable": OmpClause.Mergeable,
    "private": OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "shared": OmpClause.Shared,
    "depend": OmpClause.Depend,
    "priority":	OmpClause.Priority,
    }

class PragmaToOmpTask(PragmaToOmp):
    """Pragma to OMP Task Node transform"""

    def __init__(self):
        super().__init__(
            OmpTask,
            re.compile(r'omp +task.*'),
            STR_TO_CLAUSE_TYPE
        )
