"""Holds the data structures for the CESK machine"""

import logging
import pycparser
from cesk.values import ReferenceValue, generate_unitialized_value, cast
from cesk.values import copy_pointer, generate_null_pointer
from cesk.values import generate_pointer, generate_value

def throw(string, state=None, exit_code=0):
    """ Controlled Exit on some error """
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
        """ sets the node """
        self.node = node

    def construct_body(self, index, body):
        """ sets the index and body """
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
            if isinstance(second, pycparser.c_ast.FuncDef):
                self.construct_body(first, second.body)
            elif isinstance(second, pycparser.c_ast.Compound):
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
        if self.node is not None:
            return self.node
        return self.body.block_items[self.index]

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    counter = 0
    global_scope = None

    def __init__(self, parent=None):
        self.map_to_address = {} #A set of IdToAddr mappings
        self.parent = parent
        self.id = Envr.counter
        Envr.counter = Envr.counter + 1

    @staticmethod
    def get_global_scope():
        '''Returns global scope, uses singleton pattern'''
        if Envr.global_scope is None:
            Envr.global_scope = Envr(None)
        return Envr.global_scope

    def get_address(self, ident):
        "looks up the address associated with an identifier"""
        #print("Looking up " + ident + " in scope " + str(self.id))
        while not isinstance(ident, str):
            ident = ident.name
        if ident in self.map_to_address:
            return self.map_to_address[ident]
        if self.parent is not None:
            return self.parent.get_address(ident)
        while not isinstance(ident, str):
            ident = ident.name
        raise Exception(ident + " is not defined in this scope: " +
                        str(self.id))

    def map_new_identifier(self, ident, address):
        """Add a new identifier to the mapping"""
        self.map_to_address[ident] = address

    def is_localy_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in self.map_to_address

