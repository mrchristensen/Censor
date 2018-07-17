"""Holds the data structures for the CESK machine"""

import logging
import copy
import sys
import pycparser
from cesk.values import ReferenceValue, generate_default_value, cast
from cesk.values import generate_pointer_value, generate_null_pointer
# from cesk.interpret import execute #pylint:disable=all

def throw(string, state=None, exit_code=0):
    if state is not None:
       state.ctrl.stmt().show() 
    print(string)
    exit(exit_code)

class State: #pylint:disable=too-few-public-methods
    """Holds a program state"""
    ctrl = None #control
    envr = None  #environment
    stor = None #store
    kont = None #k(c)ontinuation

    def __init__(self, ctrl, envr, stor, kont):
        self.set_ctrl(ctrl)
        self.set_envr(envr)
        self.set_stor(stor)
        self.set_kont(kont)

    def set_ctrl(self, ctrl):
        """attaches a control object to the state"""
        self.ctrl = ctrl

    def set_envr(self, envr):
        """attaches an environment object to the state"""
        self.envr = envr

    def set_stor(self, stor):
        """attaches a stor object to the state"""
        self.stor = stor

    def set_kont(self, kont):
        """attaches a kont object to the state"""
        self.kont = kont

class Ctrl: #pylint:disable=too-few-public-methods
    """Holds the control pointer or location of the program"""

    def construct_node(self, node):
        self.node = node

    def construct_body(self, index, body):
        self.index = index
        self.body = body 

    def __init__(self, first, second=None):
        """There are two types of control: The normal ones that have an index in
        a body, and the special ones that only hold a Node. This picks which 
        constructor to use"""
        self.index = None
        self.body = None
        self.node = None
        if second is not None:
            if (isinstance(second, pycparser.c_ast.FuncDef)):
                self.construct_body(first, second.body)
            elif(isinstance(second, pycparser.c_ast.Compound)):
                self.construct_body(first, second)
            else:
                raise Exception("Ctrl init body not Compound or Function: " +
                                str(second))
        elif first is not None:
            self.construct_node(first)
        else:
            raise Exception("Malformed Ctrl init")

    def __add__(self, offset):
        """Returns the location in the same function with the line number offset
        by the value offset. This is used most commonly as loc+1 to get the
        syntactic successor to a Location.
        """
        return Ctrl(self.index+offset, self.body)

    def stmt(self):
        """Retrieves the statement at the location."""
        if (self.node is not None):
            return self.node
        return self.body.block_items[self.index]

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    counter = 0
    global_scope = None

    def __init__(self, parent = None):
        self.map_to_address = {} #A set of IdToAddr mappings
        self.parent = parent
        self.id = Envr.counter
        Envr.counter = Envr.counter + 1
        
    def get_global_scope():
        if Envr.global_scope is None:
            Envr.global_scope = Envr(None)
        return Envr.global_scope 

    def get_address(self, ident):
        "looks up the address associated with an identifier"""
        #print("Looking up " + ident + " in scope " + str(self.id))
        while not isinstance(ident, str):
            ident = ident.name
        if (ident in self.map_to_address):
            return self.map_to_address[ident]
        if (self.parent is not None):
            return self.parent.get_address(ident)
        while not isinstance(ident, str):
            ident = ident.name
        raise Exception(ident + " is not defined in this scope: " +
                        str(self.id)) 

    def get_type(self, ident):
        if (ident in self.map_to_type):
            return self.map_to_type[ident]
        if (self.parent is not None):
            return self.parent.get_type(ident)
        return None

    def map_new_identifier(self, ident, address):
        """Add a new identifier to the mapping"""
        self.map_to_address[ident] = address

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        return get_address(self, ident) is not None

    def is_localy_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in self.map_to_address

