"""AST source to source transformations"""

from .do_while_to_goto import DoWhileToGoto
from .while_to_do_while import WhileToDoWhile
from .for_to_while import ForToWhile
from .omp_parallel_for import PragmaToOmpParallelFor
from .omp_parallel_sections import PragmaToOmpParallelSections
from .omp_parallel import PragmaToOmpParallel
from .omp_for import PragmaToOmpFor
from .omp_sections import PragmaToOmpSections
from .omp_section import PragmaToOmpSection
from .omp_task import PragmaToOmpTask
from .omp_taskgroup import PragmaToOmpTaskgroup
from .omp_taskwait import PragmaToOmpTaskwait
from .omp_critical import PragmaToOmpCritical
from .omp_barrier import PragmaToOmpBarrier
from .omp_atomic import PragmaToOmpAtomic
from .omp_master import PragmaToOmpMaster
from .omp_single import PragmaToOmpSingle
from .id_generator import IDGenerator

def transform(ast):
    """Perform each transform in package"""
    transformers = [
        PragmaToOmpParallelSections(),
        PragmaToOmpParallelFor(),
        PragmaToOmpParallel(),
        PragmaToOmpFor(),
        PragmaToOmpSections(),
        PragmaToOmpSection(),
        PragmaToOmpTask(),
        PragmaToOmpTaskgroup(),
        PragmaToOmpTaskwait(),
        PragmaToOmpCritical(),
        PragmaToOmpBarrier(),
        PragmaToOmpAtomic(),
        PragmaToOmpMaster(),
        PragmaToOmpSingle(),
        ForToWhile(),
        WhileToDoWhile(),
        DoWhileToGoto(IDGenerator(ast))
    ]
    for transformer in transformers:
        ast = transformer.visit(ast)
    return ast
