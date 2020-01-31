"""Pragma to OMP Single Node transform"""

import re
from omp.omp_ast import OmpSingle
from omp.clause import NoWait, Private, FirstPrivate, CopyPrivate
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    'nowait': NoWait,
    'private': Private,
    'firstprivate': FirstPrivate,
    'copyprivate': CopyPrivate
    }

class PragmaToOmpSingle(PragmaToOmp):
    """Transform omp single pragmas"""

    def __init__(self, _=None, __=None):
        super().__init__(
            OmpSingle,
            re.compile(r'omp +single.*'),
            STR_TO_CLAUSE_TYPE
            )
