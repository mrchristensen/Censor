"""Starts the CESK machine"""

from collections import deque
from pycparser.c_ast import Node
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt, FunctionKont
from cesk.interpret import execute

def main(ast):
    """Is a stub"""
    main_function = find_main(ast)[0]

    start_index = 0
    halt_state = State(Ctrl(start_index, main_function), Envr(), Stor(), Halt())
    start_state = State(halt_state.ctrl, halt_state.envr, halt_state.stor,
                        FunctionKont(halt_state))
    queue = deque([start_state])
    while queue:
        next_state = queue.popleft()
        successors = execute(next_state)
        queue.extend(successors)
    raise Exception("Execution finished without Halt")
