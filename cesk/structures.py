"""Holds the data structures for the CESK machine"""

import logging
import pycparser
import pycparser.c_ast as AST
import cesk.linksearch as ls
from cesk.values import generate_unitialized_value
from cesk.values import copy_pointer, generate_null_pointer
from cesk.values import generate_pointer, generate_value
from cesk.values.base_values import ByteValue, SizedSet
import cesk.config as cnf
from cesk.exceptions import MemoryAccessViolation, UnknownConfiguration, \
                           CESKException

class State: #pylint:disable=too-few-public-methods
    """Holds a program state"""
    #ctrl = None #control
    #envr = None  #environment
    #stor = None #store
    #kont_addr = None #k(c)ontinuation Address
    #time_stamp = None

    _time = 0

    def __init__(self, ctrl, envr, stor, kont_addr):
        self.set_ctrl(ctrl)
        self.set_envr(envr)
        self.set_stor(stor)
        self.set_kont_addr(kont_addr)
        self.tick()

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
        """ Moves the ctrl and returns the new state """
        next_ctrl = self.ctrl.get_next()
        return State(next_ctrl, self.envr, self.stor, self.kont_addr)

    def tick(self):
        """ Sets the time stamp for the state """
        if cnf.CONFIG['tick'] == 'concrete':
            State._time += 1
            self.time_stamp = State._time
        elif cnf.CONFIG['tick'] == 'abstract':
            self.time_stamp = self.stor.get_time()
        elif cnf.CONFIG['tick'] == 'trivial':
            self.time_stamp = State._time
        else:
            raise UnknownConfiguration('tick')

    def __eq__(self, other):
        return (self.ctrl == other.ctrl and
                self.envr == other.envr and
                self.kont_addr == other.kont_addr)

    def __hash__(self):
        h = hash(self.ctrl)
        h = h * hash(self.envr) + 37
        h = h * hash(self.kont_addr) + 17
        return h


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
                raise CESKException("Ctrl init body not Compound or Function: " +
                                str(second))
        elif first:
            self.construct_node(first)
        else:
            raise CESKException("Malformed Ctrl init")

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
                    raise CESKException("Expected Return Statement")

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

        raise CESKException("Malformed ctrl: this should have been unreachable")

    def __eq__(self, other):
        if self.body:
            return other.body and self.body == other.body and \
                                 self.index == other.index
        if self.node:
            return self.node == other.node
        return False

    def __hash__(self):
        if self.body:
            return ((31 * hash(self.body)) + 62257) * hash(self.index) + 97
        else:
            return hash(self.node)

class FrameAddress:
    """ Contains a link between frame and id """

    def __init__(self, frame_id, ident):
        self.frame = frame_id
        self.ident = ident
        #super(FrameAddress, self).__init__(0, 1)

    def get_frame(self):
        """ Returns frame identifier """
        return self.frame

    def get_id(self):
        """ Returns identifier name """
        return self.ident

    def __hash__(self):
        return 1+43*hash(self.ident)+73*hash(self.frame)

    def __eq__(self, other):
        if not isinstance(other, FrameAddress):
            return False
        return self.ident == other.ident and self.frame == other.frame

    def __str__(self):
        return "("+str(self.frame)+", "+str(self.ident)+")"

class Envr:
    """Holds the enviorment (a maping of identifiers to addresses)"""
    counter = 1 #counter to track which frame you are in (one per function)
    global_id = 0
    global_envr = None

    def __init__(self, state):
        self.map_to_address = {} #A set of IdToAddr mappings
        self.scope_id = self.allocF(state)

    def allocF(self, state): #pylint: disable=no-self-use,invalid-name
        """ Allocation of frame identefiers """
        value = None
        if cnf.CONFIG['allocF'] == 'concrete':
            value = Envr.counter
            Envr.counter += 1
        elif cnf.CONFIG['allocF'] == '0-cfa':
            if state is not None:
                value = state.ctrl
        elif cnf.CONFIG['allocF'] == 'trivial':
            value = Envr.counter
        else:
            raise UnknownConfiguration('allocF')
        return value

    def get_address(self, ident):
        """looks up the address associated with an identifier"""
        while not isinstance(ident, str):
            ident = ident.name
        if ident in self.map_to_address:
            return self.map_to_address[ident]
        elif ident in Envr.global_envr:
            return Envr.global_envr.map_to_address[ident]
        raise CESKException(ident + " is not defined in this scope: " +
                        str(self.scope_id))

    def map_new_identifier(self, ident):
        """Add a new identifier to the mapping"""
        while not isinstance(ident, str):
            ident = ident.name
        if self.is_localy_defined(ident):
            return self.map_to_address[ident]
        frame_addr = FrameAddress(self.scope_id, ident)
        self.map_to_address[ident] = frame_addr
        return frame_addr

    @staticmethod
    def set_global(global_env):
        """ sets a global environment """
        global_env.scope_id = 0
        Envr.global_envr = global_env

    def is_localy_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in self.map_to_address

    @staticmethod
    def is_globaly_defined(ident):
        """returns if a given identifier is local to this scope"""
        return ident in Envr.global_envr.map_to_address

    def __contains__(self, ident):
        return self.is_localy_defined(ident) or Envr.is_globaly_defined(ident)

    def __eq__(self, other):
        return self.scope_id == other.scope_id

    def __hash__(self):
        return hash(self.scope_id)

