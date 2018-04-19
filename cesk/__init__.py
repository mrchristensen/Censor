"""Starts the CESK machine"""

from collections import deque
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt, FunctionKont
from cesk.interpret import execute, LinkSearch


def main(ast):
    """Injects execution into main funciton and maintains work queue"""
    #Search ast. link children to parents, map names FuncDef and Label nodes
    LinkSearch().visit(ast)
    main_function = find_main(ast)[0]

    start_ctrl = Ctrl(main_function.body)
    halt_state = State(start_ctrl, Envr.get_global_scope(), Stor(), Halt())
    # create start state as if main() has been called by halt
    start_state = State(start_ctrl, halt_state.envr, halt_state.stor,
                        FunctionKont(halt_state))
    queue = deque([start_state])
    while queue: #is not empty
        next_state = queue.popleft()
        successors = execute(next_state)
        queue.extend(successors)
    raise Exception("Execution finished without Halt")

def implemented_nodes():
    """ Return set of nodes that the interpreter currently implements.
    """
    return {
        'ArrayRef',
        'Assignment',
        'BinaryOp',
        'Compound',
        'Constant',
        'Decl',
        'FuncCall',
        'FuncDecl',
        'FuncDef',
        'Goto',
        'ID',
        'If',
        'Label',
        'Return',
        'TernaryOp',
        'TypeDecl',
        'UnaryOp',
        'FileAST'
    }
