"""Starts the CESK machine"""

import logging
import sys
import os
from collections import deque
import errno
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Kont, SegFault
from cesk.interpret import (decl_helper, get_value,
                            implemented_nodes as impl_nodes)
from cesk.omp_runtime import OmpRuntime
import cesk.config as cnf
import cesk.linksearch as ls
from cesk.scheduler import Scheduler

# Set up logging here
logging.basicConfig(filename='logfile.txt',
                    level=cnf.get_log_level(),
                    format='%(levelname)s %(funcName)s: %(message)s',
                    filemode='w')

def main(ast):
    """Injects execution into main funciton and maintains work queue"""
    #Search ast. link children to parents, map names FuncDef and Label nodes
    ls.LinkSearch().visit(ast)
    main_function = find_main(ast)[0]

    start_state = prepare_start_state(main_function)
    start_state.set_runtime(OmpRuntime(os.environ))

    scheduler = Scheduler(start_state)
    while not scheduler.finished():
        try:
            scheduler.step()
        except SegFault:
            print("segmentation fault detected")
            sys.exit(errno.EFAULT)

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
