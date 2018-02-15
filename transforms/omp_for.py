"""Pragma to OMP For Node transform"""

import re
from omp.omp_ast import OmpFor
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "private":	    OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate":  OmpClause.LastPrivate,
    "reduction":    OmpClause.Reduction,
    "schedule":     OmpClause.Schedule,
    "collapse":	    OmpClause.Collapse,
    "ordered":	    OmpClause.Ordered,
    "nowait":	    OmpClause.NoWait,
    }

class PragmaToOmpFor(PragmaToOmp):
    """Transform omp for pragmas"""

    def __init__(self):
        super().__init__(
            OmpFor,
            re.compile(r'omp +for.*'),
            STR_TO_CLAUSE_TYPE
            )
