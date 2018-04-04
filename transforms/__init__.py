"""
AST source to source transformations

Some transforms must be done before others to ensure correctness.
transform1 < transform2 should be read as "transform1 must be performed
before transform2." The ordering is as follows:

PragmaToOmpParallelFor < PragmaToOmpParallel
PragmaToOmpParallelSections < PragmaToOmpParallel
PragmaToOmpFor < ForToWhile
RemoveInitLists < InsertExplicitTypeCasts
ForToWhile < WhileToDoWhile
WhileToDoWhile < DoWhileToGoto
DoWhileToGoto < LiftToCompoundBlock
LiftToCompoundBlock < RemoveCompoundAssignment
RemoveCompoundAssignment < InsertExplicitTypeCasts
"""

# imports for transforms
from .do_while_to_goto import DoWhileToGoto
from .while_to_do_while import WhileToDoWhile
from .for_to_while import ForToWhile
from .if_goto import IfToIfGoto
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
from .lift_to_compound_block import LiftToCompoundBlock
# from .remove_init_lists import RemoveInitLists #implementation incomplete
from .insert_explicit_type_casts import InsertExplicitTypeCasts
from .single_return import SingleReturn

# other imports
from .id_generator import IDGenerator
from .type_environment_calculator import TypeEnvironmentCalculator

def get_transformers_omp():
    """ Return transformer constructor-dependency function tuple for all omp
        transforms.
    """
    yield (PragmaToOmpParallelSections, lambda ast: [])
    yield (PragmaToOmpParallelFor, lambda ast: [])
    yield (PragmaToOmpParallel, lambda ast: [])
    yield (PragmaToOmpFor, lambda ast: [])
    yield (PragmaToOmpSections, lambda ast: [])
    yield (PragmaToOmpSection, lambda ast: [])
    yield (PragmaToOmpTask, lambda ast: [])
    yield (PragmaToOmpTaskgroup, lambda ast: [])
    yield (PragmaToOmpTaskwait, lambda ast: [])
    yield (PragmaToOmpCritical, lambda ast: [])
    yield (PragmaToOmpBarrier, lambda ast: [])
    yield (PragmaToOmpAtomic, lambda ast: [])
    yield (PragmaToOmpMaster, lambda ast: [])
    yield (PragmaToOmpSingle, lambda ast: [])

def get_transformers(id_gen_func, type_env_func):
    """ Return transformer constructor-dependency function tuple for all
        non-omp transforms.
    """
    yield (IfToIfGoto, lambda ast: [id_gen_func(ast)])
    yield (ForToWhile, lambda ast: [])
    yield (WhileToDoWhile, lambda ast: [])
    yield (DoWhileToGoto, lambda ast: [id_gen_func(ast)])
    yield (LiftToCompoundBlock,
           lambda ast: [id_gen_func(ast), type_env_func(ast)])
    yield (RemoveCompoundAssignment,
           lambda ast: [id_gen_func(ast), type_env_func(ast)])
    #yield (RemoveInitLists, [type_env_func(ast)])
    yield (InsertExplicitTypeCasts, lambda ast: [type_env_func(ast)])
    yield (SingleReturn, lambda ast: [id_gen_func(ast)])

def get_all_transformers(id_gen_func, type_env_func):
    """ Return all transformer constructor-dependency function tuples.
    """
    yield from get_transformers_omp()
    yield from get_transformers(id_gen_func, type_env_func)

def transform(ast):
    """Perform each transform in package"""
    # one id_generator must be passed to all transforms, to
    # ensure unique ids across transforms
    id_generator = IDGenerator(ast)
    # type environments should be recalculated each time they are needed
    # for a transform, because the AST changes and so the type environments
    # should be different
    type_env_calc = TypeEnvironmentCalculator()

    id_gen_func = lambda ast: id_generator # same id generator across all
    type_env_func = type_env_calc.get_environments

    for (constructor, dep_func) in (
            get_all_transformers(id_gen_func, type_env_func)):
        transformer = constructor(*dep_func(ast))
        ast = transformer.visit(ast)
    return ast
