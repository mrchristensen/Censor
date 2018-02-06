"""Holds the data structures for the CESK machine"""

import copy
from cesk.interpret import execute #pylint:disable=all

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

    def execute(self):
        """Evaluates the code at ctrl using current state"""
        successors = execute(self)
        print("\n\n\tSuccessors:" + ''.join(str(s) for s in successors)) 
        for successor in successors:
            if successor.ctrl is not None:
                successor.execute()

class Ctrl: #pylint:disable=too-few-public-methods
    """Holds the control pointer or location of the program"""
    index = None
    function = None
    node = None

    def const_node(self, node):
        self.node = node

    def const_index(self, index, function):
        self.index = index
        self.function = function
    
    def __init__(self, first, second=None):
        if second is not None:
            self.const_index(first, second)
        else:
            self.const_node(first)

    def __add__(self, offset):
        """Returns the location in the same function with the line number offset
        by the value offset. This is used most commonly as loc+1 to get the
        syntactic successor to a Location.
        """
        return Ctrl(self.index+offset, self.function)

    def stmt(self):
        """Retrieves the statement at the location."""
        if (self.node is not None):
            return self.node;
        return self.function.body.block_items[self.index]

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    map = {} #A set of IdToAddr mappings

    def get_address(self, ident):
        "looks up the address associated with an identifier"""
        return self.map[ident]
    
    def map_new_identifier(self, ident, address):
        """Add a new identifier to the mapping"""
        self.map[ident] = address; 

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        return ident in self.map

class Stor:
    """Represents the contents of memory at a moment in time."""
    address_counter = 0
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
            self.memory[address] = self.memory[address].Merge(value)
        else:
            self.memory[address] = value

class Kont:
    """Abstract class for polymorphism of continuations"""
    def satisfy(self, needs):
        pass

class Halt(Kont):
    """Last continuation to execute"""
    def satisfy(self, value):
        print(value.data)
        exit()
        
class AssignKont(Kont):
    """Continuaton created by assignment requires a Value to assign to an
    address"""
    address = None
    return_state = None

    def __init__(self, address, return_state):
        self.address = address
        self.return_state = return_state

    def satisfy(self, value):
        new_stor = copy.deepcopy(self.return_state.stor)
        new_stor.write(self.address, value)
        return State(self.return_state.ctrl, self.return_state.envr,
            new_stor, self.return_state.kont)
        
class Value: #pylint:disable=too-few-public-methods
    """Abstract class for polymorphism between abstract and concrete values"""

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __div__(self, other):
        pass


class ConcreteValue(Value): #pylint:disable=too-few-public-methods
    """Concrete implementation of Value"""
    data = None
    type_of = None

    def __init__(self, data, type_of):
        self.data = data
        self.type_of = type_of

    def __add__(self, other):
        return self.data + other.data

    def __sub__(self, other):
        return self.data - other.data

    def __mul__(self, other):
        return self.data * other.data

    def __truediv__(self, other):
        return self.data / other.data