class Stor:
    """Represents the contents of memory at a moment in time."""

    def __init__(self, to_copy=None):
        self.NULL = generate_null_pointer(self)
        if to_copy is None:
            self.address_counter = 1 # start at 1 so that 0 can be nullptr
            self.memory = {}
            self.succ_map = {}
            self.pred_map = {}
            self.succ_map[self.NULL] = self.NULL
            self.pred_map[self.NULL] = self.NULL
        elif isinstance(to_copy, Stor): #shallow copy of stor
            self.address_counter = to_copy.address_counter
            self.memory = to_copy.memory
            self.succ_map = to_copy.succ_map
            self.pred_map = to_copy.pred_map
        else:
            raise Exception("Stor Copy Constructor Expects a Stor Object")

    def _make_new_address(self, size):
        """ Alloc address for a certian size and store unitialized value """
        logging.info("Alloc %d for %d bytes", self.address_counter, size)
        pointer = generate_pointer(self.address_counter, self, size)
        self.memory[pointer] = generate_unitialized_value(size)
        self.address_counter += size
        return pointer

    def get_next_address(self, size=1):
        """returns the next available storage address"""
        pointer = self._make_new_address(size)
        self.succ_map[pointer] = self.NULL
        self.pred_map[pointer] = self.NULL
        return pointer

    def allocate_block(self, length, size=1):
        """Moves the address counter to leave room for an array and returns
        start"""
        start_address = self.address_counter
        start_pointer = self._make_new_address(size)

        self.pred_map[start_pointer] = self.NULL

        last_pointer = start_pointer
        while self.address_counter < (start_address + length * size):
            new_pointer = self._make_new_address(size)

            self.pred_map[new_pointer] = last_pointer
            self.succ_map[last_pointer] = new_pointer
            last_pointer = new_pointer
        self.succ_map[last_pointer] = self.NULL

        return start_pointer

    def allocate_nonuniform_block(self, list_of_sizes):
        """ Takes in a list of sizes as int and allocates
             and links a block in the stor for each size """
        start_pointer = self._make_new_address(list_of_sizes[0])
        self.pred_map[start_pointer] = self.NULL

        prev = start_pointer
        for block_size in list_of_sizes[1:]:
            next_block = self._make_new_address(block_size)
            self.pred_map[next_block] = prev
            self.succ_map[prev] = next_block
            prev = next_block

        self.succ_map[prev] = self.NULL

        return start_pointer

    def add_offset_to_pointer(self, pointer, offset):
        """ updates the pointer's offset by the offset passed.
        Using the predecessor and successor maps: pointers move
        to the next block if the offset extends beyond the bounds
        of the current block.
        """
        new_pointer = copy_pointer(pointer)
        if new_pointer not in self.memory:
            if new_pointer.data == 0: #null is always null
                return new_pointer
            raise Exception("Invalid Pointer " + str(new_pointer))
        skip_size = self.memory[new_pointer].size
        if offset > 0:
            while offset != 0:
                if offset < skip_size - new_pointer.offset:
                    new_pointer.offset += offset
                    offset = 0
                else:
                    offset -= skip_size - new_pointer.offset
                    new_pointer.offset = 0
                    new_pointer = self.succ_map[new_pointer]
                    if new_pointer.data == 0:
                        return new_pointer
                    skip_size = self.memory[new_pointer].size
        else:
            while offset != 0:
                if new_pointer.offset + offset >= 0:
                    new_pointer.offset += offset
                    offset = 0
                else:
                    offset += new_pointer.offset
                    new_pointer = self.pred_map[new_pointer]
                    if new_pointer.data == 0:
                        return new_pointer
                    new_pointer.offset = self.memory[new_pointer].size
        return new_pointer

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        logging.info(" Read %s", str(address))

        if address not in self.memory:
            raise Exception("Address Not in memory")
        if address.data >= self.address_counter:
            raise Exception("ERROR: tried to access an unalocated address: " +
                            str(address))

        val = self.memory[address]
        if address.offset == 0 and val.size == address.type_size:
            return val #no special math needed

        result = 0
        bytes_to_read = address.type_size
        start = address.offset

        ptr = copy_pointer(address)
        while bytes_to_read != 0:
            num_possible = min(bytes_to_read, val.size - start)
            result += (val.get_value(start, num_possible) *
                       (2**((address.type_size-bytes_to_read)*8)))
            logging.debug("  Read %d byte(s) result so far = %d",
                          num_possible, result)
            bytes_to_read -= num_possible
            if bytes_to_read > 0:
                start = 0
                ptr = self.add_offset_to_pointer(ptr, num_possible)
                if ptr.data == 0:
                    raise Exception("Segfault")
                val = self.memory[ptr]

        return generate_value(result, size=address.type_size)

    def get_nearest_address(self, address):
        """ returns a pointer to the nearest address
            with an offset set to make difference """
        #address = generate_pointer(address, self)
        #raise Exception("Do not want to be here")
        logging.debug(" Look for address %d", address)
        if address in self.memory:
            return generate_pointer(address, self, None)
        if address > self.address_counter or address == 0:
            return self.NULL

        nearest_address = self.NULL
        for key in self.memory:
            if key.data > address:
                break
            nearest_address = key

        if nearest_address != self.NULL:
            offset = address.data - nearest_address.data
            return generate_pointer(nearest_address.data, self, offset)

        return self.NULL

    def write(self, address, value):
        """Write value to the store at address. If there is an existing value,
        merge value into the existing value.
        """

        logging.info('  Write '+str(value) + "  to  " + str(address))

        if not isinstance(address, ReferenceValue):
            raise Exception("Address should not be " + str(address))
        if address.data == 0 or address.data >= self.address_counter:
            raise Exception("Segfault") #underflow or overflow
        if address not in self.memory:
            raise Exception("Unkown address " + str(address))

        old_value = self.memory[address]
        if address.offset == 0 and value.size == old_value.size:
            self.memory[address] = value
            return

        bytes_to_write = value.size
        bytes_written = 0

        while bytes_to_write != 0:
            if address.offset != 0:
                new_data = old_value.get_value(0, address.offset)
            else:
                new_data = 0

            bytes_in_store = old_value.size - address.offset
            able_to_write = min(bytes_to_write,
                                bytes_in_store)
            new_data += (value.get_value(bytes_written, able_to_write) *
                         (2**((address.offset+bytes_written)*8)))
            bytes_to_write -= able_to_write
            bytes_in_store -= able_to_write
            bytes_written += able_to_write

            if bytes_in_store > 0:
                #get rest of object then write
                offset = old_value.size - bytes_in_store
                new_data += (old_value.get_value(offset, bytes_in_store) *
                             (2**(offset*8)))
                self._write_on_offset(address, new_data, old_value)
            elif bytes_to_write > 0:
                #more data left in value, write to store then continue
                self._write_on_offset(address, new_data, old_value)
                address = self.succ_map[address]
                old_value = self.read(address)
            else:
                self._write_on_offset(address, new_data, old_value)
                #neat finish write to store and be done

    def _write_on_offset(self, address, new_data, old_value):
        """ Manages how to write when mixing bytes """
        self.memory[address] = generate_value(new_data,
                                              old_value.type_of,
                                              old_value.size)

