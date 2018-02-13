"""Starts yeti"""
from instrumenter.instrumenter import Instrumenter


def main(ast):
    """Main entry point to the yeti tool"""
    Instrumenter().visit(ast)