class Stor: #pylint: disable=too-many-instance-attributes
    """Represents the contents of memory at a moment in time."""
    heap_address_counter = 0

    def __init__(self, to_copy=None):
        if to_copy is None:
            self.null_addr = generate_null_pointer()
            self.address_counter = 1 # start at 1 so that 0 can be nullptr
            self.memory = {}
            self.base_pointers = {}
            self.kont = {}
            self.succ_map = {}
            self.pred_map = {}
            self.succ_map[self.null_addr] = self.null_addr
            self.pred_map[self.null_addr] = self.null_addr
            self.time = 0 #tracks how many times the stor has changed
        elif isinstance(to_copy, Stor): #shallow copy of stor
            self.null_addr = to_copy.null_addr
            self.address_counter = to_copy.address_counter
            self.memory = to_copy.memory
            self.base_pointers = to_copy.frames
            self.kont = to_copy.kont
            self.succ_map = to_copy.succ_map
            self.pred_map = to_copy.pred_map
            self.time = to_copy.time
        else:
            raise CESKException("Stor Copy Constructor Expects a Stor Object")

    def _make_new_address(self, size):
        """ Alloc address for a certian size and store unitialized value """
        logging.info("Alloc %d for %d bytes", self.address_counter, size)
        #will throw error if size is None
        pointer = generate_pointer(self.address_counter, size)
        if cnf.CONFIG['store_update'] == 'strong':
            self.memory[pointer] = generate_unitialized_value(size)
        elif cnf.CONFIG['store_update'] == 'weak':#Starts with an empty set
            self.memory[pointer] = SizedSet(size)
        self.address_counter += size
        return pointer

    def allocM(self, base, list_of_sizes, length=1, extra=0): #pylint: disable=invalid-name
        """ Given a base pointer or frame address allocate memomory """
        if base in self.base_pointers:
            return self.base_pointers[base]
        self.time += 1 #update time
        start_pointer = None
        prev = None
        for _ in range(length):

            if prev is None:
                prev = self.null_addr
                start_pointer = self._make_new_address(list_of_sizes[0])
                self.pred_map[start_pointer] = prev
                prev = start_pointer
            else:
                next_block = self._make_new_address(list_of_sizes[0])
                self.succ_map[prev] = next_block
                self.pred_map[next_block] = prev
                prev = next_block

            for block_size in list_of_sizes[1:]:
                next_block = self._make_new_address(block_size)
                self.pred_map[next_block] = prev
                self.succ_map[prev] = next_block
                prev = next_block

        if extra != 0: #malloc region is not divisable by the block size
            next_block = self._make_new_address(extra)
            self.pred_map[next_block] = prev
            self.succ_map[prev] = next_block
            prev = next_block

        self.succ_map[prev] = self.null_addr

        self.base_pointers[base] = start_pointer
        return start_pointer

    def allocH(self, state): #pylint: disable=invalid-name
        """ Calls the right allocator based on input and allocH config """
        if cnf.CONFIG['allocH'] == 'abstract':
            return state.ctrl
        elif cnf.CONFIG['allocH'] == 'concrete':
            Stor.heap_address_counter += 1
            return Stor.heap_address_counter
        elif cnf.CONFIG['allocH'] == 'trivial':
            return Stor.heap_address_counter
        else:
            raise UnknownConfiguration("allocH")

    def fa2ptr(self, frame_address):
        """ Fetch store address for a frame address """
        return self.base_pointers[frame_address]

    def add_offset_to_pointer(self, pointer, offset): #pylint: disable=too-many-branches
        """ updates the pointer's offset by the offset passed.
        Using the predecessor and successor maps: pointers move
        to the next block if the offset extends beyond the bounds
        of the current block.
        """
        new_pointer = copy_pointer(pointer)
        if new_pointer not in self.memory:
            if new_pointer.data == 0: #null is always null
                new_pointer.offset += offset
                return new_pointer
            raise CESKException("Invalid Pointer " + str(new_pointer))
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
        logging.debug("Update %s to %s", str(pointer), str(new_pointer))
        return new_pointer

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        if isinstance(address, SizedSet):
            #read to all location in the set
            if not address: #if set is empty
                raise MemoryAccessViolation("Read from unassigned address")
            result = None
            for addr in address:
                temp = self.read(addr)
                if result is None:
                    result = SizedSet(temp.size)
                result.update(temp)
            return result
        if address in self.base_pointers:
            address = self.base_pointers[address]
        else:
            address.update(self) #update offset of pointer

        logging.info("Reading %s", str(address))
        if address.data >= self.address_counter or \
                address.data == 0 or \
                address not in self.memory:
            raise MemoryAccessViolation("Out of bounds read") #underflow or overflow

        val = self.memory[address]
        if address.offset == 0 and val.size == address.type_size:
            logging.debug("\tRead %s", val)
            return val #no special math needed

        #immoral read over/within byte boundary
        result = ByteValue()
        bytes_to_read = address.type_size
        start = address.offset

        ptr = address
        while bytes_to_read > 0:
            if ptr.offset >= val.size or ptr.offset < 0:
                #signifies top and bottom
                raise MemoryAccessViolation("Out of bounds read1")
            num_possible = min(bytes_to_read, val.size - start)
            result.append(val.get_byte_value(start, num_possible))
            bytes_to_read -= num_possible
            if bytes_to_read > 0:
                ptr = self.add_offset_to_pointer(ptr, num_possible)
                start = ptr.offset
                if ptr.data == 0:
                    raise MemoryAccessViolation("Out of bounds read2")
                val = self.memory[ptr]

        return result

    def write(self, address, value):
        """ Calls strong or weak write as determined by configuration """
        logging.info('  Write %s  to  %s', str(value), str(address))
        if isinstance(address, set):
            #write to all location in the set
            if not address: #if set is empty
                raise MemoryAccessViolation("Write to unassigned address")
            for addr in address:
                self.write(addr, value)
            return
        if address in self.base_pointers:
            address = self.base_pointers[address]
        else:
            address.update(self)

        if address.data == 0 or\
           address.data >= self.address_counter or\
           address not in self.memory:
            #update to record seg fault rather than error out
            #TODO produce back tracking capabilities
            raise MemoryAccessViolation("Out of Bounds Write") #underflow or overflow or invallid address

        if cnf.CONFIG['store_update'] == 'strong':
            self.strong_write(address, value)
        elif cnf.CONFIG['store_update'] == 'weak':
            self.weak_write(address, value)
        else:
            raise UnknownConfiguration('store_update')

    def weak_write(self, address, value):
        """ Adds value to a set of values stored at address """
        old_values = self.memory[address]
        if address.offset == 0 and value.size == old_values.size:
            if isinstance(value, SizedSet):
                for val in value:
                    if val not in old_values:
                        self.time += 1
                        old_values.add(val)
            else:
                if value not in old_values:
                    self.time += 1
                    old_values.add(value)
            return

        #begin a partial or overlapping write
        raise NotImplemented("Partial weak write not implemented")

    def strong_write(self, address, value):
        """Write value to the store at address. If there is an existing value,
            replace the value
        """

        old_value = self.memory[address]
        if address.offset == 0 and value.size == old_value.size:
            self.memory[address] = value
            if value != old_value:
                self.time += 1
            return

        #begin a partial or overlapping write
        bytes_to_write = value.size
        bytes_written = 0

        while bytes_to_write != 0:
            if not isinstance(address.offset, int) or \
                    address.offset >= old_value.size or \
                    address.offset < 0:
                raise MemoryAccessViolation("write out of bounds")

            #get unchanged part of value at the given address location
            if address.offset != 0:
                new_data = old_value.get_byte_value(0, address.offset)
            else:
                new_data = ByteValue() #empty byte value

            #bytes in store represents the number of bytes in the store that
            #are available to be overwritten
            bytes_in_store = old_value.size - address.offset
            able_to_write = min(bytes_to_write, bytes_in_store)

            #get value from data being written
            new_data.append(value.get_byte_value(bytes_written, able_to_write))
            
            bytes_to_write -= able_to_write
            bytes_written  += able_to_write

            #update bytes in store to represent unoverwriten bytes left
            bytes_in_store -= able_to_write

            if bytes_in_store > 0:
                #get rest of object then write
                offset = old_value.size - bytes_in_store
                new_data.append(old_value.get_byte_value(offset, bytes_in_store))
                self._write_on_offset(address, new_data, old_value)
            elif bytes_to_write > 0:
                #more data left in value, write to store then continue
                self._write_on_offset(address, new_data, old_value)
                address = self.succ_map[address] #update address and old_value
                old_value = self.read(address)
            else:
                self._write_on_offset(address, new_data, old_value)
                #neat finish write to store and be done

    def _write_on_offset(self, address, new_data, old_value):
        """ Manages how to write when mixing bytes """
        self.memory[address] = generate_value(new_data, old_value.type_of)

    def get_nearest_address(self, address):
        """ returns a pointer to the nearest address
            with an offset set to make difference """
        #address = generate_pointer(address, self)
        #raise Exception("Do not want to be here")
        logging.debug(" Look for address %d", address)
        if address in self.memory:
            return generate_pointer(address, None)
        if address > self.address_counter or address == 0:
            return self.null_addr

        nearest_address = self.null_addr
        for key in self.memory:
            if key.data > address:
                break
            nearest_address = key

        if nearest_address != self.null_addr:
            offset = address.data - nearest_address.data
            return generate_pointer(nearest_address.data, offset)

        return self.null_addr

    def write_kont(self, kont_addr, kai):
        """ records the continuation for the continuation address """
        if cnf.CONFIG['allocK'] == 'concrete':
            self.kont[kont_addr] = {kai}
        else: #allocK == 0-cfa or p4f or trivial
            if kont_addr not in self.kont:
                self.kont[kont_addr] = set()
            self.kont[kont_addr].add(kai)

    def read_kont(self, kont_addr):
        """ returns the continuation(s) for the given kont_addr """
        if kont_addr not in self.kont:
            raise CESKException("Address not in memory: " + str(kont_addr))
        return self.kont[kont_addr]

    def get_time(self):
        """ Updates when new address is allocated or store value is changed """
        return self.time

