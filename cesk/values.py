"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits
import pycparser
import logging
from pydoc import locate

BINOPS = {
    "+" : "__add__",
    "-" : "__sub__",
    "*" : "__mul__",
    "/" : "__truediv__",
    "%" : "__mod__",
    "<" : "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">" : "__gt__",
    ">=": "__ge__",
}

class ArithmeticValue:
    """Abstract class for polymorphism between abstract and concrete values"""
    #data = None #store the value a data type that matches
    #type_of = None #stores the type string
    #size = None #stores the size int

    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        if operator in BINOPS:
            method = self.__getattribute__(BINOPS[operator])
            return method(value)
        else:
            raise NotImplementedError()

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C"""
        return bool(self.data)

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass

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

    def __str__(self):
        if self.data is not None:
            return "(" + self.type_of + ") " + str(self.data)
        return super(ArithmeticValue,self).__str__()

    def set_data(self, new_data):
        self.data = new_data

class UnitializedValue(ArithmeticValue):
    """ Type to represent a unitialized value of a certian size """
    bad_use_str = 'Use of a unitialized value'
 
    def __init__(self, size):
        self.size = size
        self.data = None
        self.type_of = 'uninitialized'

    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        raise Exception(UnitializedValue.bad_use_str)        

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C"""
        raise Exception(UnitializedValue.bad_use_str)

    def get_value(self, offset, num_bytes):
        """ Returns 0, should only be valid if called from write """
        return 0
 
class Integer(ArithmeticValue): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""

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

    def set_data(self, new_data):
        self.data = self.bound(new_data)

    def bound(self, value):
        """ Simulates two's complement overflow of integral types """
        #if value > self.max_value:
        #    value = value - (self.max_value - self.min_value)
        #elif value < self.min_value:
        #    value = value + (self.max_value - self.min_value)
        #return value

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
            #result +=  pow(2,(self.size*8))
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            #Get all of the bytes
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result



class Char(Integer):
    """Concrete implementation of an char Type"""
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

class Float(ArithmeticValue):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a float.
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

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO
        return self.data

class ReferenceValue(ArithmeticValue): #pylint:disable=all
    """Abstract Class for polymorphism between Arrays, Pointers, ect."""

    def dereference(self):
        pass

    def index(self, stor, list_of_index):
        pass

    def index_for_address(self, stor, list_of_index):
        pass


class Pointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a Pointer to a store address."""

    def __init__(self, address, holding_stor, type_size, offset=0):
        self.data = int(address)
        self.stor = holding_stor
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
    
    def dereference(self):
        """Reads the address the pointer points to and returns value"""
        if self.data == 0:
            raise Exception("SegFault")
        return self.stor.read(self)

    def index(self, stor, list_of_index):
        """Reads the address with a given offset from the pointer"""
        return self.index_for_address(list_of_index).dereference()

    def index_for_address(self, list_with_offset):
        """Finds the address with a given offset from the pointer"""
        if self.data == 0:
            raise Exception("SegFault")
        if len(list_with_offset) != 1:
            raise Exception("Invalid ArrayRef on Pointer")
        offset = list_with_offset[0]
        return self.stor.add_offset_to_pointer(self, offset)

    def __add__(self, other):
        if isinstance(other, Integer):
            offset = other.data
        elif isinstance(other, int):
            offset = other
        else:
            raise Exception("Pointers can only be added to int")
        return self.stor.add_offset_to_pointer(self, offset)

    def __sub__(self, other):
        if isinstance(other, Integer):
            offset = -1 * other.data
            return self.stor.add_offset_to_pointer(self, offset)
        elif isinstance(other, int):
            offset = -1 * other
            return self.stor.add_offset_to_pointer(self, offset)
        elif isinstance(other, Pointer):
            return Integer(self.data - other.data, 'int')
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +' size '+ str(self.type_size)

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

# needs to know what size it needs to be sometimes
def generate_constant_value(value, type_of='int'):
    """ Given a string, parse it as a constant value. """
    if type_of == 'string':
        raise NotImplementedError("Need to implement string constant")
        #return PtrDecl([], TypeDecl(None, [], IdentifierType(['char'])))
    elif type_of == 'float':
        if value[-1] in "fF":
            return Float(value,'float')
        elif value[-1] in "lL":
            return Float(value,'long double')
        else:
            return Float(value, 'double') 
    elif type_of == 'int':
        u = ''
        if value[-1] in "uU":
            u = 'unsigned '
            value = value[:-1]
        if value[-1] not in "lL":
            val = int(value, 0)
            if val <= limits.RANGES['unsigned '+type_of].max:
                return Integer(val, u+type_of)
        else:
            value = value[:-1]
        type_of = 'long '+type_of
        val = int(value, 0)

        if val <= limits.RANGES['unsigned '+type_of].max:
            return Integer(val, u+type_of)
        type_of = 'long '+type_of
        if val <= limits.RANGES['unsigned '+type_of].max:
            return Integer(val, u+type_of)

    elif type_of == 'char':
        return Char(value, type_of)

    raise Exception("Unkown Constant Type %s", type_of)


def generate_value(value, type_of='bit_value', size=None):
    """ given value in bits and type_of as string, size for special cases 
        special cases include pointer, bit_value, uninitialized """
    if "char" in type_of:
        return Char(value, type_of)
    if type_of in limits.RANGES:
        return Integer(value, type_of)
    if "float" in type_of or "double" in type_of:
        return Float(value, type_of)
    if type_of == 'bit_value':
        return Integer(value, type_of, size)

    if type_of == 'pointer':
        raise Exception('Pointer not expected here/not valid to change dynamically')

    if type_of == 'uninitialized':
        return Integer(value, 'bit_value', size)

    raise Exception("Unexpected value type %s",type_of)

def generate_unitialized_value(size):
   """ Generates special value that is unitialized but has a size """
   return UnitializedValue(size)

def generate_default_value(size):
    """Generates a default value of the given size (used for uninitialized
    variables)."""
    value = Integer(0, 'bit_value', size)
    return value


def generate_pointer(address, stor, size):
    """Given a address (int) package it into a pointer"""
    return Pointer(address, stor, size, 0)


import cesk.linksearch as ls
def copy_pointer(pointer, ptr_type=None, state=None):
    """ Given a point a type and the state
        generate the cast if needed pointer (shallow copy of pointer) """
    if ptr_type is None:
        size = pointer.type_size
    else: #cast to ptr of different type
        sizes = []
        ls.get_sizes(ptr_type, sizes, state) #returns alignment
        size = sum(sizes)
    return Pointer(pointer.data, pointer.stor, size, pointer.offset)

def generate_null_pointer(stor):
    """ Build a pointer that will not dereference """
    return Pointer(0, stor, 1)

def cast(value, typedeclt, state=None): #pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    n = None

    if isinstance(typedeclt, pycparser.c_ast.Typename):
        n = cast(value, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        if isinstance(value, ReferenceValue): 
            n = copy_pointer(value, typedeclt.type, state)
        else:
            #normal number being turned into a pointer not valid to dereference
            #TODO manage tracking of this
            logging.debug(" Cast %s to %s", str(value), str(typedeclt))
            address = state.stor.get_nearest_address(value.data)
            n = copy_pointer(address, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.TypeDecl):
        types = typedeclt.type.names
        n = generate_value(value.get_value(), " ".join(types))
    else:
        logging.error('\tUnsupported cast: ' + str(typedeclt.type))
        raise Exception("Unsupported cast")
    
    assert n.data != None
    return n
