"""Starts the CESK machine"""

import logging
import sys
from collections import deque
import errno
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Halt, FunctionKont
from cesk.interpret import execute, implemented_nodes as impl_nodes
import cesk.linksearch as ls
from .structures import SegFault

def main(ast):
    """Injects execution into main funciton and maintains work queue"""
    #Search ast. link children to parents, map names FuncDef and Label nodes
    ls.LinkSearch().visit(ast)
    logging.debug("Scope Decl LUT: %s", str(ls.LinkSearch.scope_decl_lut))
    main_function = find_main(ast)[0]

    start_ctrl = Ctrl(main_function.body)
    halt_state = State(start_ctrl, Envr(), Stor(), Halt())
    # create start state as if main() has been called by halt
    start_state = State(start_ctrl, halt_state.envr, halt_state.stor,
                        FunctionKont(halt_state))
    queue = deque([start_state])
    while queue: #is not empty
        next_state = queue.popleft()
        try:
            successor = execute(next_state)
        except SegFault: #pylint: disable=broad-except
            print('segmentation fault (core dumped)')
            sys.exit(errno.EFAULT)
        queue.append(successor)
    raise Exception("Execution finished without Halt")

def implemented_nodes():
    """ returns a list of implemented node type names """
    return impl_nodes()
