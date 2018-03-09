"""AST source to source transformations"""

# imports for transforms
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
from .remove_compound_assignment import RemoveCompoundAssignment
# from .insert_explicit_type_casts import InsertExplicitTypeCasts #implementation incomplete
from .single_return import SingleReturn

# other imports
from .id_generator import IDGenerator
from .type_environment_calculator import TypeEnvironmentCalculator

def transform(ast):
    """Perform each transform in package"""
    # one id_generator must be passed to all transforms, to
    # ensure unique ids across transforms
    id_generator = IDGenerator(ast)
    # type environments should be recalculated each time they are needed
    # for a transform, because the AST changes and so the type environments
    # should be different
    # TODO: figure out a sensible way to pass the type environments to the
    # transforms that need it
    # type_env_calc = TypeEnvironmentCalculator()
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
        DoWhileToGoto(id_generator),
        # RemoveCompoundAssignment(id_generator, type_env_calc.get_environments(ast))
        # InsertExplicitTypeCasts # implementation incopmlete
        SingleReturn(id_generator),
    ]
    for transformer in transformers:
        ast = transformer.visit(ast)
    return ast
