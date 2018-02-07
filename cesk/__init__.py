"""Starts the CESK machine"""

from pycparser.c_ast import Node
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt

def main(ast):
    """Is a stub"""
    main_function = find_main(ast)[0]

    start_index = 0
    start_state = State(Ctrl(start_index, main_function), Envr(), Stor(), Halt())
    start_state.execute()
