"""Starts the CESK machine"""

import logging
import sys
from collections import deque
import errno
from graphviz import Digraph
from utils import find_main
from cesk.structures import State, Ctrl, Envr, Stor, Kont
from cesk.interpret import (decl_helper, execute, get_value,
                            implemented_nodes as impl_nodes)
import cesk.linksearch as ls
from cesk.exceptions import CESKException, MemoryAccessViolation, \
                            UnknownConfiguration
from cesk.values import generate_function_definition

class StateEnumaration: #pylint: disable=too-few-public-methods
    """ Keeps track of information about a state """
    next_id = 0
    def __init__(self, time):
        self.time = time
        self.successors = set()
        self.ident = StateEnumaration.next_id
        self.time0 = time
        StateEnumaration.next_id += 1

    def get_time(self):
        """ string of first created to last updated """
        return str(self.ident)+'-'+str(self.time0)+'/'+str(self.time)

def main(ast, graph_file_name): #pylint: disable=too-many-locals
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
    #map of states to time last seen and states generated from
    seen_set = {start_state:StateEnumaration(start_state.time_stamp)}
    failed_states = set()
    frontier = set([start_state])
    while frontier: #is not empty
        new_frontier = set()
        for next_state in frontier:
            try:
                successors = execute(next_state)
                states_evaluated += 1
                for successor in successors:
                    states_generated += 1
                    if successor not in seen_set:
                        seen_set[successor] = \
                            StateEnumaration(successor.time_stamp)
                        new_frontier.add(successor)
                    elif successor.time_stamp > seen_set[successor].time:
                        seen_set[successor].time = successor.time_stamp
                        new_frontier.add(successor)
                    else:
                        states_matched += 1
                    seen_set[next_state].successors.add(successor)

            except MemoryAccessViolation as error: #pylint: disable=broad-except
                memory_safe = False
                failed_states.add((next_state, error))
        frontier = new_frontier

    if graph_file_name is not None:
        graph = Digraph("CESK State Graph", filename=graph_file_name)
        if not memory_safe:
            #failed_state and error
            graph.attr('node', shape='diamond', style='filled', color='red')
            for state, error in failed_states:
                #print(error)
                graph.node(seen_set[state].get_time()+"\n"+str(state))

        graph.attr('node', shape='ellipse', style='solid', color='black')
        for state, enumeration in seen_set.items():
            node = enumeration.get_time()+"\n"+str(state)
            for to_state in enumeration.successors:
                node2 = seen_set[to_state].get_time()+"\n"+str(to_state)
                graph.edge(node, node2)

        graph.render()

    return memory_safe, states_generated, states_matched, states_evaluated

def implemented_nodes():
    """ returns a list of implemented node type names """
    return impl_nodes()

def prepare_start_state(main_function):
    '''Creates the first state'''
    halt_state = State(None, None, None, 0) # zero is halt kont
    start_ctrl = Ctrl(main_function.body)
    start_envr = Envr('main', None) #state for allocF
    start_stor = Stor()
    logging.debug("Globals init start")
    init_globals(start_stor)
    logging.debug("Globals init done")
    kont_addr = Kont.allocK(halt_state, start_ctrl, start_envr)
    kai = Kont(halt_state)
    start_stor.write_kont(kont_addr, kai)
    return State(start_ctrl, start_envr, start_stor, kont_addr)

def init_globals(stor):
    """ Initializes the global found by linksearch """
    fake_state = State(None, Envr("init_globals", None), stor, None)
    for decl in ls.LinkSearch.global_decl_list:
        logging.debug("Global %s", str(decl.name))
        decl_helper(decl, fake_state)
        if decl.init:
            address = fake_state.envr.get_address(decl.name)
            value = get_value(decl.init, fake_state)
            fake_state.stor.write(address, value)
    funcs = ls.LinkSearch.function_lut
    for func in funcs:
        logging.debug("Global function %s", func)
        f_addr = fake_state.envr.map_new_identifier(func)
        fake_state.stor.allocM(f_addr, [8]) # word size
        func_val = generate_function_definition(funcs[func])
        fake_state.stor.write(f_addr, func_val)

    Envr.set_global(fake_state.envr)
