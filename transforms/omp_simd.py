"""OmpSimd Transform"""

import re
from omp.omp_ast import OmpSimd
import omp.clause as OmpClause
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {
    "safelen": OmpClause.Safelen,
    "simdlen": OmpClause.Simdlen,
    "linear": OmpClause.Linear,
    "aligned": OmpClause.Aligned,
    "private": OmpClause.Private,
    "firstprivate": OmpClause.FirstPrivate,
    "lastprivate": OmpClause.LastPrivate,
    "reduction": OmpClause.Reduction,
    "collapse": OmpClause.Collapse,
}


class PragmaToOmpSimd(PragmaToOmp):
    """OmpSimd Transform"""

    def __init__(self):
        super().__init__(
            OmpSimd,
            re.compile(r'omp +simd.*'),
            STR_TO_CLAUSE_TYPE
            )
