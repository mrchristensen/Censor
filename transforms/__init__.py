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
RemoveMultideminsionalArray < LiftToCompoundBlock
RemoveMultideminsionalArray < ChangeToVoidPointer
RemoveCompoundAssignment < InsertExplicitTypeCasts
SingleReturn < InsertExplicitTypeCasts
SwitchToIf < LiftToCompoundBlock
SwitchToIf < BreakToGoto
SizeofType < LiftUnaryOp
Sequence < IfToIfGoto
DoWhileToGoto < Sequence
BreakToGoto < DoWhileToGoto
TypeDef < AlphaName
Enum < TypeDef

"""

# imports for transforms
from .sizeof_type import SizeofType
from .correct_pragma_placement import CorrectPragmaPlacement
from .loops_to_goto import WhileToGoto
from .for_to_while import ForToWhile
from .switch_if import SwitchToIf
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
from .omp_simd import PragmaToOmpSimd
from .sequence import Sequence
from .omp_not_implemented import OmpNotImplemented
from .remove_compound_assignment import RemoveCompoundAssignment
from .lift_to_compound_block import LiftToCompoundBlock
from .remove_init_lists import RemoveInitLists
from .insert_explicit_type_casts import InsertExplicitTypeCasts
from .single_return import SingleReturn
from .simplify_omp_for import SimplifyOmpFor
from .remove_multidimensional_arrays import RemoveMultidimensionalArray
from .unary_op import LiftUnaryOp
from .change_void_pointer import ChangeToVoidPointer
from .struct_ref_to_pointer import StructRefToPointerArith
from .remove_typedef import RemoveTypedef
from .break_to_goto import BreakToGoto
from .alpha_name import AlphaName
from .enum import Enum
from .setjmp import Setjmp

# other imports
from .id_generator import IDGenerator
from .type_environment_calculator import TypeEnvironmentCalculator

ID_GENERATOR = None
TYPE_ENV_CALC = None

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
    global ID_GENERATOR #pylint: disable=global-statement
    global TYPE_ENV_CALC #pylint: disable=global-statement

    ID_GENERATOR = IDGenerator(ast)

    TYPE_ENV_CALC = TypeEnvironmentCalculator(ID_GENERATOR)

    # Each dependency function must take one argument so that we can easily
    # chain transformations together without worrying about arity.
    yield (CorrectPragmaPlacement, lambda ast: [])
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
    yield (RemoveTypedef,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (AlphaName, lambda ast: [])
    yield (Enum, lambda ast: [])
    yield (SizeofType,
           lambda ast: [TYPE_ENV_CALC.get_environments(ast)])
    yield (SimplifyOmpFor,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (SwitchToIf, lambda ast: [ID_GENERATOR])
    yield (ForToWhile, lambda ast: [])
    yield (BreakToGoto,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (WhileToGoto, lambda ast: [ID_GENERATOR])
    yield (Setjmp,
           lambda ast: [])
    yield (Sequence,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (IfToIfGoto, lambda ast: [ID_GENERATOR])
    yield (RemoveCompoundAssignment,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (RemoveInitLists,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (RemoveMultidimensionalArray,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (LiftUnaryOp,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (ChangeToVoidPointer,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (StructRefToPointerArith,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])
    yield (SingleReturn, lambda ast: [ID_GENERATOR])
    yield (InsertExplicitTypeCasts,
           lambda ast: [TYPE_ENV_CALC.get_environments(ast)])
    yield (LiftToCompoundBlock,
           lambda ast: [ID_GENERATOR, TYPE_ENV_CALC.get_environments(ast)])

def get_local_transformers(ast): #pylint: disable=unused-argument
    """ Return transformer constructor-dependency function tuples for all
        local transformers.

        Following this constructor-dependency function tuple form,
        we can obtain information about the current transformation more
        easily (through doing things like `constructor.__class__.__name__`,
        for example). This is especially beneficial in regression testing
        for producing more readable, useful output.
    """
    # one id_generator must be passed to all transforms, to
    # ensure unique ids across transforms

    global ID_GENERATOR #pylint: disable=global-statement
    global TYPE_ENV_CALC #pylint: disable=global-statement

    # Each dependency function must take one argument so that we can easily
    # chain transformations together without worrying about arity.
    # NONE
    return []

def transform(ast):
    """Perform each transform in package"""
    for (constructor, dep_func) in get_transformers(ast):
        transformer = constructor(*dep_func(ast))
        ast = transformer.visit(ast)
    return ast

def local_transform(ast):
    """Perform each transform that does not depend on the global scope"""
    for (constructor, dep_func) in get_local_transformers(ast):
        transformer = constructor(*dep_func(ast))
        ast = transformer.visit(ast)
    return ast
