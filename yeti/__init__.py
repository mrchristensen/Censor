"""Starts yeti"""

import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from instrumenter.instrumenter import Instrumenter
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator

PROGRAM_NAME = 'yeti_instrumented.c'

def main(ast):
    """Main entry point to the yeti tool"""
    id_generator = IDGenerator(ast)
    environments = TypeEnvironmentCalculator().get_environments(ast)
    ast = Instrumenter(id_generator, environments).visit(ast)
    program = CWithOMPGenerator().visit(ast)
    with open(PROGRAM_NAME, 'w') as program_file:
        program_file.write(program)
        program_file.flush()
    utils.preserve_include_postprocess(PROGRAM_NAME)
