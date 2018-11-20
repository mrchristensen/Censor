'''Abstract data values'''

from .base_values import BaseFloat, BaseInteger, ReferenceValue
import cesk.limits as limits
from copy import deepcopy
from enum import Enum

class AbstractLiterals(Enum):
    '''Declarations of abstractions of literals'''
    TOP = 0
    MINUS = 1
    PLUS = 2
    ZERO = 3


class Float(BaseFloat):  #pylint:disable=too-few-public-methods
    """Abstraction of Float where Float can only be T"""

    def __init__(self, data, type_of):
        self.data = set([AbstractLiterals.TOP])
        self.type_of = type_of
        self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):
        return Float(0, self.type_of)

    def __sub__(self, other):
        return Float(0, self.type_of)

    def __mul__(self, other):
        return Float(0, self.type_of)

    def __truediv__(self, other):
        return Float(0, self.type_of)

    def __lt__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def __le__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def __eq__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def __ne__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def __gt__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def __ge__(self, other):
        return Integer(set([AbstractLiterals.ZERO, AbstractLiterals.PLUS]), 'int')

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        return self.data
    
    def get_truth_value(self):
        return set([True, False])

class Integer(BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type for PLUS-MINUS-ZERO
        Assuming no overflow happens"""

    def __init__(self, data, type_of, size=1):
        self.data = set()
        if not isinstance(data, set):
            data = {data}
        for element in data:
            if isinstance(element, AbstractLiterals):
                self.data.add(element)
            elif element == 0:
                self.data.add(AbstractLiterals.ZERO)
            elif element < 0:
                self.data.add(AbstractLiterals.MINUS)
            elif element > 0:
                self.data.add(AbstractLiterals.PLUS)
            else:
                raise Exception("Unkown value" +  str(element))
        if AbstractLiterals.TOP in self.data or (AbstractLiterals.MINUS in self.data and AbstractLiterals.PLUS in self.data and AbstractLiterals.ZERO in AbstractLiterals):
            self.data = set([AbstractLiterals.TOP])

        if type_of is 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**size - 1 

        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())
            self.min_value, self.max_value = limits.RANGES[type_of]

    def __add__(self, other):
        value = set()
        for ele1 in self.data:
            for ele2 in other.data:
                if ele1 == AbstractLiterals.MINUS and ele2 == AbstractLiterals.MINUS:
                    value.add(-1)
                elif ele1 == AbstractLiterals.PLUS and ele2 == AbstractLiterals.PLUS:
                    value.add(1)
                elif ele1 == AbstractLiterals.ZERO:
                    value.add(ele2)
                elif ele2 == AbstractLiterals.ZERO:
                    value.add(ele1)
                else:
                    value = set([AbstractLiterals.TOP])
                    break
        return Integer(value, self.type_of, self.size)

    def __neg__(self):
        value = set()
        if AbstractLiterals.ZERO in self.data:
            value.add(0)
        if AbstractLiterals.MINUS in self.data:
            value.add(1)
        if AbstractLiterals.PLUS in self.data:
            value.add(-1)
        return Integer(value, self.type_of, self.size)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        value = set()
        # Handle Top
        if AbstractLiterals.TOP in self.data or AbstractLiterals.TOP in other.data:
            if len(self.data) == 1 and AbstractLiterals.ZERO in self.data:
                return Integer(set([0]), self.type_of, self.size)
            if len(other.data) == 1 and AbstractLiterals.ZERO in other.data:
                return Integer(set([0]), self.type_of, self.size)
            return Integer(set([AbstractLiterals.TOP]), self.type_of, self.size)
        for ele1 in self.data:
            for ele2 in other.data:
                if ele1 == AbstractLiterals.ZERO or ele2 == AbstractLiterals.ZERO:
                    value.add(0)
                elif ele1 == ele2:
                    value.add(1)
                else:
                    value.add(-1)
        return Integer(value, self.type_of, self.size)

    def __truediv__(self, other):
        value = None
        return Integer(value, self.type_of, self.size)

    def __mod__(self, other):
        value = None
        return Integer(value, self.type_of, self.size)

    def __lt__(self, other):
        value = set()
        if AbstractLiterals.TOP in self.data or AbstractLiterals.TOP in other.data:
            return Integer(set([0,1]), 'int')
        if AbstractLiterals.PLUS in self.data:
            value.add(0)
        if AbstractLiterals.PLUS in other.data:
            value.add(1)
        if AbstractLiterals.MINUS in self.data:
            value.add(1)
        if AbstractLiterals.MINUS in other.data:
            value.add(0)
        if AbstractLiterals.ZERO in self.data and AbstractLiterals.ZERO in other.data:
            value.add(0)
        return Integer(value, 'int')

    def __le__(self, other):
        return (other < self).__not__()

    def __eq__(self, other):
        value = set()
        if AbstractLiterals.TOP in self.data or AbstractLiterals.TOP in other.data:
            return Integer(set([0,1]), 'int')
        if AbstractLiterals.PLUS in self.data:
            value.add(0)
            if AbstractLiterals.PLUS in other.data:
                return Integer(set([0,1]), 'int')
        if AbstractLiterals.MINUS in self.data:
            value.add(0)
            if AbstractLiterals.MINUS in other.data:
                return Integer(set([0,1]), 'int')
        if AbstractLiterals.ZERO in self.data:
            if AbstractLiterals.ZERO in other.data:
                value.add(1)
            if AbstractLiterals.MINUS in other.data:
                value.add(0)
            if AbstractLiterals.PLUS in other.data:
                value.add(0)

        return Integer(value, 'int')

    def __not__(self):
        not_values = set()
        if AbstractLiterals.TOP in self.data:
            return Integer(set([0,1]), 'int')
        if AbstractLiterals.PLUS in self.data or AbstractLiterals.MINUS in self.data:
            not_values.add(0)
        if AbstractLiterals.ZERO in self.data:
            not_values.add(1)
        return Integer(not_values, 'int')

    def __ne__(self, other):
        return (self == other).__not__()

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return (self < other).__not__()

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


    def get_truth_value(self):
        values = set()
        for val in self.data:
            if val == AbstractLiterals.ZERO:
                values.add(False)
            elif val == AbstractLiterals.TOP:
                values.add(True)
                values.add(False)
            else:
                values.add(True)
        return values


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
