"""Holds the data structures for the CESK machine"""

import logging
import pycparser
import pycparser.c_ast as AST
import cesk.linksearch as ls
from cesk.values import generate_unitialized_value
from cesk.values import generate_null_pointer
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

    def get_error(self, err_str):
        """ generates an error state based on current state """
        return ErrorState(self, err_str)

    def tick(self):
        """ Sets the time stamp for the state """
        if cnf.CONFIG['tick'] == 'concrete':
            State._time += 1
            self.time_stamp = State._time
        elif cnf.CONFIG['tick'] == 'abstract':
            if self.stor is None:
                self.time_stamp = State._time
            else:
                self.time_stamp = self.stor.get_time()
        elif cnf.CONFIG['tick'] == 'trivial':
            self.time_stamp = State._time
        else:
            raise UnknownConfiguration('tick')

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.ctrl == other.ctrl and
                self.envr == other.envr and
                self.kont_addr == other.kont_addr)

    def __hash__(self):
        result = hash(self.ctrl)
        result = result * hash(self.envr) + 37
        result = result * hash(self.kont_addr) + 17
        return result

    def __str__(self):
        return (str(self.ctrl)+"\n"+
                str(self.envr)+"\n"+
                "ka "+str(self.kont_addr)).replace(':', ' ')

