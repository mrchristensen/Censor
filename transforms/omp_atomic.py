'''Pragma to OMP Atomic Node transform'''

import re
from omp.omp_ast import OmpAtomic
from omp.clause import SeqCst, Read, Write, Update, Capture
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "seq_cst": SeqCst,
    "read": Read,
    "write": Write,
    "update": Update,
    "capture": Capture,
}

class PragmaToOmpAtomic(PragmaToOmp):
    '''Transform omp atomic pragmas'''

    def __init__(self):
        super().__init__(
            OmpAtomic,
            re.compile(r'omp +atomic.*'),
            STR_TO_CLAUSE_TYPE
            )
