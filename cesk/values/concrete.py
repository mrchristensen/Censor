'''Concerte Implementation of all the Types'''
from .base_values import BaseFloat, BaseInteger, ReferenceValue
import cesk.limits as limits
from copy import deepcopy

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

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        return self.data

    def __str__(self):
        return "%f" % self.data

class Integer(BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type"""

    def __init__(self, data, type_of, size=1):
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

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        result = self.data
        if self.data < 0:
            result += self.max_value - self.min_value + 1
            
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            #Get all of the bytes
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result

class Char(Integer):
    """ implementation of an char Type"""
    def __init__(self, data, type_of='char'):
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            v = ord(char)
        else:
            v = data
        super().__init__(v, type_of)

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
        return chr(self.data)

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
            return Integer((self.get_value() - other.get_value()), 'int')
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +\
                ' size '+ str(self.type_size)

    def get_value(self, start=-1, num_bytes=None):
        """ value of the unsigned bits stored from start to start+num_bytes """
        result = self.data + self.offset
        if self.data < 0:
            result += pow(2, self.size)
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result
