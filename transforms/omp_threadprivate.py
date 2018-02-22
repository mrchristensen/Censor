"""Pragma to OMP Threadprivate Node transform"""

import re
from omp.omp_ast import OmpThreadprivate
from omp.clause import Threadprivate
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "threadprivate": Threadprivate
}

class PragmaToOmpThreadprivate(PragmaToOmp):
    """Transform omp threadprivate pragmas"""

    def __init__(self):
        super().__init__(
            OmpThreadprivate,
            re.compile(r'omp +threadprivate\(.*\)'),
            STR_TO_CLAUSE_TYPE,
            False
            )
