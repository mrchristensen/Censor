"""Starts the CESK machine"""

from collections import deque
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt, FunctionKont
from cesk.interpret import execute, LinkSearch

def main(ast):
    """Injects execution into main funciton and maintains work queue"""
    ast = LinkSearch().visit(ast)
    main_function = find_main(ast)[0]

    start_ctrl = Ctrl(main_function.body)
    halt_state = State(start_ctrl, Envr(), Stor(), Halt())
    start_state = State(halt_state.ctrl, halt_state.envr, halt_state.stor,
                        FunctionKont(halt_state))
    queue = deque([start_state])
    while queue:
        next_state = queue.popleft()
        successors = execute(next_state)
        queue.extend(successors)
    raise Exception("Execution finished without Halt")
