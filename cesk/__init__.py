"""Starts the CESK machine"""

import logging
import sys
from collections import deque
import errno
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Kont
from cesk.interpret import (decl_helper, execute, get_value,
                            implemented_nodes as impl_nodes)
import cesk.linksearch as ls
from cesk.exceptions import CESKException, MemoryAccessViolation, \
                            UnknownConfiguration

def main(ast): #pylint: disable=too-many-locals
    """Injects execution into main funciton and maintains work queue"""

    #values to be returned
    memory_safe = True
    states_generated = 1
    states_matched = 0
    states_evaluated = 0

    #Search ast. link children to parents, map names FuncDef and Label nodes
    ls.LinkSearch().visit(ast)
    main_function = find_main(ast)[0]

    start_state = prepare_start_state(main_function)

    seen_set = {start_state:start_state.time_stamp}
    failed_states = set()
    frontier = set([start_state])
    while frontier: #is not empty
        #seen_set.update(frontier)
        new_frontier = set()
        for next_state in frontier:
            try:
                successors = execute(next_state)
                states_evaluated += 1
                for successor in successors:
                    states_generated += 1
                    if (successor not in seen_set or
                            successor.time_stamp > seen_set[successor]):
                        seen_set[successor] = successor.time_stamp
                        new_frontier.add(successor)
                    else:
                        states_matched += 1

            except MemoryAccessViolation as error: #pylint: disable=broad-except
                memory_safe = False
                failed_states.add((next_state, error))
        frontier = new_frontier

    if memory_safe:
        #failed_state and error
        for _, error in failed_states:
            print(error)

    return memory_safe, states_generated, states_matched, states_evaluated

def implemented_nodes():
    """ returns a list of implemented node type names """
    return impl_nodes()

def prepare_start_state(main_function):
    '''Creates the first state'''
    halt_state = State(None, None, None, 0) # zero is halt kont
    start_ctrl = Ctrl(main_function.body)
    start_envr = Envr(State(start_ctrl, None, None, None)) #state for allocF
    start_stor = Stor()
    init_globals(start_stor)
    logging.debug("Globals init done")
    kont_addr = Kont.allocK(halt_state, start_ctrl, start_envr)
    kai = Kont(halt_state)
    start_stor.write_kont(kont_addr, kai)
    return State(start_ctrl, start_envr, start_stor, kont_addr)

def init_globals(stor):
    """ Initializes the global found by linksearch """
    fake_state = State(None, Envr(None), stor, None)
    for decl in ls.LinkSearch.global_decl_list:
        logging.debug("Global %s", str(decl.name))
        decl_helper(decl, fake_state)
        if decl.init:
            address = fake_state.envr.get_address(decl.name)
            value = get_value(decl.init, fake_state)
            fake_state.stor.write(address, value)

    Envr.set_global(fake_state.envr)
