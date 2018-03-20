"""
AST source to source transformations

Some transforms must be done before others to ensure correctness.
transform1 < transform2 should be read as "transform1 must be performed
before transform2." The ordering is as follows:

RemoveInitLists < InsertExplicitTypeCasts
RemoveCompoundAssignment < InsertExplicitTypeCasts
InsertExplicitTypeCasts < ThreePlaceOperations

transforms that pull computations out of
if-checks, array refs, and FunctionCalls < ThreePlaceOperations
"""

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
# from .remove_init_lists import RemoveInitLists #implementation incomplete
from .insert_explicit_type_casts import InsertExplicitTypeCasts
# from .three_place_operations import ThreePlaceOperations
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
    type_env_calc = TypeEnvironmentCalculator()
    transformer_generators = [
        lambda: PragmaToOmpParallelSections(),
        lambda: PragmaToOmpParallelFor(),
        lambda: PragmaToOmpParallel(),
        lambda: PragmaToOmpFor(),
        lambda: PragmaToOmpSections(),
        lambda: PragmaToOmpSection(),
        lambda: PragmaToOmpTask(),
        lambda: PragmaToOmpTaskgroup(),
        lambda: PragmaToOmpTaskwait(),
        lambda: PragmaToOmpCritical(),
        lambda: PragmaToOmpBarrier(),
        lambda: PragmaToOmpAtomic(),
        lambda: PragmaToOmpMaster(),
        lambda: PragmaToOmpSingle(),
        lambda: ForToWhile(),
        lambda: WhileToDoWhile(),
        lambda: DoWhileToGoto(id_generator),
        lambda: RemoveCompoundAssignment(id_generator,
                                         type_env_calc.get_environments(ast)),
        # lambda: RemoveInitLists(type_env_calc.get_environments(ast)),
        lambda: InsertExplicitTypeCasts(type_env_calc.get_environments(ast)),
        # TODO: Use ThreePlaceOperations once we have transforms that pull
        # computations out of if-checks, array refs, and FunctionCalls
        # lambda: ThreePlaceOperations(id_generator,
        #                              type_env_calc.get_environments(ast)),
        lambda: SingleReturn(id_generator),
    ]
    for generator in transformer_generators:
        transformer = generator()
        ast = transformer.visit(ast)
    return ast
