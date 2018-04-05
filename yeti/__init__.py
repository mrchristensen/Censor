"""Starts yeti"""
from instrumenter.instrumenter import Instrumenter
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator


def main(ast):
    """Main entry point to the yeti tool"""
    id_generator = IDGenerator(ast)
    environments = TypeEnvironmentCalculator().get_environments(ast)
    Instrumenter(id_generator, environments).visit(ast)
