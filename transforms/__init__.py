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
PragmaToOmpFor < SimplifyOmpFor
SimplifyOmpFor < TernaryToIf
TernaryToIf < IfToIfGoto
TernaryToIf < InsertExplicitTypeCasts
TernaryToIf < LiftToCompoundBlock
RemoveMultideminsionalArray < LiftToCompoundBlock
RemoveCompoundAssignment < InsertExplicitTypeCasts
SwitchToIf < LiftToCompoundBlock
"""

# imports for transforms
from .sizeof_type import SizeofType
from .do_while_to_goto import DoWhileToGoto
from .while_to_do_while import WhileToDoWhile
from .for_to_while import ForToWhile
from .switch_if import SwitchToIf
from .if_goto import IfToIfGoto
from .ternary_to_if import TernaryToIf
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
from .omp_simd import PragmaToOmpSimd
from .omp_not_implemented import OmpNotImplemented
from .remove_compound_assignment import RemoveCompoundAssignment
from .lift_to_compound_block import LiftToCompoundBlock
from .remove_init_lists import RemoveInitLists
from .insert_explicit_type_casts import InsertExplicitTypeCasts
from .single_return import SingleReturn
from .simplify_omp_for import SimplifyOmpFor
from .remove_multidimensional_arrays import RemoveMultidimensionalArray
    
# other imports
from .id_generator import IDGenerator
from .type_environment_calculator import TypeEnvironmentCalculator

def get_transformers(ast):
    """ Return transformer constructor-dependency function tuples for all
        transformers.

        Following this constructor-dependency function tuple form,
        we can obtain information about the current transformation more
        easily (through doing things like `constructor.__class__.__name__`,
        for example). This is especially beneficial in regression testing
        for producing more readable, useful output.
    """
    # one id_generator must be passed to all transforms, to
    # ensure unique ids across transforms
    id_generator = IDGenerator(ast)

    # type environments should be recalculated each time they are needed
    # for a transform, because the AST changes and so the type environments
    # should be different
    type_env_calc = TypeEnvironmentCalculator()

    # Each dependency function must take one argument so that we can easily
    # chain transformations together without worrying about arity.
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
    yield (PragmaToOmpSimd, lambda ast: [])
    yield (OmpNotImplemented, lambda ast: [])
    yield (SizeofType,
           lambda ast: [type_env_calc.get_environments(ast)])
    yield (SimplifyOmpFor,
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (TernaryToIf,
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (SwitchToIf, lambda ast: [id_generator])
    yield (IfToIfGoto, lambda ast: [id_generator])
    yield (ForToWhile, lambda ast: [])
    yield (WhileToDoWhile, lambda ast: [])
    yield (DoWhileToGoto, lambda ast: [id_generator])
    yield (RemoveCompoundAssignment,
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (RemoveInitLists,
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (InsertExplicitTypeCasts,
           lambda ast: [type_env_calc.get_environments(ast)])
    yield (RemoveMultidimensionalArray, 
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (LiftToCompoundBlock,
           lambda ast: [id_generator, type_env_calc.get_environments(ast)])
    yield (SingleReturn, lambda ast: [id_generator])

def transform(ast):
    """Perform each transform in package"""
    for (constructor, dep_func) in get_transformers(ast):
        transformer = constructor(*dep_func(ast))
        ast = transformer.visit(ast)
    return ast