class ErrorState: #pylint: disable=too-few-public-methods
    """ Holds program state that errored upon execution """
    def __init__(self, state, msg): #ctrl, envr, stor, kont_addr, time_stamp):
        self.ctrl = state.ctrl
        self.envr = state.envr
        self.stor = state.stor
        self.kont_addr = state.kont_addr
        self.time_stamp = state.time_stamp
        self.message = msg

    def __eq__(self, other):
        if not isinstance(other, ErrorState):
            return False
        return (self.ctrl == other.ctrl and
                self.envr == other.envr and
                self.message == other.message and
                self.kont_addr == other.kont_addr)

    def __hash__(self):
        result = hash(self.ctrl) + 53
        result = result * hash(self.envr) + 37
        result = result * hash(self.kont_addr) + 17
        result = result * hash(self.message)
        return result

    def __str__(self):
        return ("Error in "+str(self.envr)+"\nat "+str(self.ctrl)+"\n"+
                "to "+str(self.kont_addr)).replace(':', ' ')+"\n"+self.message

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
                raise CESKException("Ctrl init body not Compound or Function: "+
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
        if isinstance(other, int):
            return False
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

    def __repr__(self):
        if self.body:#this will not be unique for every contral
            return (type(self.body.block_items[self.index]).__name__+" at "+
                    str(self.body.block_items[self.index].coord))
        if self.node:
            return type(self.node).__name__+" at "+str(self.node.coord)
        return "No body in ctrl"

class FrameAddress:
    """ Contains a link between frame identifier and variable identifier """

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
    """Holds the enviorment/frame (a maping of identifiers to addresses)"""
    next_frame_id = 1 #Tracks next concrete frame id
    global_envr_id = 0
    global_envr = None

    def __init__(self, func_name, ctrl):
        self.local_variables = {} #A set of IdToAddr mappings
        self.frame_id = self.allocF(func_name, ctrl)

    def allocF(self, name, ctrl): #pylint: disable=no-self-use,invalid-name
        """ Allocation of frame identefiers """
        value = None
        if name is None:
            name = 'global'

        if cnf.CONFIG['allocF'] == 'concrete':
            value = str(Envr.next_frame_id)+" "+str(name)
            Envr.next_frame_id += 1
        elif cnf.CONFIG['allocF'] == '0-cfa':
            value = name
        elif cnf.CONFIG['allocF'] == 'trivial':
            value = Envr.next_frame_id
        elif cnf.CONFIG['allocF'] == '1-cfa':
            value = (name, ctrl)
        else:
            raise UnknownConfiguration('allocF')
        return value

    def get_address(self, ident):
        """looks up the address associated with an identifier"""
        while not isinstance(ident, str):
            ident = ident.name
        if ident in self.local_variables:
            return self.local_variables[ident]
        elif ident in Envr.global_envr:
            return Envr.global_envr.local_variables[ident]
        # raise CESKException(ident + " is not defined in this scope: " +
        #                     str(self.frame_id))
        logging.debug(ident + " is not defined in this scope: " + str(self.frame_id))
        return None
        
    def map_new_identifier(self, ident):
        """Add a new identifier to the mapping"""
        frame_addr = FrameAddress(self.frame_id, ident)
        self.local_variables[ident] = frame_addr
        return frame_addr

    @staticmethod
    def set_global(global_env):
        """ sets a global environment """
        global_env.frame_id = Envr.global_envr_id
        Envr.global_envr = global_env

    def is_localy_defined(self, ident):
        """returns if a given identifier is local to this scope"""
        return ident in self.local_variables

    @staticmethod
    def is_globaly_defined(ident):
        """returns if a given identifier is local to this scope"""
        return ident in Envr.global_envr.local_variables

    def __contains__(self, ident):
        return self.is_localy_defined(ident) or Envr.is_globaly_defined(ident)

    def __eq__(self, other):
        return self.frame_id == other.frame_id

    def __hash__(self):
        return hash(self.frame_id)

    def __str__(self):
        return str(self.frame_id)

class MemoryBlock:
    """ Block of Memory """

    def __init__(self, sizes, length, extra):
        self.shape = (sizes, length, extra)
        self.size = sum(sizes)*length + extra
        self.block = []
        self.is_free = False

        for _ in range(length):
            for size in sizes:
                self._add_value(size)

        if extra != 0:
            self._add_value(extra)

        if len(sizes) == 1 and length == 1 and extra == 0:
            self._get_index = self._get_index_item
        else:
            self._get_index = self._get_index_list

        if cnf.CONFIG['store_update'] == 'strong':
            self.write = self.strong_write
            self.add = lambda s, v: s.add(v)
        elif cnf.CONFIG['store_update'] == 'weak':
            self.write = self.weak_write
            self.add = lambda s, v: s.update(v)
        else:
            raise UnknownConfiguration('store_update')

    def _add_value(self, size):
        """ Adds a memory slot to store a value """
        if cnf.CONFIG['store_update'] == 'strong':
            self.block.append(generate_unitialized_value(size))
        elif cnf.CONFIG['store_update'] == 'weak':
            self.block.append(SizedSet(size))
        else:
            raise UnknownConfiguration("store_update")

    def _get_index_item(self, offset):
        """ given an offset returns value or throws error """
        if not isinstance(offset, int):
            logging.error("TOP memory access made")
            offset = 0
        return [[0, offset]]

    def _get_index_list(self, offset):
        """ given an offset returns the number of time a succ map
            would need to be called to find the item and offset remaning """
        if not isinstance(offset, int):
            logging.error("TOP memory access made")
            return [[i, 0] for i in range(len(self.block))]
        group = sum(self.shape[0])
        index = (offset // group)
        offset = offset % group
        if index == self.shape[1]:#accesses extra part
            index *= len(self.shape[0])
            return [[index, offset]]
        index *= len(self.shape[0])
        i = 0
        while offset >= self.shape[0][i]:
            offset -= self.shape[0][i]
            index += 1
            i += 1
        return [[index, offset]]

    def not_in_block(self, offset, size):
        """ function to identify if offset is in the block """
        if isinstance(offset, int):
            return offset < 0 or offset+size > self.size
        else: #is abstract literal top
            return False #add possible memory error here

    def read(self, offset, read_size):
        """ return value or set of values based on read """
        if self.not_in_block(offset, read_size):
            raise MemoryAccessViolation("Illegal Read")

        result = SizedSet(read_size)
        for index, start in self._get_index(offset):
            if start == 0 and self.block[index].size == read_size:
                self.add(result, self.block[index])
                continue
            #immoral read over/within byte boundary
            byte_value = ByteValue()
            bytes_to_read = read_size
            value = self.block[index]
            while bytes_to_read > 0:
                num_possible = min(bytes_to_read, value.size - start)
                byte_value.append(value.get_byte_value(start, num_possible))
                bytes_to_read -= num_possible
                if bytes_to_read > 0:
                    index += 1
                    start = 0
                    value = self.block[index]
            self.add(result, byte_value)

        #return result
        if len(result) == 1 and cnf.CONFIG['store_update'] == 'strong':
            return result.pop()
        else:
            return result

    def strong_write(self, offset, value):
        """ Writes the value given at the offset given
            returns True if values are changed False otherwise"""
        if self.not_in_block(offset, value.size):
            raise MemoryAccessViolation("Illegal Write")
        for index, start in self._get_index(offset):
            if start == 0 and self.block[index].size == value.size:
                self.block[index] = value

            old_value = self.block[index]
            if start == 0 and value.size == old_value.size:
                self.block[index] = value
                return value != old_value

            #begin a partial or overlapping write
            bytes_to_write = value.size
            bytes_written = 0

            while bytes_to_write != 0:

                #get unchanged part of value at the given pointer location
                if start != 0:
                    new_data = old_value.get_byte_value(0, start)
                else:
                    new_data = ByteValue() #empty byte value

                #bytes in store represents the number of bytes in the store that
                #are available to be overwritten
                bytes_in_store = old_value.size - start
                able_to_write = min(bytes_to_write, bytes_in_store)

                #get value from data being written
                new_data.append(
                    value.get_byte_value(bytes_written, able_to_write))

                bytes_to_write -= able_to_write
                bytes_written += able_to_write

                if bytes_to_write > 0:
                    #more data left in value, write to store then continue
                    self._write_on_offset(index, new_data, old_value)
                    index += 1 #update pointer and old_value
                    start = 0
                    old_value = self.block[index]
                elif bytes_in_store > able_to_write:
                    #get rest of object then write
                    offset = start+able_to_write
                    new_data.append(
                        old_value.get_byte_value(offset,
                                                 bytes_in_store-able_to_write))
                    self._write_on_offset(index, new_data, old_value)
                else:
                    self._write_on_offset(index, new_data, old_value)
                    #neat finish write to store and be done

    def _write_on_offset(self, index, new_data, old_value):
        """ Manages how to write when mixing bytes """
        # TODO check if old/new value are sets and handle
        self.block[index] = generate_value(new_data, old_value.type_of)

    def weak_write(self, offset, value):
        """ Writes the value given at the offset given
            returns True if values are changed False otherwise"""
        if self.not_in_block(offset, value.size):
            raise MemoryAccessViolation("Illegal Write")
        is_change = False
        for index, start in self._get_index(offset):
            if start == 0 and self.block[index].size == value.size:
                old_values = self.block[index]
                if isinstance(value, SizedSet):
                    for val in value:
                        if val not in old_values:
                            is_change = True
                            old_values.add(val)
                elif value not in old_values:
                    is_change = True
                    old_values.add(value)
                #else value already in store, no update
                continue
            #begin a partial or overlapping write
            raise NotImplementedError("Partial weak write not implemented")
        return is_change

    def free(self):
        """ Marks the block as free """
        self.is_free = True

class Stor: #pylint: disable=too-many-instance-attributes
    """Represents the contents of memory at a moment in time."""
    heap_address_counter = 0

    def __init__(self, to_copy=None):
        if to_copy is None:
            self.null_addr = generate_null_pointer()
            self.next_block_id = 1 # start at 1 so that 0 can be nullptr
            self.memory = {}
            self.base_pointers = {}
            self.kont_map = {}
            self.time = 0 #tracks how many times the stor has changed
        elif isinstance(to_copy, Stor): #shallow copy of stor
            self.null_addr = to_copy.null_addr
            self.next_block_id = to_copy.next_block_id
            self.memory = to_copy.memory
            self.base_pointers = to_copy.frames
            self.kont_map = to_copy.kont
            self.time = to_copy.time
        else:
            raise CESKException("Stor Copy Constructor Expects a Stor Object")

    def _add_new_block(self, block):
        """ Add new block and return pointer """
        logging.info("Make new block: shape %s, at %d",
                     str(block.shape), self.next_block_id)
        pointer = generate_pointer(self.next_block_id, block.size)
        self.memory[self.next_block_id] = block
        self.next_block_id += block.size #Value added is arbitrary
        return pointer

    def allocM(self, base, list_of_sizes, length=1, extra=0): #pylint: disable=invalid-name
        ''' new allocM to have only successors and
            all pointers only have one base pointer per block '''
        if base in self.base_pointers:
            return self.base_pointers[base]

        new_block = MemoryBlock(list_of_sizes, length, extra)
        block_ptr = self._add_new_block(new_block)
        self.base_pointers[base] = block_ptr
        return block_ptr

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

    def _check_address(self, block, action):
        """ Checks to see if address is valid and
            reports error if found """
        if block >= self.next_block_id:
            raise MemoryAccessViolation("Out of bounds "+action)
        elif block == self.null_addr.get_block():
            raise MemoryAccessViolation("Null "+action)
        elif block not in self.memory:
            raise MemoryAccessViolation("Invalid Base in "+action)
        elif self.memory[block].is_free:
            raise MemoryAccessViolation("Base is Free, invalid "+action)

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        if isinstance(address, SizedSet):
            #read to all location in the set
            if not address: #if set is empty
                raise MemoryAccessViolation("Read from unassigned address")
            result = None #SizedSet()
            errors = set()
            for addr in address:
                try:
                    temp, _ = self.read(addr)
                    if result is None:
                        result = SizedSet(temp.size)
                    result.update(temp)
                except MemoryAccessViolation as error:
                    errors.add(str(error))
            return result, errors

        if address in self.base_pointers:
            address = self.base_pointers[address]

        logging.info("Reading %s", str(address))
        self._check_address(address.get_block(), 'read')

        return self.memory[address.get_block()].read(
            address.offset, address.type_size), set()

    def write(self, address, value):
        """ Calls strong or weak write as determined by configuration """
        if isinstance(address, SizedSet):
            #write to all location in the set
            if not address: #if set is empty
                raise MemoryAccessViolation("Write to unassigned address")
            errors = set()
            for addr in address:
                try:
                    errs = self.write(addr, value)
                    errors.update(errs)
                except MemoryAccessViolation as error:
                    logging.error(error)
                    errors.add(str(error))
            return errors

        if address in self.base_pointers:
            address = self.base_pointers[address]

        logging.info("Write %s to %s", str(value), str(address))
        logging.debug("Write size %d", value.size)
        self._check_address(address.get_block(), 'write')
        if self.memory[address.get_block()].write(address.offset, value):
            self.time += 1

        return set()

    def free(self, address):
        """ Replaces values in store with a free value """
        if isinstance(address, SizedSet):
            if not address:
                raise MemoryAccessViolation("Invalid Free")
            errors = set()
            for addr in address:
                try:
                    errs = self.free(addr)
                    errors.update(errs)
                except MemoryAccessViolation as error:
                    errors.add(str(error))
            return errors

        if address in self.base_pointers:
            address = self.base_pointers[address]

        self._check_address(address.get_block(), 'free')
        if address.offset != 0:
            raise MemoryAccessViolation("Can only free a base pointer")

        self.memory[address.get_block()].free()
        return set()

    def get_nearest_address(self, address):
        """ returns a pointer to the nearest address
            with an offset set to make difference """
        #address = generate_pointer(address, self)
        if address == 0:
            return self.null_addr
        logging.error("Converting from an unknown integer to a pointer")
        #raise MemoryAccessViolation("Convert from unknown int to pointer")
        if address > self.next_block_id:
            return self.null_addr
        if address in self.memory:
            return generate_pointer(address, None)

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
            self.kont_map[kont_addr] = {kai}
        else: #allocK == 0-cfa or p4f or trivial
            if kont_addr not in self.kont_map:
                self.kont_map[kont_addr] = set()
            self.kont_map[kont_addr].add(kai)

    def read_kont(self, kont_addr):
        """ returns the continuation(s) for the given kont_addr """
        if kont_addr not in self.kont_map:
            raise CESKException("Address not in memory: " + str(kont_addr))
        return self.kont_map[kont_addr]

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
            value = str(Kont.allocK_address)+" "+str(state.ctrl)
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
        self.return_address = address # If Kont returns to an assignment

    def invoke(self, state, value):
        """ Evaluates the return of a function """
        if self.kont_addr is 0: #Halt
            return set(), set()
        errors = set()
        if self.return_address:
            errors = state.stor.write(self.return_address, value)
        new_state = State(self.ctrl, self.envr,
                          state.stor, self.kont_addr)
        return {new_state.get_next()}, errors

    def __eq__(self, other):
        return self.ctrl == other.ctrl and \
               self.envr == other.envr and \
               self.kont_addr == other.kont_addr and \
               self.return_address == other.return_address

    def __hash__(self):
        result = 7
        result = result * hash(self.ctrl) + 37
        result = result * hash(self.envr) + 53
        result = result * hash(self.kont_addr) + 97
        result = result * hash(self.return_address) + 3
        return result
