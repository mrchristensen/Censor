"""Holds the data structures for the CESK machine"""

from collections import namedtuple

class State: #pylint:disable=too-few-public-methods
    """Holds a program state"""
    ctrl = None #control
    envr = None  #environment
    stor = None #store
    kont = None #k(c)ontinuation

class Cont: #pylint:disable=too-few-public-methods
    """Holds the control pointer or location of the program"""
    statement = "statement;"
    location = "filename:line:char"
    node = None #AST node

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    address_counter = 0
    IdToAddr = namedtuple("IdToAddr", ['identifier', 'address'])

    def __init__(self):
        self.map = {} #A set of IdToAddr mappings

    def map_new_identifier(self, ident):
        """Add a new identifier to the mapping"""
        # TODO fix this line
        #self.map.append(IdToAddr(ident, addressCounter))
        #address_counter += 1
        #return address_counter - 1

    def is_defined(self, ident):
        """returns if a given identifier is defined"""
        return ident in self.map

class Stor:
    """Represents the contents of memory at a moment in time."""
    def __init__(self, memory=None):
        if memory is None:
            self.memory = {}
        else:
            self.memory = memory

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
