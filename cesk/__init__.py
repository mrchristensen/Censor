"""Starts the CESK machine"""

import logging
import sys
import os
from collections import deque
import errno
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Kont, SegFault
from cesk.interpret import (decl_helper, execute, get_value,
                            implemented_nodes as impl_nodes)
from cesk.omp_runtime import OmpRuntime
import cesk.config as cnf
import cesk.linksearch as ls

# Set up logging here
logging.basicConfig(filename='logfile.txt',
                    level=logging.DEBUG,
                    format='%(levelname)s %(funcName)s: %(message)s',
                    filemode='w')

def main(ast):
    """Injects execution into main funciton and maintains work queue"""
    #Search ast. link children to parents, map names FuncDef and Label nodes
    ls.LinkSearch().visit(ast)
    logging.debug("Scope Decl LUT: %s", str(ls.LinkSearch.scope_decl_lut))
    main_function = find_main(ast)[0]

    start_state = prepare_start_state(main_function)
    start_state.set_runtime(OmpRuntime(os.environ))

    queue = deque([start_state])
    blocked = deque()
    while queue or blocked: #is not empty
        if not queue:
            for state in blocked:
                if not state.is_blocked():
                    state.barrier = None
                    queue.extend(state.get_next())
            if not queue:
                raise Exception("Deadlock")
            continue
        next_state = queue.popleft()
        if next_state.has_barrier():
            blocked.append(next_state)
            continue
        try:
            successors = execute(next_state)
        except SegFault: #pylint: disable=broad-except
            print('segmentation fault (core dumped)')
            sys.exit(errno.EFAULT)
        queue.extend(successors)
    #raise Exception("Execution finished without Halt")

def implemented_nodes():
    """ returns a list of implemented node type names """
    return impl_nodes()

def prepare_start_state(main_function):
    '''Creates the first state'''
    # zero is halt kont
    halt_state = State(None, None, None, Kont.allocK(), 0, 0, None)
    start_ctrl = Ctrl(main_function.body)
    start_envr = Envr(State(start_ctrl, None, None, None, 0, 0, None))
    start_stor = Stor()
    init_globals(start_stor)
    logging.debug("Globals init done")
    kont_addr = Kont.allocK()
    kai = Kont(halt_state)
    start_stor.write_kont(kont_addr, kai)
    return State(start_ctrl, start_envr, start_stor, kont_addr, 0, 0, None)

def init_globals(stor):
    """ Initializes the global found by linksearch """
    fake_state = State(None, Envr(None), stor, None, 0, 0, None)
    for decl in ls.LinkSearch.global_decl_list:
        logging.debug("Global %s", str(decl.name))
        decl_helper(decl, fake_state)
        if decl.init:
            address = fake_state.envr.get_address(decl.name)
            value = get_value(decl.init, fake_state)
            fake_state.stor.write(address, value)

    Envr.set_global(fake_state.envr)
