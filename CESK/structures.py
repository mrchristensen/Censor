"""Holds the data structures for the CESK machine"""

class State: #pylint:disable=too-few-public-methods
    """Holds a program state"""
    ctrl = None #control
    envr = None  #environment
    stor = None #store
    kont = None #k(c)ontinuation

    def set_ctrl(self, ctrl):
        """attaches a control object to the state"""
        ctrl.attach(self)
        self.ctrl = ctrl

    def set_envr(self, envr):
        """attaches an environment object to the state"""
        envr.attach(self)
        self.envr = envr

    def set_stor(self, stor):
        """attaches a stor object to the state"""
        stor.attach(self)
        self.stor = stor

class Ctrl: #pylint:disable=too-few-public-methods
    """Holds the control pointer or location of the program"""
    host_state = None
    statement = "statement;"
    location = "filename:line:char"
    node = None #AST node

    def attach(self, state):
        """makes the given state its host"""
        self.host_state = state

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    host_state = None
    map = {} #A set of IdToAddr mappings

    def attach(self, state):
        """makes the given state its host"""
        self.host_state = state

    def map_new_identifier(self, ident):
        """Add a new identifier to the mapping"""
        if self.host_state is None:
            raise Exception("Calling method in Envr with no host state")
        new_address = self.host_state.stor.get_next_address()
        self.map[ident] = new_address
        return new_address

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        return ident in self.map

class Stor:
    """Represents the contents of memory at a moment in time."""
    host_state = None
    address_counter = 0

    def __init__(self, memory=None):
        if memory is None:
            self.memory = {}
        else:
            self.memory = memory

    def attach(self, state):
        """makes the given state its host"""
        self.host_state = state

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
        memory = self.memory.copy()
        if address in self.memory:
            memory[address] = self.memory[address].merge(value)
        else:
            memory[address] = value
        return Stor(memory)

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