class Stor:
    """Represents the contents of memory at a moment in time."""
    address_counter = 1 # start at 1 so that 0 can be nullptr
    NULL = generate_null_pointer()

    def __init__(self, to_copy=None):
        if to_copy is None:
            self.memory = {}
            self.succ_map = {}
            self.pred_map = {}
            self.succ_map[Stor.NULL] = Stor.NULL
            self.pred_map[Stor.NULL] = Stor.NULL
            self.size_map = {0:1}
        elif isinstance(to_copy, Stor):
            self.memory = to_copy.memory
            self.succ_map = to_copy.succ_map
            self.pred_map = to_copy.pred_map
        else:
            raise Exception("Stor Copy Constructor Expects a Stor Object")

    def get_next_address(self, size=1):
        """returns the next available storage address"""
        pointer = generate_pointer_value(self.address_counter, self)
        self.succ_map[pointer] = Stor.NULL 
        self.pred_map[pointer] = Stor.NULL
        self.address_counter += size
        self.size_map[self.address_counter] = size
        return pointer

    def allocate_block(self, length, size=1):
        """Moves the address counter to leave room for an array and returns
        start"""
        start_address = self.address_counter
        start_pointer = generate_pointer_value(self.address_counter, self)

        self.size_map[start_address] = size
        self.pred_map[start_pointer] = Stor.NULL
        last_pointer = start_pointer
        logging.debug(length)
        while self.address_counter < (start_address + length * size):
            self.address_counter += size
            self.size_map[self.address_counter] = size
            new_pointer = generate_pointer_value(self.address_counter, self)
            self.pred_map[new_pointer] = last_pointer
            self.succ_map[last_pointer] = new_pointer
            last_pointer = new_pointer
        self.succ_map[last_pointer] = Stor.NULL

        return start_pointer

    def allocate_nonuniform_block(self, list_of_sizes):
        """Takes in a list of sizes as int and allocates and links a block in the stor for each size"""
        start_address = self.address_counter
        start_pointer = generate_pointer_value(self.address_counter, self)
        self.pred_map[start_pointer] = Stor.NULL
        self.size_map[self.address_counter] = list_of_sizes[0]
        self.address_counter += list_of_sizes[0]

        pred = start_pointer
        for block_size in list_of_sizes[1:]:
            next_block = generate_pointer_value(self.address_counter, self)
            self.size_map[self.address_counter] = block_size
            self.address_counter += block_size
            self.pred_map[next_block] = pred
            self.succ_map[pred] = next_block
            pred = next_block

        self.succ_map[pred] = Stor.NULL            
        
        return start_pointer


    def add_offset_to_pointer(self, pointer, offset):
        # TODO Document what this function does
        new_pointer = pointer
        if offset > 0:
            for _ in range(offset):
                new_pointer.offset += 1
                if self.size_map[new_pointer.data] == new_pointer.offset:
                    new_pointer.offset = 0
                    new_pointer = self.succ_map[new_pointer]
        else:
            for _ in range(abs(offset)):
                if 0 == new_pointer.offset:
                    diff = self.size_map[new_pointer.data]
                    new_pointer = self.pred_map[new_pointer]
                    new_pointer.offset = diff
                new_pointer.offset -= 1
        return new_pointer
            
    # def read(self, address):
    #     """Read the contents of the store at address. Returns None if undefined.
    #     """

    #     if address in self.memory:
    #         return self.memory[address]
    #     if address < self.address_counter:
    #         return generate_default_value("int")
    #     raise Exception("ERROR: tried to access an unalocated address: " +
    #                      str(address))

    def read(self, address, size=None):
        """Read the contents of the store at address. Returns None if undefined.
        """

        if address in self.memory:
            return self.memory[address]
        if address > self.address_counter:
            raise Exception("ERROR: tried to access an unalocated address: " +
                            str(address))

        nearest_address = Stor.NULL
        for x in self.memory:
            if x.data < address:
                nearest_address = x if x > nearest_address else nearest_address
 
        if not nearest_address == Stor.NULL:
            return self.memory[nearest_address]

        return generate_default_value("int")


    def write(self, address, value):
        """Write value to the store at address. If there is an existing value,
        merge value into the existing value.
        """
        if not isinstance(address, ReferenceValue):
            raise Exception("Address should not be " + str(address))
        if address in self.memory:
            self.memory[address] = value
        else:
            self.memory[address] = value
        logging.debug('  '+str(self.memory[address]) + " writen to " + str(address))

    def print_memory_visualization(self):
        for (address, value) in self.memory:
            if isinstance(value, values.Integer):
                print(bcolor.GREEN + str(value))
            else:
                print(str(value))
        
#Base Class
class Kont:
    """Abstract class for polymorphism of continuations"""
    def satisfy(self, current_state, value):
        pass

#Special Konts
class Halt(Kont):
    """Last continuation to execute"""
    def satisfy(self, current_state, value=None):
        if value is not None:
            exit(value.data)
        exit(0)

