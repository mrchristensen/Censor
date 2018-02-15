"""Pragma to OMP Sections Node transform"""

import re
from omp.omp_ast import OmpSection
from .pragma_to_omp import PragmaToOmp

STR_TO_CLAUSE_TYPE = {}

class PragmaToOmpSection(PragmaToOmp):
    """Pragma to OMP Sections Node transform"""

    def __init__(self):
        super().__init__(
            OmpSection,
            re.compile(r'omp +section *$'),
            STR_TO_CLAUSE_TYPE
        )
