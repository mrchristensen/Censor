'''Pragma to OMP Taskwait Node transform'''

import re
from omp.omp_ast import OmpTaskwait
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {}

class PragmaToOmpTaskwait(PragmaToOmp):
    '''Transform omp taskwait pragmas'''

    def __init__(self):
        super().__init__(
            OmpTaskwait,
            re.compile(r'omp +taskwait *$'),
            STR_TO_CLAUSE_TYPE,
            False
            )
