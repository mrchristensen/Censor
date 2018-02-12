"""Starts yeti"""

from pycparser.c_ast import Node

from instrumenter.instrumenter import Instrumenter
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt


def main(ast):
    """Is a stub"""
    instrumenter = Instrumenter()
    instrumenter.visit(ast)
