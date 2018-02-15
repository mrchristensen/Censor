"""Pragma to OMP Master Node transform"""

import re
from omp.omp_ast import OmpMaster
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {}

class PragmaToOmpMaster(PragmaToOmp):
    """Transform omp master pragmas"""

    def __init__(self):
        super().__init__(
            OmpMaster,
            re.compile(r'omp +master *'),
            STR_TO_CLAUSE_TYPE,
            )
