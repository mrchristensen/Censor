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
    #data = None #store the value
    #type_of = None #stores the type
    #size = None #stores the size

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

 
class Integer(ArithmeticValue): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""
    def bound(self, value):
        # TODO document
        if self.type_of != "":
            n = value - self.min_value
            m = self.max_value - self.min_value + 1
            k = n % m
            x = k + self.min_value
            return x
        else:
            return value
        
    def __init__(self, data, type_of):
        if type_of is None or type_of is "":
            self.type_of = ""
            self.size = None
            self.min_value = 0
            self.max_value = None
            self.data = int(data)
        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())
            self.min_value, self.max_value = limits.RANGES[type_of]
            self.data = self.bound(data)

    def __add__(self, other):
        value = self.bound(self.data + other.data)
        return Integer(value, self.type_of)

    def __sub__(self, other):
        value = self.bound(self.data - other.data)
        return Integer(value, self.type_of)

    def __mul__(self, other):
        value = self.bound(self.data * other.data)
        return Integer(value, self.type_of)

    def __truediv__(self, other):
        value = self.bound(self.data // other.data)
        return Integer(value, self.type_of)

    def __mod__(self, other):
        value = self.bound(self.data % other.data)
        return Integer(value, self.type_of)

    def get_value(self, start=0, num_bytes=None):
        """value of the unsigned bits stored"""
        if ((num_bytes is None) or
                (start == 0 and num_bytes == self.size)):
            if self.data < 0:
                return pow(2, self.size) + self.data
            else:
                return self.data
        assert start >= 0

        result = self.data
        if self.data < 0:
            result += pow(2, self.size) #should never reach here if size is not initiallized

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

    def get_value(self, start=0, num_bytes=None):
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

    def __init__(self, address, holding_stor, offset=0):
        self.data = int(address)
        self.stor = holding_stor
        self.size = limits.CONFIG.get_word_size()
        self.offset = offset

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
        return self.stor.read(self.data)

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
        if self.data == 0:
            return self
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
            return self.data - other.data
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return 'Address '+str(self.data)

    def get_value(self, start=0, num_bytes=None):
        """value of the unsigned bits stored"""
        if ((num_bytes is None) or
                (start == 0 and num_bytes == self.size)):
            return self.data

        result = self.data
        if self.data < 0:
            result += pow(2, self.size) #should never reach here if size is not initiallized

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result


class PointerVal(Pointer):
    """ Pointer to a store address with offset and size """
    def __init__(self, address, holding_stor, read_size, offset):
        self.data = int(address)
        self.stor = holding_stor
        self.size = limits.CONFIG.get_word_size()
        self.type_of = 'pointer'
        self.read_size = read_size
        self.offset = offset #stores the offset from the address
        logging.debug(" Made "+str(self))

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
        val = self.stor.read(self.data)
        if self.offset == 0 and val.size == self.read_size:
            return val
        if val.size is None:
            logging.debug("No size %s %d",str(val),self.offset)
            return Integer(val.data // (2**(self.offset*8)),None)
        logging.debug("Dereference val=%s at %d for %d/%d",str(val),self.offset,self.read_size,val.size)
        result = 0
        bytes_to_read = self.read_size
        start = self.offset
        ptr = PointerVal(self.data, self.stor, self.read_size, self.offset)
        while bytes_to_read != 0:
            num_possible = min(bytes_to_read, val.size - start)
            result += val.get_value(start, num_possible) * pow(2, self.read_size - bytes_to_read)
            bytes_to_read -= num_possible
            if bytes_to_read > 0:
                start = 0
                ptr = self.stor.add_offset_to_pointer(ptr, num_possible)
                val = self.stor.read(ptr.data)                
            else:
                break 
        return Integer(result, None) 

    def __str__(self):
        return 'PointerVal at '+str(self.data)+'.'+str(self.offset) +' '+ str(self.read_size)

# TODO Dallin: discuss default type_of with Kyle
def generate_constant_value(value, type_of='int'):
    """Given a string, parse it as a constant value."""
    if "char" in type_of:
        return Char(value, type_of)
    if "float" in type_of:
        return Float(value, 'double')
    return Integer(int(value,0), type_of)


def generate_default_value(typedecl): #pylint: disable=unused-argument
    """Generates a default value of the given type (used for uninitialized
    variables)."""
    return generate_constant_value("0", typedecl)


def generate_pointer(address, stor, offset=0):
    """Given a address (int) package it into a pointer"""
    return Pointer(address, stor, offset)


import cesk.linksearch as ls
def generate_pointer_value(pointer, ptr_type=None, state=None):
    """Given a address (int) package it into a pointer"""
    if ptr_type is None:
        if isinstance(pointer, PointerVal):
            size = pointer.read_size
        else:
            size = pointer.dereference().size
    else:
        sizes = []
        ls.get_sizes(ptr_type, sizes, state) #returns alignment
        size = sum(sizes)
    return PointerVal(pointer.data, pointer.stor, size, pointer.offset)

def generate_null_pointer():
    return Pointer(0, None)

def cast(value, typedeclt, state=None): #pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    n = None
    #logging.debug('CAST: '+str(value)+" to type "+str(typedeclt))

    if isinstance(typedeclt, pycparser.c_ast.Typename):
        n = cast(value, typedeclt.type)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        # TODO This code may need to be more thoroughly tested
        # TODO Document well, include questions about more obscure test cases
        if isinstance(value, ReferenceValue): 
            n = generate_pointer_value(value, typedeclt.type, state)
        else:
            address = state.stor.get_nearest_address(value.data)
            n = generate_pointer_value(address, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.TypeDecl):
        types = typedeclt.type.names
        n = generate_constant_value(str(value.data), " ".join(types))
    else:
        logging.error('\tUnsupported cast: ' + str(typedeclt.type))
        raise Exception("Unsupported cast")
    
    assert n.data != None
    return n