#Function Konts

class FunctionKont(Kont):
    """Continuation for function"""
    
    def __init__(self, parent_state):
        self.parent_state = parent_state

    def satisfy(self, state, value):
        if value is None:
            raise Exception("'return' expected return value")
        new_envr = self.parent_state.envr
        if new_envr is None:
            raise Exception("Tried to close Global Scope")
        if isinstance(self.parent_state.kont, FunctionKont):
            #in the case of a function call in statement position
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, new_envr, state.stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        new_state = State(state.ctrl, new_envr, state.stor, state.kont)
        return self.parent_state.kont.satisfy(new_state, value)

class VoidKont(FunctionKont):
    """Continuation for function returning void"""

    def __init__(self, parent_state):
        self.parent_state = parent_state

    def satisfy(self, state, value=None):
        new_envr = self.parent_state.envr
        if new_envr is None:
            raise Exception("Tried to close Global Scope")
        if value is not None:
            raise Exception("'return' with a value in block returning void")
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, new_envr, state.stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return self.parent_state.kont.satisfy(state)

#Statement Konts
class AssignKont(Kont):
    """Continuaton created by assignment requires a Value to assign to an
    address"""

    def __init__(self, address, parent_state):
        if not isinstance(address, ReferenceValue):
            raise Exception("Address should not be " + str(address))
        self.address = address 
        self.parent_state = parent_state

    def satisfy(self, state, value):
        new_stor = state.stor
        new_stor.write(self.address, value)
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, state.envr, new_stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return_state = State(self.parent_state.ctrl, self.parent_state.envr,
                             new_stor, self.parent_state.kont) 
        return self.parent_state.kont.satisfy(return_state, value)

class CastKont(Kont):
    """Continuation to cast to different types before satisfying the parent"""
    #TODO
    def __init__(self, parent_kont, to_type):
        self.parent_kont = parent_kont
        self.to_type = to_type

    def satisfy(self, state, value):
        cast_value = cast(value, self.to_type, state.stor)
        return self.parent_kont.satisfy(state, cast_value)
        

class IfKont(Kont):
    """Continuation for if statement, moves ctrl to correct place"""
    parent_state = None
    iftrue = None
    iffalse = None

    def __init__(self, parent_state, iftrue, iffalse):
        self.parent_state = parent_state
        self.iftrue = iftrue
        self.iffalse = iffalse

    def satisfy(self, state, value):
        if (value.get_truth_value()):
            new_ctrl = Ctrl(self.iftrue)
        elif self.iffalse is not None:
            new_ctrl = Ctrl(self.iffalse)
        else:
            return cesk.interpret.get_next(self.parent_state)
        return State(new_ctrl, state.envr, state.stor, self.parent_state.kont)

class ReturnKont(Kont): #pylint: disable=too-few-public-methods

    def __init__(self, parent_kont):
        self.parent_kont = parent_kont

    def satisfy(self, state, value):
        return self.parent_kont.satisfy(state, value)

#Expresion Konts
class LeftBinopKont(Kont):
    """Continuation for the left side of a binary operator"""

    parent_state = None 
    operator = None
    right_exp = None
    return_kont = None

    def __init__(self, parent_state, operator, rightExp, return_kont):
        self.parent_state = parent_state
        self.operator = operator
        self.rightExp = rightExp
        self.return_kont = return_kont

    def satisfy(self, current_state, value):
        left_result = value
        right_kont = RightBinopKont(self.parent_state, left_result, self.operator,
                                    self.return_kont)
        return State(Ctrl(self.rightExp), current_state.envr,
                     current_state.stor, right_kont)


class RightBinopKont(Kont):
    """Continuation for the right side of a binary operator"""

    parent_state = None 
    left_result = None
    operator = None
    return_kont = None

    def __init__(self, parent_state, left_result, operator, return_kont):
        self.parent_state = parent_state
        self.left_result = left_result
        self.operator = operator
        self.return_kont = return_kont

    def satisfy(self, state, value):
        logging.debug( "   "+str(self.left_result)+str(self.operator)+str(value))
        result = self.left_result.perform_operation(self.operator, value)
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, state.envr, state.stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return self.return_kont.satisfy(state, result)

# import is down here to allow for circular dependencies between structures.py and interpret.py
import cesk.values # pylint: disable=wrong-import-position
import cesk.interpret # pylint: disable=wrong-import-position
