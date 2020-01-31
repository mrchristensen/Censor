"""Pragma to OMP Task Node transform"""

import re
from omp.omp_ast import OmpTaskloop
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "if": OmpClause.If,
    "shared": OmpClause.Shared,
    "private": OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate": OmpClause.LastPrivate,
    "default": OmpClause.Default,
    "grainsize": OmpClause.GrainSize,
    "num_tasks": OmpClause.NumTasks,
    "collapse": OmpClause.Collapse,
    "final": OmpClause.Final,
    "priority":	OmpClause.Priority,
    "untied": OmpClause.Untied,
    "mergeable": OmpClause.Mergeable,
    "nogroup": OmpClause.NoGroup,
    }

class PragmaToOmpTaskloop(PragmaToOmp):
    """Pragma to OMP Task Node transform"""

    def __init__(self, _=None, __=None):
        super().__init__(
            OmpTaskloop,
            re.compile(r'omp +taskloop.*'),
            STR_TO_CLAUSE_TYPE
        )
