"""Pragma to OMP Flush Node transform"""

import re
from omp.omp_ast import OmpFlush
from omp.clause import Flush
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "flush": Flush
}

class PragmaToOmpFlush(PragmaToOmp):
    """Transform omp flush pragmas"""

    def __init__(self, _=None, __=None):
        super().__init__(
            OmpFlush,
            re.compile(r'omp +flush.*'),
            STR_TO_CLAUSE_TYPE,
            False
            )
