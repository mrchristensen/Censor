'''Pragma to OMP Barrier Node transform'''

import re
from omp.omp_ast import OmpBarrier
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {}

class PragmaToOmpBarrier(PragmaToOmp):
    '''Transform omp barrier pragmas'''

    def __init__(self):
        super().__init__(
            OmpBarrier,
            re.compile(r'omp +barrier *'),
            STR_TO_CLAUSE_TYPE,
            False
            )
