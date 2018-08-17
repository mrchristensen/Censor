"""Holds the data structures for the CESK machine"""

import logging
import pycparser
import pycparser.c_ast as AST
import cesk.linksearch as ls
from cesk.values import ReferenceValue, generate_unitialized_value, cast
from cesk.values import copy_pointer, generate_null_pointer
from cesk.values import generate_pointer, generate_value, generate_frame_address

class SegFault(Exception):
    '''Special Exception for Segmentation Faults'''
    pass

class State: #pylint:disable=too-few-public-methods
    """Holds a program state"""
    ctrl = None #control
    envr = None  #environment
    stor = None #store
    kont_addr = None #k(c)ontinuation Address

    def __init__(self, ctrl, envr, stor, kont_addr):
        self.set_ctrl(ctrl)
        self.set_envr(envr)
        self.set_stor(stor)
        self.set_kont_addr(kont_addr)

    def set_ctrl(self, ctrl):
        """attaches a control object to the state"""
        self.ctrl = ctrl

    def set_envr(self, envr):
        """attaches an environment object to the state"""
        self.envr = envr

    def set_stor(self, stor):
        """attaches a stor object to the state"""
        self.stor = stor

    def set_kont_addr(self, kont_addr):
        """attaches a kont_addr object to the state"""
        self.kont_addr = kont_addr

    def get_kont(self):
        '''returns kont'''
        if self.kont_addr == 0:
            return None #halt kont
        else:
            return self.stor.read_kont(self.kont_addr)

    def get_next(self):
        next_ctrl = self.ctrl.get_next()
        return State(next_ctrl, self.envr, self.stor, self.kont_addr)

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
        if second:
            if isinstance(second, pycparser.c_ast.FuncDef):
                self.construct_body(first, second.body)
            elif isinstance(second, pycparser.c_ast.Compound):
                self.construct_body(first, second)
            else:
                raise Exception("Ctrl init body not Compound or Function: " +
                                str(second))
        elif first:
            self.construct_node(first)
        else:
            raise Exception("Malformed Ctrl init")

    def stmt(self):
        """Retrieves the statement at the location."""
        if self.node:
            return self.node
        return self.body.block_items[self.index]

    def get_next(self):
        """takes state and returns a state with ctrl for the next statement
        to execute"""

        if self.body: #if a standard compound-block:index ctrl
            if self.index + 1 < len(self.body.block_items):
                #if there are more items in the compound block go to next
                return Ctrl(self.index + 1, self.body)

            else:
                #if we are falling off the end of a compound block
                parent = ls.LinkSearch.parent_lut[self.body]
                if parent is None:
                    #we are falling off and there is no parent block
                        raise Exception("Expected Return Statement")

                elif isinstance(parent, AST.Compound):
                    #find current compound block position in the parent block
                    parent_index = ls.LinkSearch.index_lut[self.body]
                    new_ctrl = Ctrl(parent_index, parent)

                else:
                    #if the parent is not a compound (probably an if statement)
                    new_ctrl = Ctrl(parent) #make a special ctrl and try again

                return new_ctrl.get_next()

        if self.node:
            #if it is a special ctrl as created by binop or assign
            #try to convert to normal ctrl and try again
            parent = ls.LinkSearch.parent_lut[self.node]
            if isinstance(parent, AST.Compound):
                #we found the compound we can create normal ctrl
                parent_index = ls.LinkSearch.index_lut[self.node]
                new_ctrl = Ctrl(parent_index, parent)
            else:
                #we couldn't make a normal try again on parent
                new_ctrl = Ctrl(parent)
            return new_ctrl.get_next()

        raise Exception("Malformed ctrl: this should have been unreachable")

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    counter = 1 #counter to track which frame you are in
    global_id = 0
    global_identifiers = {}

    def __init__(self):
        self.map_to_address = {} #A set of IdToAddr mappings
        self.scope_id = Envr.counter
        Envr.counter += 1

    def get_frame_address(self, ident):
        """ Returns the Frame Address """
        while not isinstance(ident, str):
            ident = ident.name
        return generate_frame_address(self.scope_id, ident)

    def get_address(self, ident):
        """looks up the address associated with an identifier"""
        if ident in self.map_to_address:
            return self.map_to_address[ident]
        elif ident in Envr.global_identifiers:
            return Envr.global_identifiers[ident]
        raise Exception(ident + " is not defined in this scope: " +
                        str(self.scope_id))

    def map_new_identifier(self, frame_addr, ptr_address):
        """Add a new identifier to the mapping"""
        self.map_to_address[frame_addr] = ptr_address

    def is_localy_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in self.map_to_address
    def is_globaly_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in Envr.global_identifiers

