'''Pragma to OMP Taskgroup Node transform'''

import re
from omp.omp_ast import OmpTaskgroup
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {}

class PragmaToOmpTaskgroup(PragmaToOmp):
    '''Transform omp taskgroup pragmas'''

    def __init__(self):
        super().__init__(
            OmpTaskgroup,
            re.compile(r'omp +taskgroup *$'),
            STR_TO_CLAUSE_TYPE,
            )
