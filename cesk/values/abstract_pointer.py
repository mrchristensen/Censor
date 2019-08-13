'''Abstact Pointer class that uses the
    Abstracted integer object as its offset'''
from copy import deepcopy
import cesk.limits as limits
from cesk.exceptions import MemoryAccessViolation
from .base_values import ReferenceValue, ByteValue, BaseInteger
from .factory import Factory

class AbstractPointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    '''Implementation of a Pointer to a store address.
        if it changes by a non const amount then it is top'''

    def __init__(self, address, type_size, offset=Factory.Integer(0, 'long')):
        self.data = int(address)
        self.size = limits.CONFIG.get_word_size()
        self.type_size = type_size
        if isinstance(offset, int):
            offset = Factory.Integer(offset, 'long')
        self.offset = offset
        self.type_of = 'pointer'

    def equals(self, other):
        if not isinstance(other, ReferenceValue):
            if isinstance(other, BaseInteger):
                return other.equals(self)
            return Factory.Integer(0, 'int')
        return Factory.Integer(int(self.data == other.data and
                                   self.offset == other.offset), 'int')

    def __lt__(self, other):
        return Factory.Integer(int(self.data < other.data), 'int')

    def __le__(self, other):
        return Factory.Integer(int(self.data <= other.data), 'int')

    def __ne__(self, other):
        return Factory.Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Factory.Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Factory.Integer(int(self.data >= other.data), 'int')

    def __add__(self, other):
        ptr = deepcopy(self)
        if isinstance(other, (Factory.getIntegerClass(), int)):
            ptr.offset = ptr.offset + other
        else:
            raise Exception("Pointers can only be added to int")
        return ptr

    def __sub__(self, other):
        ptr = deepcopy(self)
        if isinstance(other, Factory.getIntegerClass()):
            ptr.offset = ptr.offset - other
            return ptr
        elif isinstance(other, int):
            ptr.offset = ptr.offset - Factory.Integer(other, 'long')
            return ptr
        elif isinstance(other, Factory.getPointerClass()):
            if self.get_block() != other.get_block():
                raise MemoryAccessViolation("Invalid pointer difference")
            return Factory.Integer(self.offset.data, 'long') - \
                   Factory.Integer(other.offset.data, 'long')
        else:
            raise Exception("Pointers can only be subtracted by int,"+
                            " or used in pointer difference.")

    def __hash__(self):
        return ((self.data*7)+3)*hash(self.offset)

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return False
        return self.data == other.data and \
               self.offset == other.offset and \
               self.type_size == other.type_size

    def __str__(self):
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +\
                ' size '+ str(self.type_size)

    def get_byte_value(self, start=-1, num_bytes=None):
        '''Value of the unsigned bits stored from start to start+num_bytes'''
        if not isinstance(self.offset, int):
            return ByteValue(self.size)
        result = self.data + self.offset
        if self.data < 0:
            result += pow(2, self.size)
        if start == -1:
            start = 0
            num_bytes = self.size

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        byte_value = ByteValue(num_bytes)
        byte_value.fromInt(result)

        return byte_value

    def get_block(self):
        '''Returns block identifier'''
        return self.data