#Base Class
class Kont:
    """Abstract class for polymorphism of continuations"""
    def satisfy(self, state, value):
        '''Abstract Method'''
        pass

#Special Konts
class Halt(Kont):
    """Last continuation to execute"""
    def satisfy(self, state, value=None):
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
        super().__init__(parent_state)
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

    def __init__(self, parent_kont, to_type):
        self.parent_kont = parent_kont
        self.to_type = to_type

    def satisfy(self, state, value):
        cast_value = cast(value, self.to_type, state)
        return self.parent_kont.satisfy(state, cast_value)

#class IfKont(Kont):
#    """Continuation for if statement, moves ctrl to correct place"""
#    parent_state = None
#    iftrue = None
#    iffalse = None
#
#    def __init__(self, parent_state, iftrue, iffalse):
#        self.parent_state = parent_state
#        self.iftrue = iftrue
#        self.iffalse = iffalse
#
#    def satisfy(self, state, value):
#        if (value.get_truth_value()):
#            new_ctrl = Ctrl(self.iftrue)
#        elif self.iffalse is not None:
#            new_ctrl = Ctrl(self.iffalse)
#        else:
#            return cesk.interpret.get_next(self.parent_state)
#        return State(new_ctrl, state.envr, state.stor, self.parent_state.kont)

class ReturnKont(Kont): #pylint: disable=too-few-public-methods
    """ Manages return of a function """
    def __init__(self, parent_kont):
        self.parent_kont = parent_kont

    def satisfy(self, state, value):
        return self.parent_kont.satisfy(state, value)

#Expresion Konts
#class LeftBinopKont(Kont):
#    """Continuation for the left side of a binary operator"""
#
#    parent_state = None
#    operator = None
#    right_exp = None
#    return_kont = None
#
#    def __init__(self, parent_state, operator, rightExp, return_kont):
#        self.parent_state = parent_state
#        self.operator = operator
#        self.rightExp = rightExp
#        self.return_kont = return_kont
#
#    def satisfy(self, current_state, value):
#        left_result = value
#        right_kont = RightBinopKont(self.parent_state, left_result,
#                                    self.operator, self.return_kont)
#        return State(Ctrl(self.rightExp), current_state.envr,
#                     current_state.stor, right_kont)
#
#
#class RightBinopKont(Kont):
#    """Continuation for the right side of a binary operator"""
#
#    parent_state = None
#    left_result = None
#    operator = None
#    return_kont = None
#
#    def __init__(self, parent_state, left_result, operator, return_kont):
#        self.parent_state = parent_state
#        self.left_result = left_result
#        self.operator = operator
#        self.return_kont = return_kont
#
#    def satisfy(self, state, value):
#        result = self.left_result.perform_operation(self.operator, value)
#        if isinstance(self.parent_state.kont, FunctionKont):
#            #don't return out of function without return
#            new_state = State(self.parent_state.ctrl, state.envr, state.stor,
#                              self.parent_state.kont)
#            return cesk.interpret.get_next(new_state)
#        return self.return_kont.satisfy(state, result)

# import is down here to allow for circular dependencies
# between structures.py and interpret.py
import cesk.values # pylint: disable=wrong-import-position
import cesk.interpret # pylint: disable=wrong-import-position
