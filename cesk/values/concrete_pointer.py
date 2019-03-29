'''Concerte Implementation of all the Types'''
from copy import deepcopy
import cesk.limits as limits
from .base_values import ReferenceValue, ByteValue, BaseInteger
from .factory import Factory

class ConcretePointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    """ implementation of a Pointer to a store address."""
    def __init__(self, address, type_size, offset=0):
        self.data = int(address)
        self.size = limits.CONFIG.get_word_size()
        self.type_size = type_size
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
        if isinstance(other, Factory.getIntegerClass()):
            ptr.offset += other.data
        elif isinstance(other, int):
            ptr.offset += other
        else:
            raise Exception("Pointers can only be added to int")
        return ptr

    def __sub__(self, other):
        ptr = deepcopy(self)

        if isinstance(other, Factory.getIntegerClass()):
            ptr.offset += -1 * other.data
            return ptr
        elif isinstance(other, int):
            ptr.offset += -1 * other
            return ptr
        elif isinstance(other, Factory.getPointerClass()):
            return Factory.Integer((self.data+self.offset) -
                                   (other.data+other.offset), 'long')
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        if self.data == 0:
            return "<NULL_POINTER>"
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +\
                ' size '+ str(self.type_size)

    def __repr__(self):
        if self.data == 0:
            return str(self)
        return super.__repr__()

    def __hash__(self):
        return (hash(self.data) + 7) * hash(self.size)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.data+self.offset == other
        return self.data == other.data and self.offset == other.offset

    def get_block(self):
        """ return block identifier """
        return self.data

    def get_byte_value(self, start=-1, num_bytes=None):
        """ value of the unsigned bits stored from start to start+num_bytes """
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

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Not a valid conversion """
        raise Exception("Making a pointer from bytevalue is not valid")