class Stor:
    """Represents the contents of memory at a moment in time."""

    def __init__(self, to_copy=None):
        if to_copy is None:
            self.null_addr = generate_null_pointer(self)
            self.address_counter = 1 # start at 1 so that 0 can be nullptr
            self.memory = {}
            self.kont = {}
            self.succ_map = {}
            self.pred_map = {}
            self.succ_map[self.null_addr] = self.null_addr
            self.pred_map[self.null_addr] = self.null_addr
        elif isinstance(to_copy, Stor): #shallow copy of stor
            self.null_addr = to_copy.null_addr
            self.address_counter = to_copy.address_counter
            self.memory = to_copy.memory
            self.kont = to_copy.kont
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
        self.succ_map[pointer] = self.null_addr
        self.pred_map[pointer] = self.null_addr
        return pointer

    def allocate_block(self, length, size=1):
        """Moves the address counter to leave room for an array and returns
        start"""
        start_address = self.address_counter
        start_pointer = self._make_new_address(size)

        self.pred_map[start_pointer] = self.null_addr

        last_pointer = start_pointer
        while self.address_counter < (start_address + length * size):
            new_pointer = self._make_new_address(size)

            self.pred_map[new_pointer] = last_pointer
            self.succ_map[last_pointer] = new_pointer
            last_pointer = new_pointer
        self.succ_map[last_pointer] = self.null_addr

        return start_pointer

    def allocate_nonuniform_block(self, list_of_sizes):
        """ Takes in a list of sizes as int and allocates
             and links a block in the stor for each size """
        start_pointer = self._make_new_address(list_of_sizes[0])
        self.pred_map[start_pointer] = self.null_addr

        prev = start_pointer
        for block_size in list_of_sizes[1:]:
            next_block = self._make_new_address(block_size)
            self.pred_map[next_block] = prev
            self.succ_map[prev] = next_block
            prev = next_block

        self.succ_map[prev] = self.null_addr

        return start_pointer

    def add_offset_to_pointer(self, pointer, offset): #pylint: disable=too-many-branches
        """ updates the pointer's offset by the offset passed.
        Using the predecessor and successor maps: pointers move
        to the next block if the offset extends beyond the bounds
        of the current block.
        """
        logging.debug("Offsetting %s by %d", str(pointer), offset)
        new_pointer = pointer#copy_pointer(pointer)
        if new_pointer not in self.memory:
            if new_pointer.data == 0: #null is always null
                new_pointer.offset += offset
                return new_pointer
            raise Exception("Invalid Pointer " + str(new_pointer))
        skip_size = self.memory[new_pointer].size
        if offset > 0:
            while offset != 0:
                if (offset < skip_size - new_pointer.offset or
                        self.succ_map[new_pointer] is self.null_addr):
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
                if (new_pointer.offset + offset >= 0 or
                        self.pred_map[new_pointer] is self.null_addr):
                    new_pointer.offset += offset
                    offset = 0
                else:
                    offset += new_pointer.offset
                    new_pointer = self.pred_map[new_pointer]
                    if new_pointer.data == 0:
                        return new_pointer
                    new_pointer.offset = self.memory[new_pointer].size
        logging.debug("Pointer offset to %s", str(new_pointer))
        return new_pointer

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        logging.info("Reading %s", str(address))

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
            if ptr.offset >= val.size or ptr.offset < 0:
                raise SegFault()
            num_possible = min(bytes_to_read, val.size - start)
            result += (val.get_value(start, num_possible) *
                       (2**((address.type_size-bytes_to_read)*8)))
            logging.debug("  Read %d byte(s) result so far = %d",
                          num_possible, result)
            bytes_to_read -= num_possible
            if bytes_to_read > 0:
                ptr = self.add_offset_to_pointer(ptr, num_possible)
                start = ptr.offset
                if ptr.data == 0:
                    raise SegFault()
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
            return self.null_addr

        nearest_address = self.null_addr
        for key in self.memory:
            if key.data > address:
                break
            nearest_address = key

        if nearest_address != self.null_addr:
            offset = address.data - nearest_address.data
            return generate_pointer(nearest_address.data, self, offset)

        return self.null_addr

    def write(self, address, value):
        """Write value to the store at address. If there is an existing value,
        merge value into the existing value.
        """

        logging.info('  Write %s  to  %s', str(value), str(address))

        if not isinstance(address, ReferenceValue):
            raise Exception("Address should not be " + str(address))
        if address.data == 0 or address.data >= self.address_counter:
            raise SegFault() #underflow or overflow
        if address not in self.memory:
            raise Exception("Unkown address " + str(address))

        old_value = self.memory[address]
        if address.offset == 0 and value.size == old_value.size:
            self.memory[address] = value
            return

        bytes_to_write = value.size
        bytes_written = 0

        while bytes_to_write != 0:
            if address.offset >= old_value.size or address.offset < 0:
                raise SegFault()

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

    def write_kont(self, kont_addr, kai):
        self.kont[kont_addr] = kai

    def read_kont(self, kont_addr):
        if kont_addr not in self.kont:
            raise Exception("Address not in memory: " + str(kont_addr))
        return self.kont[kont_addr]

class Kont: #pylint: disable=too-few-public-methods
    """Kontinuations"""
    
    allocK_address = 0
    @staticmethod
    def allocK():
        value = Kont.allocK_address
        Kont.allocK_address += 1
        return value

    def __init__(self, parent_state, address = None):
        self.ctrl = parent_state.ctrl
        self.envr = parent_state.envr
        self.kont_addr = parent_state.kont_addr
        self.address = address # If Kont returns to an assignment

    def invoke(self, state, value):
        if self.kont_addr is 0:
            exit(0)
        if self.address:
            state.stor.write(self.address, value)
        new_state = State(self.ctrl, self.envr,
                          state.stor, self.kont_addr)
        return new_state.get_next()

# import is down here to allow for circular dependencies
import cesk.values # pylint: disable=wrong-import-position
