"""Pragma to OMP Critical Node transform"""

import re
from omp.omp_ast import OmpCritical
from omp.clause import Critical, Hint
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "hint": Hint,
    "critical": Critical
}

class PragmaToOmpCritical(PragmaToOmp):
    """Transform omp critical pragmas"""

    def __init__(self):
        super().__init__(
            OmpCritical,
            re.compile(r'omp +critical.*'),
            STR_TO_CLAUSE_TYPE
            )
