"""Pragma to OMP Parallel Node transform"""

import re
from omp.omp_ast import OmpParallel
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "if":	    	OmpClause.If,
    "num_threads": 	OmpClause.NumThreads,
    "default":  	OmpClause.Default,
    "private":    	OmpClause.Private,
    "firstprivate":     OmpClause.FirstPrivate,
    "shared":	    	OmpClause.Shared,
    "copyin":	        OmpClause.CopyIn,
    "reduction":	OmpClause.Reduction,
    }

class PragmaToOmpParallel(PragmaToOmp):
    """Pragma to OMP Parallel Node transform"""

    def __init__(self):
        super().__init__(
            OmpParallel,
            re.compile(r'omp +parallel( +[a-zA-Z]+(\([0-9]+\))?)*'),
            STR_TO_CLAUSE_TYPE
        )
