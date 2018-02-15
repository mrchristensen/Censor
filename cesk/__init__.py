"""Starts the CESK machine"""

from collections import deque
from pycparser.c_ast import Node
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt
from cesk.interpret import execute

def main(ast):
    """Is a stub"""
    main_function = find_main(ast)[0]

    start_index = 0
    start_state = State(Ctrl(start_index, main_function), Envr(), Stor(), Halt())
    queue = deque([start_state])
    while queue:
        successors = execute(queue.popleft())
        if successors is not NotImplemented:
            queue.extend(successors)
