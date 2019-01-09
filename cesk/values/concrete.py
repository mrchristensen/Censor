'''Concerte Implementation of all the Types'''
from .base_values import BaseFloat, BaseInteger, ReferenceValue, ByteValue
import cesk.limits as limits
from copy import deepcopy
import random
import struct

class Float(BaseFloat):  #pylint:disable=too-few-public-methods
    """ implementation of a float.
    NOTE: this class will represent 'float,' and 'double,' and 'long double'
    from C99 as a 64 bit floating point number. This gives some potentially
    incorrect rounding for c programs that use the 'float' or 'long double'
    data types, which is supposed to be represented as a 32 or float."""

    def __init__(self, data, type_of):
        self.data = float(data)
        self.type_of = type_of
        self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):
        return Float(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return Float(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return Float(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return Float(self.data / other.data, self.type_of)
        
    def __lt__(self, other):
        return Integer(int(self.data < other.data), 'int')
        
    def __le__(self, other):
        return Integer(int(self.data <= other.data), 'int')
        
    def __eq__(self, other):
        return Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Integer(int(self.data >= other.data), 'int')

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        if start == -1:
            num_bytes = self.size
            start = 0
        if self.size == 4:
            byte_array = struct.pack('!f', self.data)
        elif self.size == 8:
            byte_array = struct.pack('!d', self.data)
        else:
            return ByteValue(num_bytes) #returns top number of bytes

        byte_value = ByteValue()
        for i in range(num_bytes):
            byte_value.append(ByteValue.fromByte(byte_array[start+i]))

        return byte_value

    def __str__(self):
        return "%f" % self.data

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        float_value = cls(0.0, type_of)
        if float_value.size == 4 and byte_value.size == 4:
            float_value.data = struct.unpack('!f', byte_value.get_bytes())
        elif float_value.size == 8 and byte_value.size == 8:
            float_value.data = struct.unpack('!d', byte_value.get_bytes())

        return float_value

class Integer(BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type"""

    def __init__(self, data, type_of, size = 0):
        if type_of is 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**size - 1 
            self.data = int(data)
        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())
            self.min_value, self.max_value = limits.RANGES[type_of]
            self.data = self.bound(data)

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        data = 0
        place = 1
        for bit in byte_value.bits[::-1]:
            if bit == ByteValue.one:
                data += place
            elif bit == ByteValue.top:
                data += place*random.randint(0, 1)#unknown value pick a ranodm value
            place *= 2

        return cls(data, type_of, byte_value.size)

    def __add__(self, other):
        value = self.bound(self.data + other.data)
        return Integer(value, self.type_of, self.size)

    def __sub__(self, other):
        value = self.bound(self.data - other.data)
        return Integer(value, self.type_of, self.size)

    def __mul__(self, other):
        value = self.bound(self.data * other.data)
        return Integer(value, self.type_of, self.size)

    def __truediv__(self, other):
        value = self.bound(self.data // other.data)
        return Integer(value, self.type_of, self.size)

    def __mod__(self, other):
        value = self.bound(self.data % other.data)
        return Integer(value, self.type_of, self.size)
        
    def __lt__(self, other):
        return Integer(int(self.data < other.data), 'int')
        
    def __le__(self, other):
        return Integer(int(self.data <= other.data), 'int')
        
    def __eq__(self, other):
        return Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Integer(int(self.data >= other.data), 'int')

    def bound(self, value):
        """ Simulates two's complement overflow of integral types """
        n = value - self.min_value
        m = self.max_value - self.min_value + 1
        k = n % m
        x = k + self.min_value
        return x

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        result = self.data
        byte_value = None
        if self.data < 0:
            result += self.max_value - self.min_value + 1 #make unsigned
            
        if not ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            result //= 2**(start*8) #reduce to just the part needed
            result %= pow(2, num_bytes*8)
            byte_value = ByteValue(num_bytes)
        else:
            byte_value = ByteValue(self.size)

        byte_value.fromInt(result)
        return byte_value

class Char(Integer):
    """ implementation of an char Type"""
    def __init__(self, data, type_of='char'):
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            v = ord(char)
        else:
            v = data
        super().__init__(v, type_of)

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        data = 0
        place = 1
        for bit in byte_value.bits[::-1]:
            if bit == ByteValue.one:
                data += place
            elif bit == ByteValue.top:
                data += place*random.randint(0, 1)#unknown value pick a ranodm value
            place *= 2

        return cls(data, type_of)

    def __add__(self, other):
        value = super().__add__(other).data
        return Char(value, self.type_of)

    def __sub__(self, other):
        value = super().__sub__(other).data
        return Char(value, self.type_of)

    def __mul__(self, other):
        value = super().__mul__(other).data
        return Char(value, self.type_of)

    def __truediv__(self, other):
        value = super().__truediv__(other).data
        return Char(value, self.type_of)

    def __mod__(self, other):
        value = super().__mod__(other).data
        return Char(value, self.type_of)

    def get_char(self): 
        return chr(self.data)

    def __str__(self):
        try:
            return chr(self.data)
        except ValueError: # does not map to ascii (e.g. negative chars)
            return str(self.data)

class Pointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    """ implementation of a Pointer to a store address."""

    def __init__(self, address, type_size, offset=0):
        self.data = int(address)
        self.size = limits.CONFIG.get_word_size()
        self.type_size = type_size
        self.offset = offset
        self.type_of = 'pointer'

    def __hash__(self):
        return self.data

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return Integer(0, 'int')
        return Integer(int(self.data == other.data), 'int')
        
    def __lt__(self, other):
        return Integer(int(self.data < other.data), 'int')
        
    def __le__(self, other):
        return Integer(int(self.data <= other.data), 'int')

    def __ne__(self, other):
        return Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Integer(int(self.data >= other.data), 'int')

    def update(self, stor):
        """ moves the pointer along the pred and succ map """
        #if self.offset < 0 or self.offset >= self.type_size:
        offset = self.offset
        self.offset = 0
        ptr = stor.add_offset_to_pointer(self, offset)
        self.offset = ptr.offset
        self.data = ptr.data

    def __add__(self, other):
        ptr = deepcopy(self)
        if isinstance(other, Integer):
            ptr.offset += other.data
        elif isinstance(other, int):
            ptr.offset += other
        else:
            raise Exception("Pointers can only be added to int")
        return ptr

    def __sub__(self, other):
        ptr = deepcopy(self)

        if isinstance(other, Integer):
            ptr.offset += -1 * other.data
            return ptr
        elif isinstance(other, int):
            ptr.offset += -1 * other
            return ptr
        elif isinstance(other, Pointer):
            return Integer((self.data+self.offset) - (other.data+other.offset), 'long')
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +\
                ' size '+ str(self.type_size)

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
    def from_byte_value(cls, byte_value, type_size):
        """ Not a valid conversion """
        raise Exception("Making a pointer from bytevalue is not valid")