class Kont: #pylint: disable=too-few-public-methods
    """Kontinuations"""

    allocK_address = 2 
    @staticmethod
    def allocK(state=None, nxt_ctrl=None, nxt_envr=None): #pylint: disable=invalid-name
        """ Generator for continuation addresses """
        if cnf.CONFIG['allocK'] == "concrete":
            value = Kont.allocK_address
            Kont.allocK_address += 1
        elif cnf.CONFIG['allocK'] == "0-cfa":
                value = state.ctrl
        elif cnf.CONFIG['allocK'] == "p4f":
            value = (nxt_ctrl, nxt_envr)
        elif cnf.CONFIG['allocK'] == "trivial":
            value = Kont.allocK_address
        return value

    def __init__(self, parent_state, address=None):
        self.ctrl = parent_state.ctrl
        self.envr = parent_state.envr
        self.kont_addr = parent_state.kont_addr
        self.address = address # If Kont returns to an assignment

    def invoke(self, state, value):
        """ Evaluates the return of a function """
        if self.kont_addr is 0:
            return None
        if self.address:
            state.stor.write(self.address, value)
        new_state = State(self.ctrl, self.envr,
                          state.stor, self.kont_addr)
        return new_state.get_next()

    def __eq__(self, other):
        return self.ctrl == other.ctrl and \
               self.envr == other.envr and \
               self.kont_addr == other.kont_addr and \
               self.address == other.address

    def __hash__(self):
        h = 7
        h = h * hash(self.ctrl) + 37
        h = h * hash(self.envr) + 53
        h = h * hash(self.kont_addr) + 97
        h = h * hash(self.address) + 3
        return h
