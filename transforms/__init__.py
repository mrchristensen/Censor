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
    type_env_calc = TypeEnvironmentCalculator()
    transformer_generators = [
        lambda: PragmaToOmpParallelSections(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpParallelFor(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpParallel(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpFor(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpSections(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpSection(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpTask(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpTaskgroup(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpTaskwait(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpCritical(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpBarrier(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpAtomic(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpMaster(), # pylint: disable=unnecessary-lambda
        lambda: PragmaToOmpSingle(), # pylint: disable=unnecessary-lambda
        lambda: ForToWhile(), # pylint: disable=unnecessary-lambda
        lambda: WhileToDoWhile(), # pylint: disable=unnecessary-lambda
        lambda: DoWhileToGoto(id_generator),
        lambda: RemoveCompoundAssignment(id_generator,
                                         type_env_calc.get_environments(ast)),
        # lambda: InsertExplicitTypeCasts(type_env_calc.get_environments(ast)), # implementation incopmlete
        # lambda: ThreePlaceOperations(id_generator,
        #                              type_env_calc.get_environments(ast)), # implementation incopmlete
        lambda: SingleReturn(id_generator),
    ]
    for generator in transformer_generators:
        transformer = generator()
        ast = transformer.visit(ast)
    return ast
