"""Holds the data structures for the CESK machine"""

import copy
import pycparser
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
            raise Exception("None None Ctrl init")

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
    counter = 0;

    def __init__(self, parent = None):
        self.map_to_address = {} #A set of IdToAddr mappings
        self.map_to_type = {}
        self.parent = parent
        self.id = Envr.counter
        Envr.counter = Envr.counter + 1

    def get_address(self, ident):
        "looks up the address associated with an identifier"""
        if (ident in self.map_to_address):
            return self.map_to_address[ident]
        if (self.parent is not None):
            return self.parent.get_address(ident)
        raise Exception(ident.name + " is not defined in this scope: " +
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
    memory = {}

    def __init__(self, memory=None):
        if memory is None:
            self.memory = {}
        else:
            self.memory = memory

    def get_next_address(self):
        """returns the next available storage address"""
        self.address_counter += 1
        return self.address_counter - 1

    def allocate_array(self, length):
        """Moves the address counter to leave room for an array and returns
        start"""
        start_address = self.address_counter
        self.address_counter = self.address_counter + length
        return start_address

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        if address in self.memory:
            return self.memory[address]
        return None

    def write(self, address, value):
        """Write value to the store at address. If there is an existing value,
        merge value into the existing value.
        """
        if address in self.memory:
            self.memory[address] = value
        else:
            self.memory[address] = value
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
    parent_state = None
    
    def __init__(self, parent_state):
        self.parent_state = parent_state

    def satisfy(self, state, value):
        if value is None:
            raise Exception("'return' expected return value")
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, state.envr, state.stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return self.parent_state.kont.satisfy(state, value)

class VoidKont(FunctionKont):
    """Continuation for function returning void"""

    def __init__(self, parent_state):
        self.parent_state = parent_state

    def satisfy(self, state, value=None):
        if value is not None:
            raise Exception("'return' with a value in block returning void")
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, state.envr, state.stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return self.parent_state.kont.satisfy(state)

#Statement Konts
class AssignKont(Kont):
    """Continuaton created by assignment requires a Value to assign to an
    address"""

    def __init__(self, address, parent_state):
        self.address = address 
        self.parent_state = parent_state

    def satisfy(self, state, value):
        new_stor = copy.deepcopy(state.stor)
        new_stor.write(self.address, value)
        if isinstance(self.parent_state.kont, FunctionKont):
            #don't return out of function without return
            new_state = State(self.parent_state.ctrl, state.envr, new_stor,
                              self.parent_state.kont)
            return cesk.interpret.get_next(new_state)
        return_state = State(self.parent_state.ctrl, self.parent_state.envr,
                             new_stor, self.parent_state.kont) 
        return self.parent_state.kont.satisfy(return_state, value)

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
    parent_kont = None

    def __init__(self, parent_kont):
        self.parent_kont = parent_kont

    def satisfy(self, state, value):
        self.parent_kont.satisfy(state, value)

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
